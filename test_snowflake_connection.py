#!/usr/bin/env python3
"""
Test Snowflake Connection
Kiểm tra kết nối với Snowflake dựa trên config trong .env
"""

import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv()

def test_snowflake_connection():
    """Test connection to Snowflake"""
    
    print("=" * 70)
    print("🔍 KIỂM TRA KẾT NỐI SNOWFLAKE")
    print("=" * 70)
    print()
    
    # Get credentials from .env
    snowflake_account = os.getenv('SNOWFLAKE_ACCOUNT', '')
    snowflake_user = os.getenv('SNOWFLAKE_USER', '')
    snowflake_password = os.getenv('SNOWFLAKE_PASSWORD', '')
    snowflake_database = os.getenv('SNOWFLAKE_DATABASE', 'STOCKS')
    snowflake_schema = os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
    snowflake_warehouse = os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH')
    snowflake_role = os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
    
    print("📋 Configuration từ .env:")
    print(f"   Account:   {snowflake_account}")
    print(f"   User:      {snowflake_user}")
    print(f"   Password:  {'*' * len(snowflake_password) if snowflake_password else '(empty)'}")
    print(f"   Database:  {snowflake_database}")
    print(f"   Schema:    {snowflake_schema}")
    print(f"   Warehouse: {snowflake_warehouse}")
    print(f"   Role:      {snowflake_role}")
    print()
    
    # Check if credentials are set
    if not all([snowflake_account, snowflake_user, snowflake_password]):
        print("❌ THIẾU CREDENTIALS!")
        print("   Vui lòng cập nhật .env với Snowflake credentials")
        return False
    
    # Use account directly
    account = snowflake_account
    
    print("🔄 Đang kiểm tra kết nối...")
    print()
    
    try:
        # Import snowflake connector
        import snowflake.connector
        
        print("✅ snowflake-connector-python đã được cài đặt")
        print()
        
        # Try to connect
        print("🔌 Đang kết nối với Snowflake...")
        
        conn = snowflake.connector.connect(
            account=account,
            user=snowflake_user,
            password=snowflake_password,
            database=snowflake_database,
            schema=snowflake_schema,
            warehouse=snowflake_warehouse,
            role=snowflake_role
        )
        
        print("✅ KẾT NỐI THÀNH CÔNG!")
        print()
        
        # Test query
        print("🧪 Chạy test query...")
        cursor = conn.cursor()
        
        # Get current account info
        cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE()")
        result = cursor.fetchone()
        
        print()
        print("📊 Thông tin kết nối:")
        print(f"   Account:   {result[0]}")
        print(f"   User:      {result[1]}")
        print(f"   Role:      {result[2]}")
        print(f"   Database:  {result[3]}")
        print(f"   Schema:    {result[4]}")
        print(f"   Warehouse: {result[5]}")
        print()
        
        # Check if table exists
        print("🔍 Kiểm tra table REALTIME_QUOTES...")
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = '{snowflake_schema}' 
            AND TABLE_NAME = 'REALTIME_QUOTES'
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            print("✅ Table REALTIME_QUOTES đã tồn tại")
            
            # Count records
            cursor.execute(f"SELECT COUNT(*) FROM {snowflake_database}.{snowflake_schema}.REALTIME_QUOTES")
            count = cursor.fetchone()[0]
            print(f"   Số records: {count:,}")
            
            if count > 0:
                # Get latest record
                cursor.execute(f"""
                    SELECT TICKER, TIME, PRICE 
                    FROM {snowflake_database}.{snowflake_schema}.REALTIME_QUOTES 
                    ORDER BY TIME DESC 
                    LIMIT 1
                """)
                latest = cursor.fetchone()
                print(f"   Latest record: {latest[0]} at {latest[1]} - Price: {latest[2]}")
        else:
            print("⚠️  Table REALTIME_QUOTES chưa tồn tại")
            print("   Sẽ được tạo tự động khi Snowflake sync chạy lần đầu")
        
        print()
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("=" * 70)
        print("✅ TẤT CẢ KIỂM TRA HOÀN TẤT - KẾT NỐI OK!")
        print("=" * 70)
        print()
        print("🎯 Bạn có thể:")
        print("   1. Start Snowflake sync: make up-snowflake")
        print("   2. Production setup: sudo make prod-setup-snowflake")
        print()
        
        return True
        
    except ImportError:
        print("❌ snowflake-connector-python chưa được cài đặt!")
        print()
        print("📦 Cài đặt bằng lệnh:")
        print("   pip install snowflake-connector-python")
        print()
        return False
        
    except snowflake.connector.errors.DatabaseError as e:
        print(f"❌ LỖI KẾT NỐI: {e}")
        print()
        print("🔧 Kiểm tra lại:")
        print("   1. Snowflake account có đúng không?")
        print("   2. Username/password có đúng không?")
        print("   3. Warehouse đang chạy không?")
        print("   4. Có quyền truy cập database/schema không?")
        print()
        return False
        
    except Exception as e:
        print(f"❌ LỖI: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_snowflake_connection()
    sys.exit(0 if success else 1)

