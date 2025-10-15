from pyspark.sql import SparkSession, functions as F, types as T


def build_spark(app_name: str = "quotes-structured-streaming") -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.shuffle.partitions", "200")
        .config("spark.sql.streaming.stateStore.maintenanceInterval", "60s")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )


def get_quote_schema() -> T.StructType:
    return T.StructType(
        [
            T.StructField("ticker", T.StringType()),
            T.StructField("price", T.DoubleType()),
            T.StructField("volume", T.LongType()),
            T.StructField("reference_price", T.DoubleType()),
            T.StructField("highest_price", T.DoubleType()),
            T.StructField("lowest_price", T.DoubleType()),
            T.StructField("time", T.StringType()),  # iso string or epoch
            T.StructField("source", T.StringType()),
        ]
    )


def main():
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    topic = os.getenv("KAFKA_TOPIC", "stock-quotes")

    pg_url = f"jdbc:postgresql://{os.getenv('POSTGRES_HOST', 'postgres')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'stock_db')}"
    pg_user = os.getenv("POSTGRES_USER", "admin")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "admin")

    checkpoint_quotes = os.getenv("CHECKPOINT_QUOTES", "/u01/checkpoints/quotes_clean")
    checkpoint_metrics = os.getenv("CHECKPOINT_METRICS", "/u01/checkpoints/metrics_minute")

    spark = build_spark()

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", bootstrap)
        .option("subscribe", topic)
        .option("startingOffsets", "latest")
        .load()
    )

    schema = get_quote_schema()

    parsed = (
        raw.select(F.from_json(F.col("value").cast("string"), schema).alias("j"))
        .select("j.*")
        .withColumn(
            "event_time",
            F.coalesce(
                F.to_timestamp("time"),
                (F.col("time").cast("double")).cast("timestamp"),
                F.current_timestamp(),
            ),
        )
        .drop("time")
    )

    clean = (
        parsed.withColumn(
            "open_price",
            F.when(F.col("reference_price").isNotNull() & (F.col("reference_price") > 0), F.col("reference_price")).otherwise(
                F.col("price")
            ),
        )
        .withColumn("change", F.when(F.col("open_price") > 0, F.col("price") - F.col("open_price")))
        .withColumn(
            "change_percent",
            F.when(F.col("open_price") > 0, (F.col("price") - F.col("open_price")) / F.col("open_price") * 100),
        )
        .withColumn(
            "change_percent",
            F.when(F.abs(F.col("change_percent")) > 50, F.lit(None)).otherwise(F.col("change_percent")),
        )
        .filter((F.col("price") > 0) & (F.col("open_price") > 0))
    )

    # Minute metrics with watermark
    metrics = (
        clean.withWatermark("event_time", "10 minutes")
        .groupBy(F.window("event_time", "1 minute").alias("w"), F.col("ticker"))
        .agg(
            F.last("price").alias("last_price"),
            F.sum("volume").alias("sum_volume"),
            F.max("highest_price").alias("max_price"),
            F.min("lowest_price").alias("min_price"),
            F.avg("price").alias("avg_price"),
        )
        .select(
            F.col("ticker"),
            F.col("w.start").alias("minute_start"),
            F.col("w.end").alias("minute_end"),
            "last_price",
            "sum_volume",
            "max_price",
            "min_price",
            "avg_price",
        )
    )

    def sink_quotes(df, epoch):
        (df.select(
            "ticker",
            F.col("event_time").alias("time"),
            "price",
            "volume",
            "change",
            "change_percent",
            "open_price",
            F.col("highest_price").alias("high_price"),
            F.col("lowest_price").alias("low_price"),
        ).write.format("jdbc")
         .option("url", pg_url)
         .option("dbtable", "public.realtime_quotes_clean")
         .option("user", pg_user).option("password", pg_pass)
         .mode("append").save())

    def sink_metrics(df, epoch):
        (df.write.format("jdbc")
         .option("url", pg_url)
         .option("dbtable", "public.realtime_metrics_minute")
         .option("user", pg_user).option("password", pg_pass)
         .mode("append").save())

    q1 = (
        clean.writeStream.foreachBatch(sink_quotes)
        .option("checkpointLocation", checkpoint_quotes)
        .outputMode("append")
        .start()
    )

    q2 = (
        metrics.writeStream.foreachBatch(sink_metrics)
        .option("checkpointLocation", checkpoint_metrics)
        .outputMode("update")
        .start()
    )

    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    import os

    main()



