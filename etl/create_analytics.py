#!/usr/bin/env python3
"""
Create Analytics from Existing Data
Generates technical indicators and analytics from historical prices
"""

import os
import sys
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnalyticsGenerator:
    def __init__(self):
        self.setup_database()
        
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
    
    def create_analytics_tables(self):
        """Create analytics tables"""
        try:
            cursor = self.conn.cursor()
            
            # Stock analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_analytics (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(10),
                    date DATE,
                    sma_5 DECIMAL(10,2),
                    sma_10 DECIMAL(10,2),
                    sma_20 DECIMAL(10,2),
                    sma_50 DECIMAL(10,2),
                    ema_12 DECIMAL(10,2),
                    ema_26 DECIMAL(10,2),
                    macd DECIMAL(10,4),
                    macd_signal DECIMAL(10,4),
                    macd_histogram DECIMAL(10,4),
                    rsi DECIMAL(10,2),
                    bollinger_upper DECIMAL(10,2),
                    bollinger_middle DECIMAL(10,2),
                    bollinger_lower DECIMAL(10,2),
                    volume_sma DECIMAL(15,2),
                    price_change_1d DECIMAL(10,4),
                    price_change_5d DECIMAL(10,4),
                    price_change_10d DECIMAL(10,4),
                    price_change_20d DECIMAL(10,4),
                    volatility DECIMAL(10,4),
                    support_level DECIMAL(10,2),
                    resistance_level DECIMAL(10,2),
                    trend_direction VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Market summary table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_summary (
                    id SERIAL PRIMARY KEY,
                    date DATE,
                    total_tickers INTEGER,
                    advancing_tickers INTEGER,
                    declining_tickers INTEGER,
                    unchanged_tickers INTEGER,
                    total_volume BIGINT,
                    total_value DECIMAL(20,2),
                    market_cap DECIMAL(20,2),
                    vn_index DECIMAL(10,2),
                    hnx_index DECIMAL(10,2),
                    upcom_index DECIMAL(10,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Top performers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS top_performers (
                    id SERIAL PRIMARY KEY,
                    date DATE,
                    period VARCHAR(20),
                    ticker VARCHAR(10),
                    price_change DECIMAL(10,4),
                    volume BIGINT,
                    market_cap DECIMAL(20,2),
                    rank INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.close()
            logger.info("✅ Analytics tables created")
                
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
    
    def calculate_technical_indicators(self, prices_df):
        """Calculate technical indicators"""
        try:
            df = prices_df.copy()
            df = df.sort_values('trading_date')
            
            # Simple Moving Averages
            df['sma_5'] = df['close_price'].rolling(window=5).mean()
            df['sma_10'] = df['close_price'].rolling(window=10).mean()
            df['sma_20'] = df['close_price'].rolling(window=20).mean()
            df['sma_50'] = df['close_price'].rolling(window=50).mean()
            
            # Exponential Moving Averages
            df['ema_12'] = df['close_price'].ewm(span=12).mean()
            df['ema_26'] = df['close_price'].ewm(span=26).mean()
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # RSI
            delta = df['close_price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bollinger_middle'] = df['close_price'].rolling(window=20).mean()
            bb_std = df['close_price'].rolling(window=20).std()
            df['bollinger_upper'] = df['bollinger_middle'] + (bb_std * 2)
            df['bollinger_lower'] = df['bollinger_middle'] - (bb_std * 2)
            
            # Volume SMA
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            
            # Price changes
            df['price_change_1d'] = df['close_price'].pct_change(1) * 100
            df['price_change_5d'] = df['close_price'].pct_change(5) * 100
            df['price_change_10d'] = df['close_price'].pct_change(10) * 100
            df['price_change_20d'] = df['close_price'].pct_change(20) * 100
            
            # Volatility (20-day rolling standard deviation)
            df['volatility'] = df['price_change_1d'].rolling(window=20).std()
            
            # Support and Resistance (simplified)
            df['support_level'] = df['low_price'].rolling(window=20).min()
            df['resistance_level'] = df['high_price'].rolling(window=20).max()
            
            # Trend direction
            df['trend_direction'] = 'SIDEWAYS'
            df.loc[df['sma_20'] > df['sma_50'], 'trend_direction'] = 'UPTREND'
            df.loc[df['sma_20'] < df['sma_50'], 'trend_direction'] = 'DOWNTREND'
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Technical indicators calculation failed: {e}")
            return prices_df
    
    def generate_stock_analytics(self):
        """Generate analytics for all stocks"""
        logger.info("📊 Generating stock analytics...")
        
        try:
            cursor = self.conn.cursor()
            
            # Get tickers with sufficient data
            cursor.execute("""
                SELECT ticker, COUNT(*) as record_count
                FROM historical_prices 
                GROUP BY ticker 
                HAVING COUNT(*) >= 50
                ORDER BY record_count DESC
                LIMIT 200
            """)
            
            tickers = cursor.fetchall()
            logger.info(f"Processing {len(tickers)} tickers with sufficient data")
            
            analytics_data = []
            
            for i, (ticker, record_count) in enumerate(tickers):
                try:
                    # Get historical data
                    cursor.execute("""
                        SELECT trading_date, open_price, high_price, low_price, close_price, volume
                        FROM historical_prices 
                        WHERE ticker = %s 
                        ORDER BY trading_date
                    """, (ticker,))
                    
                    data = cursor.fetchall()
                    if len(data) < 50:
                        continue
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(data, columns=['trading_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume'])
                    
                    # Calculate technical indicators
                    df_with_indicators = self.calculate_technical_indicators(df)
                    
                    # Prepare data for insertion
                    for _, row in df_with_indicators.iterrows():
                        if pd.notna(row['sma_20']):  # Only insert rows with calculated indicators
                            analytics_data.append((
                                ticker,
                                row['trading_date'],
                                row['sma_5'],
                                row['sma_10'],
                                row['sma_20'],
                                row['sma_50'],
                                row['ema_12'],
                                row['ema_26'],
                                row['macd'],
                                row['macd_signal'],
                                row['macd_histogram'],
                                row['rsi'],
                                row['bollinger_upper'],
                                row['bollinger_middle'],
                                row['bollinger_lower'],
                                row['volume_sma'],
                                row['price_change_1d'],
                                row['price_change_5d'],
                                row['price_change_10d'],
                                row['price_change_20d'],
                                row['volatility'],
                                row['support_level'],
                                row['resistance_level'],
                                row['trend_direction']
                            ))
                    
                    if (i + 1) % 50 == 0:
                        logger.info(f"   Processed {i + 1}/{len(tickers)} tickers")
                
                except Exception as e:
                    logger.warning(f"   Failed to process {ticker}: {e}")
            
            # Insert analytics data
            if analytics_data:
                insert_query = """
                    INSERT INTO stock_analytics (
                        ticker, date, sma_5, sma_10, sma_20, sma_50,
                        ema_12, ema_26, macd, macd_signal, macd_histogram,
                        rsi, bollinger_upper, bollinger_middle, bollinger_lower,
                        volume_sma, price_change_1d, price_change_5d,
                        price_change_10d, price_change_20d, volatility,
                        support_level, resistance_level, trend_direction
                    ) VALUES %s
                """
                
                execute_values(cursor, insert_query, analytics_data)
                logger.info(f"✅ Stock analytics: {len(analytics_data)} records inserted")
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"❌ Stock analytics generation failed: {e}")
    
    def generate_market_summary(self):
        """Generate market summary"""
        logger.info("📈 Generating market summary...")
        
        try:
            cursor = self.conn.cursor()
            
            # Get latest date
            cursor.execute("SELECT MAX(trading_date) FROM historical_prices")
            latest_date = cursor.fetchone()[0]
            
            if not latest_date:
                logger.warning("No data found for market summary")
                return
            
            # Get market data for latest date
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_tickers,
                    COUNT(CASE WHEN close_price > open_price THEN 1 END) as advancing,
                    COUNT(CASE WHEN close_price < open_price THEN 1 END) as declining,
                    COUNT(CASE WHEN close_price = open_price THEN 1 END) as unchanged,
                    SUM(volume) as total_volume,
                    SUM(close_price * volume) as total_value
                FROM historical_prices 
                WHERE trading_date = %s
            """, (latest_date,))
            
            market_data = cursor.fetchone()
            
            if market_data:
                summary_data = (
                    latest_date,
                    market_data[0],  # total_tickers
                    market_data[1],  # advancing
                    market_data[2],  # declining
                    market_data[3],  # unchanged
                    market_data[4],  # total_volume
                    market_data[5],  # total_value
                    None,  # market_cap (would need additional data)
                    None,  # vn_index
                    None,  # hnx_index
                    None   # upcom_index
                )
                
                cursor.execute("""
                    INSERT INTO market_summary (
                        date, total_tickers, advancing_tickers, declining_tickers,
                        unchanged_tickers, total_volume, total_value, market_cap,
                        vn_index, hnx_index, upcom_index
                    ) VALUES %s
                """, (summary_data,))
                
                logger.info(f"✅ Market summary generated for {latest_date}")
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"❌ Market summary generation failed: {e}")
    
    def generate_top_performers(self):
        """Generate top performers"""
        logger.info("🏆 Generating top performers...")
        
        try:
            cursor = self.conn.cursor()
            
            # Get latest date
            cursor.execute("SELECT MAX(trading_date) FROM historical_prices")
            latest_date = cursor.fetchone()[0]
            
            if not latest_date:
                return
            
            # Top gainers (1 day)
            cursor.execute("""
                WITH price_changes AS (
                    SELECT 
                        ticker,
                        close_price,
                        LAG(close_price) OVER (PARTITION BY ticker ORDER BY trading_date) as prev_price,
                        volume
                    FROM historical_prices 
                    WHERE trading_date = %s OR trading_date = %s
                )
                SELECT 
                    ticker,
                    ((close_price - prev_price) / prev_price * 100) as price_change,
                    volume
                FROM price_changes 
                WHERE prev_price IS NOT NULL AND close_price IS NOT NULL
                ORDER BY price_change DESC
                LIMIT 20
            """, (latest_date, latest_date - timedelta(days=1)))
            
            top_gainers = cursor.fetchall()
            
            # Insert top gainers
            for i, (ticker, price_change, volume) in enumerate(top_gainers):
                cursor.execute("""
                    INSERT INTO top_performers (
                        date, period, ticker, price_change, volume, rank
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (latest_date, '1D', ticker, price_change, volume, i + 1))
            
            logger.info(f"✅ Top performers: {len(top_gainers)} records")
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"❌ Top performers generation failed: {e}")
    
    def run_analytics_generation(self):
        """Run complete analytics generation"""
        logger.info("🚀 STARTING ANALYTICS GENERATION")
        logger.info("=" * 50)
        
        try:
            # Create tables
            self.create_analytics_tables()
            
            # Generate analytics
            self.generate_stock_analytics()
            self.generate_market_summary()
            self.generate_top_performers()
            
            # Print final statistics
            self.print_final_stats()
            
            logger.info("🎉 ANALYTICS GENERATION FINISHED!")
            
        except Exception as e:
            logger.error(f"❌ Analytics generation failed: {e}")
            sys.exit(1)
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()
    
    def print_final_stats(self):
        """Print final statistics"""
        try:
            cursor = self.conn.cursor()
            
            # Get counts
            cursor.execute("SELECT COUNT(*) FROM stock_analytics")
            analytics_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM market_summary")
            summary_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM top_performers")
            performers_count = cursor.fetchone()[0]
            
            logger.info("📊 ANALYTICS STATISTICS:")
            logger.info("=" * 30)
            logger.info(f"   Stock analytics: {analytics_count:,} records")
            logger.info(f"   Market summary: {summary_count:,} records")
            logger.info(f"   Top performers: {performers_count:,} records")
            
            cursor.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to print stats: {e}")

if __name__ == "__main__":
    generator = AnalyticsGenerator()
    generator.run_analytics_generation()
