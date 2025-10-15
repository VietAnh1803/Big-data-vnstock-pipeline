import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import json
import time
import threading
from queue import Queue
from kafka import KafkaConsumer
from sqlalchemy import create_engine, text
import urllib.parse

# Page config
st.set_page_config(
    page_title="Vietnam Stock Dashboard - Hybrid",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

"""Custom CSS loader - prefer external styles.css, fallback to built-in."""
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception:
        # Minimal fallback if file missing
        st.markdown(
            """
    <style>
            body { background-color: #0E1117; color: #FAFAFA; }
            h1, h2, h3, h4, h5, h6 { color: #00A9FF; }
    </style>
            """,
            unsafe_allow_html=True,
        )

# Load CSS
load_css()

# Database connection - PostgreSQL fallback
def get_db_connection():
    try:
        # Use environment variables with correct password
        user = os.getenv('POSTGRES_USER', 'admin')
        password = os.getenv('POSTGRES_PASSWORD', 'admin')
        # Prefer localhost if running on the same host; fall back to docker service name
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'stock_db')
        
        # URL encode password for special characters
        import urllib.parse
        encoded_password = urllib.parse.quote_plus(password)
        
        # Force TCP connection with explicit host and port - NO SOCKET
        connection_string = f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{db}?sslmode=disable"
        
        engine = create_engine(connection_string, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# =============================
# Kafka realtime consumer (background)
# =============================
class RealtimeBuffer:
    def __init__(self):
        self.latest_by_ticker = {}
        self.latest_timestamp = None
        self.total_messages = 0
        self._lock = threading.Lock()

    def update(self, message_value: dict):
        ticker = message_value.get("ticker") or message_value.get("symbol")
        event_time = message_value.get("time") or message_value.get("timestamp")
        with self._lock:
            if ticker:
                self.latest_by_ticker[ticker] = message_value
            self.total_messages += 1
            # Keep latest wall-clock from payload if present
            if event_time:
                self.latest_timestamp = event_time

    def snapshot(self):
        with self._lock:
            return (
                dict(self.latest_by_ticker),
                self.latest_timestamp,
                self.total_messages,
            )

@st.cache_resource(show_spinner=False)
def start_kafka_consumer():
    """Start Kafka consumer in a background thread and return realtime buffer."""
    buffer = RealtimeBuffer()

    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(",")
    kafka_topic = os.getenv("KAFKA_TOPIC", "stock-quotes")
    kafka_group = os.getenv("KAFKA_GROUP_ID", "dashboard-consumer-group")

    def _consume_loop():
        consumer = None
        attempt = 0
        max_attempts = 30
        backoff_seconds = 3
        while consumer is None and attempt < max_attempts:
            try:
                consumer = KafkaConsumer(
                    kafka_topic,
                    bootstrap_servers=kafka_servers,
                    group_id=kafka_group,
                    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                    key_deserializer=lambda m: m.decode("utf-8") if m else None,
                    auto_offset_reset="latest",
                    enable_auto_commit=True,
                    consumer_timeout_ms=30000,
                )
            except Exception as e:
                attempt += 1
                print(f"Kafka consumer connect failed (attempt {attempt}/{max_attempts}): {e}")
                time.sleep(backoff_seconds)
                backoff_seconds = min(backoff_seconds * 2, 60)

        if consumer is None:
            print("Kafka consumer giving up after retries")
            return

        for msg in consumer:
            try:
                payload = msg.value if isinstance(msg.value, dict) else {}
                buffer.update(payload)
            except Exception:
                continue

    thread = threading.Thread(target=_consume_loop, name="kafka-consumer-thread", daemon=True)
    thread.start()
    return buffer

# Data fetching functions - PostgreSQL fallback
def get_ticker_list():
    """Get available tickers from PostgreSQL"""
    engine = get_db_connection()
    if not engine:
        # Fallback to hardcoded list if DB connection fails
        return ['HPG', 'MSN', 'VCB', 'VHM', 'VIC', 'FPT', 'TCB', 'GAS', 'PLX', 'POW']
    
    try:
        # Get all tickers with valid data, ordered by volume (most active first)
        # Prefer realtime tickers from realtime_quotes; fallback to historical if empty
        query_rt = text("""
            SELECT DISTINCT ticker
            FROM realtime_quotes
            WHERE time >= NOW() - INTERVAL '2 days'
            ORDER BY ticker
            LIMIT 200
        """)
        df = pd.read_sql(query_rt, engine)
        if df.empty:
            query_hist = text("""
                SELECT DISTINCT ticker
            FROM historical_prices 
            WHERE close_price > 0 
                  AND trading_date >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY ticker
                LIMIT 200
            """)
            df = pd.read_sql(query_hist, engine)
        
        if not df.empty:
            tickers = df['ticker'].tolist()
            st.sidebar.success(f"📊 Found {len(tickers)} active tickers")
            return tickers
        else:
            # Fallback if no recent data
            return ['HPG', 'MSN', 'VCB', 'VHM', 'VIC', 'FPT', 'TCB', 'GAS', 'PLX', 'POW']
            
    except Exception as e:
        st.sidebar.error(f"Error fetching tickers: {e}")
        return ['HPG', 'MSN', 'VCB', 'VHM', 'VIC', 'FPT', 'TCB', 'GAS', 'PLX', 'POW']

def get_realtime_data(ticker=None, limit=1000):
    """Get real-time data from PostgreSQL using realtime_quotes when available."""
    engine = get_db_connection()
    if not engine:
        return pd.DataFrame()
    
    try:
        if ticker and ticker != "All":
            # First try realtime_quotes
            query_rt = text("""
                WITH prev AS (
                    SELECT hp.ticker, MAX(hp.trading_date) AS d
                    FROM historical_prices hp
                    WHERE hp.ticker = :ticker
                    GROUP BY hp.ticker
                ), prev_close AS (
                    SELECT hp.ticker, hp.close_price AS prev_close
                    FROM historical_prices hp
                    JOIN prev p ON p.ticker = hp.ticker AND p.d = hp.trading_date
                )
                SELECT COALESCE(rq.time, rq.created_at) AS time,
                       rq.price,
                       rq.volume,
                       rq.total_volume,
                       /* compute if missing */
                       COALESCE(rq.change, CASE WHEN pc.prev_close IS NOT NULL AND pc.prev_close > 0 THEN rq.price - pc.prev_close END) AS change,
                       COALESCE(rq.change_percent, CASE WHEN pc.prev_close IS NOT NULL AND pc.prev_close > 0 THEN (rq.price - pc.prev_close) / pc.prev_close * 100 END) AS change_percent,
                       COALESCE(rq.reference_price, pc.prev_close) AS open_price,
                       rq.highest_price AS high_price,
                       rq.lowest_price AS low_price,
                       rq.bid_price,
                       rq.ask_price,
                       rq.ceiling_price,
                       rq.floor_price
                FROM realtime_quotes rq
                LEFT JOIN prev_close pc ON pc.ticker = rq.ticker
                WHERE rq.ticker = :ticker
                ORDER BY COALESCE(rq.time, rq.created_at) DESC
                LIMIT :limit
            """)
            df = pd.read_sql(query_rt, engine, params={"ticker": ticker, "limit": limit})
            if df.empty:
                # Fallback to historical_prices
                query_hist = text("""
                SELECT trading_date as time, close_price as price, volume, 
                           ((close_price - open_price) / NULLIF(open_price,0) * 100) as change_percent,
                       open_price, high_price, low_price
                FROM historical_prices
                WHERE ticker = :ticker
                ORDER BY trading_date DESC
                LIMIT :limit
            """)
                df = pd.read_sql(query_hist, engine, params={"ticker": ticker, "limit": limit})
        else:
            # Latest snapshot for all tickers from realtime_quotes
            query_rt_all = text("""
                WITH latest AS (
                    SELECT ticker, MAX(COALESCE(time, created_at)) AS max_time
                    FROM realtime_quotes
                    GROUP BY ticker
                ), prev AS (
                    SELECT hp.ticker, MAX(hp.trading_date) AS d
                    FROM historical_prices hp
                    GROUP BY hp.ticker
                ), prev_close AS (
                    SELECT hp.ticker, hp.close_price AS prev_close
                    FROM historical_prices hp
                    JOIN prev p ON p.ticker = hp.ticker AND p.d = hp.trading_date
                )
                SELECT rq.ticker,
                       COALESCE(rq.time, rq.created_at) AS time,
                       rq.price,
                       rq.volume,
                       rq.total_volume,
                       COALESCE(rq.change, CASE WHEN pc.prev_close IS NOT NULL AND pc.prev_close > 0 THEN rq.price - pc.prev_close END) AS change,
                       COALESCE(rq.change_percent, CASE WHEN pc.prev_close IS NOT NULL AND pc.prev_close > 0 THEN (rq.price - pc.prev_close) / pc.prev_close * 100 END) AS change_percent,
                       COALESCE(rq.reference_price, pc.prev_close) AS open_price,
                       rq.highest_price AS high_price,
                       rq.lowest_price AS low_price,
                       rq.bid_price,
                       rq.ask_price,
                       rq.ceiling_price,
                       rq.floor_price
                FROM realtime_quotes rq
                JOIN latest ON latest.ticker = rq.ticker
                           AND latest.max_time = COALESCE(rq.time, rq.created_at)
                LEFT JOIN prev_close pc ON pc.ticker = rq.ticker
                ORDER BY rq.volume DESC NULLS LAST
                LIMIT :limit
            """)
            df = pd.read_sql(query_rt_all, engine, params={"limit": limit})
            if df.empty:
                # Fallback to latest trading day from historical_prices
                query_hist_all = text("""
                SELECT 
                    ticker, trading_date as time, close_price as price, volume,
                        ((close_price - open_price) / NULLIF(open_price,0) * 100) as change_percent,
                    open_price, high_price, low_price
                FROM historical_prices h1
                WHERE trading_date = (
                    SELECT MAX(trading_date) 
                    FROM historical_prices h2 
                    WHERE h2.ticker = h1.ticker
                )
                AND close_price > 0
                ORDER BY volume DESC
                LIMIT :limit
            """)
                df = pd.read_sql(query_hist_all, engine, params={"limit": limit})
        
        return df
    except Exception as e:
        st.error(f"Error fetching realtime data: {e}")
        return pd.DataFrame()

# Utility to drop entirely-null columns for cleaner display
def drop_all_null_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    non_all_null_cols = [c for c in df.columns if not df[c].isna().all()]
    return df[non_all_null_cols]

# Utilities for merging realtime with DB history
def _parse_event_time(value):
    try:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value))
        s = str(value).replace('Z', '+00:00')
        return datetime.fromisoformat(s)
    except Exception:
        return None

