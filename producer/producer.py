"""
Producer service for Vietnam Stock Market data.
Fetches real-time stock quotes using vnstock and publishes to Kafka.
"""

import os
import time
import json
import logging
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
from vnstock import Vnstock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'stock-quotes')
PRODUCER_INTERVAL = int(os.getenv('PRODUCER_INTERVAL', '300'))

# Get list of stocks to track from environment (comma-separated) or use all
STOCK_FILTER = os.getenv('STOCK_SYMBOLS', '')  # Empty means all stocks


def get_all_stock_symbols():
    """Get all available stock symbols from vnstock."""
    try:
        logger.info("Fetching all available stock symbols from vnstock...")
        
        # Use Vnstock to get listing companies
        stock = Vnstock().stock(symbol='ACB', source='VCI')
        
        # Try to get all listing companies
        df = stock.listing.all_symbols()
        
        if df is not None and not df.empty:
            # Get ticker column
            if 'ticker' in df.columns:
                symbols = df['ticker'].tolist()
            elif 'symbol' in df.columns:
                symbols = df['symbol'].tolist()
            elif 'code' in df.columns:
                symbols = df['code'].tolist()
            else:
                # Fallback to first column if standard column names not found
                symbols = df.iloc[:, 0].tolist()
            
            # Remove any NaN or empty values
            symbols = [s for s in symbols if s and str(s).strip() and str(s) != 'nan']
            
            logger.info(f"Found {len(symbols)} stock symbols from vnstock")
            return symbols
        else:
            logger.warning("No stock symbols found from API, using default list")
            return get_default_symbols()
            
    except Exception as e:
        logger.error(f"Error fetching stock symbols from vnstock: {e}")
        logger.info("Falling back to default stock list")
        return get_default_symbols()


def get_default_symbols():
    """Get default list of top Vietnamese stocks."""
    return [
        # Top HOSE stocks
        'VNM', 'VIC', 'VHM', 'HPG', 'TCB', 'VPB', 'MSN', 'FPT', 
        'MWG', 'BID', 'CTG', 'GAS', 'PLX', 'SSI', 'VRE', 'VCB',
        'ACB', 'MBB', 'HDB', 'POW', 'VCI', 'SAB', 'VJC', 'VNM',
        'NVL', 'PDR', 'VHC', 'DGC', 'DXG', 'KDH', 'VND', 'HCM',
        # Top HNX stocks
        'PVS', 'SHS', 'NVB', 'PVX', 'PVC', 'CEO', 'VCS', 'TNG',
        # Top UPCOM stocks  
        'VGC', 'MCH', 'ACV', 'VNR', 'BCG'
    ]


# Initialize stock symbols based on configuration
if STOCK_FILTER:
    # Use manually specified symbols
    STOCK_SYMBOLS = [s.strip() for s in STOCK_FILTER.split(',')]
    logger.info(f"Using {len(STOCK_SYMBOLS)} manually specified symbols")
else:
    # Get all available symbols
    STOCK_SYMBOLS = get_all_stock_symbols()


def create_kafka_producer():
    """Create and return a Kafka producer with retry logic."""
    max_retries = 10
    retry_interval = 5
    
    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Successfully connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
            return producer
        except KafkaError as e:
            logger.warning(f"Attempt {attempt + 1}/{max_retries}: Failed to connect to Kafka: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)
            else:
                logger.error("Max retries reached. Could not connect to Kafka.")
                raise


def fetch_stock_data(stock):
    """Fetch real-time stock data using vnstock."""
    try:
        # Initialize vnstock client
        stock_client = Vnstock().stock(symbol=stock, source='VCI')
        
        # Get real-time quote data
        quote = stock_client.quote.intraday(symbol=stock, page_size=1)
        
        if quote is not None and not quote.empty:
            latest = quote.iloc[0]
            
            # Prepare data payload
            data = {
                'ticker': stock,
                'time': datetime.now().isoformat(),
                'price': float(latest.get('matchPrice', 0)),
                'volume': int(latest.get('matchVolume', 0)),
                'total_volume': int(latest.get('accumulatedVol', 0)),
                'change': float(latest.get('priceChange', 0)),
                'change_percent': float(latest.get('priceChangePercent', 0)),
                'ceiling_price': float(latest.get('ceilingPrice', 0)),
                'floor_price': float(latest.get('floorPrice', 0)),
                'reference_price': float(latest.get('refPrice', 0)),
                'highest_price': float(latest.get('highestPrice', 0)),
                'lowest_price': float(latest.get('lowestPrice', 0)),
                'bid_price': float(latest.get('bidPrice1', 0)),
                'ask_price': float(latest.get('askPrice1', 0)),
            }
            
            return data
        else:
            logger.warning(f"No data returned for {stock}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching data for {stock}: {e}")
        return None


def main():
    """Main producer loop."""
    logger.info("Starting Vietnam Stock Market Producer...")
    logger.info(f"Tracking symbols: {', '.join(STOCK_SYMBOLS)}")
    logger.info(f"Publishing to topic: {KAFKA_TOPIC}")
    logger.info(f"Update interval: {PRODUCER_INTERVAL} seconds")
    
    # Create Kafka producer
    producer = create_kafka_producer()
    
    message_count = 0
    
    try:
        while True:
            start_time = time.time()
            
            # Fetch and publish data for each stock
            for symbol in STOCK_SYMBOLS:
                try:
                    data = fetch_stock_data(symbol)
                    
                    if data:
                        # Send to Kafka
                        future = producer.send(KAFKA_TOPIC, value=data)
                        
                        # Wait for confirmation
                        record_metadata = future.get(timeout=10)
                        
                        message_count += 1
                        
                        if message_count % 20 == 0:
                            logger.info(f"Published {message_count} messages. Latest: {symbol} @ {data['price']}")
                        
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}")
                    continue
            
            # Ensure producer flushes all buffered messages
            producer.flush()
            
            # Calculate sleep time to maintain consistent interval
            elapsed_time = time.time() - start_time
            sleep_time = max(0, PRODUCER_INTERVAL - elapsed_time)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                logger.warning(f"Processing took {elapsed_time:.2f}s, longer than interval {PRODUCER_INTERVAL}s")
                
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")
        raise
    finally:
        logger.info(f"Shutting down producer. Total messages published: {message_count}")
        producer.close()


if __name__ == "__main__":
    main()

