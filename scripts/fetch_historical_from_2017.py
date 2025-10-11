#!/usr/bin/env python3
"""
Fetch Historical Data from 2017
Fetches complete historical data from 2017 to present
"""

import os
import sys
import time
import logging
import pandas as pd
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HistoricalDataFetcher2017:
    def __init__(self):
        self.setup_database()
        self.setup_vnstock()
        
    def setup_database(self):
        """Setup database connection"""
        try:
            # Database connection
            user = os.getenv('POSTGRES_USER', 'admin')
            password = os.getenv('POSTGRES_PASSWORD', 'admin123@')
            host = os.getenv('POSTGRES_HOST', 'postgres')
            port = os.getenv('POSTGRES_PORT', '5432')
            db = os.getenv('POSTGRES_DB', 'stock_db')
            
            # Direct psycopg2 connection
            self.conn = psycopg2.connect(
                host=host, port=port, database=db, user=user, password=password,
                connect_timeout=10
            )
            self.conn.autocommit = True
            
            logger.info("✅ Database connection established")
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def setup_vnstock(self):
        """Setup vnstock API"""
        try:
            import vnstock as vn
            self.vn = vn
            logger.info("✅ vnstock API loaded")
        except Exception as e:
            logger.error(f"❌ vnstock import failed: {e}")
            sys.exit(1)
    
    def get_tickers_to_fetch(self):
        """Get list of tickers that need historical data from 2017"""
        try:
            cursor = self.conn.cursor()
            
            # Get tickers that don't have data from 2017
            cursor.execute("""
                SELECT DISTINCT ticker 
                FROM ticker_info 
                WHERE ticker NOT IN (
                    SELECT DISTINCT ticker 
                    FROM historical_prices 
                    WHERE trading_date <= '2018-01-01'
                )
                ORDER BY ticker
            """)
            
            tickers = [row[0] for row in cursor.fetchall()]
            cursor.close()
            
            logger.info(f"📊 Found {len(tickers)} tickers that need data from 2017")
            return tickers
            
        except Exception as e:
            logger.error(f"❌ Failed to get tickers: {e}")
            return []
    
    def fetch_ticker_historical_data(self, ticker, start_date='2017-01-01', end_date='2025-10-11'):
        """Fetch historical data for a single ticker from 2017"""
        try:
            # Try different vnstock methods
            historical_data = None
            
            # Method 1: Try with Trading class
            try:
                trading = self.vn.Trading(ticker, source='VCI')
                historical_data = trading.get_historical_data(start_date, end_date)
                logger.info(f"   ✅ Fetched {ticker} via Trading class")
            except Exception as e:
                logger.warning(f"   ⚠️ Trading class failed for {ticker}: {e}")
            
            # Method 2: Try with Quote class
            if historical_data is None or historical_data.empty:
                try:
                    quote = self.vn.Quote(ticker, source='VCI')
                    historical_data = quote.get_historical_data(start_date, end_date)
                    logger.info(f"   ✅ Fetched {ticker} via Quote class")
                except Exception as e:
                    logger.warning(f"   ⚠️ Quote class failed for {ticker}: {e}")
            
            # Method 3: Try with Company class
            if historical_data is None or historical_data.empty:
                try:
                    company = self.vn.Company(ticker, source='VCI')
                    historical_data = company.get_historical_data(start_date, end_date)
                    logger.info(f"   ✅ Fetched {ticker} via Company class")
                except Exception as e:
                    logger.warning(f"   ⚠️ Company class failed for {ticker}: {e}")
            
            # Method 4: Try direct API call (fallback)
            if historical_data is None or historical_data.empty:
                try:
                    # This is a fallback method - might need adjustment based on actual API
                    historical_data = self.vn.stock_historical_data(ticker, start_date, end_date)
                    logger.info(f"   ✅ Fetched {ticker} via direct API")
                except Exception as e:
                    logger.warning(f"   ⚠️ Direct API failed for {ticker}: {e}")
            
            if historical_data is not None and not historical_data.empty:
                return self.process_historical_data(historical_data, ticker)
            else:
                logger.warning(f"   ❌ No data found for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"   ❌ Failed to fetch {ticker}: {e}")
            return None
    
    def process_historical_data(self, df, ticker):
        """Process and clean historical data"""
        try:
            # Standardize column names
            column_mapping = {
                'date': 'trading_date',
                'Date': 'trading_date',
                'open': 'open_price',
                'Open': 'open_price',
                'high': 'high_price',
                'High': 'high_price',
                'low': 'low_price',
                'Low': 'low_price',
                'close': 'close_price',
                'Close': 'close_price',
                'volume': 'volume',
                'Volume': 'volume',
                'adj_close': 'adjusted_close',
                'Adj Close': 'adjusted_close'
            }
            
            # Rename columns
            df = df.rename(columns=column_mapping)
            
            # Ensure required columns exist
            required_columns = ['trading_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    if col == 'trading_date':
                        df[col] = df.index if hasattr(df, 'index') else pd.date_range('2017-01-01', periods=len(df))
                    else:
                        df[col] = 0
            
            # Add ticker column
            df['ticker'] = ticker
            
            # Convert date column
            if 'trading_date' in df.columns:
                df['trading_date'] = pd.to_datetime(df['trading_date']).dt.date
            
            # Calculate change and change_percent
            df['change'] = df['close_price'] - df['open_price']
            df['change_percent'] = (df['change'] / df['open_price'] * 100).round(4)
            
            # Select and reorder columns
            final_columns = [
                'ticker', 'trading_date', 'open_price', 'high_price', 
                'low_price', 'close_price', 'adjusted_close', 'volume', 
                'change', 'change_percent'
            ]
            
            df = df[final_columns]
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['ticker', 'trading_date'])
            
            return df
            
        except Exception as e:
            logger.error(f"   ❌ Failed to process data for {ticker}: {e}")
            return None
    
    def insert_historical_data(self, df, ticker):
        """Insert historical data into database"""
        try:
            if df is None or df.empty:
                return False
            
            cursor = self.conn.cursor()
            
            # Prepare data for insertion
            data_to_insert = []
            for _, row in df.iterrows():
                data_to_insert.append((
                    row['ticker'],
                    row['trading_date'],
                    row['open_price'],
                    row['high_price'],
                    row['low_price'],
                    row['close_price'],
                    row.get('adjusted_close', row['close_price']),
                    row['volume'],
                    row['change'],
                    row['change_percent']
                ))
            
            # Insert with conflict resolution (ON CONFLICT DO NOTHING)
            insert_query = """
                INSERT INTO historical_prices (
                    ticker, trading_date, open_price, high_price, low_price,
                    close_price, adjusted_close, volume, change, change_percent
                ) VALUES %s
                ON CONFLICT (ticker, trading_date) DO NOTHING
            """
            
            execute_values(cursor, insert_query, data_to_insert)
            cursor.close()
            
            logger.info(f"   ✅ Inserted {len(data_to_insert)} records for {ticker}")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Failed to insert data for {ticker}: {e}")
            return False
    
    def run_historical_fetch(self):
        """Run complete historical data fetch from 2017"""
        logger.info("🚀 STARTING HISTORICAL DATA FETCH FROM 2017")
        logger.info("=" * 60)
        
        try:
            # Get tickers to fetch
            tickers = self.get_tickers_to_fetch()
            
            if not tickers:
                logger.info("✅ All tickers already have data from 2017")
                return
            
            success_count = 0
            failed_count = 0
            total_records = 0
            
            for i, ticker in enumerate(tickers):
                try:
                    logger.info(f"📈 Fetching {ticker} ({i+1}/{len(tickers)})")
                    
                    # Fetch historical data
                    df = self.fetch_ticker_historical_data(ticker)
                    
                    if df is not None:
                        # Insert into database
                        if self.insert_historical_data(df, ticker):
                            success_count += 1
                            total_records += len(df)
                        else:
                            failed_count += 1
                    else:
                        failed_count += 1
                    
                    # Rate limiting
                    time.sleep(1)  # 1 second delay between requests
                    
                    # Progress update every 50 tickers
                    if (i + 1) % 50 == 0:
                        logger.info(f"   📊 Progress: {i+1}/{len(tickers)} tickers processed")
                        logger.info(f"   ✅ Success: {success_count}, ❌ Failed: {failed_count}")
                        logger.info(f"   📈 Total records: {total_records:,}")
                
                except Exception as e:
                    logger.error(f"   ❌ Error processing {ticker}: {e}")
                    failed_count += 1
            
            # Final statistics
            logger.info("🎉 HISTORICAL DATA FETCH COMPLETED!")
            logger.info("=" * 60)
            logger.info(f"✅ Successfully processed: {success_count} tickers")
            logger.info(f"❌ Failed: {failed_count} tickers")
            logger.info(f"📈 Total new records: {total_records:,}")
            
            # Print final database statistics
            self.print_final_stats()
            
        except Exception as e:
            logger.error(f"❌ Historical fetch failed: {e}")
            sys.exit(1)
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()
    
    def print_final_stats(self):
        """Print final database statistics"""
        try:
            cursor = self.conn.cursor()
            
            # Get overall statistics
            cursor.execute("""
                SELECT 
                    MIN(trading_date) as earliest_date,
                    MAX(trading_date) as latest_date,
                    COUNT(DISTINCT ticker) as total_tickers,
                    COUNT(*) as total_records
                FROM historical_prices
            """)
            
            stats = cursor.fetchone()
            
            logger.info("📊 FINAL DATABASE STATISTICS:")
            logger.info("=" * 40)
            logger.info(f"   📅 Date range: {stats[0]} to {stats[1]}")
            logger.info(f"   📈 Total tickers: {stats[2]:,}")
            logger.info(f"   📊 Total records: {stats[3]:,}")
            
            # Get records by year
            cursor.execute("""
                SELECT 
                    EXTRACT(YEAR FROM trading_date) as year,
                    COUNT(*) as records
                FROM historical_prices 
                GROUP BY EXTRACT(YEAR FROM trading_date)
                ORDER BY year
            """)
            
            year_stats = cursor.fetchall()
            
            logger.info("📅 RECORDS BY YEAR:")
            for year, records in year_stats:
                logger.info(f"   {int(year)}: {records:,} records")
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to print stats: {e}")

if __name__ == "__main__":
    fetcher = HistoricalDataFetcher2017()
    fetcher.run_historical_fetch()