def merge_realtime_row(ticker: str, db_df: pd.DataFrame, payload: dict) -> pd.DataFrame:
    if not payload:
        return db_df
    # Build one-row DataFrame from Kafka payload
    price = pd.to_numeric(pd.Series([payload.get('price')]), errors='coerce').iloc[0]
    ref = pd.to_numeric(pd.Series([payload.get('reference_price') or payload.get('reference')]), errors='coerce').iloc[0]
    vol = pd.to_numeric(pd.Series([payload.get('volume')]), errors='coerce').iloc[0]
    chg = pd.to_numeric(pd.Series([payload.get('change')]), errors='coerce').iloc[0]
    chg_pct = pd.to_numeric(pd.Series([payload.get('change_percent')]), errors='coerce').iloc[0]
    if pd.isna(chg) and not pd.isna(price) and not pd.isna(ref) and ref != 0:
        chg = price - ref
    if pd.isna(chg_pct) and not pd.isna(price) and not pd.isna(ref) and ref != 0:
        chg_pct = (price - ref) / ref * 100.0
    event_time = _parse_event_time(payload.get('time') or payload.get('timestamp')) or datetime.now()
    rt_row = pd.DataFrame([
        {
            'time': event_time,
            'price': price,
            'volume': vol,
            'total_volume': vol,
            'change': chg,
            'change_percent': chg_pct,
            'open_price': ref,
            'high_price': pd.to_numeric(pd.Series([payload.get('highest_price')]), errors='coerce').iloc[0],
            'low_price': pd.to_numeric(pd.Series([payload.get('lowest_price')]), errors='coerce').iloc[0],
        }
    ])
    # Merge: append, sort by time, drop duplicates on time keep last
    combined = (pd.concat([rt_row, db_df], ignore_index=True)
                  .sort_values('time'))
    combined = combined.drop_duplicates(subset=['time'], keep='last')
    # Keep last N points for performance
    if len(combined) > 500:
        combined = combined.tail(500)
    return combined

