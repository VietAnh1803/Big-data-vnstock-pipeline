#!/usr/bin/env python3
"""
Quick script to check what data you have in Snowflake
"""
import snowflake.connector

print("="*60)
print("CHECKING SNOWFLAKE DATA")
print("="*60)

try:
    # Connect
    print("\n📡 Connecting to Snowflake...")
    conn = snowflake.connector.connect(
        user='vietanh1803',
        password='Vanhdzai1803@!',
        account='BRWNIAD-WC21582',
        warehouse='COMPUTE_WH',
        database='STOCKS',
        schema='PUBLIC'
    )
    print("✅ Connected successfully!")
    
    cursor = conn.cursor()
    
    # Check tables
    print("\n📊 Tables in STOCKS.PUBLIC:")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table[1]}")
    
    # Check stock_quotes data
    print("\n📈 Stock Quotes Summary:")
    cursor.execute("""
        SELECT COUNT(*) as total_records,
               COUNT(DISTINCT ticker) as total_tickers,
               MIN(time) as earliest_record,
               MAX(time) as latest_record
        FROM stock_quotes
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"  Total Records: {result[0]:,}")
        print(f"  Total Tickers: {result[1]}")
        print(f"  Earliest: {result[2]}")
        print(f"  Latest: {result[3]}")
    
    # Top tickers by record count
    print("\n🏆 Top 10 Tickers by Record Count:")
    cursor.execute("""
        SELECT ticker, COUNT(*) as record_count
        FROM stock_quotes
        GROUP BY ticker
        ORDER BY record_count DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,} records")
    
    # Recent records
    print("\n🕐 Latest 5 Records:")
    cursor.execute("""
        SELECT ticker, time, price, volume
        FROM stock_quotes
        ORDER BY time DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[2]:,.0f} VND @ {row[1]} (Vol: {row[3]:,})")
    
    print("\n" + "="*60)
    print("✅ DATA CHECK COMPLETE!")
    print("="*60)
    
    # Export suggestion
    total = result[0] if result else 0
    print(f"\n💡 You have {total:,} records ready to migrate!")
    print("\nNext steps:")
    print("1. Follow MIGRATION_MANUAL_STEPS.md to export/import")
    print("2. Or wait for automatic migration fix")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPlease check:")
    print("- Snowflake credentials are correct")
    print("- Database 'STOCKS' exists")
    print("- Table 'stock_quotes' exists")

