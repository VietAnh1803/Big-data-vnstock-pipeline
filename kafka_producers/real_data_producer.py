#!/usr/bin/env python3
"""
Vietnam Stock Real Data Producer - Using VNStock API
Fetches real stock data from VNStock library
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from kafka import KafkaProducer
from kafka.errors import KafkaError
import pytz
import vnstock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VietnamStockRealDataProducer:
    """Real Data Producer for Vietnam Stock Market using VNStock API"""

    def __init__(self):
        self.kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.collection_interval = int(os.getenv('COLLECTION_INTERVAL', '30'))  # seconds
        self.market_open_hour = int(os.getenv('MARKET_OPEN_HOUR', '9'))
        self.market_close_hour = int(os.getenv('MARKET_CLOSE_HOUR', '15'))
        self.timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        self.max_workers = int(os.getenv('MAX_WORKERS', '16'))

        self.producer = self._init_kafka_producer()
        self.popular_stocks = self._load_tickers()
        self.market_indices = ['VNINDEX', 'HNXINDEX', 'UPCOMINDEX', 'VN30']

        logger.info(f"📊 Loaded {len(self.popular_stocks)} Vietnam stocks for real data collection")

    def _init_kafka_producer(self):
        """Initialize Kafka Producer"""
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                batch_size=32768,
                linger_ms=100,
                buffer_memory=67108864,
                max_block_ms=60000,
                request_timeout_ms=30000
            )
            logger.info("✅ Kafka Producer initialized successfully")
            return producer
        except KafkaError as e:
            logger.error(f"❌ Kafka Producer initialization failed: {e}")
            exit(1)

    def _load_tickers(self) -> List[str]:
        """Load tickers from env/file if provided; fallback to top200_tickers.txt, then curated list."""
        tickers_env = os.getenv('TICKERS')
        tickers_file = os.getenv('TICKERS_FILE', '').strip()
        
        # Priority 1: TICKERS environment variable
        if tickers_env:
            items = [t.strip().upper() for t in tickers_env.split(',') if t.strip()]
            if items:
                logger.info(f"📋 Loaded {len(items)} tickers from TICKERS env variable")
                return items
        
        # Priority 2: TICKERS_FILE environment variable
        if tickers_file:
            try:
                with open(tickers_file, 'r') as f:
                    items = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
                if items:
                    logger.info(f"📋 Loaded {len(items)} tickers from TICKERS_FILE: {tickers_file}")
                    return items
            except Exception as e:
                logger.warning(f"⚠️ Failed to read TICKERS_FILE '{tickers_file}': {e}")
        
        # Priority 3: Try default top200_tickers.txt file
        default_file = '/app/data/top200_tickers.txt'
        try:
            with open(default_file, 'r') as f:
                items = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
                if items:
                    logger.info(f"📋 Loaded {len(items)} tickers from default file: {default_file}")
                    return items
        except Exception as e:
            logger.warning(f"⚠️ Failed to read default tickers file '{default_file}': {e}")
        
        # Fallback: curated list (~60)
        logger.warning("⚠️ Using fallback curated list (~60 tickers). Consider providing TICKERS_FILE for more tickers.")
        return [
            # VN30 core
            'VCB', 'VIC', 'VHM', 'HPG', 'FPT', 'MWG', 'PNJ', 'VNM', 'GAS', 'PLX',
            'SAB', 'VRE', 'SSI', 'HCM', 'VND', 'CTG', 'BID', 'MBB', 'TCB', 'ACB',
            'MSN', 'VPB', 'GVR', 'POW', 'VJC',

            # Large-cap banks & finance
            'STB', 'HDB', 'SSB', 'EIB', 'SHB', 'OCB', 'LPB', 'VIB', 'TPB', 'VCI',

            # Real estate & retail
            'VPI', 'VSC', 'KDH', 'PDR', 'VRE', 'NVL', 'NLG',

            # Industrial & utilities
            'GEX', 'REE', 'VSH', 'POW', 'PLX', 'PVT', 'PVD', 'GAS', 'DGC',

            # Consumer & materials
            'DPM', 'DCM', 'HSG', 'VHC', 'ANV', 'SAB', 'MSN', 'PNJ', 'MWG',

            # Transport & logistics
            'HVN', 'HAH', 'VTP',

            # Additional diversified/liquid names
            'HPG', 'HAG', 'HAX', 'VGC', 'VTO'
        ]

    def _is_market_open(self) -> bool:
        """Check if the Vietnam stock market is open (GMT+7)"""
        now_utc = datetime.now(pytz.utc)
        now_hcm = now_utc.astimezone(self.timezone)
        
        # Check if it's a weekday
        if now_hcm.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
            
        # Check market hours (9:00 - 15:00 GMT+7)
        if self.market_open_hour <= now_hcm.hour < self.market_close_hour:
            return True
        return False

    def _fetch_real_stock_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch real stock data from VNStock API"""
        try:
            # Get intraday data from VNStock
            df = vnstock.stock_intraday_data(symbol=ticker, page_size=1)
            
            if df is not None and not df.empty:
                latest = df.iloc[0]
                current_time = datetime.now(self.timezone)
                
                # Extract data from VNStock response - handle different column names safely
                try:
                    current_price = float(latest.get('averagePrice', latest.get('price', 0)))
                    prev_price_change = float(latest.get('prevPriceChange', latest.get('change', 0)))
                    volume = int(latest.get('volume', 0))
                    quote_time = str(latest.get('time', current_time.strftime('%H:%M:%S')))
                    
                    # Calculate percent change safely
                    if current_price > 0 and prev_price_change != 0:
                        percent_change = (prev_price_change / (current_price - prev_price_change) * 100)
                    else:
                        percent_change = 0
                    
                    return {
                        'ticker': ticker,
                        'price': round(current_price, 2),
                        'volume': volume,
                        'change': round(prev_price_change, 2),
                        'percent_change': round(percent_change, 2),
                        'high': round(current_price * 1.02, 2),  # Estimate high
                        'low': round(current_price * 0.98, 2),   # Estimate low
                        'open_price': round(current_price - prev_price_change, 2),
                        'close_price': current_price,
                        'quote_time': quote_time,
                        'ingest_time': current_time.isoformat(),
                        'data_source': 'VNStock Real Data'
                    }
                except (KeyError, ValueError) as e:
                    logger.warning(f"⚠️ Data format issue for {ticker}: {str(e)}")
                    return None
            else:
                logger.warning(f"⚠️ No data returned for {ticker}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching real data for {ticker}: {str(e)}")
            return None

    def _publish_to_kafka(self, topic: str, data: Dict[str, Any]):
        """Publish data to a Kafka topic"""
        try:
            key_bytes = (data.get('ticker') or 'NA').encode('utf-8')
            self.producer.send(topic, key=key_bytes, value=data)
            self.producer.flush()  # Ensure message is sent immediately
            logger.info(f"✅ Published to topic '{topic}': {data.get('ticker', 'N/A')}")
        except KafkaError as e:
            logger.error(f"❌ Failed to publish to topic '{topic}': {e}")

    def collect_real_realtime_quotes(self):
        """Collect real-time quotes using VNStock API"""
        if not self._is_market_open():
            logger.info("Market is closed. Skipping real-time quote collection.")
            return

        logger.info(f"📈 Collecting REAL-TIME quotes for {len(self.popular_stocks)} stocks...")

        success_count = 0
        error_count = 0
        no_data_count = 0

        def worker(ticker: str) -> Optional[Dict[str, Any]]:
            try:
                return self._fetch_real_stock_data(ticker)
            except Exception as e:
                logger.error(f"❌ Error fetching {ticker}: {e}")
                return None

        # Parallel fetch to increase throughput; control workers via MAX_WORKERS
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_map = {executor.submit(worker, t): t for t in self.popular_stocks}
            for future in as_completed(future_map):
                ticker = future_map[future]
                try:
                    data = future.result()
                    if data:
                        self._publish_to_kafka('realtime_quotes', data)
                        success_count += 1
                    else:
                        no_data_count += 1
                except Exception as e:
                    logger.error(f"❌ Error in future for {ticker}: {e}")
                    error_count += 1

        logger.info(
            f"✅ Cycle stats: published={success_count}, no_data={no_data_count}, errors={error_count}, tickers={len(self.popular_stocks)}"
        )

    def run_schedule(self):
        """Schedule real data collection"""
        logger.info("🚀 Starting Vietnam Stock REAL DATA Producer...")
        logger.info("📊 Using VNStock API for authentic market data")
        
        cycle_count = 0
        while True:
            cycle_count += 1
            logger.info(f"🔄 Real Data Collection Cycle #{cycle_count}")
            
            vietnam_time = datetime.now(self.timezone)
            logger.info(f"🇻🇳 Vietnam Time (GMT+7): {vietnam_time.strftime('%Y-%m-%d %H:%M:%S %z')}")
            
            if self._is_market_open():
                logger.info("📊 Market Status: OPEN - Collecting REAL data")
                self.collect_real_realtime_quotes()
            else:
                logger.info("📊 Market Status: CLOSED")
            
            logger.info(f"✅ Real data collection cycle #{cycle_count} completed")
            time.sleep(self.collection_interval)

    def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("✅ Real data producer stopped successfully")

if __name__ == "__main__":
    producer = VietnamStockRealDataProducer()
    try:
        producer.run_schedule()
    except KeyboardInterrupt:
        logger.info("🛑 Stopping Vietnam Stock Real Data Producer...")
    finally:
        producer.stop()
