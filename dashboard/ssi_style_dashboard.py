#!/usr/bin/env python3
"""
SSI-Style Professional Vietnam Stock Dashboard
Inspired by SSI iBoard with modern UI and real-time data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Vietnam Stock Market Dashboard",
    page_icon="📈",
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
</style>
""", unsafe_allow_html=True)

class SSIStyleDashboard:
    """SSI-Inspired Professional Stock Dashboard"""
    
    # Chart styling constants - ensure consistency across all charts
    VOLUME_CHART_COLOR = "#FFD700"  # Gold color - bright and visible on dark background
    VOLUME_CHART_OPACITY = 0.95  # High opacity for better visibility
    
    def __init__(self):
        # Database configuration
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', '5432')),
            'database': os.getenv('POSTGRES_DB', 'stock_db'),
            'user': os.getenv('POSTGRES_USER', 'stock_app'),
            'password': os.getenv('POSTGRES_PASSWORD', '')
        }
        
        # Initialize session state
        if 'last_update' not in st.session_state:
            st.session_state.last_update = datetime.now()
            
    def get_db_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.db_config)
        except Exception as e:
            st.error(f"❌ Database connection failed: {e}")
            return None
            
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        conn = self.get_db_connection()
        if not conn:
            return pd.DataFrame()
            
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return pd.DataFrame(results)
        except Exception as e:
            st.error(f"❌ Query execution failed: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def get_realtime_quotes(self, limit: int = 100) -> pd.DataFrame:
        """Get real-time stock quotes with enhanced data"""
        # Take the latest row per ticker within last hour, then sort for display
        query = """
            WITH latest AS (
                SELECT *,
                       ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
                FROM realtime_quotes
                WHERE time >= NOW() - INTERVAL '1 hour'
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
    
    def get_market_summary(self) -> pd.DataFrame:
        """Get comprehensive market summary"""
        # Get latest record per ticker to count unique tickers correctly
        query = """
            WITH latest_quotes AS (
                SELECT DISTINCT ON (ticker) 
                    ticker,
                    price,
                    volume,
                    percent_change,
                    time
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
    
    def get_top_performers(self, limit: int = 20) -> pd.DataFrame:
        """Get top performing stocks"""
        query = """
            WITH latest AS (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
                FROM realtime_quotes
                WHERE time >= NOW() - INTERVAL '1 hour'
                  AND percent_change IS NOT NULL
            )
            SELECT 
                ticker,
                price,
                percent_change,
                volume,
                change,
                time as ingest_time
            FROM latest
            WHERE rn = 1
            ORDER BY percent_change DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def get_worst_performers(self, limit: int = 20) -> pd.DataFrame:
        """Get worst performing stocks"""
        query = """
            WITH latest AS (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS rn
                FROM realtime_quotes
                WHERE time >= NOW() - INTERVAL '1 hour'
                  AND percent_change IS NOT NULL
            )
            SELECT 
                ticker,
                price,
                percent_change,
                volume,
                change,
                time as ingest_time
            FROM latest
            WHERE rn = 1
            ORDER BY percent_change ASC
            LIMIT %s
        """
        return self.execute_query(query, (limit,))
    
    def get_stock_history(self, ticker: str, days: int = 30) -> pd.DataFrame:
        """Get historical data for a specific stock"""
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
            AND time >= NOW() - INTERVAL '%s days'
            GROUP BY 1
            ORDER BY 1 ASC
        """
        return self.execute_query(query, (ticker, days))
    
    def get_recent_records(self, ticker: str, limit: int = 100) -> pd.DataFrame:
        """Get recent records for a specific stock"""
        query = """
            SELECT 
                ticker,
                time,
                price,
                open_price as open,
                high,
                low,
                close_price as close,
                volume,
                change,
                percent_change
            FROM realtime_quotes
            WHERE ticker = %s
            ORDER BY time DESC
            LIMIT %s
        """
        return self.execute_query(query, (ticker, limit))
    
    def get_total_volume_for_range(self, ticker: str, days: int) -> int:
        """Accurately compute total traded volume for the selected range.
        - For 1 day: sum for today's VN date (Asia/Ho_Chi_Minh)
        - For 7/30 days: sum since NOW() - INTERVAL '{days} days'
        """
        if days == 1:
            query = """
                SELECT COALESCE(SUM(volume), 0) AS total_volume
                FROM realtime_quotes
                WHERE ticker = %s
                  AND (time AT TIME ZONE 'Asia/Ho_Chi_Minh')::date = (NOW() AT TIME ZONE 'Asia/Ho_Chi_Minh')::date
            """
            df = self.execute_query(query, (ticker,))
        else:
            query = """
                SELECT COALESCE(SUM(volume), 0) AS total_volume
                FROM realtime_quotes
                WHERE ticker = %s
                  AND time >= NOW() - INTERVAL %s
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
        """Create professional candlestick chart"""
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
        st.markdown('<h1 class="main-header">📈 Vietnam Stock Market Dashboard</h1>', unsafe_allow_html=True)
        
        # Status bar
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            current_time = datetime.now().strftime('%H:%M:%S')
            st.markdown(f'<div class="refresh-indicator">🔄 Real-time | Cập nhật: {current_time}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="status-online">● Online</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="status-online">● Kafka Active</div>', unsafe_allow_html=True)
        
        with col4:
            if st.button("🔄 Refresh", key="main_refresh"):
                # Preserve current page before rerun
                if 'current_page' in st.session_state:
                    st.session_state.preserved_page = st.session_state['current_page']
                # Preserve currently selected ticker if exists
                if 'selected_ticker' in st.session_state and st.session_state.get('selected_ticker'):
                    st.session_state.preserved_ticker = st.session_state.get('selected_ticker')
                st.session_state.last_update = datetime.now()
                st.rerun()
        
        st.markdown("---")
    
    def display_market_overview(self):
        """Display market overview with SSI-style metrics"""
        st.markdown('<h2 class="sub-header">📊 Tổng Quan Thị Trường</h2>', unsafe_allow_html=True)
        
        market_summary = self.get_market_summary()
        
        if not market_summary.empty:
            summary = market_summary.iloc[0]
            
            # Ensure values are integers for ticker counts
            total_tickers = int(summary['total_tickers'])
            gainers = int(summary['gainers'])
            losers = int(summary['losers'])
            unchanged = int(summary['unchanged'])
            
            # Debug log (commented out in production)
            logger.info(f"Market summary: total={total_tickers}, gainers={gainers}, losers={losers}, unchanged={unchanged}")
            
            # Key metrics in SSI style
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                # Tổng số mã cổ phiếu đang được theo dõi
                st.metric(
                    "Tổng Cổ Phiếu",
                    f"{total_tickers:,}",
                    delta=f"{gainers} mã tăng"
                )
            
            with col2:
                # Tổng khối lượng giao dịch
                st.metric(
                    "Tổng Khối Lượng",
                    f"{summary['total_volume']:,}",
                    delta=f"{losers} mã giảm"
                )
            
            with col3:
                # Giá trung bình của thị trường
                st.metric(
                    "Giá Trung Bình",
                    f"{summary['avg_price']:,.0f} VND",
                    delta=f"{unchanged} mã không đổi"
                )
            
            with col4:
                last_update = summary['last_update'].strftime('%H:%M:%S') if summary['last_update'] else 'N/A'
                st.metric(
                    "Cập Nhật Cuối",
                    last_update,
                    delta="Real-time"
                )
            
            # Market performance chart
            st.markdown('<h3 class="sub-header">📈 Phân Bố Hiệu Suất</h3>', unsafe_allow_html=True)
            
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
        st.markdown('<h2 class="sub-header">📋 Bảng Giá Real-time</h2>', unsafe_allow_html=True)
        
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_ticker = st.text_input("🔍 Tìm kiếm mã cổ phiếu:", placeholder="VD: VCB, VIC, HPG...")
        
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
            st.warning("⚠️ Không có dữ liệu real-time")
    
    def display_top_performers(self):
        """Display top performers"""
        st.markdown('<h2 class="sub-header">🚀 Top Cổ Phiếu Tăng Giá</h2>', unsafe_allow_html=True)
        
        top_performers = self.get_top_performers(20)
        
        if not top_performers.empty:
            # Create chart
            fig = go.Figure(data=go.Bar(
                x=top_performers['ticker'],
                y=top_performers['percent_change'],
                marker_color='#00C851',
                text=[f"{x:+.2f}%" for x in top_performers['percent_change']],
                textposition="auto"
            ))
            
            fig.update_layout(
                title="Top 20 Cổ Phiếu Tăng Giá Mạnh Nhất",
                xaxis_title="Mã Cổ Phiếu",
                yaxis_title="Thay Đổi (%)",
                template="plotly_dark",
                height=500,
                font=dict(size=14, color="white"),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display table
            st.markdown('<h3 class="sub-header">📊 Chi Tiết Top Performers</h3>', unsafe_allow_html=True)
            
            display_df = top_performers[['ticker', 'price', 'percent_change', 'volume', 'change']].copy()
            display_df['price'] = display_df['price'].apply(lambda x: f"{x:,.0f}")
            display_df['percent_change'] = display_df['percent_change'].apply(lambda x: f"{x:+.2f}%")
            display_df['volume'] = display_df['volume'].apply(lambda x: f"{x:,}")
            display_df['change'] = display_df['change'].apply(lambda x: f"{x:+,.0f}")
            
            display_df.columns = ['Mã', 'Giá', 'Thay Đổi %', 'Khối Lượng', 'Thay Đổi']
            
            st.dataframe(display_df, use_container_width=True)
    
    def display_stock_analysis(self):
        """Display individual stock analysis"""
        st.markdown('<h2 class="sub-header">🔍 Phân Tích Cổ Phiếu</h2>', unsafe_allow_html=True)
        
        # Get available tickers (only active ones with recent data)
        tickers_query = """
            SELECT DISTINCT ticker
            FROM realtime_quotes
            WHERE time >= NOW() - INTERVAL '7 days'
            ORDER BY ticker
        """
        tickers_df = self.execute_query(tickers_query)
        
        if not tickers_df.empty:
            tickers = tickers_df['ticker'].tolist()
            
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
                current_quote = self.execute_query(
                    "SELECT * FROM realtime_quotes WHERE ticker = %s ORDER BY time DESC LIMIT 1",
                    (selected_ticker,)
                )
                
                if not current_quote.empty:
                    quote = current_quote.iloc[0]
                    
                    # Current price metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Giá Hiện Tại", f"{quote['price']:,.0f} VND")
                    
                    with col2:
                        change_color = "normal"
                        if quote['percent_change'] > 0:
                            change_color = "normal"
                        elif quote['percent_change'] < 0:
                            change_color = "inverse"
                        
                        st.metric(
                            "Thay Đổi",
                            f"{quote['change']:+,.0f} VND",
                            delta=f"{quote['percent_change']:+.2f}%"
                        )
                    
                    with col3:
                        st.metric("Khối Lượng", f"{quote['volume']:,}")
                    
                    with col4:
                        st.metric("Cao/Thấp", f"{quote['high']:,.0f} / {quote['low']:,.0f}")
                    
                    # Historical chart
                    st.markdown('<h3 class="sub-header">📈 Biểu Đồ Lịch Sử</h3>', unsafe_allow_html=True)
                    
                    # Time range selector
                    time_range = st.radio("Khoảng thời gian:", ["1 ngày", "7 ngày", "30 ngày"], horizontal=True)
                    
                    days_map = {"1 ngày": 1, "7 ngày": 7, "30 ngày": 30}
                    days = days_map[time_range]
                    
                    # Check if ticker has recent data
                    recent_check = self.execute_query(
                        "SELECT MAX(time) as last_update FROM realtime_quotes WHERE ticker = %s",
                        (selected_ticker,)
                    )
                    
                    if not recent_check.empty and recent_check.iloc[0]['last_update']:
                        last_update = recent_check.iloc[0]['last_update']
                        age_hours = (datetime.now().replace(tzinfo=last_update.tzinfo) - last_update).total_seconds() / 3600
                        
                        if age_hours > 24:
                            st.warning(f"⚠️ Dữ liệu cũ: {selected_ticker} có bản ghi cuối cách đây {int(age_hours)} giờ ({last_update.strftime('%Y-%m-%d %H:%M')}). Mã này có thể không còn được thu thập.")
                    
                    # Auto-refresh toggle
                    auto_refresh = st.checkbox("🔄 Tự động làm mới sau mỗi 10 giây", value=False, key=f"auto_refresh_{selected_ticker}")
                    
                    # Get historical data with minute-level granularity for MA calculation
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
                    
                    try:
                        # Format interval string
                        interval_str = f"{days} days"
                        data = self.execute_query(query, (selected_ticker, interval_str))
                        
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
                            
                            # Remove rows with invalid data
                            data = data[data[['open', 'high', 'low', 'close']].notna().all(axis=1)]
                            
                            if not data.empty:
                                # Tính toán MA5, MA20
                                data['MA5'] = data['close'].rolling(window=5, min_periods=1).mean()
                                data['MA20'] = data['close'].rolling(window=20, min_periods=1).mean()
                                
                                # Professional volume chart: một màu nhất quán, sáng, dễ nhìn
                                # Senior data engineers thường dùng một màu duy nhất cho volume để đơn giản và rõ ràng
                                volume_color = '#00BCD4'  # Cyan sáng - màu professional, dễ nhìn trên dark background
                                
                                # Tạo biểu đồ subplot: Candlestick + Volume
                                fig = make_subplots(
                                    rows=2, cols=1, shared_xaxes=True,
                                    row_heights=[0.7, 0.3],  # Price 70%, Volume 30% - tỷ lệ chuẩn professional
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
                                
                                # Volume chart - professional style: một màu nhất quán, opacity vừa phải
                                fig.add_trace(go.Bar(
                                    x=data['datetime'],
                                    y=data['volume'],
                                    marker_color=volume_color,  # Màu nhất quán, professional
                                    marker_line_width=0,  # Không có viền để clean
                                    name='Khối lượng',
                                    hovertemplate="<b>%{x}</b><br>Khối lượng: %{y:,.0f}<extra></extra>",
                                    opacity=0.75,  # Opacity vừa phải - không quá nổi bật nhưng vẫn rõ
                                    base=0  # Đảm bảo bars bắt đầu từ 0
                                ), row=2, col=1)
                                
                                # Layout - professional style
                                fig.update_layout(
                                    title=f"📈 Biểu đồ giá & khối lượng - {selected_ticker}",
                                    template='plotly_dark',
                                    xaxis_rangeslider_visible=False,
                                    height=650,  # Chiều cao chuẩn professional
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
                                    vn_today = (datetime.utcnow() + timedelta(hours=7)).date()
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
                                st.warning(f"⚠️ Không có dữ liệu hợp lệ cho {selected_ticker} trong {days} ngày gần đây")
                        else:
                            st.warning(f"⚠️ Không có dữ liệu lịch sử cho {selected_ticker} trong {days} ngày gần đây")
                    except Exception as e:
                        logger.error(f"Error querying data for {selected_ticker}: {e}", exc_info=True)
                        st.error(f"⚠️ Lỗi khi truy vấn dữ liệu: {e}")
                else:
                    st.warning(f"⚠️ Không tìm thấy dữ liệu hiện tại cho {selected_ticker}")
                
                # Display recent records table - always show when ticker is selected
                st.markdown("---")
                st.markdown('<h3 class="sub-header">📊 Dữ Liệu Chi Tiết (100 Bản Ghi Gần Nhất)</h3>', unsafe_allow_html=True)
                
                recent_records = self.get_recent_records(selected_ticker, limit=100)
                
                if not recent_records.empty:
                    # Format the dataframe for display
                    display_df = recent_records.copy()
                    
                    # Sort by time descending (newest first)
                    display_df = display_df.sort_values('time', ascending=False)
                    
                    # Format columns for better readability
                    display_df['time'] = pd.to_datetime(display_df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
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
                    csv_df['time'] = pd.to_datetime(csv_df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Convert to CSV
                    csv_data = csv_df.to_csv(index=False).encode('utf-8-sig')  # utf-8-sig for Excel compatibility
                    
                    # Download button
                    st.download_button(
                        label="📥 Tải Xuống CSV",
                        data=csv_data,
                        file_name=f"{selected_ticker}_recent_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key=f"download_csv_{selected_ticker}"
                    )
                else:
                    st.warning(f"⚠️ Không có dữ liệu chi tiết cho {selected_ticker}")
    
    def run(self):
        """Run the SSI-style dashboard"""
        # Display header
        self.display_header()
        
        # Sidebar navigation
        st.sidebar.title("📊 Điều Hướng")
        page_options = ["Tổng Quan", "Bảng Giá", "Top Performers", "Phân Tích Cổ Phiếu"]
        
        # Restore preserved page (if refresh button was used)
        if 'preserved_page' in st.session_state:
            st.session_state['current_page'] = st.session_state['preserved_page']
            del st.session_state['preserved_page']

        page = st.sidebar.selectbox(
            "Chọn Trang:",
            page_options,
            key="current_page"
        )
        
        # Display selected page
        if page == "Tổng Quan":
            self.display_market_overview()
        elif page == "Bảng Giá":
            self.display_price_board()
        elif page == "Top Performers":
            self.display_top_performers()
        elif page == "Phân Tích Cổ Phiếu":
            self.display_stock_analysis()
        
        # Footer
        st.markdown("---")
        st.markdown("### 🚀 Vietnam Stock Market Dashboard")
        st.markdown("**Nền Tảng:** Kafka + PostgreSQL + Streamlit | **Nguồn:** VNStock Real-time")
        st.markdown(f"**Cập Nhật:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    dashboard = SSIStyleDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
