#!/usr/bin/env python3
"""Export FULL historical data from Snowflake (2017-now)"""
import snowflake.connector
import csv
import os
from datetime import datetime

print("="*80)
print("EXPORTING FULL HISTORY FROM SNOWFLAKE (2017 - NOW)")
print("="*80)

print("\n📡 Connecting to Snowflake...")
conn = snowflake.connector.connect(
    user='vietanh1803',
    password='Vanhdzai1803@!',
    account='BRWNIAD-WC21582',
    warehouse='COMPUTE_WH',
    database='STOCKS',
    schema='PUBLIC'
)
print("✅ Connected!")

cursor = conn.cursor()

# Check data range
print("\n📊 Checking available data...")
cursor.execute("""
    SELECT 
        MIN(DATE) as earliest,
        MAX(DATE) as latest,
        COUNT(*) as total,
        COUNT(DISTINCT TICKER) as tickers
    FROM PRICES_DAILY
""")

earliest, latest, total, tickers = cursor.fetchone()
print(f"  Time Range: {earliest} → {latest}")
print(f"  Total Records: {total:,}")
print(f"  Unique Tickers: {tickers}")

# Auto-confirm for automation
print(f"\n⚠️  Will export {total:,} records from {earliest} to {latest}!")
print("✅ Auto-confirmed (running in batch mode)")

# Export
print(f"\n📥 Exporting {total:,} records...")
print("This may take 5-10 minutes...")

cursor.execute("""
    SELECT 
        TICKER,
        DATE,
        CLOSE as price,
        VOLUME,
        VOLUME as total_volume,
        (CLOSE - OPEN) as change,
        CASE 
            WHEN OPEN = 0 THEN 0
            ELSE ((CLOSE - OPEN) / OPEN * 100)
        END as change_percent,
        HIGH as ceiling_price,
        LOW as floor_price,
        OPEN as reference_price,
        HIGH as highest_price,
        LOW as lowest_price,
        CLOSE as bid_price,
        CLOSE as ask_price
    FROM PRICES_DAILY
    WHERE DATE >= '2017-01-01'
    ORDER BY DATE, TICKER
""")

filename = f'full_history_{datetime.now().strftime("%Y%m%d")}.csv'

with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'ticker', 'time', 'price', 'volume', 'total_volume',
        'change', 'change_percent', 'ceiling_price', 'floor_price',
        'reference_price', 'highest_price', 'lowest_price',
        'bid_price', 'ask_price'
    ])
    
    count = 0
    start_time = datetime.now()
    
    for row in cursor:
        writer.writerow(row)
        count += 1
        
        if count % 10000 == 0:
            elapsed = (datetime.now() - start_time).seconds
            rate = count / elapsed if elapsed > 0 else 0
            remaining = (total - count) / rate if rate > 0 else 0
            print(f"  ✓ {count:,} / {total:,} ({count*100//total}%) - "
                  f"Rate: {rate:.0f} rec/s - ETA: {remaining/60:.1f} min")

elapsed_total = (datetime.now() - start_time).seconds
print(f"\n✅ Export complete!")
print(f"  File: {filename}")
print(f"  Records: {count:,}")
print(f"  Time: {elapsed_total//60}m {elapsed_total%60}s")
print(f"  Size: {os.path.getsize(filename)/1024/1024:.1f} MB")

conn.close()

print(f"\n🎯 Next step: Import to PostgreSQL")
print(f"Run: ./import_full_history.sh")

