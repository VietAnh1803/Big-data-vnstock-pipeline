#!/usr/bin/env python3
"""Scan ALL tables in Snowflake for historical data from 2017"""
import snowflake.connector
from datetime import datetime

print("=" * 100)
print("🔍 SCANNING ALL SNOWFLAKE TABLES FOR 2017-NOW DATA")
print("=" * 100)

# Connect
conn = snowflake.connector.connect(
    user='vietanh1803',
    password='Vanhdzai1803@!',
    account='BRWNIAD-WC21582',
    warehouse='COMPUTE_WH',
    database='STOCKS',
    schema='PUBLIC'
)

cursor = conn.cursor()

# Get ALL tables
print("\n[1/3] Discovering all tables...")
cursor.execute("SHOW TABLES IN STOCKS.PUBLIC")
all_tables = [row[1] for row in cursor.fetchall()]
print(f"✅ Found {len(all_tables)} tables: {', '.join(all_tables)}")

# Scan each table
print("\n[2/3] Scanning each table for historical data...\n")

tables_with_2017_data = []

for table_name in all_tables:
    print(f"\n{'='*80}")
    print(f"📊 TABLE: {table_name}")
    print(f"{'='*80}")
    
    try:
        # Get count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_count = cursor.fetchone()[0]
        print(f"  📈 Total Records: {total_count:,}")
        
        if total_count == 0:
            print(f"  ⚠️  Empty table, skipping...")
            continue
        
        # Get columns
        cursor.execute(f"DESCRIBE TABLE {table_name}")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"  📋 Columns ({len(columns)}): {', '.join(columns[:15])}")
        
        # Try to find date/time column
        date_columns = [c for c in columns if any(keyword in c.upper() for keyword in ['DATE', 'TIME', 'TIMESTAMP', 'TS', 'DT'])]
        
        if not date_columns:
            print(f"  ⚠️  No date/time column found, skipping...")
            continue
        
        print(f"  📅 Date columns: {', '.join(date_columns)}")
        
        # Check each date column for 2017 data
        for date_col in date_columns:
            try:
                # Get min/max dates
                cursor.execute(f"SELECT MIN({date_col}), MAX({date_col}) FROM {table_name}")
                min_date, max_date = cursor.fetchone()
                
                if min_date is None or max_date is None:
                    continue
                
                print(f"\n  🕒 {date_col}:")
                print(f"     Min: {min_date}")
                print(f"     Max: {max_date}")
                
                # Convert to datetime for comparison
                if isinstance(min_date, str):
                    try:
                        min_year = int(min_date[:4])
                    except:
                        continue
                else:
                    min_year = min_date.year if hasattr(min_date, 'year') else None
                
                if min_year and min_year <= 2017:
                    print(f"  ✅ HAS DATA FROM 2017! (starts: {min_date})")
                    
                    # Get count from 2017
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {date_col} >= '2017-01-01'")
                    count_2017 = cursor.fetchone()[0]
                    print(f"  📊 Records from 2017-now: {count_2017:,}")
                    
                    # Get sample
                    cursor.execute(f"SELECT * FROM {table_name} WHERE {date_col} >= '2017-01-01' LIMIT 2")
                    print(f"\n  Sample from 2017:")
                    for i, row in enumerate(cursor.fetchall(), 1):
                        print(f"    Row {i}: {row[:8]}")
                    
                    tables_with_2017_data.append({
                        'table': table_name,
                        'date_column': date_col,
                        'min_date': min_date,
                        'max_date': max_date,
                        'count_2017_now': count_2017,
                        'total_count': total_count
                    })
                else:
                    print(f"  ℹ️  Data starts from {min_year}, not from 2017")
                    
            except Exception as e:
                print(f"  ⚠️  Error checking {date_col}: {e}")
                continue
        
    except Exception as e:
        print(f"  ❌ Error scanning table: {e}")

# Summary
print("\n" + "="*100)
print("🎯 SUMMARY")
print("="*100)

if tables_with_2017_data:
    print(f"\n✅ Found {len(tables_with_2017_data)} table(s) with data from 2017:\n")
    for item in tables_with_2017_data:
        print(f"  📊 {item['table']}")
        print(f"     Date Column: {item['date_column']}")
        print(f"     Range: {item['min_date']} → {item['max_date']}")
        print(f"     Records (2017-now): {item['count_2017_now']:,} / {item['total_count']:,}")
        print()
else:
    print("\n❌ NO TABLES WITH DATA FROM 2017 FOUND!")
    print("\n💡 Your Snowflake database only contains recent data (2025)")
    print("   If you need 2017-now data, you'll need to:")
    print("   1. Import historical data into Snowflake first, OR")
    print("   2. Use a different data source for 2017-2024")

conn.close()

print("\n" + "="*100)
print("✅ SCAN COMPLETE")
print("="*100)

