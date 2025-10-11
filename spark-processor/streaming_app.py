"""
Spark Structured Streaming application for processing stock market data.
Reads from Kafka, processes, and writes to both Snowflake and PostgreSQL.
"""

import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, to_timestamp, current_timestamp, window
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, 
    LongType, TimestampType
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'stock-quotes')

# PostgreSQL configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'stock_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin')

# Snowflake configuration
SNOWFLAKE_URL = os.getenv('SNOWFLAKE_URL', '')
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER', '')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD', '')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE', '')
SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'public')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE', '')
SNOWFLAKE_ROLE = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')

# Define schema for incoming JSON data
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


def create_spark_session():
    """Create and configure Spark session with necessary packages."""
    logger.info("Creating Spark session...")
    
    spark = SparkSession.builder \
        .appName("VietnamStockStreamingApp") \
        .config("spark.jars", "/opt/spark/jars-extra/*") \
        .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoint") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    logger.info("Spark session created successfully")
    
    return spark


def write_to_postgres(batch_df, batch_id):
    """Write batch to PostgreSQL."""
    try:
        if batch_df.count() > 0:
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
            
            logger.info(f"Batch {batch_id}: Written {batch_df.count()} records to PostgreSQL")
    except Exception as e:
        logger.error(f"Batch {batch_id}: Error writing to PostgreSQL: {e}")


def write_to_snowflake(batch_df, batch_id):
    """Write batch to Snowflake."""
    try:
        # Only write to Snowflake if credentials are configured
        if not SNOWFLAKE_URL or not SNOWFLAKE_USER or not SNOWFLAKE_PASSWORD:
            logger.warning(f"Batch {batch_id}: Snowflake credentials not configured, skipping Snowflake write")
            return
            
        if batch_df.count() > 0:
            snowflake_options = {
                "sfURL": SNOWFLAKE_URL,
                "sfUser": SNOWFLAKE_USER,
                "sfPassword": SNOWFLAKE_PASSWORD,
                "sfDatabase": SNOWFLAKE_DATABASE,
                "sfSchema": SNOWFLAKE_SCHEMA,
                "sfWarehouse": SNOWFLAKE_WAREHOUSE,
                "sfRole": SNOWFLAKE_ROLE,
                "dbtable": "REALTIME_QUOTES"
            }
            
            batch_df.write \
                .format("snowflake") \
                .options(**snowflake_options) \
                .mode("append") \
                .save()
            
            logger.info(f"Batch {batch_id}: Written {batch_df.count()} records to Snowflake")
    except Exception as e:
        logger.error(f"Batch {batch_id}: Error writing to Snowflake: {e}")


def process_batch(batch_df, batch_id):
    """Process each micro-batch and write to multiple sinks."""
    try:
        logger.info(f"Processing batch {batch_id}...")
        
        # Add processing timestamp
        processed_df = batch_df.withColumn("processed_time", current_timestamp())
        
        # Write to PostgreSQL (for dashboard)
        write_to_postgres(processed_df, batch_id)
        
        # Write to Snowflake (for data warehouse)
        write_to_snowflake(processed_df, batch_id)
        
        logger.info(f"Batch {batch_id} processing completed")
        
    except Exception as e:
        logger.error(f"Error processing batch {batch_id}: {e}")


def main():
    """Main streaming application."""
    logger.info("Starting Vietnam Stock Streaming Application...")
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        # Read from Kafka
        logger.info(f"Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}, topic: {KAFKA_TOPIC}")
        
        kafka_df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", KAFKA_TOPIC) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        logger.info("Successfully connected to Kafka stream")
        
        # Parse JSON data
        parsed_df = kafka_df.select(
            from_json(col("value").cast("string"), stock_schema).alias("data")
        ).select("data.*")
        
        # Convert string timestamp to timestamp type
        transformed_df = parsed_df.withColumn(
            "time",
            to_timestamp(col("time"))
        )
        
        logger.info("Starting streaming query with foreachBatch...")
        
        # Write stream using foreachBatch
        query = transformed_df \
            .writeStream \
            .foreachBatch(process_batch) \
            .outputMode("append") \
            .trigger(processingTime='10 seconds') \
            .start()
        
        logger.info("Streaming query started successfully")
        logger.info("Application is now processing stock data in real-time...")
        
        # Wait for termination
        query.awaitTermination()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
    except Exception as e:
        logger.error(f"Error in streaming application: {e}")
        raise
    finally:
        logger.info("Stopping Spark session...")
        spark.stop()


if __name__ == "__main__":
    main()