def clean_quotes_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    df = df.copy()
    # Parse time
    if 'time' in df.columns:
        try:
            df['time'] = pd.to_datetime(df['time'], errors='coerce', utc=False)
        except Exception:
            pass
    # Numeric coercion
    numeric_candidates = ['price','open_price','high_price','low_price','volume','total_volume','change','change_percent']
    for col in [c for c in numeric_candidates if c in df.columns]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    # Impute open/high/low
    if 'open_price' in df.columns:
        if 'open_price' in df.columns and df['open_price'].isna().any():
            df['open_price'] = df['open_price'].fillna(df.get('reference_price') if 'reference_price' in df.columns else None)
        df['open_price'] = df['open_price'].fillna(df.get('price'))
    if 'high_price' in df.columns:
        df['high_price'] = df['high_price'].fillna(df.get('price'))
    if 'low_price' in df.columns:
        df['low_price'] = df['low_price'].fillna(df.get('price'))
    # Compute change/percent if missing
    if 'price' in df.columns and 'open_price' in df.columns:
        need_change = ('change' in df.columns and df['change'].isna().any()) or ('change' not in df.columns)
        need_pct = ('change_percent' in df.columns and df['change_percent'].isna().any()) or ('change_percent' not in df.columns)
        if need_change:
            df['change'] = (df['price'] - df['open_price']).where(df['open_price'] > 0)
        if need_pct:
            df['change_percent'] = ((df['price'] - df['open_price']) / df['open_price'] * 100).where(df['open_price'] > 0)
    # Remove impossible/outlier rows
    if 'change_percent' in df.columns:
        df.loc[df['change_percent'].abs() > 50, ['change','change_percent']] = pd.NA
    # Basic validity filters
    if 'price' in df.columns:
        df = df[df['price'] > 0]
    if 'open_price' in df.columns:
        df = df[df['open_price'] > 0]
    # Drop any-all-null columns and rows lacking time
    df = drop_all_null_columns(df)
    if 'time' in df.columns:
        df = df.dropna(subset=['time'])
        df = df.sort_values('time')
    return df

