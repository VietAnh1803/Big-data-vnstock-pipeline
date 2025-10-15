#!/usr/bin/env python3

"""
Snowflake Database Cleanup Script
Removes empty tables from Snowflake to optimize storage and reduce costs
"""

import os
import sys
import logging
import snowflake.connector
from snowflake.connector import DictCursor
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/snowflake_cleanup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SnowflakeCleanup:
    def __init__(self):
        load_dotenv()
        self.conn = None
        self.setup_connection()

    def setup_connection(self):
        """Setup Snowflake connection"""
        try:
            self.conn = snowflake.connector.connect(
                user=os.getenv('SNOWFLAKE_USER'),
                password=os.getenv('SNOWFLAKE_PASSWORD'),
                account=os.getenv('SNOWFLAKE_ACCOUNT'),
                warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
                database=os.getenv('SNOWFLAKE_DATABASE'),
                schema=os.getenv('SNOWFLAKE_SCHEMA')
            )
            logger.info("✅ Snowflake connection established")
        except Exception as e:
            logger.error(f"❌ Snowflake connection failed: {e}")
            sys.exit(1)

    def get_all_tables(self):
        """Get all tables in the current schema"""
        try:
            cursor = self.conn.cursor(DictCursor)
            cursor.execute("""
                SELECT TABLE_NAME, TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = CURRENT_SCHEMA()
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
            cursor.close()
            logger.info(f"📊 Found {len(tables)} tables in Snowflake")
            return tables
        except Exception as e:
            logger.error(f"❌ Failed to get tables: {e}")
            return []

    def get_table_row_counts(self):
        """Get row count for each table"""
        tables = self.get_all_tables()
        table_counts = {}
        
        for table in tables:
            table_name = table['TABLE_NAME']
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_counts[table_name] = count
                cursor.close()
                logger.info(f"📈 {table_name}: {count:,} records")
            except Exception as e:
                logger.warning(f"⚠️ Failed to count {table_name}: {e}")
                table_counts[table_name] = -1
        
        return table_counts

    def get_table_sizes(self):
        """Get storage size for each table"""
        try:
            cursor = self.conn.cursor(DictCursor)
            cursor.execute("""
                SELECT 
                    TABLE_NAME,
                    BYTES,
                    ROW_COUNT
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = CURRENT_SCHEMA()
                ORDER BY BYTES DESC
            """)
            sizes = cursor.fetchall()
            cursor.close()
            return sizes
        except Exception as e:
            logger.error(f"❌ Failed to get table sizes: {e}")
            return []

    def identify_empty_tables(self):
        """Identify tables with 0 records"""
        table_counts = self.get_table_row_counts()
        empty_tables = []
        
        for table_name, count in table_counts.items():
            if count == 0:
                empty_tables.append(table_name)
                logger.info(f"🗑️ Empty table found: {table_name}")
        
        return empty_tables

    def backup_table_structure(self, tables):
        """Backup table structures before deletion"""
        backup_file = f"/app/logs/snowflake_backup_{len(tables)}_tables.sql"
        
        try:
            with open(backup_file, 'w') as f:
                f.write("-- Snowflake Table Structure Backup\n")
                f.write(f"-- Generated: {os.popen('date').read().strip()}\n")
                f.write(f"-- Tables to be deleted: {', '.join(tables)}\n\n")
                
                for table in tables:
                    cursor = self.conn.cursor()
                    cursor.execute(f"SHOW CREATE TABLE {table}")
                    result = cursor.fetchone()
                    if result:
                        f.write(f"-- Table: {table}\n")
                        f.write(f"{result[0]};\n\n")
                    cursor.close()
            
            logger.info(f"✅ Table structures backed up to: {backup_file}")
            return backup_file
        except Exception as e:
            logger.error(f"❌ Failed to backup table structures: {e}")
            return None

    def drop_empty_tables(self, empty_tables, dry_run=True):
        """Drop empty tables from Snowflake"""
        if not empty_tables:
            logger.info("ℹ️ No empty tables to drop")
            return
        
        logger.info(f"🗑️ Found {len(empty_tables)} empty tables to drop")
        
        if dry_run:
            logger.info("🔍 DRY RUN - No tables will be actually dropped")
            for table in empty_tables:
                logger.info(f"   Would drop: {table}")
            return
        
        # Backup table structures
        backup_file = self.backup_table_structure(empty_tables)
        
        # Drop tables
        dropped_count = 0
        for table in empty_tables:
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                cursor.close()
                logger.info(f"✅ Dropped table: {table}")
                dropped_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to drop {table}: {e}")
        
        logger.info(f"🎉 Successfully dropped {dropped_count}/{len(empty_tables)} empty tables")

    def optimize_warehouse(self):
        """Optimize warehouse after cleanup"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("ALTER WAREHOUSE COMPUTE_WH SUSPEND")
            cursor.execute("ALTER WAREHOUSE COMPUTE_WH RESUME")
            cursor.close()
            logger.info("✅ Warehouse optimized")
        except Exception as e:
            logger.warning(f"⚠️ Failed to optimize warehouse: {e}")

    def show_final_status(self):
        """Show final database status"""
        logger.info("📊 Final Snowflake Database Status:")
        
        # Show remaining tables
        table_counts = self.get_table_row_counts()
        total_records = sum(count for count in table_counts.values() if count > 0)
        
        logger.info(f"📈 Total tables: {len(table_counts)}")
        logger.info(f"📈 Total records: {total_records:,}")
        
        # Show table sizes
        sizes = self.get_table_sizes()
        if sizes:
            total_size = sum(size['BYTES'] for size in sizes if size['BYTES'])
            logger.info(f"💾 Total storage: {total_size / (1024**3):.2f} GB")

    def run_cleanup(self, dry_run=True):
        """Main cleanup function"""
        logger.info("🚀 Starting Snowflake cleanup process...")
        
        # Get current status
        logger.info("📊 Current database status:")
        self.get_table_row_counts()
        
        # Identify empty tables
        empty_tables = self.identify_empty_tables()
        
        if not empty_tables:
            logger.info("✅ No empty tables found. Database is already optimized!")
            return
        
        # Show empty tables
        logger.info(f"🗑️ Empty tables to be removed: {len(empty_tables)}")
        for table in empty_tables:
            logger.info(f"   - {table}")
        
        # Drop empty tables
        self.drop_empty_tables(empty_tables, dry_run)
        
        if not dry_run:
            # Optimize warehouse
            self.optimize_warehouse()
            
            # Show final status
            self.show_final_status()
        
        logger.info("🎉 Snowflake cleanup completed!")

    def close_connection(self):
        """Close Snowflake connection"""
        if self.conn:
            self.conn.close()
            logger.info("✅ Snowflake connection closed")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Cleanup empty tables in Snowflake')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Dry run mode (default: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Actually execute the cleanup (overrides dry-run)')
    
    args = parser.parse_args()
    
    # Determine if this is a dry run
    dry_run = not args.execute
    
    cleanup = SnowflakeCleanup()
    try:
        cleanup.run_cleanup(dry_run=dry_run)
    finally:
        cleanup.close_connection()



