#!/usr/bin/env python3
"""
Vietnam Stock Pipeline - Spark Structured Streaming Consumer
Real-time processing of Kafka stock data using Spark Structured Streaming
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Dict, Any

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.streaming import StreamingQuery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VietnamStockSparkConsumer:
    """Spark Structured Streaming Consumer for Vietnam Stock Data"""
    
    def __init__(self):
        """Initialize Spark session and configuration"""
        self.spark = None
        self.kafka_config = {
            "kafka.bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "vietnam-stock-kafka:9092"),
            "subscribe": "realtime_quotes",
            "startingOffsets": "latest",
            "failOnDataLoss": "false",
            # Control per-trigger offsets for stability
            "maxOffsetsPerTrigger": os.getenv("MAX_OFFSETS_PER_TRIGGER", "50000")
        }
        
        self.postgres_config = {
            "url": os.getenv("POSTGRES_URL", "jdbc:postgresql://vietnam-stock-postgres:5432/stock_db"),
            "user": os.getenv("POSTGRES_USER", "stock_app"),
            "password": os.getenv("POSTGRES_PASSWORD", ""),
            "driver": "org.postgresql.Driver"
        }
        
        self._init_spark_session()
    
    def _init_spark_session(self):
        """Initialize Spark session with proper configuration"""
        try:
            self.spark = SparkSession.builder \
                .appName("Vietnam Stock Spark Consumer") \
                .config("spark.master", "local[*]") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .config("spark.sql.streaming.checkpointLocation", "/tmp/spark-checkpoint") \
                .config("spark.sql.streaming.kafka.useDeprecatedOffsetFetching", "false") \
                .config("spark.sql.shuffle.partitions", os.getenv("SPARK_SHUFFLE_PARTITIONS", "200")) \
                .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.postgresql:postgresql:42.6.0") \
                .getOrCreate()
            
            # Set log level
            self.spark.sparkContext.setLogLevel("WARN")
            
            logger.info("Spark session initialized successfully")
            logger.info(f"Spark UI: http://localhost:4040")
            
        except Exception as e:
            logger.error(f"Failed to initialize Spark session: {e}")
            raise
    
    def get_schema(self) -> StructType:
        """Define schema for stock data"""
        return StructType([
            StructField("ticker", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("volume", LongType(), True),
            StructField("change", DoubleType(), True),
            StructField("percent_change", DoubleType(), True),
            StructField("high", DoubleType(), True),
            StructField("low", DoubleType(), True),
            StructField("open_price", DoubleType(), True),
            StructField("close_price", DoubleType(), True),
            StructField("quote_time", StringType(), True),  # Will be converted to time format
            StructField("ingest_time", StringType(), True),  # Will be converted to timestamp
            StructField("data_source", StringType(), True)
        ])
    
    def read_kafka_stream(self):
        """Read data from Kafka topic"""
        try:
            # Read from Kafka
            kafka_df = self.spark \
                .readStream \
                .format("kafka") \
                .options(**self.kafka_config) \
                .load()
            
            # Parse JSON data
            parsed_df = kafka_df.select(
                from_json(col("value").cast("string"), self.get_schema()).alias("data")
            ).select("data.*")
            
            # Data cleaning and validation
            cleaned_df = self._clean_and_validate_data(parsed_df)
            
            logger.info("Kafka stream reading configured with data cleaning")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Failed to read Kafka stream: {e}")
            raise
    
    def _clean_and_validate_data(self, df):
        """Clean and validate stock data"""
        try:
            # Data cleaning transformations
            cleaned_df = df.select(
                # Basic fields - ensure they exist and are valid
                col("ticker").alias("ticker"),
                col("price").alias("price"),
                col("volume").alias("volume"),
                col("change").alias("change"),
                col("percent_change").alias("percent_change"),
                col("high").alias("high"),
                col("low").alias("low"),
                col("open_price").alias("open_price"),
                col("close_price").alias("close_price"),
                
                # Convert quote_time from string to proper time format
                when(col("quote_time").isNull() | (col("quote_time") == ""), 
                     date_format(current_timestamp(), "HH:mm:ss"))
                .otherwise(col("quote_time"))
                .alias("quote_time"),
                
                # Convert ingest_time to proper timestamp
                when(col("ingest_time").isNull() | (col("ingest_time") == ""),
                     current_timestamp())
                .otherwise(to_timestamp(col("ingest_time"), "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX"))
                .alias("ingest_time"),
                
                # Data source validation
                when(col("data_source").isNull() | (col("data_source") == ""),
                     lit("VNStock Real Data"))
                .otherwise(col("data_source"))
                .alias("data_source")
            ).filter(
                # Filter out invalid records
                col("ticker").isNotNull() &
                # Ticker must be 2-5 uppercase letters (exclude series/warrants like MSN02, VSH17, etc.)
                col("ticker").rlike('^[A-Z]{2,5}$') &
                col("price").isNotNull() &
                (col("price") > 0) &
                col("volume").isNotNull() &
                (col("volume") >= 0)
            )
            
            logger.info("Data cleaning and validation completed")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Failed to clean and validate data: {e}")
            # Return original dataframe if cleaning fails
            return df
    
    def write_to_postgres(self, df, epoch_id):
        """Write batch data to PostgreSQL with proper data type handling"""
        try:
            # Debug: Print DataFrame schema
            logger.info(f"DataFrame schema for batch {epoch_id}: {df.schema}")
            
            # Prepare data for PostgreSQL with correct types and column mapping
            # Map ingest_time to 'time' column (primary timestamp in DB)
            prepared_df = df.select(
                col("ticker"),
                col("price"),
                col("volume"),
                col("change"),
                col("percent_change"),
                col("high"),
                col("low"),
                col("open_price"),
                col("close_price"),
                # Map ingest_time to 'time' column (primary timestamp in DB)
                col("ingest_time").alias("time"),
                col("quote_time").cast("string"),
                col("data_source")
            )
            
            # Coalesce partitions to reduce JDBC connection fan-out
            to_write = prepared_df.coalesce(int(os.getenv("JDBC_WRITE_PARTITIONS", "8")))

            # Write to PostgreSQL in batch
            to_write.write \
                .format("jdbc") \
                .option("url", self.postgres_config["url"]) \
                .option("dbtable", "realtime_quotes") \
                .option("user", self.postgres_config["user"]) \
                .option("password", self.postgres_config["password"]) \
                .option("driver", self.postgres_config["driver"]) \
                .option("batchsize", os.getenv("JDBC_BATCH_SIZE", "10000")) \
                .mode("append") \
                .save()
            
            count = prepared_df.count()
            logger.info(f"Batch {epoch_id}: Inserted {count} cleaned records to PostgreSQL")
            
        except Exception as e:
            logger.error(f"Failed to write batch {epoch_id} to PostgreSQL: {e}")
    
    def start_streaming(self):
        """Start Spark Structured Streaming"""
        try:
            logger.info("Starting Spark Structured Streaming...")
            
            # Read Kafka stream
            stream_df = self.read_kafka_stream()
            
            # Start streaming query
            query = stream_df.writeStream \
                .foreachBatch(self.write_to_postgres) \
                .outputMode("append") \
                .trigger(processingTime=os.getenv("STREAM_TRIGGER", "15 seconds")) \
                .option("checkpointLocation", "/tmp/spark-checkpoint") \
                .start()
            
            logger.info("Spark Structured Streaming started")
            logger.info(f"Query ID: {query.id}")
            logger.info(f"Query Name: {query.name}")
            
            return query
            
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            raise
    
    def run(self):
        """Main execution method"""
        try:
            logger.info("Starting Vietnam Stock Spark Consumer...")
            
            # Start streaming
            query = self.start_streaming()
            
            # Keep running
            query.awaitTermination()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            if 'query' in locals():
                query.stop()
        except Exception as e:
            logger.error(f"Error in main execution: {e}")
            raise
        finally:
            if self.spark:
                self.spark.stop()
                logger.info("Spark session stopped")

def main():
    """Main entry point"""
    consumer = VietnamStockSparkConsumer()
    consumer.run()

if __name__ == "__main__":
    main()