# Main dashboard
def main():
    st.markdown('<h1 class="main-header">📈 Vietnam Stock Dashboard - Professional</h1>', unsafe_allow_html=True)
    
    # Auto-refresh every 30 seconds
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (5s)", value=True)
    if auto_refresh:
        time.sleep(5)
        st.rerun()
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")

    # Start Kafka consumer (background) and show realtime freshness
    rt_buffer = start_kafka_consumer()
    latest_by_ticker, latest_ts, total_msgs = rt_buffer.snapshot()
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚡ Realtime Stream")
    st.sidebar.write(f"Messages: {total_msgs}")
    if latest_ts:
        st.sidebar.write(f"Last event: {latest_ts}")
    else:
        st.sidebar.write("Last event: N/A")
    
    # Get tickers from PostgreSQL
    tickers = get_ticker_list()
    if not tickers:
        st.error("❌ No tickers available from database")
        return
    
    # Ticker selection with search
    selected_ticker = st.sidebar.selectbox(
        "📊 Select Ticker",
        ["All"] + tickers,
        index=0,
        help="Select 'All' for market overview or specific ticker for analysis"
    )
    
    # Time range
    time_range = st.sidebar.selectbox(
        "⏰ Time Range",
        ["1 Week", "1 Month", "3 Months", "6 Months", "1 Year"],
        index=2
    )
    
    # Manual refresh button
    if st.sidebar.button("🔄 Manual Refresh"):
        st.rerun()
    
    # Add info boxes
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Data Source**: PostgreSQL Database")
    st.sidebar.info("🔄 **Real-time**: Auto-refresh every 30s")
    st.sidebar.info(f"📊 **Active Tickers**: {len(tickers)}")
    st.sidebar.info(f"🕐 **Last Update**: {datetime.now().strftime('%H:%M:%S')}")
    
    # Main content
    if selected_ticker == "All":
        st.subheader("📊 Market Overview - All Active Tickers")
        
        # Get latest market data for all tickers from pre-aggregated metrics if available
        engine = get_db_connection()
        metrics_q = None
        all_ticker_data = pd.DataFrame()
        try:
            if engine:
                metrics_q = text("""
                    WITH latest_minute AS (
                        SELECT ticker, MAX(minute_start) AS max_min
                        FROM realtime_metrics_minute
                        GROUP BY ticker
                    )
                    SELECT m.ticker,
                           m.minute_end AS time,
                           m.last_price AS price,
                           m.sum_volume AS volume
                    FROM realtime_metrics_minute m
                    JOIN latest_minute lm ON lm.ticker=m.ticker AND lm.max_min=m.minute_start
                    ORDER BY m.sum_volume DESC NULLS LAST
                    LIMIT 1000
                """)
                all_ticker_data = pd.read_sql(metrics_q, engine)
        except Exception:
            all_ticker_data = pd.DataFrame()
        if all_ticker_data.empty:
            # Fallback to realtime_quotes snapshot
            all_ticker_data = get_realtime_data("All", 1000)
        # Overlay Kafka latest snapshot per ticker (price, volume, change, change_percent, open_price)
        if latest_by_ticker and not all_ticker_data.empty:
            live_rows = []
            for tkr, payload in latest_by_ticker.items():
                price = pd.to_numeric(pd.Series([payload.get('price')]), errors='coerce').iloc[0]
                ref = pd.to_numeric(pd.Series([payload.get('reference_price') or payload.get('reference')]), errors='coerce').iloc[0]
                vol = pd.to_numeric(pd.Series([payload.get('volume')]), errors='coerce').iloc[0]
                chg = pd.to_numeric(pd.Series([payload.get('change')]), errors='coerce').iloc[0]
                chg_pct = pd.to_numeric(pd.Series([payload.get('change_percent')]), errors='coerce').iloc[0]
                if pd.isna(chg) and not pd.isna(price) and not pd.isna(ref) and ref != 0:
                    chg = price - ref
                if pd.isna(chg_pct) and not pd.isna(price) and not pd.isna(ref) and ref != 0:
                    chg_pct = (price - ref) / ref * 100.0
                live_rows.append({
                    'ticker': tkr,
                    'price': price,
                    'volume': vol,
                    'change': chg,
                    'change_percent': chg_pct,
                    'open_price': ref,
                })
            live_df = pd.DataFrame(live_rows)
            if not live_df.empty:
                # Keep only tickers also present in DB snapshot to avoid clutter
                if 'ticker' in all_ticker_data.columns:
                    live_df = live_df[live_df['ticker'].isin(all_ticker_data['ticker'])]
                # Update fields with live values where present
                all_ticker_data = all_ticker_data.merge(live_df, on='ticker', how='left', suffixes=('', '_live'))
                for col in ['price','volume','change','change_percent','open_price']:
                    live_col = f"{col}_live"
                    if live_col in all_ticker_data.columns:
                        all_ticker_data[col] = all_ticker_data[live_col].combine_first(all_ticker_data.get(col))
                        all_ticker_data.drop(columns=[live_col], inplace=True)
        
        if not all_ticker_data.empty:
            # Clean and validate data
            all_ticker_data = clean_quotes_df(all_ticker_data)
            
            # Display market metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📈 Total Tickers", len(all_ticker_data))
            
            with col2:
                avg_change = all_ticker_data['change_percent'].mean()
                st.metric("📊 Avg Change %", f"{avg_change:.2f}%")
            
            with col3:
                total_volume = all_ticker_data['volume'].sum()
                st.metric("📦 Total Volume", f"{total_volume:,}")
            
            with col4:
                latest_date = all_ticker_data['time'].max()
                try:
                st.metric("📅 Latest Data", latest_date.strftime("%Y-%m-%d"))
                except Exception:
                    st.metric("📅 Latest Data", str(latest_date))
            
            # Market performance summary (DB snapshot)
            st.subheader("📈 Market Performance Summary")
            
            # Top gainers and losers
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🚀 Top Gainers")
                cols = [c for c in ['ticker','price','change_percent','volume','total_volume'] if c in all_ticker_data.columns]
                top_gainers = all_ticker_data.nlargest(10, 'change_percent')[cols]
                if 'change_percent' in top_gainers.columns:
                top_gainers['change_percent'] = top_gainers['change_percent'].round(2)
                st.dataframe(top_gainers, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("📉 Top Losers")
                cols = [c for c in ['ticker','price','change_percent','volume','total_volume'] if c in all_ticker_data.columns]
                top_losers = all_ticker_data.nsmallest(10, 'change_percent')[cols]
                if 'change_percent' in top_losers.columns:
                top_losers['change_percent'] = top_losers['change_percent'].round(2)
                st.dataframe(top_losers, use_container_width=True, hide_index=True)
            
            # Volume leaders
            st.subheader("📦 Volume Leaders")
            cols = [c for c in ['ticker','price','change_percent','volume','total_volume'] if c in all_ticker_data.columns]
            volume_leaders = all_ticker_data.nlargest(20, 'volume')[cols]
            if 'change_percent' in volume_leaders.columns:
            volume_leaders['change_percent'] = volume_leaders['change_percent'].round(2)
            if 'volume' in volume_leaders.columns:
            volume_leaders['volume'] = volume_leaders['volume'].apply(lambda x: f"{x:,}")
            st.dataframe(volume_leaders, use_container_width=True, hide_index=True)
            
            # Full market data table with search (DB snapshot)
            st.subheader("🔍 Full Market Data")
            search_ticker = st.text_input("🔍 Search Ticker:", placeholder="Type ticker symbol...")
            
            if search_ticker:
                filtered_data = all_ticker_data[all_ticker_data['ticker'].str.contains(search_ticker.upper(), case=False)]
            else:
                filtered_data = all_ticker_data
            
            # Format the data for display
            display_data = filtered_data.copy()
            if 'change_percent' in display_data.columns:
            display_data['change_percent'] = display_data['change_percent'].round(2)
            if 'volume' in display_data.columns:
            display_data['volume'] = display_data['volume'].apply(lambda x: f"{x:,}")
            if 'price' in display_data.columns:
            display_data['price'] = display_data['price'].round(2)
            
            st.dataframe(display_data, use_container_width=True, hide_index=True)
            
            # Realtime Kafka snapshot (best-effort) next to DB snapshot
            st.subheader("⚡ Live Stream (Kafka snapshot)")
            if latest_by_ticker:
                # Convert to DataFrame for display and compute missing change/change_percent
                live_rows = []
                for tkr, payload in list(latest_by_ticker.items())[:200]:
                    price = payload.get("price")
                    ref = payload.get("reference_price") or payload.get("reference")
                    chg_pct = payload.get("change_percent")
                    chg = payload.get("change")
                    if chg_pct in (None, "", "None") and price not in (None, 0) and ref not in (None, 0):
                        try:
                            chg_pct = (float(price) - float(ref)) / float(ref) * 100.0
                        except Exception:
                            chg_pct = None
                    if chg in (None, "", "None") and price not in (None, 0) and ref not in (None, 0):
                        try:
                            chg = float(price) - float(ref)
                        except Exception:
                            chg = None
                    live_rows.append({
                        "ticker": tkr,
                        "time": payload.get("time") or payload.get("timestamp"),
                        "price": price,
                        "volume": payload.get("volume"),
                        "change": chg,
                        "change_percent": chg_pct,
                        "reference_price": ref,
                        "bid_price": payload.get("bid_price"),
                        "ask_price": payload.get("ask_price"),
                    })
                live_df = pd.DataFrame(live_rows)
                live_df = drop_all_null_columns(live_df)
                if not live_df.empty:
                    # Basic formatting
                    if "change_percent" in live_df.columns:
                        live_df["change_percent"] = pd.to_numeric(live_df["change_percent"], errors="coerce").round(2)
                    if "change" in live_df.columns:
                        live_df["change"] = pd.to_numeric(live_df["change"], errors="coerce").round(2)
                    if "price" in live_df.columns:
                        live_df["price"] = pd.to_numeric(live_df["price"], errors="coerce").round(2)
                    st.dataframe(live_df.sort_values(by=["time"], ascending=False), use_container_width=True, hide_index=True)
                else:
                    st.info("Chưa có dữ liệu live hợp lệ từ Kafka.")
            else:
                st.info("Đang chờ dữ liệu live từ Kafka…")
            
        else:
            st.warning("⚠️ No market data available from database")
    
    else:
        st.subheader(f"📈 {selected_ticker} Analysis")
        
        # Get ticker data from PostgreSQL and merge with latest Kafka payload for this ticker (if any)
        ticker_data = get_realtime_data(selected_ticker, 300)
        # Merge realtime snapshot
        if latest_by_ticker and selected_ticker in latest_by_ticker:
            ticker_data = merge_realtime_row(selected_ticker, ticker_data, latest_by_ticker[selected_ticker])
        
        if not ticker_data.empty:
            # Clean and validate
            ticker_data = clean_quotes_df(ticker_data)

            # Display ticker metrics
            col1, col2, col3, col4 = st.columns(4)
            
            latest = ticker_data.iloc[0]
            
            with col1:
                if 'price' in ticker_data.columns:
                st.metric("💰 Current Price", f"{latest['price']:,.2f}")
                else:
                    st.metric("💰 Current Price", "—")
            
            with col2:
                if 'change_percent' in ticker_data.columns and pd.notna(latest.get('change_percent')):
                st.metric("📈 Change %", f"{latest['change_percent']:.2f}%", delta=f"{latest['change_percent']:.2f}%")
                else:
                    st.metric("📈 Change %", "—")
            
            with col3:
                if 'volume' in ticker_data.columns:
                st.metric("📦 Volume", f"{latest['volume']:,}")
                else:
                    st.metric("📦 Volume", "—")
            
            with col4:
                st.metric("📅 Data Points", len(ticker_data))
            
            # Price chart with candlestick if we have OHLC data
            st.subheader("📊 Price Chart")
            
            if all(c in ticker_data.columns for c in ['open_price','high_price','low_price','price']):
                # Candlestick chart
                fig = go.Figure(data=go.Candlestick(
                    x=ticker_data['time'],
                    open=ticker_data['open_price'],
                    high=ticker_data['high_price'],
                    low=ticker_data['low_price'],
                    close=ticker_data['price'],
                    name=selected_ticker
                ))
                
                # Add moving averages
                ticker_data['MA5'] = ticker_data['price'].rolling(window=5).mean()
                ticker_data['MA20'] = ticker_data['price'].rolling(window=20).mean()
                fig.add_trace(go.Scatter(x=ticker_data['time'], y=ticker_data['MA5'], mode='lines', name='MA5', line=dict(color='red', dash='dash')))
                fig.add_trace(go.Scatter(x=ticker_data['time'], y=ticker_data['MA20'], mode='lines', name='MA20', line=dict(color='green', dash='dot')))
            else:
                # Line chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=ticker_data['time'],
                    y=ticker_data['price'],
                    mode='lines',
                    name='Price',
                    line=dict(color='#00A9FF', width=2)
                ))
                
                # Add moving averages
                ticker_data['MA5'] = ticker_data['price'].rolling(window=5).mean()
                ticker_data['MA20'] = ticker_data['price'].rolling(window=20).mean()
                fig.add_trace(go.Scatter(x=ticker_data['time'], y=ticker_data['MA5'], mode='lines', name='MA5', line=dict(color='red', dash='dash')))
                fig.add_trace(go.Scatter(x=ticker_data['time'], y=ticker_data['MA20'], mode='lines', name='MA20', line=dict(color='green', dash='dot')))
            
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Price",
                hovermode="x unified",
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font_color='#FAFAFA',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            st.subheader("📦 Volume Analysis")
            fig_volume = go.Figure()
            fig_volume.add_trace(go.Bar(
                x=ticker_data['time'],
                y=ticker_data['volume'],
                name='Volume',
                marker_color='#00A9FF',
                opacity=0.7
            ))
            fig_volume.update_layout(
                xaxis_title="Time",
                yaxis_title="Volume",
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font_color='#FAFAFA',
                height=300
            )
            st.plotly_chart(fig_volume, use_container_width=True)
            
            # Performance metrics
            st.subheader("📊 Performance Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                price_change = ticker_data['price'].iloc[0] - ticker_data['price'].iloc[-1]
                st.metric("💰 Price Change", f"{price_change:,.2f}")
            
            with col2:
                avg_volume = ticker_data['volume'].mean()
                st.metric("📦 Avg Volume", f"{avg_volume:,.0f}")
            
            with col3:
                max_price = ticker_data['price'].max()
                st.metric("📈 52W High", f"{max_price:,.2f}")
            
            with col4:
                min_price = ticker_data['price'].min()
                st.metric("📉 52W Low", f"{min_price:,.2f}")
            
            # Data explorer
            st.subheader("🔍 Data Explorer")
            st.dataframe(ticker_data, use_container_width=True)
            
        else:
            st.warning(f"⚠️ No data available for {selected_ticker} from database")
    
    # Footer
    st.markdown("---")
    st.markdown("**🔗 Data Source:** PostgreSQL Database")
    st.markdown("**⏰ Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
