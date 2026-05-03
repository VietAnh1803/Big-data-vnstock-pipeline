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
try:
    # vnstock3 package namespace
    from vnstock3 import Vnstock  # type: ignore
except Exception:  # pragma: no cover
    Vnstock = None

try:
    # vnstock v3+
    from vnstock import Vnstock as VnstockV3  # type: ignore
except Exception:  # pragma: no cover
    VnstockV3 = None

try:
    # Legacy fallback for older package versions
    import vnstock as vnstock_legacy  # type: ignore
except Exception:  # pragma: no cover
    vnstock_legacy = None

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
        self.vnstock_api_key = os.getenv("VNSTOCK_API_KEY", "").strip()
        self.vnstock_client = self._init_quote_client()
        self.vnstock_source = os.getenv("VNSTOCK_SOURCE", "KBS")
        self.max_requests_per_minute = int(os.getenv("VNSTOCK_MAX_REQUESTS_PER_MINUTE", "18"))
        self.use_largecap_first = os.getenv("VNSTOCK_USE_LARGECAP_FIRST", "true").strip().lower() == "true"
        self.max_tickers_in_rotation = int(os.getenv("VNSTOCK_MAX_TICKERS_IN_ROTATION", "30"))
        self._ticker_cursor = 0
        self._last_price_by_ticker: Dict[str, float] = {}
        self.vn_market_holidays = self._load_vn_market_holidays()

        self.producer = self._init_kafka_producer()
        self.popular_stocks = self._load_tickers()
        self.popular_stocks = self._optimize_ticker_universe(self.popular_stocks)
        self.market_indices = ['VNINDEX', 'HNXINDEX', 'UPCOMINDEX', 'VN30']

        logger.info(f"Loaded {len(self.popular_stocks)} Vietnam stocks for real data collection")

    def _load_vn_market_holidays(self) -> set[str]:
        """Load Vietnamese market holiday list in YYYY-MM-DD format."""
        raw = os.getenv("VN_MARKET_HOLIDAYS", "").strip()
        holidays = {d.strip() for d in raw.split(",") if d.strip()} if raw else set()
        return holidays

    def _init_quote_client(self):
        """Initialize vnstock quote client (v3 preferred)."""
        init_kwargs = {"show_log": False}
        if self.vnstock_api_key:
            init_kwargs["api_key"] = self.vnstock_api_key

        if Vnstock is not None:
            try:
                # Prefer vnstock v3 API surface.
                return Vnstock(**init_kwargs)
            except Exception as e:
                logger.warning(f"vnstock3 init failed, fallback to other API: {e}")
                try:
                    # Fallback in case installed version does not support api_key kwarg.
                    return Vnstock(show_log=False)
                except Exception:
                    pass
        if VnstockV3 is not None:
            try:
                return VnstockV3(**init_kwargs)
            except Exception as e:
                logger.warning(f"vnstock v3 init failed, fallback to legacy API: {e}")
                try:
                    return VnstockV3(show_log=False)
                except Exception:
                    pass
        return None

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
            logger.info("Kafka Producer initialized successfully")
            return producer
        except KafkaError as e:
            logger.error(f"Kafka Producer initialization failed: {e}")
            exit(1)

    def _load_tickers(self) -> List[str]:
        """Load tickers from env/file if provided; fallback to top200_tickers.txt, then curated list."""
        tickers_env = os.getenv('TICKERS')
        tickers_file = os.getenv('TICKERS_FILE', '').strip()
        
        # Priority 1: TICKERS environment variable
        if tickers_env:
            items = [t.strip().upper() for t in tickers_env.split(',') if t.strip()]
            if items:
                logger.info(f"Loaded {len(items)} tickers from TICKERS env variable")
                return items
        
        # Priority 2: TICKERS_FILE environment variable
        if tickers_file:
            try:
                with open(tickers_file, 'r') as f:
                    items = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
                if items:
                    logger.info(f"Loaded {len(items)} tickers from TICKERS_FILE: {tickers_file}")
                    return items
            except Exception as e:
                logger.warning(f"Failed to read TICKERS_FILE '{tickers_file}': {e}")
        
        # Priority 3: Try default top200_tickers.txt file
        default_file = '/app/data/top200_tickers.txt'
        try:
            with open(default_file, 'r') as f:
                items = [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
                if items:
                    logger.info(f"Loaded {len(items)} tickers from default file: {default_file}")
                    return items
        except Exception as e:
            logger.warning(f"Failed to read default tickers file '{default_file}': {e}")
        
        # Fallback: curated list (~60)
        logger.warning("Using fallback curated list (~60 tickers). Consider providing TICKERS_FILE for more tickers.")
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

    def _optimize_ticker_universe(self, tickers: List[str]) -> List[str]:
        """
        Optimize ticker rotation for free-tier API:
        - prioritize large/liquid tickers first
        - cap rotation universe to improve revisit frequency
        """
        if not tickers:
            return tickers

        deduped = list(dict.fromkeys([t.strip().upper() for t in tickers if t.strip()]))
        if not deduped:
            return deduped

        # Prioritized large-cap/liquid basket (VN30/banks/market leaders).
        priority_order = [
            "VCB", "BID", "CTG", "TCB", "MBB", "ACB", "VPB", "HDB", "STB", "EIB",
            "VIC", "VHM", "VRE", "NVL", "KDH", "NLG",
            "HPG", "GVR", "DGC", "GAS", "PLX", "POW",
            "FPT", "MWG", "PNJ", "VNM", "MSN", "SAB",
            "SSI", "VND", "HCM", "VCI",
            "VJC", "HVN", "HAH", "VTP",
        ]

        if self.use_largecap_first:
            priority = [t for t in priority_order if t in deduped]
            remain = [t for t in deduped if t not in set(priority)]
            ordered = priority + remain
        else:
            ordered = deduped

        if self.max_tickers_in_rotation > 0:
            ordered = ordered[: self.max_tickers_in_rotation]

        logger.info(
            "Ticker rotation optimized: total=%s, largecap_first=%s, top10=%s",
            len(ordered),
            self.use_largecap_first,
            ",".join(ordered[:10]),
        )
        return ordered

    def _is_market_open(self) -> bool:
        """Check if the Vietnam stock market is open (GMT+7)"""
        now_utc = datetime.now(pytz.utc)
        now_hcm = now_utc.astimezone(self.timezone)
        now_date = now_hcm.date()
        date_key = now_date.isoformat()
        month_day = now_date.strftime("%m-%d")

        # Fixed-date public holidays (approx baseline, can override via VN_MARKET_HOLIDAYS)
        fixed_holidays = {"01-01", "04-30", "05-01", "09-02"}
        if date_key in self.vn_market_holidays or month_day in fixed_holidays:
            return False
        
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
            # Prefer vnstock v3 quote adapter.
            if self.vnstock_client is not None:
                stock_obj = self.vnstock_client.stock(symbol=ticker, source=self.vnstock_source)
                df = stock_obj.quote.intraday(page_size=1, show_log=False)
            elif vnstock_legacy is not None:
                # Legacy fallback path for backward compatibility.
                df = vnstock_legacy.stock_intraday_data(symbol=ticker, page_size=1)
            else:
                logger.error("No vnstock client available")
                return None
            
            if df is not None and not df.empty:
                latest = df.iloc[0]
                current_time = datetime.now(self.timezone)
                
                # Extract data from vnstock response with tolerant column mapping.
                try:
                    current_price = float(
                        latest.get('averagePrice',
                                   latest.get('price',
                                              latest.get('match_price',
                                                         latest.get('close', 0))))
                    )
                    # Some sources (e.g., KBS intraday) only expose time/price/volume.
                    # Prefer provider's absolute change if present; otherwise infer
                    # from previous observed tick for the same ticker.
                    provider_change = latest.get(
                        'prevPriceChange',
                        latest.get('change', latest.get('price_change', None))
                    )
                    inferred_prev_price = self._last_price_by_ticker.get(ticker, current_price)
                    if provider_change is not None:
                        change_abs = float(provider_change)
                        base_price = current_price - change_abs
                    else:
                        change_abs = current_price - inferred_prev_price
                        base_price = inferred_prev_price
                    volume = int(latest.get('volume', latest.get('match_qtty', 0)))
                    quote_time_raw = str(
                        latest.get('time',
                                   latest.get('match_time',
                                              current_time.strftime('%H:%M:%S')))
                    )
                    # Keep compatibility with DB schema (quote_time VARCHAR(10)).
                    # vnstock may return full datetime; we only keep HH:MM:SS.
                    quote_time = quote_time_raw[-8:] if len(quote_time_raw) >= 8 else quote_time_raw
                    
                    # Calculate percent change safely (against base price).
                    percent_change = (change_abs / base_price * 100) if base_price else 0
                    self._last_price_by_ticker[ticker] = current_price
                    
                    return {
                        'ticker': ticker,
                        'price': round(current_price, 2),
                        'volume': volume,
                        'change': round(change_abs, 2),
                        'percent_change': round(percent_change, 2),
                        'high': round(current_price * 1.02, 2),  # Estimate high
                        'low': round(current_price * 0.98, 2),   # Estimate low
                        'open_price': round(base_price if base_price else current_price, 2),
                        'close_price': current_price,
                        'quote_time': quote_time,
                        'ingest_time': current_time.isoformat(),
                        'data_source': 'VNStock Real Data'
                    }
                except (KeyError, ValueError) as e:
                    logger.warning(f"Data format issue for {ticker}: {str(e)}")
                    return None
            else:
                logger.warning(f"No data returned for {ticker}")
                return None
                
        except BaseException as e:
            err_msg = str(e)
            if "Rate limit exceeded" in err_msg or "GIỚI HẠN API ĐÃ ĐẠT TỐI ĐA" in err_msg:
                logger.warning("VNStock rate limit reached while fetching %s", ticker)
            logger.error(f"Error fetching real data for {ticker}: {str(e)}")
            return None

    def _publish_to_kafka(self, topic: str, data: Dict[str, Any]):
        """Publish data to a Kafka topic"""
        try:
            key_bytes = (data.get('ticker') or 'NA').encode('utf-8')
            self.producer.send(topic, key=key_bytes, value=data)
            self.producer.flush()  # Ensure message is sent immediately
            logger.info(f"Published to topic '{topic}': {data.get('ticker', 'N/A')}")
        except KafkaError as e:
            logger.error(f"Failed to publish to topic '{topic}': {e}")

    def collect_real_realtime_quotes(self):
        """Collect real-time quotes using VNStock API"""
        if not self._is_market_open():
            logger.info("Market is closed. Skipping real-time quote collection.")
            return

        # Respect vnstock rate limit by selecting a capped ticker slice per cycle.
        per_cycle_limit = max(1, int(self.max_requests_per_minute * self.collection_interval / 60))
        selected_tickers = self._select_tickers_for_cycle(per_cycle_limit)
        logger.info(
            f"Collecting REAL-TIME quotes for {len(selected_tickers)} tickers this cycle "
            f"(limit={per_cycle_limit}/cycle, source={self.vnstock_source})"
        )

        success_count = 0
        error_count = 0
        no_data_count = 0

        def worker(ticker: str) -> Optional[Dict[str, Any]]:
                try:
                    return self._fetch_real_stock_data(ticker)
                except Exception as e:
                    logger.error(f"Error fetching {ticker}: {e}")
                    return None

        # Parallel fetch to increase throughput; control workers via MAX_WORKERS
        worker_count = max(1, min(self.max_workers, len(selected_tickers), per_cycle_limit))
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_map = {executor.submit(worker, t): t for t in selected_tickers}
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
                    logger.error(f"Error in future for {ticker}: {e}")
                    error_count += 1

        logger.info(
            f"Cycle stats: published={success_count}, no_data={no_data_count}, errors={error_count}, "
            f"tickers={len(selected_tickers)}, cursor={self._ticker_cursor}"
        )

    def _select_tickers_for_cycle(self, limit: int) -> List[str]:
        """Round-robin ticker selection to distribute requests across full universe."""
        total = len(self.popular_stocks)
        if total == 0:
            return []
        limit = max(1, min(limit, total))
        start = self._ticker_cursor % total
        end = start + limit
        if end <= total:
            selected = self.popular_stocks[start:end]
        else:
            selected = self.popular_stocks[start:] + self.popular_stocks[:end - total]
        self._ticker_cursor = (start + limit) % total
        return selected

    def run_schedule(self):
        """Schedule real data collection"""
        logger.info("Starting Vietnam Stock REAL DATA Producer...")
        logger.info("Using VNStock API for authentic market data")
        
        cycle_count = 0
        while True:
            cycle_count += 1
            logger.info(f"Real Data Collection Cycle #{cycle_count}")
            
            vietnam_time = datetime.now(self.timezone)
            logger.info(f"Vietnam Time (GMT+7): {vietnam_time.strftime('%Y-%m-%d %H:%M:%S %z')}")
            
            if self._is_market_open():
                logger.info("Market Status: OPEN - Collecting REAL data")
                self.collect_real_realtime_quotes()
            else:
                logger.info("Market Status: CLOSED")
            
            logger.info(f"Real data collection cycle #{cycle_count} completed")
            time.sleep(self.collection_interval)

    def stop(self):
        """Stop the Kafka producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Real data producer stopped successfully")

if __name__ == "__main__":
    producer = VietnamStockRealDataProducer()
    try:
        producer.run_schedule()
    except KeyboardInterrupt:
        logger.info("Stopping Vietnam Stock Real Data Producer...")
    finally:
        producer.stop()
