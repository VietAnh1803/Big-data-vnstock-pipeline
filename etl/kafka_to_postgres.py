#!/usr/bin/env python3
"""
Kafka to PostgreSQL Consumer
Consumes messages from Kafka and stores them in PostgreSQL
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def safe_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None

def safe_int(x):
    try:
        if x is None:
            return None
        return int(x)
    except Exception:
        return None

class KafkaToPostgresConsumer:
    def __init__(self):
        self.setup_kafka()
        self.setup_postgres()
        self.batch = []
        self.batch_size = int(os.getenv('BATCH_SIZE', '100'))
        self.batch_timeout = int(os.getenv('BATCH_TIMEOUT', '10'))
        self.prev_close_cache = {}
        
    def setup_kafka(self):
        """Setup Kafka consumer"""
        try:
            load_dotenv()
            
            kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
            topic = os.getenv('KAFKA_TOPIC', 'stock-quotes')
            group_id = os.getenv('KAFKA_GROUP_ID', 'postgres-consumer-group')
            
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=kafka_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda m: m.decode('utf-8') if m else None,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                consumer_timeout_ms=10000
            )
            
            logger.info("✅ Kafka consumer initialized")
            
        except Exception as e:
            logger.error(f"❌ Kafka setup failed: {e}")
            sys.exit(1)
    
    def setup_postgres(self):
        """Setup PostgreSQL connection"""
        try:
            load_dotenv()
            
            self.postgres_host = os.getenv('POSTGRES_HOST', 'postgres')
            self.postgres_port = os.getenv('POSTGRES_PORT', '5432')
            self.postgres_db = os.getenv('POSTGRES_DB', 'stock_db')
            self.postgres_user = os.getenv('POSTGRES_USER', 'admin')
            self.postgres_password = os.getenv('POSTGRES_PASSWORD', 'admin')
            
            self.conn = psycopg2.connect(
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_db,
                user=self.postgres_user,
                password=self.postgres_password
            )
            self.conn.autocommit = True
            
            logger.info("✅ PostgreSQL connection established")
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL setup failed: {e}")
            sys.exit(1)
    
    def process_message(self, message):
        """Process a single Kafka message"""
        try:
            data = message.value or {}

            # Extract event time from payload; fallback to now()
            event_ts = None
            try:
                ts_str = data.get('time') or data.get('timestamp')
                if ts_str:
                    # Accept ISO format; fallback to float epoch
                    if isinstance(ts_str, (int, float)):
                        event_ts = datetime.fromtimestamp(float(ts_str))
                    else:
                        event_ts = datetime.fromisoformat(str(ts_str).replace('Z', '+00:00'))
            except Exception:
                event_ts = None
            if event_ts is None:
                event_ts = datetime.now()

            # Compute price and changes
            price = safe_float(data.get('price'))
            volume = safe_int(data.get('volume'))
            # Prefer reference_price; fallback to open_price
            reference_price = safe_float(data.get('reference_price'))
            if reference_price is None:
                reference_price = safe_float(data.get('open_price'))
            # If still missing, pull previous close from historical_prices
            ticker = data.get('ticker', '')
            if reference_price in (None, 0) and ticker:
                try:
                    if ticker in self.prev_close_cache:
                        reference_price = self.prev_close_cache[ticker]
                    else:
                        with self.conn.cursor() as cursor:
                            cursor.execute(
                                """
                                SELECT close_price
                                FROM historical_prices
                                WHERE ticker = %s
                                ORDER BY trading_date DESC
                                LIMIT 1
                                """,
                                (ticker,)
                            )
                            row = cursor.fetchone()
                            if row and row[0]:
                                reference_price = safe_float(row[0])
                                self.prev_close_cache[ticker] = reference_price
                except Exception:
                    reference_price = reference_price

            highest_price = safe_float(data.get('highest_price'))
            lowest_price = safe_float(data.get('lowest_price'))
            bid_price = safe_float(data.get('bid_price'))
            ask_price = safe_float(data.get('ask_price'))

            # Drop invalid payloads without usable price/ref
            if price in (None, 0) or reference_price in (None, 0):
                return

            # Derive change and change_percent when possible
            if price is not None and reference_price not in (None, 0):
                change = round(price - reference_price, 6)
                change_percent = round((price - reference_price) / reference_price * 100, 6)
            else:
                # If still missing, skip this record
                return

            record = (
                ticker,
                event_ts,  # time
                price or 0.0,
                volume or 0,
                change,
                change_percent,
                reference_price or 0.0,
                highest_price or 0.0,
                lowest_price or 0.0,
                bid_price or 0.0,
                ask_price or 0.0,
                event_ts,
            )

            self.batch.append(record)

            if len(self.batch) >= self.batch_size:
                self.flush_batch()

        except Exception as e:
            logger.error(f"❌ Failed to process message: {e}")
    
    def flush_batch(self):
        """Flush batch to PostgreSQL"""
        if not self.batch:
            return
            
        try:
            query = """
            INSERT INTO realtime_quotes (
                ticker, time, price, volume, change, change_percent,
                reference_price, highest_price, lowest_price, bid_price, ask_price, created_at
            ) VALUES %s
            ON CONFLICT (ticker, time) DO UPDATE SET
                price = EXCLUDED.price,
                volume = EXCLUDED.volume,
                change = EXCLUDED.change,
                change_percent = EXCLUDED.change_percent,
                reference_price = EXCLUDED.reference_price,
                highest_price = EXCLUDED.highest_price,
                lowest_price = EXCLUDED.lowest_price,
                bid_price = EXCLUDED.bid_price,
                ask_price = EXCLUDED.ask_price,
                created_at = EXCLUDED.created_at
            """
            
            with self.conn.cursor() as cursor:
                execute_values(cursor, query, self.batch)
            
            logger.info(f"✅ Batch {len(self.batch)}: Inserted {len(self.batch)} records")
            self.batch = []
            
        except Exception as e:
            logger.error(f"❌ Failed to flush batch: {e}")
            self.batch = []
    
    def run(self):
        """Main consumer loop"""
        logger.info("🚀 Starting Kafka to PostgreSQL consumer...")
        
        batch_count = 0
        total_records = 0
        last_flush = time.time()
        
        try:
            for message in self.consumer:
                self.process_message(message)
                
                # Flush batch based on timeout
                now = time.time()
                if now - last_flush >= self.batch_timeout:
                    self.flush_batch()
                    last_flush = now
                
                total_records += 1
                
        except KeyboardInterrupt:
            logger.info("🛑 Consumer stopped by user")
        except Exception as e:
            logger.error(f"❌ Consumer error: {e}")
        finally:
            # Flush remaining batch
            self.flush_batch()
            self.consumer.close()
            self.conn.close()
            logger.info(f"📊 Total records processed: {total_records}")

if __name__ == "__main__":
    consumer = KafkaToPostgresConsumer()
    consumer.run()
