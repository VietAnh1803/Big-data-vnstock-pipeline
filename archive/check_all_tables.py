#!/usr/bin/env python3
"""Check all Snowflake tables"""
import snowflake.connector

conn = snowflake.connector.connect(
    user='vietanh1803',
    password='Vanhdzai1803@!',
    account='BRWNIAD-WC21582',
    warehouse='COMPUTE_WH',
    database='STOCKS',
    schema='PUBLIC'
)

cursor = conn.cursor()

tables = ['PRICES_REALTIME', 'PRICES_DAILY', 'VNSTOCK_INTRADAY', 'MARKET_DATA', 'ORDER_BOOK']

print("=" * 80)
print("CHECKING ALL TABLES")
print("=" * 80)

for table in tables:
    try:
        print(f"\n📊 Table: {table}")
        print("-" * 80)
        
        # Count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  Total Records: {count:,}")
        
        if count > 0:
            # Columns
            cursor.execute(f"SELECT * FROM {table} LIMIT 1")
            columns = [desc[0] for desc in cursor.description]
            print(f"  Columns: {', '.join(columns[:10])}")
            
            # Date range
            if 'TIME' in columns or 'TIMESTAMP' in columns or 'DATE' in columns:
                time_col = 'TIME' if 'TIME' in columns else ('TIMESTAMP' if 'TIMESTAMP' in columns else 'DATE')
                cursor.execute(f"SELECT MIN({time_col}), MAX({time_col}) FROM {table}")
                min_t, max_t = cursor.fetchone()
                print(f"  Time Range: {min_t} → {max_t}")
            
            # Sample
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            print(f"\n  Sample Data:")
            for i, row in enumerate(cursor.fetchall(), 1):
                print(f"    Row {i}: {row[:5]}...")
                
    except Exception as e:
        print(f"  ❌ Error: {e}")

conn.close()

print("\n" + "=" * 80)
print("✅ SCAN COMPLETE")
print("=" * 80)

