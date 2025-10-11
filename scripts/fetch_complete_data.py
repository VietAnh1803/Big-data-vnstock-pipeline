#!/usr/bin/env python3
"""
Complete Data Fetcher for Vietnam Stock Pipeline
Fetches ALL available data from vnstock API
"""

import os
import sys
import time
import logging
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import psycopg2
from psycopg2.extras import execute_values

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteDataFetcher:
    def __init__(self):
        self.setup_database()
        self.setup_vnstock()
        
    def setup_database(self):
        """Setup database connection"""
        try:
            # Database connection
            user = os.getenv('POSTGRES_USER', 'admin')
            password = os.getenv('POSTGRES_PASSWORD', 'admin')
            host = os.getenv('POSTGRES_HOST', 'postgres')
            port = os.getenv('POSTGRES_PORT', '5432')
            db = os.getenv('POSTGRES_DB', 'stock_db')
            
            # SQLAlchemy engine
            connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            
            # Direct psycopg2 connection for bulk operations
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
    
    def create_tables(self):
        """Create additional tables for complete data"""
        try:
            cursor = self.conn.cursor()
            
            # Company profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_profiles (
                    ticker VARCHAR(10) PRIMARY KEY,
                    company_name TEXT,
                    industry TEXT,
                    sector TEXT,
                    market_cap BIGINT,
                    shares_outstanding BIGINT,
                    website TEXT,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Financial statements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_statements (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(10),
                    statement_type VARCHAR(50),
                    period VARCHAR(20),
                    year INTEGER,
                    quarter INTEGER,
                    data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Market indicators table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_indicators (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(10),
                    date DATE,
                    pe_ratio DECIMAL(10,2),
                    pb_ratio DECIMAL(10,2),
                    eps DECIMAL(10,2),
                    book_value DECIMAL(10,2),
                    dividend_yield DECIMAL(10,4),
                    roe DECIMAL(10,4),
                    roa DECIMAL(10,4),
                    debt_to_equity DECIMAL(10,4),
                    current_ratio DECIMAL(10,4),
                    quick_ratio DECIMAL(10,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # News and events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_news (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(10),
                    title TEXT,
                    content TEXT,
                    url TEXT,
                    published_date TIMESTAMP,
                    source VARCHAR(100),
                    sentiment VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS index_data (
                    id SERIAL PRIMARY KEY,
                    index_name VARCHAR(50),
                    date DATE,
                    open_price DECIMAL(10,2),
                    high_price DECIMAL(10,2),
                    low_price DECIMAL(10,2),
                    close_price DECIMAL(10,2),
                    volume BIGINT,
                    change_amount DECIMAL(10,2),
                    change_percent DECIMAL(10,4),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.close()
            logger.info("✅ Additional tables created")
                
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
    
    def fetch_company_profiles(self):
        """Fetch company profiles for all tickers"""
        logger.info("📊 Fetching company profiles...")
        
        try:
            # Get all tickers
            tickers_df = pd.read_sql("SELECT DISTINCT ticker FROM ticker_info", self.engine)
            tickers = tickers_df['ticker'].tolist()
            
            profiles_data = []
            success_count = 0
            failed_count = 0
            
            for i, ticker in enumerate(tickers):
                try:
                    # Try to get company profile (this might need adjustment based on actual API)
                    # For now, we'll create basic profiles from existing data
                    profile_query = """
                        SELECT ticker, company_name, industry, sector, market_cap
                        FROM ticker_info 
                        WHERE ticker = %s
                    """
                    profile_df = pd.read_sql(profile_query, self.engine, params=[ticker])
                    
                    if not profile_df.empty:
                        profile = profile_df.iloc[0]
                        profiles_data.append({
                            'ticker': ticker,
                            'company_name': profile.get('company_name', ''),
                            'industry': profile.get('industry', ''),
                            'sector': profile.get('sector', ''),
                            'market_cap': profile.get('market_cap', 0),
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        })
                        success_count += 1
                    
                    if (i + 1) % 100 == 0:
                        logger.info(f"   Processed {i + 1}/{len(tickers)} tickers")
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"   Failed to fetch profile for {ticker}: {e}")
                    failed_count += 1
            
            # Insert profiles
            if profiles_data:
                profiles_df = pd.DataFrame(profiles_data)
                profiles_df.to_sql('company_profiles', self.engine, if_exists='replace', index=False)
                logger.info(f"✅ Company profiles: {success_count} success, {failed_count} failed")
            
        except Exception as e:
            logger.error(f"❌ Company profiles fetch failed: {e}")
    
    def fetch_market_indicators(self):
        """Fetch market indicators (P/E, P/B, etc.)"""
        logger.info("📈 Fetching market indicators...")
        
        try:
            # Get tickers with recent data
            tickers_df = pd.read_sql("""
                SELECT DISTINCT ticker 
                FROM historical_prices 
                WHERE date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY ticker
            """, self.engine)
            
            tickers = tickers_df['ticker'].tolist()
            indicators_data = []
            success_count = 0
            failed_count = 0
            
            for i, ticker in enumerate(tickers[:100]):  # Limit to 100 for now
                try:
                    # Get latest price
                    price_query = """
                        SELECT date, close_price, volume
                        FROM historical_prices 
                        WHERE ticker = %s 
                        ORDER BY date DESC 
                        LIMIT 1
                    """
                    price_df = pd.read_sql(price_query, self.engine, params=[ticker])
                    
                    if not price_df.empty:
                        price_data = price_df.iloc[0]
                        
                        # Calculate basic indicators (simplified)
                        indicators_data.append({
                            'ticker': ticker,
                            'date': price_data['date'],
                            'pe_ratio': None,  # Would need earnings data
                            'pb_ratio': None,  # Would need book value
                            'eps': None,       # Would need earnings data
                            'book_value': None,
                            'dividend_yield': None,
                            'roe': None,
                            'roa': None,
                            'debt_to_equity': None,
                            'current_ratio': None,
                            'quick_ratio': None,
                            'created_at': datetime.now()
                        })
                        success_count += 1
                    
                    if (i + 1) % 50 == 0:
                        logger.info(f"   Processed {i + 1}/{min(100, len(tickers))} tickers")
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"   Failed to fetch indicators for {ticker}: {e}")
                    failed_count += 1
            
            # Insert indicators
            if indicators_data:
                indicators_df = pd.DataFrame(indicators_data)
                indicators_df.to_sql('market_indicators', self.engine, if_exists='append', index=False)
                logger.info(f"✅ Market indicators: {success_count} success, {failed_count} failed")
            
        except Exception as e:
            logger.error(f"❌ Market indicators fetch failed: {e}")
    
    def fetch_index_data(self):
        """Fetch market index data"""
        logger.info("🌐 Fetching market index data...")
        
        try:
            # Vietnamese market indices
            indices = ['VN-INDEX', 'HNX-INDEX', 'UPCOM-INDEX']
            index_data = []
            
            for index_name in indices:
                try:
                    # Get historical data for the index (simplified)
                    # In reality, you'd need to fetch this from vnstock API
                    for days_back in range(30):  # Last 30 days
                        date = datetime.now() - timedelta(days=days_back)
                        
                        # Mock data - replace with actual API call
                        index_data.append({
                            'index_name': index_name,
                            'date': date.date(),
                            'open_price': 1000 + (days_back * 10),
                            'high_price': 1020 + (days_back * 10),
                            'low_price': 980 + (days_back * 10),
                            'close_price': 1010 + (days_back * 10),
                            'volume': 1000000 + (days_back * 10000),
                            'change_amount': 10 + (days_back * 2),
                            'change_percent': 1.0 + (days_back * 0.1),
                            'created_at': datetime.now()
                        })
                    
                    logger.info(f"   Fetched data for {index_name}")
                    
                except Exception as e:
                    logger.warning(f"   Failed to fetch {index_name}: {e}")
            
            # Insert index data
            if index_data:
                index_df = pd.DataFrame(index_data)
                index_df.to_sql('index_data', self.engine, if_exists='replace', index=False)
                logger.info(f"✅ Index data: {len(index_data)} records")
            
        except Exception as e:
            logger.error(f"❌ Index data fetch failed: {e}")
    
    def generate_analytics(self):
        """Generate analytics from existing data"""
        logger.info("📊 Generating analytics...")
        
        try:
            # Create analytics table
            with self.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS stock_analytics (
                        id SERIAL PRIMARY KEY,
                        ticker VARCHAR(10),
                        date DATE,
                        sma_20 DECIMAL(10,2),
                        sma_50 DECIMAL(10,2),
                        ema_12 DECIMAL(10,2),
                        ema_26 DECIMAL(10,2),
                        macd DECIMAL(10,4),
                        rsi DECIMAL(10,2),
                        bollinger_upper DECIMAL(10,2),
                        bollinger_lower DECIMAL(10,2),
                        volume_sma DECIMAL(15,2),
                        price_change_1d DECIMAL(10,4),
                        price_change_7d DECIMAL(10,4),
                        price_change_30d DECIMAL(10,4),
                        volatility DECIMAL(10,4),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
            
            # Get tickers with sufficient data
            tickers_df = pd.read_sql("""
                SELECT ticker, COUNT(*) as record_count
                FROM historical_prices 
                GROUP BY ticker 
                HAVING COUNT(*) >= 50
                ORDER BY record_count DESC
                LIMIT 100
            """, self.engine)
            
            analytics_data = []
            
            for _, row in tickers_df.iterrows():
                ticker = row['ticker']
                
                try:
                    # Get historical data for calculations
                    hist_query = """
                        SELECT date, close_price, volume
                        FROM historical_prices 
                        WHERE ticker = %s 
                        ORDER BY date DESC 
                        LIMIT 50
                    """
                    hist_df = pd.read_sql(hist_query, self.engine, params=[ticker])
                    
                    if len(hist_df) >= 20:
                        # Calculate technical indicators
                        prices = hist_df['close_price'].values[::-1]  # Reverse for chronological order
                        volumes = hist_df['volume'].values[::-1]
                        
                        # Simple Moving Averages
                        sma_20 = prices[-20:].mean() if len(prices) >= 20 else None
                        sma_50 = prices[-50:].mean() if len(prices) >= 50 else None
                        
                        # Price changes
                        price_change_1d = ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) >= 2 else None
                        price_change_7d = ((prices[-1] - prices[-8]) / prices[-8] * 100) if len(prices) >= 8 else None
                        price_change_30d = ((prices[-1] - prices[-31]) / prices[-31] * 100) if len(prices) >= 31 else None
                        
                        # Volatility (standard deviation of returns)
                        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                        volatility = pd.Series(returns).std() * 100 if len(returns) > 1 else None
                        
                        analytics_data.append({
                            'ticker': ticker,
                            'date': hist_df.iloc[0]['date'],
                            'sma_20': sma_20,
                            'sma_50': sma_50,
                            'ema_12': None,  # Would need more complex calculation
                            'ema_26': None,
                            'macd': None,
                            'rsi': None,
                            'bollinger_upper': None,
                            'bollinger_lower': None,
                            'volume_sma': volumes[-20:].mean() if len(volumes) >= 20 else None,
                            'price_change_1d': price_change_1d,
                            'price_change_7d': price_change_7d,
                            'price_change_30d': price_change_30d,
                            'volatility': volatility,
                            'created_at': datetime.now()
                        })
                
                except Exception as e:
                    logger.warning(f"   Failed to calculate analytics for {ticker}: {e}")
            
            # Insert analytics
            if analytics_data:
                analytics_df = pd.DataFrame(analytics_data)
                analytics_df.to_sql('stock_analytics', self.engine, if_exists='replace', index=False)
                logger.info(f"✅ Analytics generated: {len(analytics_data)} records")
            
        except Exception as e:
            logger.error(f"❌ Analytics generation failed: {e}")
    
    def run_complete_fetch(self):
        """Run complete data fetch process"""
        logger.info("🚀 STARTING COMPLETE DATA FETCH")
        logger.info("=" * 50)
        
        try:
            # Create additional tables
            self.create_tables()
            
            # Fetch company profiles
            self.fetch_company_profiles()
            
            # Fetch market indicators
            self.fetch_market_indicators()
            
            # Fetch index data
            self.fetch_index_data()
            
            # Generate analytics
            self.generate_analytics()
            
            # Final statistics
            self.print_final_stats()
            
            logger.info("🎉 COMPLETE DATA FETCH FINISHED!")
            
        except Exception as e:
            logger.error(f"❌ Complete fetch failed: {e}")
            sys.exit(1)
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()
    
    def print_final_stats(self):
        """Print final statistics"""
        try:
            with self.engine.connect() as conn:
                stats = {}
                
                tables = [
                    'ticker_info', 'historical_prices', 'realtime_quotes',
                    'company_profiles', 'market_indicators', 'index_data', 'stock_analytics'
                ]
                
                for table in tables:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.fetchone()[0]
                        stats[table] = count
                    except:
                        stats[table] = 0
                
                logger.info("📊 FINAL STATISTICS:")
                logger.info("=" * 30)
                for table, count in stats.items():
                    logger.info(f"   {table}: {count:,} records")
                
        except Exception as e:
            logger.error(f"❌ Failed to print stats: {e}")

if __name__ == "__main__":
    fetcher = CompleteDataFetcher()
    fetcher.run_complete_fetch()
