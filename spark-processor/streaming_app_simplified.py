"""
Simplified Spark Structured Streaming application for stock data.
Reads from Kafka and writes to PostgreSQL only (no Snowflake streaming).
"""

import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, current_timestamp
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, LongType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'stock-quotes')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'stock_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin')

# Define schema for JSON data
stock_schema = StructType([
    StructField("ticker", StringType(), True),
    StructField("time", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("volume", LongType(), True),
    StructField("total_volume", LongType(), True),
    StructField("change", DoubleType(), True),
    StructField("change_percent", DoubleType(), True),
    StructField("ceiling_price", DoubleType(), True),
    StructField("floor_price", DoubleType(), True),
    StructField("reference_price", DoubleType(), True),
    StructField("highest_price", DoubleType(), True),
    StructField("lowest_price", DoubleType(), True),
    StructField("bid_price", DoubleType(), True),
    StructField("ask_price", DoubleType(), True),
])


def write_to_postgres_batch(batch_df, batch_id):
    """Write batch to PostgreSQL."""
    try:
        if batch_df.rdd.isEmpty():
            logger.info(f"Batch {batch_id}: Empty batch, skipping")
            return
            
        count = batch_df.count()
        logger.info(f"Batch {batch_id}: Processing {count} records")
        
        jdbc_url = f"jdbc:postgresql://{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        
        batch_df.write \
            .format("jdbc") \
            .option("url", jdbc_url) \
            .option("dbtable", "realtime_quotes") \
            .option("user", POSTGRES_USER) \
            .option("password", POSTGRES_PASSWORD) \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
        
        logger.info(f"Batch {batch_id}: Successfully written {count} records to PostgreSQL")
    except Exception as e:
        logger.error(f"Batch {batch_id}: Error writing to PostgreSQL: {e}", exc_info=True)


def main():
    """Main streaming application."""
    try:
        logger.info("Starting Simplified Stock Streaming Application...")
        
        # Create Spark session
        spark = SparkSession.builder \
            .appName("StockStreamingSimplified") \
            .config("spark.jars", "/opt/spark/jars-extra/*") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint-simple") \
            .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
            .config("spark.streaming.kafka.consumer.cache.enabled", "false") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark session created")
        
        # Read from Kafka
        logger.info(f"Reading from Kafka topic: {KAFKA_TOPIC}")
        
        kafka_df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", KAFKA_TOPIC) \
            .option("startingOffsets", "latest") \
            .option("maxOffsetsPerTrigger", 100) \
            .option("failOnDataLoss", "false") \
            .load()
        
        logger.info("Kafka stream loaded")
        
        # Parse JSON
        parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_value") \
            .select(from_json(col("json_value"), stock_schema).alias("data")) \
            .select("data.*")
        
        # Convert timestamp and add processing time
        final_df = parsed_df \
            .withColumn("time", to_timestamp(col("time"))) \
            .withColumn("processed_time", current_timestamp())
        
        logger.info("Starting streaming query...")
        
        # Write using foreachBatch
        query = final_df \
            .writeStream \
            .foreachBatch(write_to_postgres_batch) \
            .outputMode("append") \
            .trigger(processingTime='10 seconds') \
            .option("checkpointLocation", "/tmp/checkpoint-simple") \
            .start()
        
        logger.info("Streaming query started successfully")
        logger.info(f"Consuming from Kafka: {KAFKA_BOOTSTRAP_SERVERS}/{KAFKA_TOPIC}")
        logger.info(f"Writing to PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
        
        # Wait for termination
        query.awaitTermination()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Error in streaming application: {e}", exc_info=True)
        raise
    finally:
        logger.info("Stopping Spark session")
        spark.stop()


if __name__ == "__main__":
    main()





