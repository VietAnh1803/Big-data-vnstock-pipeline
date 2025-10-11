"""
Direct Kafka to PostgreSQL consumer (bypassing Spark).
Reads messages from Kafka and writes directly to PostgreSQL.
"""

import os
import json
import logging
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import psycopg2
from psycopg2.extras import execute_batch
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'stock-quotes')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'postgres-consumer-group')

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'stock_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin')

BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))
BATCH_TIMEOUT = int(os.getenv('BATCH_TIMEOUT', '10'))


def get_db_connection():
    """Create PostgreSQL connection."""
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )


def insert_batch(conn, records):
    """Insert batch of records into PostgreSQL."""
    if not records:
        return 0
    
    insert_sql = """
    INSERT INTO realtime_quotes (
        ticker, time, price, volume, total_volume,
        change, change_percent, ceiling_price, floor_price,
        reference_price, highest_price, lowest_price,
        bid_price, ask_price, processed_time
    ) VALUES (
        %(ticker)s, %(time)s, %(price)s, %(volume)s, %(total_volume)s,
        %(change)s, %(change_percent)s, %(ceiling_price)s, %(floor_price)s,
        %(reference_price)s, %(highest_price)s, %(lowest_price)s,
        %(bid_price)s, %(ask_price)s, %(processed_time)s
    )
    ON CONFLICT (ticker, time) DO NOTHING;
    """
    
    try:
        with conn.cursor() as cursor:
            execute_batch(cursor, insert_sql, records, page_size=100)
            conn.commit()
            return len(records)
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting batch: {e}")
        return 0


def process_message(message):
    """Parse and prepare message for database insertion."""
    try:
        data = json.loads(message.value.decode('utf-8'))
        
        # Add processed_time
        data['processed_time'] = datetime.now()
        
        # Convert time string to datetime if needed
        if isinstance(data.get('time'), str):
            try:
                data['time'] = datetime.fromisoformat(data['time'].replace('Z', '+00:00'))
            except:
                data['time'] = datetime.now()
        
        return data
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return None


def main():
    """Main consumer loop."""
    logger.info("Starting Kafka to PostgreSQL consumer...")
    logger.info(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS}/{KAFKA_TOPIC}")
    logger.info(f"PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    logger.info(f"Batch size: {BATCH_SIZE}, Batch timeout: {BATCH_TIMEOUT}s")
    
    # Create Kafka consumer
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: x
    )
    
    logger.info("Kafka consumer created")
    
    # Create database connection
    db_conn = get_db_connection()
    logger.info("PostgreSQL connection established")
    
    batch = []
    last_flush_time = time.time()
    total_processed = 0
    batch_count = 0
    
    try:
        for message in consumer:
            # Process message
            record = process_message(message)
            if record:
                batch.append(record)
            
            # Flush batch if size or timeout reached
            current_time = time.time()
            should_flush = (
                len(batch) >= BATCH_SIZE or
                (batch and current_time - last_flush_time >= BATCH_TIMEOUT)
            )
            
            if should_flush:
                inserted = insert_batch(db_conn, batch)
                batch_count += 1
                total_processed += inserted
                
                logger.info(
                    f"Batch {batch_count}: Inserted {inserted}/{len(batch)} records "
                    f"(Total: {total_processed})"
                )
                
                batch = []
                last_flush_time = current_time
    
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Error in consumer loop: {e}", exc_info=True)
    finally:
        # Flush remaining batch
        if batch:
            inserted = insert_batch(db_conn, batch)
            total_processed += inserted
            logger.info(f"Final batch: Inserted {inserted}/{len(batch)} records")
        
        consumer.close()
        db_conn.close()
        logger.info(f"Consumer stopped. Total processed: {total_processed}")


if __name__ == "__main__":
    main()





