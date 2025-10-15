#!/usr/bin/env python3
"""
Kafka VNStock Producer
Real-time data streaming to Kafka for Big Data Analytics
Based on your comprehensive architecture design
"""

import os
import sys
import logging
import json
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
from vnstock import *
import pandas as pd
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KafkaVNStockProducer:
    def __init__(self):
        self.setup_kafka()
        self.setup_vnstock()
        self.setup_topics()
        
    def setup_kafka(self):
        """Setup Kafka producer"""
        try:
            load_dotenv()
            
            # Kafka configuration
            kafka_servers = os.getenv('KAFKA_SERVERS', 'localhost:9092').split(',')
            
            self.producer = KafkaProducer(
                bootstrap_servers=kafka_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                max_block_ms=10000
            )
            
            logger.info(f"✅ Kafka producer connected to {kafka_servers}")
            
        except Exception as e:
            logger.error(f"❌ Kafka setup failed: {e}")
            sys.exit(1)
    
    def setup_vnstock(self):
        """Setup vnstock imports"""
        try:
            # Import vnstock components
            from vnstock import *
            self.vnstock = locals()
            logger.info("✅ VNStock library loaded")
        except Exception as e:
            logger.error(f"❌ VNStock import failed: {e}")
            sys.exit(1)
    
    def setup_topics(self):
        """Define Kafka topics for different data types"""
        self.topics = {
            'price_data': 'vnstock.price.data',
            'company_profiles': 'vnstock.company.profiles',
            'financial_reports': 'vnstock.financial.reports',
            'market_indices': 'vnstock.market.indices',
            'top_performers': 'vnstock.top.performers',
            'foreign_trading': 'vnstock.foreign.trading',
            'company_news': 'vnstock.company.news',
            'market_events': 'vnstock.market.events',
            'realtime_quotes': 'vnstock.realtime.quotes'
        }
        logger.info("✅ Kafka topics configured")
    
    def send_price_data(self, symbol, price_data):
        """Send price data to Kafka"""
        try:
            message = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'data_type': 'price_data',
                'data': price_data.to_dict() if hasattr(price_data, 'to_dict') else price_data
            }
            
            self.producer.send(
                self.topics['price_data'],
                key=symbol,
                value=message
            )
            
            logger.debug(f"📊 Sent price data for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send price data for {symbol}: {e}")
    
    def send_company_profile(self, symbol, profile_data):
        """Send company profile to Kafka"""
        try:
            message = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'data_type': 'company_profile',
                'data': profile_data
            }
            
            self.producer.send(
                self.topics['company_profiles'],
                key=symbol,
                value=message
            )
            
            logger.debug(f"🏢 Sent company profile for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send company profile for {symbol}: {e}")
    
    def send_financial_report(self, symbol, report_type, report_data):
        """Send financial report to Kafka"""
        try:
            message = {
                'symbol': symbol,
                'report_type': report_type,
                'timestamp': datetime.now().isoformat(),
                'data_type': 'financial_report',
                'data': report_data
            }
            
            self.producer.send(
                self.topics['financial_reports'],
                key=f"{symbol}_{report_type}",
                value=message
            )
            
            logger.debug(f"📊 Sent {report_type} for {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send {report_type} for {symbol}: {e}")
    
    def send_market_data(self, data_type, data):
        """Send market data to Kafka"""
        try:
            message = {
                'data_type': data_type,
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            topic = self.topics.get(data_type, 'vnstock.market.data')
            self.producer.send(topic, value=message)
            
            logger.debug(f"📈 Sent {data_type} market data")
            
        except Exception as e:
            logger.error(f"❌ Failed to send {data_type}: {e}")
    
    def fetch_and_stream_price_data(self, symbols):
        """Fetch and stream price data for symbols"""
        logger.info("📊 Streaming price data...")
        
        for i, symbol in enumerate(symbols):
            try:
                logger.info(f"   Fetching price data for {symbol} ({i+1}/{len(symbols)})")
                
                # Get latest price data
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                
                try:
                    price_data = self.vnstock['stock_historical_data'](
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date,
                        resolution='1D'
                    )
                    
                    if price_data and not price_data.empty:
                        # Send latest record
                        latest_record = price_data.iloc[-1]
                        self.send_price_data(symbol, latest_record)
                        
                        # Send all records for historical analysis
                        for _, record in price_data.iterrows():
                            self.send_price_data(symbol, record)
                
                except Exception as e:
                    logger.warning(f"   ⚠️ Price data failed for {symbol}: {e}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
        
        logger.info("✅ Price data streaming completed")
    
    def fetch_and_stream_company_profiles(self, symbols):
        """Fetch and stream company profiles"""
        logger.info("🏢 Streaming company profiles...")
        
        for i, symbol in enumerate(symbols):
            try:
                logger.info(f"   Fetching profile for {symbol} ({i+1}/{len(symbols)})")
                
                try:
                    overview = self.vnstock['company_overview'](symbol)
                    if overview and not overview.empty:
                        profile_data = overview.iloc[0].to_dict()
                        self.send_company_profile(symbol, profile_data)
                
                except Exception as e:
                    logger.warning(f"   ⚠️ Company profile failed for {symbol}: {e}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
        
        logger.info("✅ Company profiles streaming completed")
    
    def fetch_and_stream_financial_reports(self, symbols):
        """Fetch and stream financial reports"""
        logger.info("📊 Streaming financial reports...")
        
        report_types = ['IncomeStatement', 'BalanceSheet', 'CashFlow']
        
        for i, symbol in enumerate(symbols[:50]):  # Limit to first 50 for now
            try:
                logger.info(f"   Fetching financials for {symbol} ({i+1}/50)")
                
                for report_type in report_types:
                    try:
                        report_data = self.vnstock['financial_report'](
                            symbol=symbol,
                            report_type=report_type,
                            frequency='Quarterly'
                        )
                        
                        if report_data and not report_data.empty:
                            for _, row in report_data.iterrows():
                                self.send_financial_report(symbol, report_type, row.to_dict())
                    
                    except Exception as e:
                        logger.warning(f"   ⚠️ {report_type} failed for {symbol}: {e}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Error processing {symbol}: {e}")
        
        logger.info("✅ Financial reports streaming completed")
    
    def fetch_and_stream_market_data(self):
        """Fetch and stream market data"""
        logger.info("📈 Streaming market data...")
        
        # Market Indices
        indices = ['VNINDEX', 'HNXINDEX', 'UPCOMINDEX', 'VN30', 'HNX30']
        
        for index_code in indices:
            try:
                logger.info(f"   Fetching {index_code} data...")
                
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                
                try:
                    index_data = self.vnstock['stock_historical_data'](
                        symbol=index_code,
                        start_date=start_date,
                        end_date=end_date,
                        resolution='1D'
                    )
                    
                    if index_data and not index_data.empty:
                        for _, row in index_data.iterrows():
                            self.send_market_data('market_indices', {
                                'index_code': index_code,
                                'data': row.to_dict()
                            })
                
                except Exception as e:
                    logger.warning(f"   ⚠️ Index data failed for {index_code}: {e}")
                
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Error processing {index_code}: {e}")
        
        # Top Performers
        try:
            logger.info("   Fetching top performers...")
            
            # Top gainers
            gainers = self.vnstock['top_stock_heatmap'](report_type='gainers')
            if gainers and not gainers.empty:
                self.send_market_data('top_performers', {
                    'type': 'gainers',
                    'data': gainers.to_dict('records')
                })
            
            # Top losers
            losers = self.vnstock['top_stock_heatmap'](report_type='losers')
            if losers and not losers.empty:
                self.send_market_data('top_performers', {
                    'type': 'losers',
                    'data': losers.to_dict('records')
                })
        
        except Exception as e:
            logger.warning(f"   ⚠️ Top performers failed: {e}")
        
        # Foreign Trading
        try:
            logger.info("   Fetching foreign trading...")
            
            foreign_data = self.vnstock['foreign_trade_stock_list'](
                report_type='matched',
                metric='netBuyVal'
            )
            
            if foreign_data and not foreign_data.empty:
                self.send_market_data('foreign_trading', {
                    'data': foreign_data.to_dict('records')
                })
        
        except Exception as e:
            logger.warning(f"   ⚠️ Foreign trading failed: {e}")
        
        logger.info("✅ Market data streaming completed")
    
    def get_symbol_list(self):
        """Get list of symbols to process"""
        # For now, use a predefined list of major stocks
        # In production, this would come from a database or API
        return [
            'FPT', 'HPG', 'VCB', 'TCB', 'VIC', 'VHM', 'VRE', 'MSN', 'VNM', 'GAS',
            'PLX', 'POW', 'CTG', 'BID', 'MBB', 'ACB', 'TPB', 'STB', 'VPB', 'HDB',
            'VJC', 'HVN', 'VGC', 'VPI', 'VSH', 'VSC', 'VTO', 'VTV', 'VWS', 'VXB'
        ]
    
    def run_streaming_producer(self):
        """Run the streaming producer"""
        logger.info("🚀 STARTING KAFKA VNSTOCK STREAMING PRODUCER")
        logger.info("=" * 60)
        
        try:
            # Get symbol list
            symbols = self.get_symbol_list()
            logger.info(f"📊 Processing {len(symbols)} symbols")
            
            # Stream different data types
            self.fetch_and_stream_price_data(symbols)
            self.fetch_and_stream_company_profiles(symbols)
            self.fetch_and_stream_financial_reports(symbols)
            self.fetch_and_stream_market_data()
            
            # Flush all messages
            self.producer.flush()
            
            logger.info("🎉 STREAMING PRODUCER COMPLETED!")
            
        except Exception as e:
            logger.error(f"❌ Streaming producer failed: {e}")
            sys.exit(1)
        finally:
            if hasattr(self, 'producer'):
                self.producer.close()
    
    def run_continuous_producer(self):
        """Run continuous streaming (for real-time)"""
        logger.info("🔄 STARTING CONTINUOUS STREAMING PRODUCER")
        logger.info("=" * 60)
        
        symbols = self.get_symbol_list()
        
        try:
            while True:
                logger.info("🔄 Starting new streaming cycle...")
                
                # Stream price data every cycle
                self.fetch_and_stream_price_data(symbols)
                
                # Stream market data every cycle
                self.fetch_and_stream_market_data()
                
                # Flush messages
                self.producer.flush()
                
                logger.info("⏰ Waiting 60 seconds before next cycle...")
                time.sleep(60)  # Wait 1 minute
                
        except KeyboardInterrupt:
            logger.info("🛑 Streaming stopped by user")
        except Exception as e:
            logger.error(f"❌ Continuous streaming failed: {e}")
        finally:
            if hasattr(self, 'producer'):
                self.producer.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Kafka VNStock Producer')
    parser.add_argument('--mode', choices=['batch', 'continuous'], default='batch',
                       help='Run mode: batch (once) or continuous (real-time)')
    
    args = parser.parse_args()
    
    producer = KafkaVNStockProducer()
    
    if args.mode == 'continuous':
        producer.run_continuous_producer()
    else:
        producer.run_streaming_producer()
