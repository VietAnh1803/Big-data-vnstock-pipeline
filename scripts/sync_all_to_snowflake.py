#!/usr/bin/env python3
"""
Sync ALL tables to Snowflake for BIG DATA warehouse
Đồng bộ TẤT CẢ bảng lên Snowflake
"""

import os
import sys
import time
import logging
import psycopg2
import snowflake.connector
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
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


def create_snowflake_tables(sf_conn):
    """Create all tables in Snowflake."""
    logger.info("Creating Snowflake tables...")
    
    cursor = sf_conn.cursor()
    
    # Ticker info
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TICKER_INFO (
            ticker VARCHAR(10) PRIMARY KEY,
            company_name VARCHAR(300),
            company_name_eng VARCHAR(300),
            short_name VARCHAR(100),
            exchange VARCHAR(20),
            industry_name VARCHAR(200),
            sector_name VARCHAR(200),
            listed_shares NUMBER(20),
            charter_capital NUMBER(20),
            par_value NUMBER(20),
            listing_date DATE,
            website VARCHAR(300),
            description TEXT,
            phone VARCHAR(50),
            fax VARCHAR(50),
            email VARCHAR(100),
            address TEXT,
            company_type VARCHAR(100),
            created_at TIMESTAMP_NTZ,
            updated_at TIMESTAMP_NTZ,
            synced_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    
    # Balance Sheet
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS BALANCE_SHEET (
            id NUMBER(20) PRIMARY KEY,
            ticker VARCHAR(10),
            report_date DATE,
            quarter NUMBER(2),
            year NUMBER(4),
            total_assets NUMBER(20),
            current_assets NUMBER(20),
            total_liabilities NUMBER(20),
            total_equity NUMBER(20),
            created_at TIMESTAMP_NTZ,
            synced_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    
    # Income Statement
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS INCOME_STATEMENT (
            id NUMBER(20) PRIMARY KEY,
            ticker VARCHAR(10),
            report_date DATE,
            quarter NUMBER(2),
            year NUMBER(4),
            total_revenue NUMBER(20),
            net_revenue NUMBER(20),
            gross_profit NUMBER(20),
            profit_after_tax NUMBER(20),
            eps FLOAT,
            created_at TIMESTAMP_NTZ,
            synced_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    
    # Cash Flow
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CASH_FLOW_STATEMENT (
            id NUMBER(20) PRIMARY KEY,
            ticker VARCHAR(10),
            report_date DATE,
            quarter NUMBER(2),
            year NUMBER(4),
            operating_cash_flow NUMBER(20),
            investing_cash_flow NUMBER(20),
            financing_cash_flow NUMBER(20),
            created_at TIMESTAMP_NTZ,
            synced_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    
    # Financial Ratios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS FINANCIAL_RATIOS (
            id NUMBER(20) PRIMARY KEY,
            ticker VARCHAR(10),
            report_date DATE,
            quarter NUMBER(2),
            year NUMBER(4),
            pe_ratio FLOAT,
            pb_ratio FLOAT,
            roe FLOAT,
            roa FLOAT,
            current_ratio FLOAT,
            debt_to_equity FLOAT,
            created_at TIMESTAMP_NTZ,
            synced_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    
    # Historical Prices
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HISTORICAL_PRICES (
            id NUMBER(20) PRIMARY KEY,
            ticker VARCHAR(10),
            trading_date DATE,
            open_price FLOAT,
            high_price FLOAT,
            low_price FLOAT,
            close_price FLOAT,
            adjusted_close FLOAT,
            volume NUMBER(20),
            change FLOAT,
            change_percent FLOAT,
            created_at TIMESTAMP_NTZ,
            synced_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """)
    
    cursor.close()
    logger.info("✅ Snowflake tables created/verified")


def sync_table(table_name, pg_conn, sf_conn, batch_size=1000):
    """Sync a table from PostgreSQL to Snowflake."""
    logger.info(f"Syncing table: {table_name}")
    
    pg_cursor = pg_conn.cursor()
    sf_cursor = sf_conn.cursor()
    
    # Get row count
    pg_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = pg_cursor.fetchone()[0]
    
    if total_rows == 0:
        logger.info(f"  No data in {table_name}")
        return 0
    
    # Get column names
    pg_cursor.execute(f"SELECT * FROM {table_name} LIMIT 0")
    columns = [desc[0] for desc in pg_cursor.description]
    columns_str = ', '.join(columns)
    placeholders = ', '.join(['%s'] * len(columns))
    
    # Fetch and insert in batches
    pg_cursor.execute(f"SELECT {columns_str} FROM {table_name}")
    
    inserted = 0
    batch = []
    
    for row in pg_cursor:
        batch.append(row)
        
        if len(batch) >= batch_size:
            try:
                sf_cursor.executemany(
                    f"INSERT INTO {table_name.upper()} ({columns_str}) VALUES ({placeholders})",
                    batch
                )
                inserted += len(batch)
                logger.info(f"  Progress: {inserted}/{total_rows} rows")
                batch = []
            except Exception as e:
                logger.error(f"Error inserting batch: {e}")
                batch = []
    
    # Insert remaining
    if batch:
        try:
            sf_cursor.executemany(
                f"INSERT INTO {table_name.upper()} ({columns_str}) VALUES ({placeholders})",
                batch
            )
            inserted += len(batch)
        except Exception as e:
            logger.error(f"Error inserting final batch: {e}")
    
    pg_cursor.close()
    sf_cursor.close()
    
    logger.info(f"✅ {table_name}: {inserted}/{total_rows} rows synced")
    return inserted


def main():
    """Main sync function."""
    logger.info("=" * 70)
    logger.info("SYNCING ALL TABLES TO SNOWFLAKE - BIG DATA WAREHOUSE")
    logger.info("=" * 70)
    
    # Check credentials
    if not all([SF_ACCOUNT, SF_USER, SF_PASSWORD]):
        logger.error("❌ Missing Snowflake credentials!")
        return
    
    try:
        # Connect
        logger.info("Connecting to databases...")
        pg_conn = get_pg_connection()
        sf_conn = get_sf_connection()
        logger.info("✅ Connected to PostgreSQL and Snowflake")
        
        # Create tables
        create_snowflake_tables(sf_conn)
        
        # Sync tables
        tables = [
            'ticker_info',
            'historical_prices',
            'stock_analytics'
        ]
        
        total_synced = 0
        for table in tables:
            try:
                count = sync_table(table, pg_conn, sf_conn)
                total_synced += count
            except Exception as e:
                logger.error(f"Error syncing {table}: {e}")
                continue
        
        pg_conn.close()
        sf_conn.close()
        
        logger.info("=" * 70)
        logger.info(f"✅ SYNC COMPLETED!")
        logger.info(f"   Total rows synced: {total_synced:,}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

