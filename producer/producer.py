#!/usr/bin/env python3
"""
Simple Kafka Producer for Vietnam Stock Data
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
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

class SimpleStockProducer:
    def __init__(self):
        self.setup_kafka()
        self.setup_vnstock()
        
    def setup_kafka(self):
        """Setup Kafka producer"""
        try:
            load_dotenv()
            
            kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
            
            self.producer = KafkaProducer(
                bootstrap_servers=kafka_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                max_block_ms=10000
            )
            
            logger.info("✅ Kafka producer initialized")
            
        except Exception as e:
            logger.error(f"❌ Kafka setup failed: {e}")
            sys.exit(1)
    
    def setup_vnstock(self):
        """Setup vnstock"""
        try:
            import vnstock
            self.vnstock = vnstock
            logger.info("✅ VNStock initialized")
        except Exception as e:
            logger.error(f"❌ VNStock setup failed: {e}")
            sys.exit(1)
    
    def fetch_stock_data(self, ticker):
        """Fetch intraday/real-time data for a ticker with fallbacks."""
        def build_payload(now_ts, price, volume, ref, high, low, bid, ask, total_vol=None):
            return {
                'ticker': ticker,
                'time': now_ts,
                'price': float(price) if price is not None else 0.0,
                'volume': int(volume) if volume is not None else 0,
                'total_volume': int(total_vol if total_vol is not None else (volume or 0)),
                'change': None,  # let consumer compute using reference_price
                'change_percent': None,  # let consumer compute using reference_price
                'ceiling_price': None,
                'floor_price': None,
                'reference_price': float(ref) if ref is not None else 0.0,
                'highest_price': float(high) if high is not None else None,
                'lowest_price': float(low) if low is not None else None,
                'bid_price': float(bid) if bid is not None else None,
                'ask_price': float(ask) if ask is not None else None
            }

        now_ts = datetime.now().isoformat()
        try:
            # 1) Try vnstock realtime quotes API if available
            try:
                # Hypothetical realtime endpoint in vnstock (name may differ). Wrap in try.
                quotes = None
                if hasattr(self.vnstock, 'realtime_quotes'):
                    quotes = self.vnstock.realtime_quotes(symbol=ticker)
                elif hasattr(self.vnstock, 'stock_intraday_data'):
                    # fallback intraday candles (minute)
                    quotes = self.vnstock.stock_intraday_data(symbol=ticker, page_size=1)
                if quotes is not None and not getattr(quotes, 'empty', False):
                    row = quotes.iloc[-1] if hasattr(quotes, 'iloc') else quotes[-1]
                    price = row.get('price') or row.get('close')
                    ref = row.get('reference') or row.get('reference_price')
                    volume = row.get('volume')
                    total_vol = row.get('total_volume') or volume
                    high = row.get('high') or row.get('highest_price')
                    low = row.get('low') or row.get('lowest_price')
                    bid = row.get('bid_price') or row.get('bid')
                    ask = row.get('ask_price') or row.get('ask')
                    payload = build_payload(now_ts, price, volume, ref, high, low, bid, ask, total_vol)
                    # Only return if price and ref are present; else fall through
                    if payload['price'] and payload['reference_price']:
                        return payload
            except Exception as e:
                logger.debug(f"Realtime fetch failed for {ticker}: {e}")

            # 2) Fallback to daily data: compute reference as previous day's close
            df = self.vnstock.stock_historical_data(
                symbol=ticker,
                start_date=(datetime.now() - pd.Timedelta(days=5)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                resolution='1D'
            )
            if df is not None and not df.empty:
                df = df.sort_values(by=df.columns[0]) if df.shape[1] > 0 else df  # ensure ascending by date col
                if len(df) >= 2:
                    latest = df.iloc[-1]
                    prev = df.iloc[-2]
                    price = float(latest.get('close', latest.get('Close', 0.0)))
                    volume = int(latest.get('volume', latest.get('Volume', 0)))
                    high = float(latest.get('high', latest.get('High', 0.0)))
                    low = float(latest.get('low', latest.get('Low', 0.0)))
                    ref = float(prev.get('close', prev.get('Close', price)))
                    payload = build_payload(now_ts, price, volume, ref, high, low, None, None, volume)
                    return payload
                else:
                    latest = df.iloc[-1]
                    price = float(latest.get('close', latest.get('Close', 0.0)))
                    volume = int(latest.get('volume', latest.get('Volume', 0)))
                    high = float(latest.get('high', latest.get('High', 0.0)))
                    low = float(latest.get('low', latest.get('Low', 0.0)))
                    ref = price  # no previous row available
                    payload = build_payload(now_ts, price, volume, ref, high, low, None, None, volume)
                    return payload

            # 3) Final fallback – empty payload (will be filtered by consumer)
            return build_payload(now_ts, 0.0, 0, 0.0, None, None, None, None, 0)

        except Exception as e:
            logger.warning(f"⚠️ No data returned for {ticker}: {e}")
            return build_payload(now_ts, 0.0, 0, 0.0, None, None, None, None, 0)
    
    def publish_message(self, data):
        """Publish message to Kafka"""
        try:
            topic = os.getenv('KAFKA_TOPIC', 'stock-quotes')
            key = data['ticker']
            
            future = self.producer.send(topic, key=key, value=data)
            record_metadata = future.get(timeout=10)
            
            logger.debug(f"Published {data['ticker']} to {topic}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish {data['ticker']}: {e}")
            return False
    
    def run(self):
        """Main producer loop"""
        logger.info("🚀 Starting stock data producer...")
        
        # Sample tickers
        tickers = ['VIC', 'VCB', 'VHM', 'HPG', 'MSN', 'VRE', 'CTG', 'BID', 'TCB', 'GAS']
        
        message_count = 0
        
        while True:
            try:
                for ticker in tickers:
                    data = self.fetch_stock_data(ticker)
                    if self.publish_message(data):
                        message_count += 1
                    
                    time.sleep(1)  # Be nice to the API
                
                logger.info(f"Published {len(tickers)} messages. Total: {message_count}")
                
                # Wait for next cycle
                # Default 60s; can set PRODUCER_INTERVAL=120 for 2 phút
                interval = int(os.getenv('PRODUCER_INTERVAL', '60'))
                logger.info(f"⏳ Waiting {interval} seconds for next cycle...")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Producer stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Producer error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    producer = SimpleStockProducer()
    producer.run()
