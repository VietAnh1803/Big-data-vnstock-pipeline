#!/usr/bin/env python3
"""
SSI-Style Vietnam Stock Dashboard
Inspired by SSI iBoard with modern UI and real-time data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from psycopg2.extras import RealDictCursor
import snowflake.connector
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import numpy as np
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Vietnam Stock Market Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SSI-Style CSS
st.markdown("""
<style>
    /* SSI-Inspired Dark Theme */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    .stSidebar {
        background-color: #1e1e1e;
    }
    
    .stSelectbox > div > div {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #4a4a4a;
    }
    
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #0d5a8a;
    }

    /* Ensure download button text is always visible */
    .stDownloadButton > button {
        background-color: #1f77b4;
        color: #ffffff !important;
        border: none;
        border-radius: 6px;
        font-weight: 700;
    }

    .stDownloadButton > button:hover {
        background-color: #0d5a8a;
        color: #ffffff !important;
    }
    
    /* Header Style */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Price Colors */
    .price-up {
        color: #00C851;
        font-weight: bold;
    }
    
    .price-down {
        color: #ff4444;
        font-weight: bold;
    }
    
    .price-neutral {
        color: #ffbb33;
        font-weight: bold;
    }
    
    /* Table Styling - Enhanced for visibility */
    .dataframe {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
    }
    
    .dataframe th {
        background-color: #2d2d2d !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border: 1px solid #4a4a4a !important;
    }
    
    .dataframe td {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
        border: 1px solid #3a3a3a !important;
    }
    
    /* Streamlit dataframe specific styling */
    div[data-testid="stDataFrame"] {
        color: #e0e0e0 !important;
    }
    
    div[data-testid="stDataFrame"] table {
        color: #e0e0e0 !important;
        background-color: #1e1e1e !important;
    }
    
    div[data-testid="stDataFrame"] th {
        color: #ffffff !important;
        background-color: #2d2d2d !important;
        font-weight: bold !important;
    }
    
    div[data-testid="stDataFrame"] td {
        color: #e0e0e0 !important;
        background-color: #1e1e1e !important;
    }
    
    /* Streamlit table container */
    .stDataFrame {
        color: #e0e0e0 !important;
    }
    
    .stDataFrame > div {
        color: #e0e0e0 !important;
    }
    
    /* Label Styling - Blue Ocean Gradient for better visibility */
    /* Metric labels - Tổng Cổ Phiếu, Tổng Khối Lượng, Giá Trung Bình, Cập Nhật Cuối */
    div[data-testid="stMetricLabel"] {
        background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #42a5f5 !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    
    div[data-testid="stMetricLabel"] p {
        background: linear-gradient(135deg, #1976d2 0%, #42a5f5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #42a5f5 !important;
        font-weight: bold !important;
    }
    
    /* Text input labels - Tìm kiếm mã cổ phiếu */
    label[data-testid="stWidgetLabel"] {
        background: linear-gradient(135deg, #1565c0 0%, #42a5f5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #42a5f5 !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    
    label[data-testid="stWidgetLabel"] p {
        background: linear-gradient(135deg, #1565c0 0%, #42a5f5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #42a5f5 !important;
        font-weight: bold !important;
    }
    
    /* Selectbox labels - Sắp xếp theo, Hiển thị, Chọn Cổ Phiếu */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSelectbox"] label p {
        background: linear-gradient(135deg, #1565c0 0%, #42a5f5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #42a5f5 !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    
    /* Radio button labels - Khoảng thời gian */
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] label p {
        background: linear-gradient(135deg, #1565c0 0%, #42a5f5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        color: #42a5f5 !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }
    
    /* All labels fallback - ensure all labels are visible */
    label {
        color: #42a5f5 !important;
        font-weight: bold !important;
    }
    
    label p {
        color: #42a5f5 !important;
        font-weight: bold !important;
    }
    
    /* Status Indicators */
    .status-online {
        color: #00C851;
        font-weight: bold;
    }
    
    .status-offline {
        color: #ff4444;
        font-weight: bold;
    }

    .status-warning {
        color: #ffbb33;
        font-weight: bold;
    }
    
    /* Refresh Indicator */
    .refresh-indicator {
        background: linear-gradient(90deg, #1f77b4, #2a5298);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* BI-style KPI cards */
    .bi-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 8px 0 16px 0;
    }

    .bi-kpi-card {
        background: linear-gradient(180deg, rgba(25, 38, 77, 0.95) 0%, rgba(13, 24, 55, 0.95) 100%);
        border: 1px solid rgba(66, 165, 245, 0.25);
        border-radius: 10px;
        padding: 12px 14px;
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.25);
    }

    .bi-kpi-label {
        color: #8eb7ff;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.2px;
        margin-bottom: 6px;
    }

    .bi-kpi-value {
        color: #ffffff;
        font-size: 32px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 4px;
    }

    .bi-kpi-sub {
        color: #a7c7ff;
        font-size: 12px;
        opacity: 0.95;
    }

    .bi-section {
        background: rgba(9, 16, 34, 0.72);
        border: 1px solid rgba(53, 109, 194, 0.25);
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 16px;
    }

    /* Mobile responsiveness */
    @media (max-width: 1024px) {
        .bi-kpi-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .main-header {
            font-size: 2rem;
        }
    }

    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 0.6rem;
            padding-right: 0.6rem;
        }
        .main-header {
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.1rem;
            margin-bottom: 0.6rem;
        }
        .bi-kpi-grid {
            grid-template-columns: 1fr;
            gap: 8px;
            margin: 6px 0 12px 0;
        }
        .bi-kpi-card {
            padding: 10px 12px;
        }
        .bi-kpi-value {
            font-size: 24px;
        }
        .refresh-indicator {
            padding: 6px 10px;
            font-size: 12px;
        }
        .stButton > button,
        .stDownloadButton > button {
            width: 100%;
            min-height: 40px;
        }
        div[data-testid="stMetric"] {
            padding: 6px 8px;
        }
        div[data-testid="stDataFrame"] {
            font-size: 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

class SSIStyleDashboard:
    """SSI-inspired stock dashboard"""
    
    # Chart styling constants - ensure consistency across all charts
    VOLUME_CHART_COLOR = "#FFD700"  # Gold color - bright and visible on dark background
    VOLUME_CHART_OPACITY = 0.95  # High opacity for better visibility
    PRICE_UNIT_MULTIPLIER = 1000  # Vietnamese equity board prices are typically in thousand VND
    VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
    VN_TRADING_MORNING_START = (9, 0)
    VN_TRADING_MORNING_END = (11, 30)
    VN_TRADING_AFTERNOON_START = (13, 0)
    VN_TRADING_AFTERNOON_END = (15, 0)
    
    def __init__(self):
        # Database configuration
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', '5432')),
            'database': os.getenv('POSTGRES_DB', 'stock_db'),
            'user': os.getenv('POSTGRES_USER', 'stock_app'),
            'password': os.getenv('POSTGRES_PASSWORD', '')
        }
        self.dashboard_data_source = os.getenv("DASHBOARD_DATA_SOURCE", "snowflake").strip().lower()
        self.dashboard_lookback_hours = int(os.getenv("DASHBOARD_LOOKBACK_HOURS", "2"))
        self.sf_config = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT', ''),
            'user': os.getenv('SNOWFLAKE_USER', ''),
            'password': os.getenv('SNOWFLAKE_PASSWORD', ''),
            'role': os.getenv('SNOWFLAKE_ROLE', ''),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'STOCK_WH'),
            'database': os.getenv('SNOWFLAKE_DATABASE', 'STOCK_DWH'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', 'DW'),
        }
        
        # Initialize session state
        if 'last_update' not in st.session_state:
            st.session_state.last_update = self._now_vn()
        self.vn_market_holidays = self._load_vn_market_holidays()

    def _vnd(self, value):
        """Convert board price unit to VND display unit."""
        try:
            return float(value) * self.PRICE_UNIT_MULTIPLIER
        except Exception:
            return value

    def _scale_price_columns(self, df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
        """Scale selected price-like columns from board unit to VND."""
        if df is None or df.empty:
            return df
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce") * self.PRICE_UNIT_MULTIPLIER
        return df

    def _get_col_name(self, df: pd.DataFrame, expected: str) -> Optional[str]:
        """Return actual column name ignoring case, or None if missing."""
        if df is None or df.empty:
            return None
        expected_lower = expected.lower()
        for col in df.columns:
            if str(col).lower() == expected_lower:
                return col
        return None

    def _now_vn(self) -> datetime:
        """Current time in Vietnam timezone."""
        return datetime.now(self.VN_TZ)

    def _to_vn_datetime(self, value: Any) -> Optional[datetime]:
        """Normalize datetime-like value to Vietnam timezone."""
        if value is None:
            return None
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            return None
        if getattr(ts, "tzinfo", None) is None:
            ts = ts.tz_localize(self.VN_TZ)
        else:
            ts = ts.tz_convert(self.VN_TZ)
        return ts.to_pydatetime()

    def _fmt_vn(self, value: Any, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime-like value in Vietnam timezone."""
        vn_dt = self._to_vn_datetime(value)
        return vn_dt.strftime(fmt) if vn_dt else "N/A"

    def _load_vn_market_holidays(self) -> set[str]:
        """Load holiday list from env in YYYY-MM-DD format."""
        raw = os.getenv("VN_MARKET_HOLIDAYS", "").strip()
        return {d.strip() for d in raw.split(",") if d.strip()} if raw else set()

    def _is_vn_market_open(self, now_vn: Optional[datetime] = None) -> bool:
        """Return True if current Vietnam time is in regular trading sessions."""
        now_vn = now_vn or self._now_vn()
        now_date = now_vn.date()
        date_key = now_date.isoformat()
        month_day = now_date.strftime("%m-%d")
        fixed_holidays = {"01-01", "04-30", "05-01", "09-02"}

        if date_key in self.vn_market_holidays or month_day in fixed_holidays:
            return False

        # Weekend market close
        if now_vn.weekday() >= 5:
            return False

        hh_mm = (now_vn.hour, now_vn.minute)
        in_morning = self.VN_TRADING_MORNING_START <= hh_mm <= self.VN_TRADING_MORNING_END
        in_afternoon = self.VN_TRADING_AFTERNOON_START <= hh_mm <= self.VN_TRADING_AFTERNOON_END
        return in_morning or in_afternoon

    def _get_market_status(self, now_vn: Optional[datetime] = None) -> tuple[str, str]:
        """Return market status label and css class for UI."""
        now_vn = now_vn or self._now_vn()
        date_key = now_vn.date().isoformat()
        month_day = now_vn.strftime("%m-%d")
        fixed_holidays = {"01-01", "04-30", "05-01", "09-02"}
        if date_key in self.vn_market_holidays or month_day in fixed_holidays:
            return "Nghỉ lễ", "status-warning"
        if now_vn.weekday() >= 5:
            return "Cuối tuần", "status-warning"
        if self._is_vn_market_open(now_vn):
            return "Đang giao dịch", "status-online"
        return "Ngoài giờ giao dịch", "status-warning"

    def _render_kpi_cards(self, summary: pd.Series):
        """Render BI-style KPI cards for market overview."""
        total_tickers = int(summary['total_tickers'])
        total_volume = int(summary['total_volume'])
        avg_price_vnd = self._vnd(summary['avg_price'])
        last_update = self._fmt_vn(summary.get('last_update'), '%H:%M:%S')
        gainers = int(summary['gainers'])
        losers = int(summary['losers'])
        unchanged = int(summary['unchanged'])

        html = f"""
        <div class="bi-kpi-grid">
            <div class="bi-kpi-card">
                <div class="bi-kpi-label">Tổng cổ phiếu</div>
                <div class="bi-kpi-value">{total_tickers:,}</div>
                <div class="bi-kpi-sub">{gainers:,} mã tăng</div>
            </div>
            <div class="bi-kpi-card">
                <div class="bi-kpi-label">Tổng khối lượng</div>
                <div class="bi-kpi-value">{total_volume:,}</div>
                <div class="bi-kpi-sub">{losers:,} mã giảm</div>
            </div>
            <div class="bi-kpi-card">
                <div class="bi-kpi-label">Giá trung bình</div>
                <div class="bi-kpi-value">{avg_price_vnd:,.0f} VND</div>
                <div class="bi-kpi-sub">{unchanged:,} mã không đổi</div>
            </div>
            <div class="bi-kpi-card">
                <div class="bi-kpi-label">Cập nhật cuối</div>
                <div class="bi-kpi-value">{last_update}</div>
                <div class="bi-kpi-sub">Realtime</div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

    def get_available_tickers(self, days: int = 7, limit: int = 300) -> List[str]:
        """Get recent active tickers for global BI filters."""
        if self.dashboard_data_source == "snowflake":
            query = """
                SELECT DISTINCT TICKER
                FROM STOCK_DWH.SILVER.REALTIME_QUOTES_CLEAN
                WHERE EVENT_TIME >= DATEADD(day, -?, CURRENT_TIMESTAMP())
                ORDER BY TICKER
                LIMIT ?
            """
            df = self.execute_query(query, (days, limit))
        elif self.dashboard_data_source == "legacy":
            query = """
                SELECT DISTINCT ticker
                FROM realtime_quotes
                WHERE time >= NOW() - (%s || ' days')::interval
                ORDER BY ticker
                LIMIT %s
            """
            df = self.execute_query(query, (days, limit))
        else:
            query = """
                SELECT DISTINCT ticker
                FROM silver.realtime_quotes_clean
                WHERE event_time >= NOW() - (%s || ' days')::interval
                ORDER BY ticker
                LIMIT %s
            """
            df = self.execute_query(query, (days, limit))

        if df.empty:
            return []
        ticker_col = self._get_col_name(df, "ticker")
        if not ticker_col:
            return []
        return [str(x) for x in df[ticker_col].dropna().tolist()]

    def get_pipeline_health_snapshot(self) -> Dict[str, Any]:
        """Get a lightweight pipeline health snapshot for BI panel."""
        snapshot = {
            "last_update": None,
            "active_tickers": 0,
            "records_lookback": 0,
            "stale_minutes": None,
            "status": "Chưa có dữ liệu",
            "market_open": False,
        }

        try:
            if self.dashboard_data_source == "snowflake":
                query = """
                    SELECT
                        MAX(EVENT_TIME) AS last_update,
                        COUNT(DISTINCT TICKER) AS active_tickers,
                        COUNT(*) AS records_lookback
                    FROM STOCK_DWH.SILVER.REALTIME_QUOTES_CLEAN
                    WHERE EVENT_TIME >= DATEADD(hour, -?, CURRENT_TIMESTAMP())
                """
                df = self.execute_query(query, (self.dashboard_lookback_hours,))
            elif self.dashboard_data_source == "legacy":
                query = """
                    SELECT
                        MAX(time) AS last_update,
                        COUNT(DISTINCT ticker) AS active_tickers,
                        COUNT(*) AS records_lookback
                    FROM realtime_quotes
                    WHERE time >= NOW() - (%s || ' hours')::interval
                """
                df = self.execute_query(query, (self.dashboard_lookback_hours,))
            else:
                query = """
                    SELECT
                        MAX(event_time) AS last_update,
                        COUNT(DISTINCT ticker) AS active_tickers,
                        COUNT(*) AS records_lookback
                    FROM silver.realtime_quotes_clean
                    WHERE event_time >= NOW() - (%s || ' hours')::interval
                """
                df = self.execute_query(query, (self.dashboard_lookback_hours,))

            if not df.empty:
                row = df.iloc[0]
                snapshot["last_update"] = row.get("last_update")
                snapshot["active_tickers"] = int(row.get("active_tickers") or 0)
                snapshot["records_lookback"] = int(row.get("records_lookback") or 0)

                if snapshot["last_update"] is not None:
                    last_update_vn = self._to_vn_datetime(snapshot["last_update"])
                    now_ref = self._now_vn()
                    stale_minutes = (now_ref - last_update_vn).total_seconds() / 60
                    snapshot["stale_minutes"] = max(0, stale_minutes)
                    market_open = self._is_vn_market_open(now_ref)
                    snapshot["market_open"] = market_open
                    if not market_open:
                        snapshot["status"] = "Ngoài giờ giao dịch"
                    elif stale_minutes <= 10:
                        snapshot["status"] = "Tốt"
                    elif stale_minutes <= 30:
                        snapshot["status"] = "Cần theo dõi"
                    else:
                        snapshot["status"] = "Trễ dữ liệu"
        except Exception as exc:
            logger.warning("Failed to build pipeline health snapshot: %s", exc)

        return snapshot

    def render_pipeline_health_panel(self):
        """Render BI panel for pipeline health and data quality."""
        health = self.get_pipeline_health_snapshot()
        last_update = self._fmt_vn(health["last_update"])
        stale = f"{health['stale_minutes']:.1f} phút" if health["stale_minutes"] is not None else "N/A"

        st.markdown("### Pipeline Health & Data Quality")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Trạng thái", health["status"])
        col2.metric("Ticker hoạt động", f"{health['active_tickers']:,}")
        col3.metric("Bản ghi lookback", f"{health['records_lookback']:,}")
        col4.metric("Độ trễ dữ liệu", stale)
        market_note = "Đang trong giờ giao dịch VN" if health.get("market_open") else "Ngoài giờ giao dịch VN"
        st.caption(f"Cập nhật gần nhất: {last_update} | Nguồn: {self.dashboard_data_source} | {market_note}")
            
    def get_db_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    def get_snowflake_connection(self):
        """Get Snowflake connection for visualization queries."""
        try:
            base_kwargs = {
                'account': self.sf_config['account'],
                'user': self.sf_config['user'],
                'password': self.sf_config['password'],
                'warehouse': self.sf_config['warehouse'],
                'database': self.sf_config['database'],
                'schema': self.sf_config['schema'],
            }
            if self.sf_config['role']:
                try:
                    role_kwargs = dict(base_kwargs)
                    role_kwargs['role'] = self.sf_config['role']
                    return snowflake.connector.connect(**role_kwargs)
                except Exception as e:
                    logger.warning("Snowflake role '%s' not usable, fallback to default role: %s", self.sf_config['role'], e)
            return snowflake.connector.connect(**base_kwargs)
        except Exception as e:
            st.error(f"Snowflake connection failed: {e}")
            return None
            
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        if self.dashboard_data_source == "snowflake":
            conn = self.get_snowflake_connection()
            if not conn:
                return pd.DataFrame()
            try:
                # Snowflake Python connector uses pyformat style (%s).
                # Normalize mixed placeholders to avoid runtime formatting errors.
                sf_query = query.replace("?", "%s")
                exec_params = tuple(params) if params is not None else ()
                with conn.cursor(snowflake.connector.DictCursor) as cursor:
                    cursor.execute(sf_query, exec_params)
                    df = pd.DataFrame(cursor.fetchall())
                    if not df.empty:
                        df.columns = [str(c).lower() for c in df.columns]
                    return df
            except Exception as e:
                logger.error("Snowflake query failed. params=%s query=%s", params, query, exc_info=True)
                st.error(f"Snowflake query execution failed: {e}")
                return pd.DataFrame()
            finally:
                conn.close()

        conn = self.get_db_connection()
        if not conn:
            return pd.DataFrame()
            
        try:
            pg_query = query.replace("?", "%s")
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if params is None:
                    cursor.execute(pg_query)
                else:
                    cursor.execute(pg_query, tuple(params))
                results = cursor.fetchall()
                df = pd.DataFrame(results)
                if not df.empty:
                    df.columns = [str(c).lower() for c in df.columns]
                return df
        except Exception as e:
            st.error(f"Query execution failed: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def get_realtime_quotes(self, limit: int = 100) -> pd.DataFrame:
        """Get real-time stock quotes from selected source."""
        if self.dashboard_data_source == "snowflake":
            query = """
                SELECT
                    ticker,
                    close_price AS price,
                    volume,
                    change_abs AS change,
                    pct_change AS percent_change,
                    high_price AS high,
                    low_price AS low,
                    open_price,
                    close_price,
                    bucket_minute AS ingest_time,
                    CASE
                        WHEN change_abs > 0 THEN 'up'
                        WHEN change_abs < 0 THEN 'down'
                        ELSE 'neutral'
                    END AS price_trend
                FROM STOCK_DWH.DW.VW_FACT_QUOTE_1M_ENRICHED
                WHERE bucket_minute >= DATEADD(hour, -?, CURRENT_TIMESTAMP())
                QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY bucket_minute DESC) = 1
                ORDER BY volume DESC, percent_change DESC
                LIMIT ?
            """
            return self.execute_query(query, (self.dashboard_lookback_hours, limit))

        if self.dashboard_data_source == "legacy":
            query = """
                WITH latest AS (
                    SELECT *,
                           ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
                    FROM realtime_quotes
                    WHERE time >= NOW() - INTERVAL '1 hour'
                )
                SELECT
                    ticker, price, volume, change, percent_change, high, low, open_price, close_price,
                    time as ingest_time,
                    CASE
                        WHEN percent_change > 0 THEN 'up'
                        WHEN percent_change < 0 THEN 'down'
                        ELSE 'neutral'
                    END as price_trend
                FROM latest
                WHERE rn = 1
                ORDER BY volume DESC, percent_change DESC
                LIMIT %s
            """
            return self.execute_query(query, (limit,))

        query = """
            WITH latest AS (
                SELECT
                    d.ticker_code AS ticker,
                    f.close_price AS price,
                    f.volume,
                    (f.close_price - f.open_price) AS change,
                    CASE
                        WHEN f.open_price IS NULL OR f.open_price = 0 THEN 0
                        ELSE ((f.close_price - f.open_price) / f.open_price) * 100
                    END AS percent_change,
                    f.high_price AS high,
                    f.low_price AS low,
                    f.open_price,
                    f.close_price,
                    f.bucket_minute AS ingest_time,
                    ROW_NUMBER() OVER (PARTITION BY d.ticker_code ORDER BY f.bucket_minute DESC) AS rn
                FROM dw.fact_quote_1m f
                JOIN dw.dim_ticker d ON d.ticker_sk = f.ticker_sk
                WHERE f.bucket_minute >= NOW() - (%s || ' hours')::interval
            )
            SELECT 
                ticker,
                price,
                volume,
                change,
                percent_change,
                high,
                low,
                open_price,
                close_price,
                ingest_time,
                CASE 
                    WHEN percent_change > 0 THEN 'up'
                    WHEN percent_change < 0 THEN 'down'
                    ELSE 'neutral'
                END as price_trend
            FROM latest
            WHERE rn = 1
            ORDER BY volume DESC, percent_change DESC
            LIMIT %s
        """
        return self.execute_query(query, (self.dashboard_lookback_hours, limit))
    
    def get_market_summary(self) -> pd.DataFrame:
        """Get comprehensive market summary from selected source."""
        if self.dashboard_data_source == "snowflake":
            query = """
                WITH latest_quotes AS (
                    SELECT
                        ticker,
                        close_price AS price,
                        volume,
                        pct_change AS percent_change,
                        bucket_minute AS time
                    FROM STOCK_DWH.DW.VW_FACT_QUOTE_1M_ENRICHED
                    WHERE bucket_minute >= DATEADD(hour, -?, CURRENT_TIMESTAMP())
                    QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY bucket_minute DESC) = 1
                )
                SELECT
                    COUNT(DISTINCT ticker) AS total_tickers,
                    COALESCE(SUM(volume), 0) AS total_volume,
                    COALESCE(AVG(price), 0) AS avg_price,
                    COUNT_IF(percent_change > 0) AS gainers,
                    COUNT_IF(percent_change < 0) AS losers,
                    COUNT_IF(COALESCE(percent_change, 0) = 0) AS unchanged,
                    MAX(time) AS last_update
                FROM latest_quotes
            """
            return self.execute_query(query, (self.dashboard_lookback_hours,))

        if self.dashboard_data_source == "legacy":
            query = """
                WITH latest_quotes AS (
                    SELECT DISTINCT ON (ticker)
                        ticker, price, volume, percent_change, time
                    FROM realtime_quotes
                    WHERE time >= NOW() - INTERVAL '1 hour'
                    ORDER BY ticker, time DESC
                )
                SELECT
                    COUNT(DISTINCT ticker) as total_tickers,
                    COALESCE(SUM(volume), 0) as total_volume,
                    COALESCE(AVG(price), 0) as avg_price,
                    COUNT(CASE WHEN percent_change > 0 THEN 1 END) as gainers,
                    COUNT(CASE WHEN percent_change < 0 THEN 1 END) as losers,
                    COUNT(CASE WHEN percent_change = 0 THEN 1 END) as unchanged,
                    MAX(time) as last_update
                FROM latest_quotes
            """
            return self.execute_query(query)

        query = """
            WITH latest_quotes AS (
                SELECT DISTINCT ON (d.ticker_code)
                    d.ticker_code AS ticker,
                    f.close_price AS price,
                    f.volume,
                    CASE
                        WHEN f.open_price IS NULL OR f.open_price = 0 THEN 0
                        ELSE ((f.close_price - f.open_price) / f.open_price) * 100
                    END AS percent_change,
                    f.bucket_minute AS time
                FROM dw.fact_quote_1m f
                JOIN dw.dim_ticker d ON d.ticker_sk = f.ticker_sk
                WHERE f.bucket_minute >= NOW() - (%s || ' hours')::interval
                ORDER BY d.ticker_code, f.bucket_minute DESC
            )
            SELECT 
                COUNT(DISTINCT ticker) as total_tickers,
                COALESCE(SUM(volume), 0) as total_volume,
                COALESCE(AVG(price), 0) as avg_price,
                COUNT(CASE WHEN percent_change > 0 THEN 1 END) as gainers,
                COUNT(CASE WHEN percent_change < 0 THEN 1 END) as losers,
                COUNT(CASE WHEN percent_change = 0 THEN 1 END) as unchanged,
                MAX(time) as last_update
            FROM latest_quotes
        """
        return self.execute_query(query, (self.dashboard_lookback_hours,))
    
    def get_top_performers(self, limit: int = 20) -> pd.DataFrame:
        """Get top performing stocks from selected source."""
        if self.dashboard_data_source == "snowflake":
            query = """
                SELECT
                    ticker,
                    close_price AS price,
                    pct_change AS percent_change,
                    volume,
                    change_abs AS change,
                    bucket_minute AS ingest_time
                FROM STOCK_DWH.DW.VW_FACT_QUOTE_1M_ENRICHED
                WHERE bucket_minute >= DATEADD(hour, -?, CURRENT_TIMESTAMP())
                QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY bucket_minute DESC) = 1
                ORDER BY percent_change DESC
                LIMIT ?
            """
            return self.execute_query(query, (self.dashboard_lookback_hours, limit))

        if self.dashboard_data_source == "legacy":
            query = """
                WITH latest AS (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
                    FROM realtime_quotes
                    WHERE time >= NOW() - INTERVAL '1 hour'
                      AND percent_change IS NOT NULL
                )
                SELECT ticker, price, percent_change, volume, change, time as ingest_time
                FROM latest
                WHERE rn = 1
                ORDER BY percent_change DESC
                LIMIT %s
            """
            return self.execute_query(query, (limit,))

        query = """
            WITH latest AS (
                SELECT
                    d.ticker_code AS ticker,
                    f.close_price AS price,
                    CASE
                        WHEN f.open_price IS NULL OR f.open_price = 0 THEN 0
                        ELSE ((f.close_price - f.open_price) / f.open_price) * 100
                    END AS percent_change,
                    f.volume,
                    (f.close_price - f.open_price) AS change,
                    f.bucket_minute AS ingest_time,
                    ROW_NUMBER() OVER (PARTITION BY d.ticker_code ORDER BY f.bucket_minute DESC) AS rn
                FROM dw.fact_quote_1m f
                JOIN dw.dim_ticker d ON d.ticker_sk = f.ticker_sk
                WHERE f.bucket_minute >= NOW() - (%s || ' hours')::interval
            )
            SELECT 
                ticker,
                price,
                percent_change,
                volume,
                change,
                ingest_time
            FROM latest
            WHERE rn = 1
              AND percent_change IS NOT NULL
            ORDER BY percent_change DESC
            LIMIT %s
        """
        return self.execute_query(query, (self.dashboard_lookback_hours, limit))
    
    def get_worst_performers(self, limit: int = 20) -> pd.DataFrame:
        """Get worst performing stocks from selected source."""
        if self.dashboard_data_source == "snowflake":
            query = """
                SELECT
                    ticker,
                    close_price AS price,
                    pct_change AS percent_change,
                    volume,
                    change_abs AS change,
                    bucket_minute AS ingest_time
                FROM STOCK_DWH.DW.VW_FACT_QUOTE_1M_ENRICHED
                WHERE bucket_minute >= DATEADD(hour, -?, CURRENT_TIMESTAMP())
                QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY bucket_minute DESC) = 1
                ORDER BY percent_change ASC
                LIMIT ?
            """
            return self.execute_query(query, (self.dashboard_lookback_hours, limit))

        if self.dashboard_data_source == "legacy":
            query = """
                WITH latest AS (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
                    FROM realtime_quotes
                    WHERE time >= NOW() - INTERVAL '1 hour'
                      AND percent_change IS NOT NULL
                )
                SELECT ticker, price, percent_change, volume, change, time as ingest_time
                FROM latest
                WHERE rn = 1
                ORDER BY percent_change ASC
                LIMIT %s
            """
            return self.execute_query(query, (limit,))

        query = """
            WITH latest AS (
                SELECT
                    d.ticker_code AS ticker,
                    f.close_price AS price,
                    CASE
                        WHEN f.open_price IS NULL OR f.open_price = 0 THEN 0
                        ELSE ((f.close_price - f.open_price) / f.open_price) * 100
                    END AS percent_change,
                    f.volume,
                    (f.close_price - f.open_price) AS change,
                    f.bucket_minute AS ingest_time,
                    ROW_NUMBER() OVER (PARTITION BY d.ticker_code ORDER BY f.bucket_minute DESC) AS rn
                FROM dw.fact_quote_1m f
                JOIN dw.dim_ticker d ON d.ticker_sk = f.ticker_sk
                WHERE f.bucket_minute >= NOW() - (%s || ' hours')::interval
            )
            SELECT 
                ticker,
                price,
                percent_change,
                volume,
                change,
                ingest_time
            FROM latest
            WHERE rn = 1
              AND percent_change IS NOT NULL
            ORDER BY percent_change ASC
            LIMIT %s
        """
        return self.execute_query(query, (self.dashboard_lookback_hours, limit))
    
    def get_stock_history(self, ticker: str, days: int = 30) -> pd.DataFrame:
        """Get historical data for a specific stock from selected source."""
        if self.dashboard_data_source == "snowflake":
            query = """
                SELECT
                    f.BUCKET_MINUTE AS date,
                    f.OPEN_PRICE AS open,
                    f.HIGH_PRICE AS high,
                    f.LOW_PRICE AS low,
                    f.CLOSE_PRICE AS close,
                    f.VOLUME AS volume
                FROM STOCK_DWH.DW.FACT_QUOTE_1M f
                JOIN STOCK_DWH.DW.DIM_TICKER d ON d.TICKER_SK = f.TICKER_SK
                WHERE d.TICKER_CODE = ?
                  AND f.BUCKET_MINUTE >= DATEADD(day, -?, CURRENT_TIMESTAMP())
                ORDER BY 1 ASC
            """
            return self.execute_query(query, (ticker, days))

        if self.dashboard_data_source == "legacy":
            query = """
                SELECT
                    DATE_TRUNC('minute', time) as date,
                    MIN(open_price) as open,
                    MAX(high) as high,
                    MIN(low) as low,
                    MAX(close_price) as close,
                    SUM(volume) as volume
                FROM realtime_quotes
                WHERE ticker = %s
                  AND time >= NOW() - (%s || ' days')::interval
                GROUP BY 1
                ORDER BY 1 ASC
            """
            return self.execute_query(query, (ticker, days))

        query = """
            SELECT 
                f.bucket_minute as date,
                f.open_price as open,
                f.high_price as high,
                f.low_price as low,
                f.close_price as close,
                f.volume as volume
            FROM dw.fact_quote_1m f
            JOIN dw.dim_ticker d ON d.ticker_sk = f.ticker_sk
            WHERE d.ticker_code = %s
              AND f.bucket_minute >= NOW() - (%s || ' days')::interval
            ORDER BY 1 ASC
        """
        return self.execute_query(query, (ticker, days))
    
    def get_recent_records(self, ticker: str, limit: int = 100) -> pd.DataFrame:
        """Get recent records for a specific stock from selected source."""
        if self.dashboard_data_source == "snowflake":
            query = """
                SELECT
                    TICKER, EVENT_TIME AS time, PRICE, OPEN_PRICE AS open, HIGH, LOW,
                    CLOSE_PRICE AS close, VOLUME, CHANGE, PERCENT_CHANGE
                FROM STOCK_DWH.SILVER.REALTIME_QUOTES_CLEAN
                WHERE TICKER = ?
                ORDER BY EVENT_TIME DESC
                LIMIT ?
            """
            return self.execute_query(query, (ticker, limit))

        if self.dashboard_data_source == "legacy":
            query = """
                SELECT
                    ticker, time, price, open_price as open, high, low, close_price as close, volume, change, percent_change
                FROM realtime_quotes
                WHERE ticker = %s
                ORDER BY time DESC
                LIMIT %s
            """
            return self.execute_query(query, (ticker, limit))

        query = """
            SELECT 
                ticker,
                event_time as time,
                price,
                open_price as open,
                high,
                low,
                close_price as close,
                volume,
                change,
                percent_change
            FROM silver.realtime_quotes_clean
            WHERE ticker = %s
            ORDER BY event_time DESC
            LIMIT %s
        """
        return self.execute_query(query, (ticker, limit))
    
    def get_total_volume_for_range(self, ticker: str, days: int) -> int:
        """Accurately compute total traded volume for the selected range.
        - For 1 day: sum for today's VN date (Asia/Ho_Chi_Minh)
        - For 7/30 days: sum since NOW() - INTERVAL '{days} days'
        """
        table_name = "silver.realtime_quotes_clean" if self.dashboard_data_source != "legacy" else "realtime_quotes"
        time_col = "event_time" if self.dashboard_data_source != "legacy" else "time"
        if self.dashboard_data_source == "snowflake":
            if days == 1:
                query = """
                    SELECT COALESCE(SUM(VOLUME), 0) AS total_volume
                    FROM STOCK_DWH.SILVER.REALTIME_QUOTES_CLEAN
                    WHERE TICKER = ?
                      AND CAST(CONVERT_TIMEZONE('Asia/Ho_Chi_Minh', EVENT_TIME) AS DATE) = CAST(CONVERT_TIMEZONE('Asia/Ho_Chi_Minh', CURRENT_TIMESTAMP()) AS DATE)
                """
                df = self.execute_query(query, (ticker,))
            else:
                query = """
                    SELECT COALESCE(SUM(VOLUME), 0) AS total_volume
                    FROM STOCK_DWH.SILVER.REALTIME_QUOTES_CLEAN
                    WHERE TICKER = ?
                      AND EVENT_TIME >= DATEADD(day, -?, CURRENT_TIMESTAMP())
                """
                df = self.execute_query(query, (ticker, days))
            if not df.empty and 'TOTAL_VOLUME' in [c.upper() for c in df.columns]:
                col = next(c for c in df.columns if c.upper() == 'TOTAL_VOLUME')
                return int(float(df.iloc[0][col] or 0))
            return 0

        if days == 1:
            query = """
                SELECT COALESCE(SUM(volume), 0) AS total_volume
                FROM """ + table_name + """
                WHERE ticker = %s
                  AND (""" + time_col + """ AT TIME ZONE 'Asia/Ho_Chi_Minh')::date = (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date
            """
            df = self.execute_query(query, (ticker,))
        else:
            query = """
                SELECT COALESCE(SUM(volume), 0) AS total_volume
                FROM """ + table_name + """
                WHERE ticker = %s
                  AND """ + time_col + """ >= NOW() - INTERVAL %s
            """
            interval_str = f"{days} days"
            df = self.execute_query(query, (ticker, interval_str))
        if not df.empty and 'total_volume' in df.columns:
            try:
                return int(pd.to_numeric(df.iloc[0]['total_volume'], errors='coerce').fillna(0))
            except Exception:
                return int(float(df.iloc[0]['total_volume'] or 0))
        return 0
    
    def create_candlestick_chart(self, df: pd.DataFrame, ticker: str) -> go.Figure:
        """Create candlestick chart"""
        if df.empty:
            return go.Figure()
        
        fig = go.Figure(data=go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=ticker,
            increasing_line_color='#00C851',
            decreasing_line_color='#ff4444',
            increasing_fillcolor='rgba(0,200,81,0.3)',
            decreasing_fillcolor='rgba(255,68,68,0.3)'
        ))
        
        fig.update_layout(
            title=f"{ticker} - Biểu Đồ Nến Chuyên Nghiệp",
            xaxis_title="Thời Gian",
            yaxis_title="Giá (VND)",
            template="plotly_dark",
            height=500,
            font=dict(size=14, color="white"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                rangeslider=dict(visible=False)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                tickformat=","
            )
        )
        
        return fig
    
    def create_volume_chart(self, df: pd.DataFrame, ticker: str) -> go.Figure:
        """Create volume chart"""
        try:
            if df.empty:
                logger.warning(f"Empty dataframe for volume chart: {ticker}")
                return go.Figure()
            
            if 'volume' not in df.columns:
                logger.warning(f"Volume column not found for {ticker}")
                return go.Figure()
            
            if 'date' not in df.columns:
                logger.warning(f"Date column not found for {ticker}")
                return go.Figure()
            
            # Use all data, fill nulls with 0
            volume_df = df[['date', 'volume']].copy()
            # Convert volume from Decimal to float
            volume_df['volume'] = pd.to_numeric(volume_df['volume'], errors='coerce').fillna(0)
            
            # Ensure date column is datetime
            if not pd.api.types.is_datetime64_any_dtype(volume_df['date']):
                volume_df['date'] = pd.to_datetime(volume_df['date'], errors='coerce')
            
            # Remove rows with invalid dates
            volume_df = volume_df[volume_df['date'].notna()]
            
            if volume_df.empty:
                logger.warning(f"No valid date/volume data for {ticker}")
                return go.Figure()
            
            # Sort by date
            volume_df = volume_df.sort_values('date')
            
            # Calculate appropriate y-axis range based on actual data
            volume_min = float(volume_df['volume'].min())
            volume_max = float(volume_df['volume'].max())
            
            # Remove extreme outliers (top 1%) for better visualization
            if len(volume_df) > 10:
                q99 = float(volume_df['volume'].quantile(0.99))
                volume_max = min(volume_max, q99 * 1.5)  # Cap at 1.5x of 99th percentile
            
            # Add padding: 5% at bottom, 15% at top
            padding_bottom = max(0, volume_min * 0.05) if volume_min >= 0 else abs(volume_min) * 0.05
            padding_top = volume_max * 0.15
            
            y_min = max(0, volume_min - padding_bottom)
            y_max = volume_max + padding_top
            
            # Round to nice numbers for better readability
            if y_max > 10000:
                y_max = int(np.ceil(y_max / 10000)) * 10000
            elif y_max > 1000:
                y_max = int(np.ceil(y_max / 1000)) * 1000
            else:
                y_max = int(np.ceil(y_max / 100)) * 100
            
            logger.info(f"Creating volume chart for {ticker}: {len(volume_df)} data points, volume range: {volume_min:.0f} - {volume_max:.0f}, y-axis: {y_min:.0f} - {y_max:.0f}")
            
            fig = go.Figure(data=go.Bar(
                x=volume_df['date'],
                y=volume_df['volume'],
                name="Khối Lượng",
                marker_color=self.VOLUME_CHART_COLOR,  # Use consistent color constant
                opacity=self.VOLUME_CHART_OPACITY,  # Use consistent opacity constant
                hovertemplate='<b>%{x}</b><br>Khối lượng: %{y:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"{ticker} - Khối Lượng Giao Dịch",
                xaxis_title="Thời Gian",
                yaxis_title="Khối Lượng",
                template="plotly_dark",
                height=300,
                font=dict(size=14, color="white"),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    type='date'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(255,255,255,0.1)',
                    tickformat=",.",
                    range=[y_min, y_max]  # Set appropriate y-axis range
                ),
                showlegend=False
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating volume chart for {ticker}: {e}", exc_info=True)
            return go.Figure()
    
    def display_header(self):
        """Display SSI-style header"""
        st.markdown('<h1 class="main-header">Vietnam Stock Market Dashboard</h1>', unsafe_allow_html=True)
        now_vn = self._now_vn()
        market_status, market_status_class = self._get_market_status(now_vn)
        
        # Status bar
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            current_time = now_vn.strftime('%H:%M:%S')
            st.markdown(f'<div class="refresh-indicator">Real-time | Cập nhật: {current_time}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="status-online">● Online</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'<div class="{market_status_class}">● {market_status}</div>', unsafe_allow_html=True)
        
        with col4:
            if st.button("Refresh", key="main_refresh"):
                # Preserve current page before rerun
                current_section = st.session_state.get("current_section", "Realtime Dashboard")
                if current_section == "Realtime Dashboard" and 'current_page_realtime' in st.session_state:
                    st.session_state.preserved_page = st.session_state['current_page_realtime']
                elif current_section == "BI Dashboard" and 'current_page_bi' in st.session_state:
                    st.session_state.preserved_page = st.session_state['current_page_bi']
                # Preserve currently selected ticker if exists
                if 'selected_ticker' in st.session_state and st.session_state.get('selected_ticker'):
                    st.session_state.preserved_ticker = st.session_state.get('selected_ticker')
                st.session_state.last_update = self._now_vn()
                st.rerun()
        
        if market_status != "Đang giao dịch":
            st.info("Thị trường hiện không giao dịch. Dashboard giữ dữ liệu gần nhất, không kỳ vọng tick realtime mới.")

        st.markdown("---")
    
    def display_market_overview(self):
        """Display market overview with SSI-style metrics"""
        st.markdown('<h2 class="sub-header">Tổng Quan Thị Trường</h2>', unsafe_allow_html=True)
        st.caption("Đơn vị giá hiển thị: VND (quy đổi từ bảng giá nghìn đồng x1000).")
        
        market_summary = self.get_market_summary()
        
        if not market_summary.empty:
            summary = market_summary.iloc[0]
            logger.info(
                "Market summary: total=%s, gainers=%s, losers=%s, unchanged=%s",
                int(summary['total_tickers']),
                int(summary['gainers']),
                int(summary['losers']),
                int(summary['unchanged']),
            )
            self._render_kpi_cards(summary)
            
            # Market performance chart
            st.markdown('<h3 class="sub-header">Phân Bố Hiệu Suất</h3>', unsafe_allow_html=True)
            
            performance_data = {
                'Loại': ['Tăng Giá', 'Giảm Giá', 'Không Đổi'],
                'Số Lượng': [summary['gainers'], summary['losers'], summary['unchanged']],
                'Màu': ['#00C851', '#ff4444', '#ffbb33']
            }
            
            fig = go.Figure(data=go.Bar(
                x=performance_data['Loại'],
                y=performance_data['Số Lượng'],
                marker_color=performance_data['Màu'],
                text=[f"{int(v):,}" for v in performance_data['Số Lượng']],
                textposition="auto"
            ))
            
            fig.update_layout(
                template="plotly_dark",
                height=400,
                font=dict(size=14, color="white"),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def display_price_board(self):
        """Display SSI-style price board"""
        st.markdown('<h2 class="sub-header">Bảng Giá Real-time</h2>', unsafe_allow_html=True)
        st.caption("Đơn vị giá hiển thị: VND (quy đổi từ bảng giá nghìn đồng x1000).")
        
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_ticker = st.text_input("Tìm kiếm mã cổ phiếu:", placeholder="VD: VCB, VIC, HPG...")
        
        with col2:
            sort_by = st.selectbox("Sắp xếp theo:", ["Khối lượng", "Thay đổi %", "Giá"])
        
        with col3:
            limit = st.selectbox("Hiển thị:", [50, 100, 200, 500])
        
        # Get real-time quotes
        quotes_df = self.get_realtime_quotes(limit)
        
        if not quotes_df.empty:
            # Apply search filter
            if search_ticker:
                quotes_df = quotes_df[quotes_df['ticker'].str.contains(search_ticker.upper(), na=False)]
            
            # Apply sorting
            if sort_by == "Khối lượng":
                quotes_df = quotes_df.sort_values('volume', ascending=False)
            elif sort_by == "Thay đổi %":
                quotes_df = quotes_df.sort_values('percent_change', ascending=False)
            elif sort_by == "Giá":
                quotes_df = quotes_df.sort_values('price', ascending=False)
            
            # Display as styled table
            display_df = quotes_df[['ticker', 'price', 'change', 'percent_change', 'volume', 'high', 'low']].copy()
            display_df = self._scale_price_columns(display_df, ['price', 'change', 'high', 'low'])
            
            # Format columns
            display_df['price'] = display_df['price'].apply(lambda x: f"{x:,.0f}")
            display_df['change'] = display_df['change'].apply(lambda x: f"{x:,.0f}")
            display_df['percent_change'] = display_df['percent_change'].apply(lambda x: f"{x:+.2f}%")
            display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,}")
            display_df['high'] = display_df['high'].apply(lambda x: f"{x:,.0f}")
            display_df['low'] = display_df['low'].apply(lambda x: f"{x:,.0f}")
            
            # Rename columns
            display_df.columns = ['Mã', 'Giá', 'Thay Đổi', 'Thay Đổi %', 'Khối Lượng', 'Cao', 'Thấp']
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
        else:
            st.warning("Không có dữ liệu real-time")
    
    def display_top_performers(self, top_n: int = 20, min_volume: int = 0, focus_tickers: Optional[List[str]] = None):
        """Display top performers"""
        st.markdown('<h2 class="sub-header">Top Cổ Phiếu Tăng Giá</h2>', unsafe_allow_html=True)
        st.caption("Đơn vị giá hiển thị: VND (quy đổi từ bảng giá nghìn đồng x1000).")
        trend_filter = st.selectbox(
            "Lọc xu hướng trong Top performers:",
            ["Tất cả", "Xu hướng tăng", "Xu hướng giảm", "Không đổi"],
            key="top_performers_trend_filter"
        )
        
        candidate_size = max(100, top_n * 5)
        top_performers = self.get_top_performers(candidate_size)
        if not top_performers.empty:
            if min_volume > 0 and "volume" in top_performers.columns:
                top_performers = top_performers[top_performers["volume"] >= min_volume]
            if focus_tickers:
                focus_set = {t.upper() for t in focus_tickers}
                top_performers = top_performers[top_performers["ticker"].astype(str).str.upper().isin(focus_set)]

            if trend_filter == "Xu hướng tăng":
                top_performers = top_performers[top_performers["percent_change"] > 0]
            elif trend_filter == "Xu hướng giảm":
                top_performers = top_performers[top_performers["percent_change"] < 0]
            elif trend_filter == "Không đổi":
                top_performers = top_performers[top_performers["percent_change"] == 0]

            gainers_df = top_performers[top_performers["percent_change"] > 0].sort_values("percent_change", ascending=False)
            losers_df = top_performers[top_performers["percent_change"] < 0].sort_values("percent_change", ascending=True)
            neutral_df = top_performers[top_performers["percent_change"] == 0].sort_values("ticker", ascending=True)
            top_performers = pd.concat([gainers_df, losers_df, neutral_df], ignore_index=True).head(top_n)
        
        if not top_performers.empty:
            gainers_count = int((top_performers["percent_change"] > 0).sum())
            losers_count = int((top_performers["percent_change"] < 0).sum())
            neutral_count = int((top_performers["percent_change"] == 0).sum())
            st.caption(
                f"Thứ tự hiển thị: Tăng ({gainers_count}) -> Giảm ({losers_count}) -> Không đổi ({neutral_count})."
            )
            bar_colors = [
                '#00C851' if v > 0 else ('#ff4444' if v < 0 else '#ffbb33')
                for v in top_performers['percent_change']
            ]
            # Create chart
            fig = go.Figure(data=go.Bar(
                x=top_performers['percent_change'],
                y=top_performers['ticker'],
                marker_color=bar_colors,
                text=[f"{x:+.2f}%" for x in top_performers['percent_change']],
                textposition="outside",
                orientation='h'
            ))
            
            fig.update_layout(
                title="Top 20 Cổ Phiếu Tăng Giá Mạnh Nhất",
                xaxis_title="Thay Đổi (%)",
                yaxis_title="Mã Cổ Phiếu",
                template="plotly_dark",
                height=500,
                font=dict(size=14, color="white"),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', categoryorder='total ascending')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display table
            st.markdown('<h3 class="sub-header">Chi Tiết Top Performers</h3>', unsafe_allow_html=True)
            
            display_df = top_performers[['ticker', 'price', 'percent_change', 'volume', 'change']].copy()
            display_df = self._scale_price_columns(display_df, ['price', 'change'])
            display_df['price'] = display_df['price'].apply(lambda x: f"{x:,.0f}")
            display_df['percent_change'] = display_df['percent_change'].apply(lambda x: f"{x:+.2f}%")
            display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,}")
            display_df['change'] = display_df['change'].apply(lambda x: f"{x:+,.0f}")
            
            display_df.columns = ['Mã', 'Giá', 'Thay Đổi %', 'Khối Lượng', 'Thay Đổi']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Không có dữ liệu phù hợp với bộ lọc BI hiện tại.")
    
    def display_stock_analysis(self, focus_tickers: Optional[List[str]] = None):
        """Display individual stock analysis"""
        st.markdown('<h2 class="sub-header">Phân Tích Cổ Phiếu</h2>', unsafe_allow_html=True)
        st.caption("Đơn vị giá hiển thị: VND (quy đổi từ bảng giá nghìn đồng x1000).")
        
        # Get available tickers (only active ones with recent data)
        if self.dashboard_data_source == "snowflake":
            tickers_query = """
                SELECT DISTINCT TICKER
                FROM STOCK_DWH.SILVER.REALTIME_QUOTES_CLEAN
                WHERE EVENT_TIME >= DATEADD(day, -7, CURRENT_TIMESTAMP())
                ORDER BY TICKER
            """
        elif self.dashboard_data_source == "legacy":
            tickers_query = """
                SELECT DISTINCT ticker
                FROM realtime_quotes
                WHERE time >= NOW() - INTERVAL '7 days'
                ORDER BY ticker
            """
        else:
            tickers_query = """
                SELECT DISTINCT ticker
                FROM silver.realtime_quotes_clean
                WHERE event_time >= NOW() - INTERVAL '7 days'
                ORDER BY ticker
            """
        tickers_df = self.execute_query(tickers_query)
        
        if not tickers_df.empty:
            ticker_col = self._get_col_name(tickers_df, "ticker")
            if not ticker_col:
                st.error("Không tìm thấy cột mã cổ phiếu trong dữ liệu truy vấn.")
                return
            tickers = tickers_df[ticker_col].tolist()
            if focus_tickers:
                focus_set = {t.upper() for t in focus_tickers}
                filtered = [t for t in tickers if str(t).upper() in focus_set]
                if filtered:
                    tickers = filtered

            # Trend filter for ticker dropdown (PowerBI-style UX)
            trend_filter = st.selectbox(
                "Lọc mã theo xu hướng:",
                ["Tất cả", "Xu hướng tăng", "Xu hướng giảm", "Không đổi"],
                key="ticker_trend_filter"
            )
            latest_quotes = self.get_realtime_quotes(limit=500)
            if not latest_quotes.empty and "ticker" in latest_quotes.columns and "percent_change" in latest_quotes.columns:
                latest_quotes["ticker"] = latest_quotes["ticker"].astype(str).str.upper()
                trend_map = latest_quotes.set_index("ticker")["percent_change"].to_dict()
                if trend_filter == "Xu hướng tăng":
                    tickers = [t for t in tickers if float(trend_map.get(str(t).upper(), 0)) > 0]
                elif trend_filter == "Xu hướng giảm":
                    tickers = [t for t in tickers if float(trend_map.get(str(t).upper(), 0)) < 0]
                elif trend_filter == "Không đổi":
                    tickers = [t for t in tickers if float(trend_map.get(str(t).upper(), 0)) == 0]

            if not tickers:
                st.warning("Không có mã phù hợp với bộ lọc xu hướng hiện tại.")
                return
            
            # Restore preserved ticker if set by refresh
            preserved_ticker = st.session_state.get('preserved_ticker')
            current_ticker = preserved_ticker or st.session_state.get('selected_ticker')
            if not current_ticker or current_ticker not in tickers:
                current_ticker = tickers[0]
            
            idx = tickers.index(current_ticker) if current_ticker in tickers else 0
            selected_ticker = st.selectbox(
                "Chọn Cổ Phiếu:",
                options=tickers,
                index=idx,
                key="selected_ticker"
            )
            # Clear preserved ticker once applied
            if preserved_ticker and st.session_state.get('preserved_ticker'):
                del st.session_state['preserved_ticker']
            
            if selected_ticker:
                # Get current quote
                if self.dashboard_data_source == "snowflake":
                    current_quote = self.execute_query(
                        """
                        SELECT
                            ticker,
                            close_price AS price,
                            change_abs AS change,
                            pct_change AS percent_change,
                            volume,
                            high_price AS high,
                            low_price AS low,
                            bucket_minute AS time
                        FROM STOCK_DWH.DW.VW_FACT_QUOTE_1M_ENRICHED
                        WHERE ticker = ?
                        QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY bucket_minute DESC) = 1
                        """,
                        (selected_ticker,)
                    )
                elif self.dashboard_data_source == "legacy":
                    current_quote = self.execute_query(
                        "SELECT ticker, price, change, percent_change, volume, high, low, time FROM realtime_quotes WHERE ticker = %s ORDER BY time DESC LIMIT 1",
                        (selected_ticker,)
                    )
                else:
                    current_quote = self.execute_query(
                        """
                        SELECT
                            d.ticker_code AS ticker,
                            f.close_price AS price,
                            (f.close_price - f.open_price) AS change,
                            CASE
                                WHEN f.open_price IS NULL OR f.open_price = 0 THEN 0
                                ELSE ((f.close_price - f.open_price) / f.open_price) * 100
                            END AS percent_change,
                            f.volume,
                            f.high_price AS high,
                            f.low_price AS low,
                            f.bucket_minute AS time
                        FROM dw.fact_quote_1m f
                        JOIN dw.dim_ticker d ON d.ticker_sk = f.ticker_sk
                        WHERE d.ticker_code = %s
                        ORDER BY f.bucket_minute DESC
                        LIMIT 1
                        """,
                        (selected_ticker,)
                    )
                
                if not current_quote.empty:
                    quote = current_quote.iloc[0]
                    quote_price = self._vnd(quote['price'])
                    quote_change = self._vnd(quote['change'])
                    quote_high = self._vnd(quote['high'])
                    quote_low = self._vnd(quote['low'])
                    
                    # Current price metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Giá Hiện Tại", f"{quote_price:,.0f} VND")
                    
                    with col2:
                        change_color = "normal"
                        if quote['percent_change'] > 0:
                            change_color = "normal"
                        elif quote['percent_change'] < 0:
                            change_color = "inverse"
                        
                        st.metric(
                            "Thay Đổi",
                            f"{quote_change:+,.0f} VND",
                            delta=f"{quote['percent_change']:+.2f}%"
                        )
                    
                    with col3:
                        st.metric("Khối Lượng", f"{quote['volume']:,}")
                    
                    with col4:
                        st.metric("Cao/Thấp", f"{quote_high:,.0f} / {quote_low:,.0f}")
                    
                    # Historical chart
                    st.markdown('<h3 class="sub-header">Biểu Đồ Lịch Sử</h3>', unsafe_allow_html=True)
                    
                    # Time range selector
                    time_range = st.radio("Khoảng thời gian:", ["1 ngày", "7 ngày", "30 ngày"], horizontal=True)
                    
                    days_map = {"1 ngày": 1, "7 ngày": 7, "30 ngày": 30}
                    days = days_map[time_range]
                    
                    # Check if ticker has recent data
                    if self.dashboard_data_source == "snowflake":
                        recent_check = self.execute_query(
                            "SELECT MAX(EVENT_TIME) as last_update FROM STOCK_DWH.SILVER.REALTIME_QUOTES_CLEAN WHERE TICKER = ?",
                            (selected_ticker,)
                        )
                    elif self.dashboard_data_source == "legacy":
                        recent_check = self.execute_query(
                            "SELECT MAX(time) as last_update FROM realtime_quotes WHERE ticker = %s",
                            (selected_ticker,)
                        )
                    else:
                        recent_check = self.execute_query(
                            "SELECT MAX(event_time) as last_update FROM silver.realtime_quotes_clean WHERE ticker = %s",
                            (selected_ticker,)
                        )
                    
                    if not recent_check.empty and recent_check.iloc[0]['last_update']:
                        last_update = self._to_vn_datetime(recent_check.iloc[0]['last_update'])
                        age_hours = (self._now_vn() - last_update).total_seconds() / 3600
                        
                        if age_hours > 24:
                            st.warning(f"Dữ liệu cũ: {selected_ticker} có bản ghi cuối cách đây {int(age_hours)} giờ ({last_update.strftime('%Y-%m-%d %H:%M')}, giờ VN). Mã này có thể không còn được thu thập.")
                    
                    # Auto-refresh toggle
                    auto_refresh = st.checkbox("Tự động làm mới sau mỗi 10 giây", value=False, key=f"auto_refresh_{selected_ticker}")
                    
                    # Get historical data with minute-level granularity for MA calculation
                    if self.dashboard_data_source == "snowflake":
                        query = """
                            SELECT 
                                TICKER as symbol,
                                EVENT_TIME as datetime,
                                OPEN_PRICE as open,
                                HIGH,
                                LOW,
                                CLOSE_PRICE as close,
                                VOLUME
                            FROM STOCK_DWH.SILVER.REALTIME_QUOTES_CLEAN
                            WHERE TICKER = ?
                              AND EVENT_TIME >= DATEADD(day, -?, CURRENT_TIMESTAMP())
                            ORDER BY EVENT_TIME ASC
                        """
                    elif self.dashboard_data_source == "legacy":
                        query = """
                            SELECT 
                                ticker as symbol,
                                time as datetime,
                                open_price as open,
                                high,
                                low,
                                close_price as close,
                                volume
                            FROM realtime_quotes
                            WHERE ticker = %s
                            AND time >= NOW() - INTERVAL %s
                            ORDER BY time ASC
                        """
                    else:
                        query = """
                            SELECT 
                                ticker as symbol,
                                event_time as datetime,
                                open_price as open,
                                high,
                                low,
                                close_price as close,
                                volume
                            FROM silver.realtime_quotes_clean
                            WHERE ticker = %s
                            AND event_time >= NOW() - INTERVAL %s
                            ORDER BY event_time ASC
                        """
                    
                    try:
                        # Format interval string
                        interval_str = f"{days} days"
                        query_params = (selected_ticker, days) if self.dashboard_data_source == "snowflake" else (selected_ticker, interval_str)
                        data = self.execute_query(query, query_params)
                        
                        if not data.empty:
                            # Convert datetime to datetime type if needed
                            if not pd.api.types.is_datetime64_any_dtype(data['datetime']):
                                data['datetime'] = pd.to_datetime(data['datetime'])
                            
                            # Convert numeric columns
                            data['open'] = pd.to_numeric(data['open'], errors='coerce')
                            data['high'] = pd.to_numeric(data['high'], errors='coerce')
                            data['low'] = pd.to_numeric(data['low'], errors='coerce')
                            data['close'] = pd.to_numeric(data['close'], errors='coerce')
                            data['volume'] = pd.to_numeric(data['volume'], errors='coerce').fillna(0)
                            data = self._scale_price_columns(data, ['open', 'high', 'low', 'close'])
                            
                            # Remove rows with invalid data
                            data = data[data[['open', 'high', 'low', 'close']].notna().all(axis=1)]
                            
                            if not data.empty:
                                # Tính toán MA5, MA20
                                data['MA5'] = data['close'].rolling(window=5, min_periods=1).mean()
                                data['MA20'] = data['close'].rolling(window=20, min_periods=1).mean()
                                
                                # Volume chart: dùng một màu nhất quán, sáng, dễ nhìn
                                # Dùng một màu duy nhất cho volume giúp biểu đồ đơn giản và rõ ràng
                                volume_color = '#00BCD4'  # Cyan sáng, dễ nhìn trên dark background
                                
                                # Tạo biểu đồ subplot: Candlestick + Volume
                                fig = make_subplots(
                                    rows=2, cols=1, shared_xaxes=True,
                                    row_heights=[0.7, 0.3],  # Price 70%, Volume 30% - tỷ lệ dễ theo dõi
                                    vertical_spacing=0.03
                                )
                                
                                # Candlestick chart
                                fig.add_trace(go.Candlestick(
                                    x=data['datetime'],
                                    open=data['open'],
                                    high=data['high'],
                                    low=data['low'],
                                    close=data['close'],
                                    name='Giá',
                                    increasing_line_color='#26a69a',
                                    decreasing_line_color='#ef5350',
                                    increasing_fillcolor='rgba(38,166,154,0.3)',
                                    decreasing_fillcolor='rgba(239,83,80,0.3)',
                                    hoverinfo='x+y+text',
                                    hovertext=[f"Mở: {o:,.0f}<br>Cao: {h:,.0f}<br>Thấp: {l:,.0f}<br>Đóng: {c:,.0f}" 
                                              for o, h, l, c in zip(data['open'], data['high'], data['low'], data['close'])]
                                ), row=1, col=1)
                                
                                # MA lines
                                fig.add_trace(go.Scatter(
                                    x=data['datetime'], 
                                    y=data['MA5'],
                                    line=dict(color='cyan', width=1.5),
                                    name='MA5',
                                    hovertemplate='<b>%{x}</b><br>MA5: %{y:,.0f}<extra></extra>'
                                ), row=1, col=1)
                                
                                fig.add_trace(go.Scatter(
                                    x=data['datetime'], 
                                    y=data['MA20'],
                                    line=dict(color='orange', width=1.5),
                                    name='MA20',
                                    hovertemplate='<b>%{x}</b><br>MA20: %{y:,.0f}<extra></extra>'
                                ), row=1, col=1)
                                
                                # Volume chart: một màu nhất quán, opacity vừa phải
                                fig.add_trace(go.Bar(
                                    x=data['datetime'],
                                    y=data['volume'],
                                    marker_color=volume_color,  # Màu nhất quán
                                    marker_line_width=0,  # Không có viền để clean
                                    name='Khối lượng',
                                    hovertemplate="<b>%{x}</b><br>Khối lượng: %{y:,.0f}<extra></extra>",
                                    opacity=0.75,  # Opacity vừa phải - không quá nổi bật nhưng vẫn rõ
                                    base=0  # Đảm bảo bars bắt đầu từ 0
                                ), row=2, col=1)
                                
                                # Layout biểu đồ
                                fig.update_layout(
                                    title=f"Biểu đồ giá & khối lượng - {selected_ticker}",
                                    template='plotly_dark',
                                    xaxis_rangeslider_visible=False,
                                    height=650,  # Chiều cao phù hợp để quan sát
                                    margin=dict(l=50, r=25, t=60, b=45),
                                    font=dict(family='Segoe UI', size=13, color='white'),
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    showlegend=True,
                                    legend=dict(
                                        orientation="h", 
                                        yanchor="bottom", 
                                        y=1.02, 
                                        xanchor="right", 
                                        x=1,
                                        font=dict(size=11),
                                        bgcolor='rgba(0,0,0,0)'
                                    )
                                )
                                
                                fig.update_xaxes(
                                    showgrid=True, 
                                    gridcolor='rgba(255,255,255,0.1)',  # Grid nhẹ nhàng, không quá nổi
                                    row=2, 
                                    col=1,
                                    title_font=dict(size=12),
                                    tickfont=dict(size=11)
                                )
                                fig.update_yaxes(
                                    title_text="Giá (VND)", 
                                    row=1, 
                                    col=1, 
                                    showgrid=True, 
                                    gridcolor='rgba(255,255,255,0.1)',
                                    tickformat=",.",
                                    title_font=dict(size=12),
                                    tickfont=dict(size=11)
                                )
                                fig.update_yaxes(
                                    title_text="Khối lượng", 
                                    row=2, 
                                    col=1, 
                                    showgrid=True, 
                                    gridcolor='rgba(255,255,255,0.1)',  # Grid nhẹ nhàng
                                    tickformat=",.",  # Format số với dấu phẩy
                                    title_font=dict(size=12),
                                    tickfont=dict(size=11)
                                )
                                
                                # Hiển thị chart
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Tổng khối lượng giao dịch theo khoảng thời gian đã chọn
                                # Original logic: sum on the filtered dataframe (aligned with chart)
                                vol_series = pd.to_numeric(data['volume'], errors='coerce').fillna(0)
                                if days == 1:
                                    # Limit to today's VN date only
                                    dt_series = pd.to_datetime(data['datetime'], errors='coerce')
                                    try:
                                        # If tz-aware, convert to VN
                                        vn_dates = dt_series.dt.tz_convert('Asia/Ho_Chi_Minh').dt.date
                                    except Exception:
                                        # If tz-naive, shift +7h to approximate VN date
                                        vn_dates = (dt_series + pd.Timedelta(hours=7)).dt.date
                                    vn_today = self._now_vn().date()
                                    total_volume = int(vol_series[vn_dates == vn_today].sum())
                                else:
                                    total_volume = int(vol_series.sum())
                                volume_label = f"Tổng Khối Lượng ({time_range})"
                                st.metric(volume_label, f"{total_volume:,}")

                                # Thông tin gần nhất
                                latest = data.iloc[-1]
                                if len(data) > 1:
                                    prev = data.iloc[-2]
                                    change = latest['close'] - prev['close']
                                    pct = (change / prev['close'] * 100) if prev['close'] > 0 else 0
                                else:
                                    change = 0
                                    pct = 0
                                
                                color = "#26a69a" if change >= 0 else "#ef5350"
                                st.markdown(f"""
                                    <div style="font-size:18px; margin-top:15px;">
                                        <b>Giá hiện tại:</b> {latest['close']:,.0f} VND &nbsp;&nbsp;
                                        <span style="color:{color};">
                                            ({change:+,.0f} / {pct:+.2f}%)
                                        </span>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Auto-refresh logic
                                if auto_refresh:
                                    import time
                                    time.sleep(10)
                                    st.rerun()
                            else:
                                st.warning(f"Không có dữ liệu hợp lệ cho {selected_ticker} trong {days} ngày gần đây")
                        else:
                            st.warning(f"Không có dữ liệu lịch sử cho {selected_ticker} trong {days} ngày gần đây")
                    except Exception as e:
                        logger.error(f"Error querying data for {selected_ticker}: {e}", exc_info=True)
                        st.error(f"Lỗi khi truy vấn dữ liệu: {e}")
                else:
                    st.warning(f"Không tìm thấy dữ liệu hiện tại cho {selected_ticker}")
                
                # Display recent records table - always show when ticker is selected
                st.markdown("---")
                st.markdown('<h3 class="sub-header">Dữ Liệu Chi Tiết (100 Bản Ghi Gần Nhất)</h3>', unsafe_allow_html=True)
                
                recent_records = self.get_recent_records(selected_ticker, limit=100)
                
                if not recent_records.empty:
                    # Format the dataframe for display
                    display_df = recent_records.copy()
                    
                    # Sort by time descending (newest first)
                    display_df = display_df.sort_values('time', ascending=False)
                    
                    # Format columns for better readability
                    display_df['time'] = (
                        pd.to_datetime(display_df['time'], errors='coerce', utc=True)
                        .dt.tz_convert(self.VN_TZ)
                        .dt.strftime('%Y-%m-%d %H:%M:%S')
                    )
                    display_df = self._scale_price_columns(display_df, ['price', 'open', 'high', 'low', 'close', 'change'])
                    display_df['price'] = display_df['price'].apply(lambda x: f"{float(x):,.0f}")
                    display_df['open'] = display_df['open'].apply(lambda x: f"{float(x):,.0f}" if pd.notna(x) else "N/A")
                    display_df['high'] = display_df['high'].apply(lambda x: f"{float(x):,.0f}" if pd.notna(x) else "N/A")
                    display_df['low'] = display_df['low'].apply(lambda x: f"{float(x):,.0f}" if pd.notna(x) else "N/A")
                    display_df['close'] = display_df['close'].apply(lambda x: f"{float(x):,.0f}" if pd.notna(x) else "N/A")
                    display_df['volume'] = display_df['volume'].apply(lambda x: f"{int(float(x)):,}" if pd.notna(x) else "0")
                    display_df['change'] = display_df['change'].apply(lambda x: f"{float(x):+,.0f}" if pd.notna(x) else "N/A")
                    display_df['percent_change'] = display_df['percent_change'].apply(lambda x: f"{float(x):+.2f}%" if pd.notna(x) else "N/A")
                    
                    # Rename columns to Vietnamese
                    display_df.columns = ['Mã', 'Thời Gian', 'Giá', 'Mở', 'Cao', 'Thấp', 'Đóng', 'Khối Lượng', 'Thay Đổi', 'Thay Đổi %']
                    
                    # Reorder columns
                    display_df = display_df[['Mã', 'Thời Gian', 'Giá', 'Mở', 'Cao', 'Thấp', 'Đóng', 'Khối Lượng', 'Thay Đổi', 'Thay Đổi %']]
                    
                    # Display table with enhanced styling
                    st.markdown("""
                    <style>
                    div[data-testid="stDataFrame"] {
                        color: #e0e0e0 !important;
                    }
                    div[data-testid="stDataFrame"] table {
                        color: #e0e0e0 !important;
                        background-color: #1e1e1e !important;
                    }
                    div[data-testid="stDataFrame"] th {
                        color: #ffffff !important;
                        background-color: #2d2d2d !important;
                        font-weight: bold !important;
                    }
                    div[data-testid="stDataFrame"] td {
                        color: #e0e0e0 !important;
                        background-color: #1e1e1e !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    st.dataframe(display_df, use_container_width=True, height=400)
                    
                    # Prepare CSV data for download (use original data, not formatted)
                    csv_df = recent_records.copy()
                    csv_df = csv_df.sort_values('time', ascending=False)
                    csv_df['time'] = (
                        pd.to_datetime(csv_df['time'], errors='coerce', utc=True)
                        .dt.tz_convert(self.VN_TZ)
                        .dt.strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    # Convert to CSV
                    csv_data = csv_df.to_csv(index=False).encode('utf-8-sig')  # utf-8-sig for Excel compatibility
                    
                    # Download button
                    st.download_button(
                        label="Tải Xuống CSV",
                        data=csv_data,
                        file_name=f"{selected_ticker}_recent_records_{self._now_vn().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key=f"download_csv_{selected_ticker}"
                    )
                else:
                    st.warning(f"Không có dữ liệu chi tiết cho {selected_ticker}")
    
    def run(self):
        """Run the SSI-style dashboard"""
        # Display header
        self.display_header()
        
        # Sidebar navigation
        st.sidebar.title("Điều Hướng")
        section_options = ["Realtime Dashboard", "BI Dashboard"]
        section = st.sidebar.radio("Chọn Khu Vực:", section_options, key="current_section")
        if section == "Realtime Dashboard":
            st.sidebar.caption("Theo dõi thị trường tức thời, ưu tiên tốc độ cập nhật.")
        else:
            st.sidebar.caption("Phân tích dữ liệu tổng hợp, xu hướng và hiệu suất.")

        # Restore preserved page (if refresh button was used)
        if 'preserved_page' in st.session_state:
            if section == "Realtime Dashboard":
                st.session_state['current_page_realtime'] = st.session_state['preserved_page']
            else:
                st.session_state['current_page_bi'] = st.session_state['preserved_page']
            del st.session_state['preserved_page']

        if section == "Realtime Dashboard":
            page_options = ["Tổng quan", "Bảng giá"]
            page = st.sidebar.selectbox(
                "Chọn Trang:",
                page_options,
                key="current_page_realtime"
            )
            st.markdown("### Realtime Dashboard")
            st.caption("Dữ liệu thị trường cập nhật liên tục từ pipeline streaming.")

            if page == "Tổng quan":
                self.display_market_overview()
            elif page == "Bảng giá":
                self.display_price_board()
        else:
            page_options = ["Top performers", "Phân tích cổ phiếu"]
            page = st.sidebar.selectbox(
                "Chọn Trang:",
                page_options,
                key="current_page_bi"
            )
            st.sidebar.markdown("---")
            st.sidebar.markdown("### Global BI Filters")
            bi_top_n = st.sidebar.slider("Top N cổ phiếu", min_value=10, max_value=50, value=20, step=5)
            bi_min_volume = st.sidebar.number_input("Khối lượng tối thiểu", min_value=0, value=1000, step=1000)
            available_tickers = self.get_available_tickers(days=7, limit=300)
            bi_focus_tickers = st.sidebar.multiselect(
                "Danh sách ticker ưu tiên",
                options=available_tickers,
                default=[],
                help="Để trống để xem toàn thị trường."
            )
            st.markdown("### BI Dashboard")
            st.caption("Phân tích dữ liệu tổng hợp trên tầng DW (dim/fact).")
            self.render_pipeline_health_panel()

            if page == "Top performers":
                self.display_top_performers(
                    top_n=bi_top_n,
                    min_volume=int(bi_min_volume),
                    focus_tickers=bi_focus_tickers
                )
            elif page == "Phân tích cổ phiếu":
                self.display_stock_analysis(focus_tickers=bi_focus_tickers)
        
        # Footer
        st.markdown("---")
        st.markdown("### Vietnam Stock Market Dashboard")
        st.markdown(f"**Khu Vực Hiện Tại:** {section}")
        st.markdown("**Nền Tảng:** Kafka + PostgreSQL + Streamlit | **Nguồn:** VNStock Real-time")
        st.markdown(f"**Cập Nhật (Giờ VN):** {self._now_vn().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    dashboard = SSIStyleDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
