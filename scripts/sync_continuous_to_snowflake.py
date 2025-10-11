"""
Continuous sync from PostgreSQL to Snowflake.
Runs periodically to sync new data.
"""

import os
import logging
import time
from datetime import datetime
import psycopg2
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PostgreSQL config
PG_HOST = os.getenv('POSTGRES_HOST', 'postgres')
PG_PORT = os.getenv('POSTGRES_PORT', '5432')
PG_DB = os.getenv('POSTGRES_DB', 'stock_db')
PG_USER = os.getenv('POSTGRES_USER', 'admin')
PG_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin')

# Snowflake config
SF_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT', '')
SF_USER = os.getenv('SNOWFLAKE_USER', '')
SF_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD', '')
SF_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
SF_DATABASE = os.getenv('SNOWFLAKE_DATABASE', 'STOCKS')
SF_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
SF_ROLE = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')

# Sync interval (seconds)
SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', '300'))  # Default: 5 minutes


def get_pg_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )


def get_sf_connection():
    """Get Snowflake connection."""
    return snowflake.connector.connect(
        account=SF_ACCOUNT,
        user=SF_USER,
        password=SF_PASSWORD,
        warehouse=SF_WAREHOUSE,
        database=SF_DATABASE,
        schema=SF_SCHEMA,
        role=SF_ROLE
    )


def sync_new_data():
    """Sync new data from PostgreSQL to Snowflake."""
    try:
        logger.info("Starting sync cycle...")
        
        # Connect to databases
        pg_conn = get_pg_connection()
        sf_conn = get_sf_connection()
        
        # Get latest timestamp in Snowflake
        sf_cursor = sf_conn.cursor()
        sf_cursor.execute("""
            SELECT MAX(TIME) as latest_time
            FROM REALTIME_QUOTES
        """)
        result = sf_cursor.fetchone()
        latest_sf_time = result[0] if result and result[0] else '2017-01-01'
        
        logger.info(f"Latest Snowflake time: {latest_sf_time}")
        
        # Get new records from PostgreSQL
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute("""
            SELECT ticker, time, price, volume, total_volume,
                   change, change_percent, ceiling_price, floor_price,
                   reference_price, highest_price, lowest_price,
                   bid_price, ask_price, processed_time
            FROM realtime_quotes
            WHERE processed_time > %s
            ORDER BY processed_time
            LIMIT 10000
        """, (latest_sf_time,))
        
        records = pg_cursor.fetchall()
        
        if not records:
            logger.info("No new records to sync")
            pg_conn.close()
            sf_conn.close()
            return 0
        
        logger.info(f"Found {len(records)} new records to sync")
        
        # Insert into Snowflake
        sf_cursor.execute("""
            CREATE TABLE IF NOT EXISTS REALTIME_QUOTES (
                TICKER VARCHAR(10),
                TIME TIMESTAMP,
                PRICE FLOAT,
                VOLUME BIGINT,
                TOTAL_VOLUME BIGINT,
                CHANGE FLOAT,
                CHANGE_PERCENT FLOAT,
                CEILING_PRICE FLOAT,
                FLOOR_PRICE FLOAT,
                REFERENCE_PRICE FLOAT,
                HIGHEST_PRICE FLOAT,
                LOWEST_PRICE FLOAT,
                BID_PRICE FLOAT,
                ASK_PRICE FLOAT,
                PROCESSED_TIME TIMESTAMP,
                PRIMARY KEY (TICKER, TIME)
            )
        """)
        
        # Batch insert
        insert_sql = """
            INSERT INTO REALTIME_QUOTES (
                TICKER, TIME, PRICE, VOLUME, TOTAL_VOLUME,
                CHANGE, CHANGE_PERCENT, CEILING_PRICE, FLOOR_PRICE,
                REFERENCE_PRICE, HIGHEST_PRICE, LOWEST_PRICE,
                BID_PRICE, ASK_PRICE, PROCESSED_TIME
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        sf_cursor.executemany(insert_sql, records)
        sf_conn.commit()
        
        logger.info(f"Successfully synced {len(records)} records to Snowflake")
        
        # Close connections
        pg_cursor.close()
        sf_cursor.close()
        pg_conn.close()
        sf_conn.close()
        
        return len(records)
        
    except Exception as e:
        logger.error(f"Error during sync: {e}", exc_info=True)
        return 0


def main():
    """Main continuous sync loop."""
    logger.info("Starting continuous Snowflake sync...")
    logger.info(f"Sync interval: {SYNC_INTERVAL} seconds")
    logger.info(f"PostgreSQL: {PG_HOST}:{PG_PORT}/{PG_DB}")
    logger.info(f"Snowflake: {SF_ACCOUNT}/{SF_DATABASE}/{SF_SCHEMA}")
    
    if not SF_ACCOUNT or not SF_USER or not SF_PASSWORD:
        logger.warning("Snowflake credentials not configured. Sync disabled.")
        return
    
    total_synced = 0
    cycle = 0
    
    try:
        while True:
            cycle += 1
            logger.info(f"--- Sync cycle {cycle} ---")
            
            synced = sync_new_data()
            total_synced += synced
            
            logger.info(f"Total synced so far: {total_synced} records")
            logger.info(f"Next sync in {SYNC_INTERVAL} seconds...")
            
            time.sleep(SYNC_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error in sync loop: {e}", exc_info=True)
    finally:
        logger.info(f"Sync stopped. Total synced: {total_synced} records")


if __name__ == "__main__":
    main()


