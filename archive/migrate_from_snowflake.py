#!/usr/bin/env python3
"""
Migration script for your Snowflake data
Maps PRICES_DAILY and VNSTOCK_INTRADAY to PostgreSQL stock_quotes
"""
import snowflake.connector
import psycopg2
from datetime import datetime
import sys

print("="*80)
print("SNOWFLAKE → POSTGRESQL MIGRATION")
print("="*80)

# Connect to Snowflake
print("\n📡 Connecting to Snowflake...")
sf_conn = snowflake.connector.connect(
    user='vietanh1803',
    password='Vanhdzai1803@!',
    account='BRWNIAD-WC21582',
    warehouse='COMPUTE_WH',
    database='STOCKS',
    schema='PUBLIC'
)
print("✅ Snowflake connected!")

# Connect to PostgreSQL
print("\n🐘 Connecting to PostgreSQL...")
pg_conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='stock_db',
    user='admin',
    password='admin'
)
print("✅ PostgreSQL connected!")

# Get data summary
sf_cursor = sf_conn.cursor()
sf_cursor.execute("SELECT COUNT(*) FROM PRICES_DAILY")
daily_count = sf_cursor.fetchone()[0]

sf_cursor.execute("SELECT COUNT(*) FROM VNSTOCK_INTRADAY")
intraday_count = sf_cursor.fetchone()[0]

print(f"\n📊 Data available:")
print(f"  PRICES_DAILY: {daily_count:,} records")
print(f"  VNSTOCK_INTRADAY: {intraday_count:,} records")

# Ask user which to migrate
print(f"\n🔄 Migration options:")
print(f"  1. PRICES_DAILY ({daily_count:,} records) - Historical daily prices")
print(f"  2. VNSTOCK_INTRADAY ({intraday_count:,} records) - Intraday data")
print(f"  3. Both")

choice = input("\nSelect (1/2/3): ").strip()

migrated_total = 0

# Migrate PRICES_DAILY
if choice in ['1', '3']:
    print(f"\n📥 Migrating PRICES_DAILY...")
    
    # Fetch data
    sf_cursor.execute("""
        SELECT 
            TICKER,
            DATE as time,
            CLOSE as price,
            VOLUME as volume,
            VOLUME as total_volume,
            (CLOSE - OPEN) as change,
            ((CLOSE - OPEN) / OPEN * 100) as change_percent,
            HIGH as ceiling_price,
            LOW as floor_price,
            OPEN as reference_price,
            HIGH as highest_price,
            LOW as lowest_price,
            CLOSE as bid_price,
            CLOSE as ask_price
        FROM PRICES_DAILY
        ORDER BY DATE, TICKER
    """)
    
    # Prepare PostgreSQL insert
    pg_cursor = pg_conn.cursor()
    
    batch = []
    count = 0
    
    for row in sf_cursor:
        batch.append(row)
        
        if len(batch) >= 1000:
            pg_cursor.executemany("""
                INSERT INTO stock_quotes (
                    ticker, time, price, volume, total_volume,
                    change, change_percent, ceiling_price, floor_price,
                    reference_price, highest_price, lowest_price,
                    bid_price, ask_price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ticker, time) DO UPDATE SET
                    price = EXCLUDED.price,
                    volume = EXCLUDED.volume
            """, batch)
            pg_conn.commit()
            count += len(batch)
            print(f"  ✓ Migrated {count:,} / {daily_count:,} records...")
            batch = []
    
    # Insert remaining
    if batch:
        pg_cursor.executemany("""
            INSERT INTO stock_quotes (
                ticker, time, price, volume, total_volume,
                change, change_percent, ceiling_price, floor_price,
                reference_price, highest_price, lowest_price,
                bid_price, ask_price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker, time) DO UPDATE SET
                price = EXCLUDED.price,
                volume = EXCLUDED.volume
        """, batch)
        pg_conn.commit()
        count += len(batch)
    
    migrated_total += count
    print(f"  ✅ PRICES_DAILY: {count:,} records migrated!")

# Migrate VNSTOCK_INTRADAY
if choice in ['2', '3']:
    print(f"\n📥 Migrating VNSTOCK_INTRADAY...")
    
    # Fetch data
    sf_cursor.execute("""
        SELECT 
            TICKER,
            TRADE_TIME as time,
            PRICE as price,
            VOLUME as volume,
            VOLUME as total_volume,
            PRICE_CHANGE as change,
            PERCENT_CHANGE as change_percent,
            PRICE * 1.07 as ceiling_price,
            PRICE * 0.93 as floor_price,
            PRICE - PRICE_CHANGE as reference_price,
            PRICE as highest_price,
            PRICE as lowest_price,
            PRICE as bid_price,
            PRICE as ask_price
        FROM VNSTOCK_INTRADAY
        WHERE TRADE_TIME IS NOT NULL
        ORDER BY TRADE_TIME, TICKER
    """)
    
    # Prepare PostgreSQL insert
    pg_cursor = pg_conn.cursor()
    
    batch = []
    count = 0
    
    for row in sf_cursor:
        batch.append(row)
        
        if len(batch) >= 1000:
            pg_cursor.executemany("""
                INSERT INTO stock_quotes (
                    ticker, time, price, volume, total_volume,
                    change, change_percent, ceiling_price, floor_price,
                    reference_price, highest_price, lowest_price,
                    bid_price, ask_price
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ticker, time) DO UPDATE SET
                    price = EXCLUDED.price,
                    volume = EXCLUDED.volume
            """, batch)
            pg_conn.commit()
            count += len(batch)
            print(f"  ✓ Migrated {count:,} / {intraday_count:,} records...")
            batch = []
    
    # Insert remaining
    if batch:
        pg_cursor.executemany("""
            INSERT INTO stock_quotes (
                ticker, time, price, volume, total_volume,
                change, change_percent, ceiling_price, floor_price,
                reference_price, highest_price, lowest_price,
                bid_price, ask_price
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (ticker, time) DO UPDATE SET
                price = EXCLUDED.price,
                volume = EXCLUDED.volume
        """, batch)
        pg_conn.commit()
        count += len(batch)
    
    migrated_total += count
    print(f"  ✅ VNSTOCK_INTRADAY: {count:,} records migrated!")

# Summary
print(f"\n" + "="*80)
print(f"✅ MIGRATION COMPLETE!")
print(f"="*80)
print(f"Total records migrated: {migrated_total:,}")

# Verify
pg_cursor.execute("SELECT COUNT(*), MIN(time), MAX(time) FROM stock_quotes")
total, min_time, max_time = pg_cursor.fetchone()
print(f"\n📊 PostgreSQL Summary:")
print(f"  Total records: {total:,}")
print(f"  Time range: {min_time} → {max_time}")

sf_conn.close()
pg_conn.close()

print(f"\n🎉 Ready! Access dashboard at: http://localhost:8501")

