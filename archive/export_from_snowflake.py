#!/usr/bin/env python3
"""Export data from Snowflake to CSV"""
import snowflake.connector
import csv

print("Connecting to Snowflake...")
conn = snowflake.connector.connect(
    user='vietanh1803',
    password='Vanhdzai1803@!',
    account='BRWNIAD-WC21582',
    warehouse='COMPUTE_WH',
    database='STOCKS',
    schema='PUBLIC'
)

cursor = conn.cursor()

# Export PRICES_DAILY
print("\nExporting PRICES_DAILY...")
cursor.execute("""
    SELECT 
        TICKER,
        DATE,
        CLOSE as price,
        VOLUME,
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

with open('prices_daily.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ticker', 'time', 'price', 'volume', 'total_volume', 
                     'change', 'change_percent', 'ceiling_price', 'floor_price',
                     'reference_price', 'highest_price', 'lowest_price',
                     'bid_price', 'ask_price'])
    count = 0
    for row in cursor:
        writer.writerow(row)
        count += 1
        if count % 1000 == 0:
            print(f"  {count:,} records...")

print(f"✅ Exported {count:,} records to prices_daily.csv")

# Export VNSTOCK_INTRADAY
print("\nExporting VNSTOCK_INTRADAY...")
cursor.execute("""
    SELECT 
        TICKER,
        TRADE_TIME,
        PRICE,
        VOLUME,
        VOLUME as total_volume,
        PRICE_CHANGE,
        PERCENT_CHANGE,
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

with open('vnstock_intraday.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['ticker', 'time', 'price', 'volume', 'total_volume',
                     'change', 'change_percent', 'ceiling_price', 'floor_price',
                     'reference_price', 'highest_price', 'lowest_price',
                     'bid_price', 'ask_price'])
    count = 0
    for row in cursor:
        writer.writerow(row)
        count += 1
        if count % 1000 == 0:
            print(f"  {count:,} records...")

print(f"✅ Exported {count:,} records to vnstock_intraday.csv")

conn.close()
print("\n🎉 Export complete! Now run import_to_postgres.sh")

