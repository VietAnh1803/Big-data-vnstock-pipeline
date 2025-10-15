#!/usr/bin/env python3
"""
PostgreSQL to Snowflake Data Synchronization Script
- Check data in both databases
- Remove empty tables in Snowflake
- Sync data from PostgreSQL to Snowflake
"""

import os
import sys
import logging
from datetime import datetime
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import urllib.parse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataSyncManager:
    def __init__(self):
        self.postgres_engine = None
        self.snowflake_engine = None
        
    def setup_postgres_connection(self):
        """Setup PostgreSQL connection"""
        try:
            # Use postgres host for container-to-container connection
            user = os.getenv('POSTGRES_USER', 'admin')
            password = os.getenv('POSTGRES_PASSWORD', 'admin123@')
            host = os.getenv('POSTGRES_HOST', 'postgres')  # Use postgres host
            port = os.getenv('POSTGRES_PORT', '5432')
            db = os.getenv('POSTGRES_DB', 'stock_db')
            
            encoded_password = urllib.parse.quote_plus(password)
            connection_string = f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{db}?sslmode=disable"
            
            self.postgres_engine = create_engine(connection_string, pool_pre_ping=True)
            logger.info("✅ PostgreSQL connection established")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return False
    
    def setup_snowflake_connection(self):
        """Setup Snowflake connection"""
        try:
            # Snowflake connection parameters
            snowflake_config = {
                'user': os.getenv('SNOWFLAKE_USER', 'BRWNIAD'),
                'password': os.getenv('SNOWFLAKE_PASSWORD', 'Vanh@123456'),
                'account': os.getenv('SNOWFLAKE_ACCOUNT', 'BRWNIAD-WC21582'),
                'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
                'database': os.getenv('SNOWFLAKE_DATABASE', 'STOCKS'),  # Changed to STOCKS
                'schema': os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
            }
            
            connection_string = f"snowflake://{snowflake_config['user']}:{snowflake_config['password']}@{snowflake_config['account']}/{snowflake_config['database']}/{snowflake_config['schema']}?warehouse={snowflake_config['warehouse']}"
            
            self.snowflake_engine = create_engine(connection_string)
            logger.info("✅ Snowflake connection established")
            return True
        except Exception as e:
            logger.error(f"❌ Snowflake connection failed: {e}")
            return False
    
    def get_postgres_tables_info(self):
        """Get information about PostgreSQL tables"""
        try:
            query = text("""
                SELECT 
                    table_name,
                    (SELECT COUNT(*) FROM information_schema.columns 
                     WHERE table_name = t.table_name AND table_schema = 'public') as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            tables_df = pd.read_sql(query, self.postgres_engine)
            
            # Get row counts for each table
            table_info = []
            for _, row in tables_df.iterrows():
                table_name = row['table_name']
                try:
                    count_query = text(f"SELECT COUNT(*) as row_count FROM {table_name}")
                    count_result = pd.read_sql(count_query, self.postgres_engine)
                    row_count = count_result['row_count'].iloc[0]
                    
                    table_info.append({
                        'table_name': table_name,
                        'column_count': row['column_count'],
                        'row_count': row_count
                    })
                except Exception as e:
                    logger.warning(f"⚠️ Could not get row count for {table_name}: {e}")
                    table_info.append({
                        'table_name': table_name,
                        'column_count': row['column_count'],
                        'row_count': 'ERROR'
                    })
            
            return pd.DataFrame(table_info)
        except Exception as e:
            logger.error(f"❌ Error getting PostgreSQL tables info: {e}")
            return pd.DataFrame()
    
    def get_snowflake_tables_info(self):
        """Get information about Snowflake tables"""
        try:
            query = text("""
                SELECT 
                    TABLE_NAME,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                     WHERE TABLE_NAME = t.TABLE_NAME AND TABLE_SCHEMA = 'PUBLIC') as COLUMN_COUNT
                FROM INFORMATION_SCHEMA.TABLES t
                WHERE TABLE_SCHEMA = 'PUBLIC' 
                AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            
            tables_df = pd.read_sql(query, self.snowflake_engine)
            
            # Get row counts for each table
            table_info = []
            for _, row in tables_df.iterrows():
                table_name = row['TABLE_NAME']
                try:
                    count_query = text(f"SELECT COUNT(*) as ROW_COUNT FROM {table_name}")
                    count_result = pd.read_sql(count_query, self.snowflake_engine)
                    row_count = count_result['ROW_COUNT'].iloc[0]
                    
                    table_info.append({
                        'table_name': table_name,
                        'column_count': row['COLUMN_COUNT'],
                        'row_count': row_count
                    })
                except Exception as e:
                    logger.warning(f"⚠️ Could not get row count for {table_name}: {e}")
                    table_info.append({
                        'table_name': table_name,
                        'column_count': row['COLUMN_COUNT'],
                        'row_count': 'ERROR'
                    })
            
            return pd.DataFrame(table_info)
        except Exception as e:
            logger.error(f"❌ Error getting Snowflake tables info: {e}")
            return pd.DataFrame()
    
    def drop_empty_snowflake_tables(self):
        """Drop empty tables in Snowflake"""
        try:
            snowflake_tables = self.get_snowflake_tables_info()
            empty_tables = snowflake_tables[snowflake_tables['row_count'] == 0]
            
            if empty_tables.empty:
                logger.info("✅ No empty tables found in Snowflake")
                return
            
            logger.info(f"🗑️ Found {len(empty_tables)} empty tables in Snowflake")
            
            for _, table in empty_tables.iterrows():
                table_name = table['table_name']
                try:
                    drop_query = text(f"DROP TABLE IF EXISTS {table_name}")
                    self.snowflake_engine.execute(drop_query)
                    logger.info(f"✅ Dropped empty table: {table_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to drop table {table_name}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error dropping empty tables: {e}")
    
    def sync_table_data(self, table_name):
        """Sync data from PostgreSQL to Snowflake for a specific table"""
        try:
            logger.info(f"🔄 Syncing table: {table_name}")
            
            # Get data from PostgreSQL
            query = text(f"SELECT * FROM {table_name}")
            df = pd.read_sql(query, self.postgres_engine)
            
            if df.empty:
                logger.warning(f"⚠️ Table {table_name} is empty in PostgreSQL")
                return False
            
            logger.info(f"📊 Found {len(df)} rows in PostgreSQL table {table_name}")
            
            # Drop and recreate table in Snowflake
            try:
                drop_query = text(f"DROP TABLE IF EXISTS {table_name}")
                self.snowflake_engine.execute(drop_query)
                logger.info(f"🗑️ Dropped existing table {table_name} in Snowflake")
            except Exception as e:
                logger.warning(f"⚠️ Could not drop table {table_name}: {e}")
            
            # Insert data into Snowflake
            df.to_sql(table_name, self.snowflake_engine, if_exists='replace', index=False, method='multi')
            logger.info(f"✅ Successfully synced {len(df)} rows to Snowflake table {table_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to sync table {table_name}: {e}")
            return False
    
    def sync_all_tables(self):
        """Sync all tables from PostgreSQL to Snowflake"""
        try:
            postgres_tables = self.get_postgres_tables_info()
            
            if postgres_tables.empty:
                logger.error("❌ No tables found in PostgreSQL")
                return
            
            logger.info(f"🔄 Starting sync of {len(postgres_tables)} tables")
            
            success_count = 0
            for _, table in postgres_tables.iterrows():
                table_name = table['table_name']
                row_count = table['row_count']
                
                if row_count == 0:
                    logger.info(f"⏭️ Skipping empty table: {table_name}")
                    continue
                
                if self.sync_table_data(table_name):
                    success_count += 1
            
            logger.info(f"🎉 Sync completed! {success_count}/{len(postgres_tables)} tables synced successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during sync: {e}")
    
    def generate_sync_report(self):
        """Generate a comprehensive sync report"""
        try:
            logger.info("📋 Generating sync report...")
            
            postgres_tables = self.get_postgres_tables_info()
            snowflake_tables = self.get_snowflake_tables_info()
            
            print("\n" + "="*80)
            print("📊 DATA SYNCHRONIZATION REPORT")
            print("="*80)
            
            print(f"\n🗄️ PostgreSQL Database:")
            print(f"   Total tables: {len(postgres_tables)}")
            if not postgres_tables.empty:
                total_rows = postgres_tables['row_count'].sum()
                print(f"   Total rows: {total_rows:,}")
                print("\n   Table details:")
                for _, table in postgres_tables.iterrows():
                    print(f"   - {table['table_name']}: {table['row_count']:,} rows, {table['column_count']} columns")
            
            print(f"\n❄️ Snowflake Database:")
            print(f"   Total tables: {len(snowflake_tables)}")
            if not snowflake_tables.empty:
                total_rows = snowflake_tables['row_count'].sum()
                print(f"   Total rows: {total_rows:,}")
                print("\n   Table details:")
                for _, table in snowflake_tables.iterrows():
                    print(f"   - {table['table_name']}: {table['row_count']:,} rows, {table['column_count']} columns")
            
            print("\n" + "="*80)
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")

def main():
    """Main function"""
    logger.info("🚀 Starting PostgreSQL to Snowflake Data Synchronization")
    
    sync_manager = DataSyncManager()
    
    # Setup connections
    if not sync_manager.setup_postgres_connection():
        logger.error("❌ Cannot proceed without PostgreSQL connection")
        return
    
    if not sync_manager.setup_snowflake_connection():
        logger.error("❌ Cannot proceed without Snowflake connection")
        return
    
    # Generate initial report
    sync_manager.generate_sync_report()
    
    # Drop empty tables in Snowflake
    logger.info("\n🗑️ Dropping empty tables in Snowflake...")
    sync_manager.drop_empty_snowflake_tables()
    
    # Sync all tables
    logger.info("\n🔄 Starting data synchronization...")
    sync_manager.sync_all_tables()
    
    # Generate final report
    logger.info("\n📋 Final report:")
    sync_manager.generate_sync_report()
    
    logger.info("🎉 Data synchronization completed!")

if __name__ == "__main__":
    main()
