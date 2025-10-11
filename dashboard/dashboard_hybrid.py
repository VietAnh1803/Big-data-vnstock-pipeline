import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import json
import time
from sqlalchemy import create_engine, text
import urllib.parse

# Page config
st.set_page_config(
    page_title="Vietnam Stock Dashboard - Hybrid",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stSidebar {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
</style>
""", unsafe_allow_html=True)

# Database connection - PostgreSQL fallback
def get_db_connection():
    try:
        # Use environment variables with correct password
        user = os.getenv('POSTGRES_USER', 'admin')
        password = os.getenv('POSTGRES_PASSWORD', 'admin123@')
        host = os.getenv('POSTGRES_HOST', 'postgres')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'stock_db')
        
        # URL encode password for special characters
        encoded_password = urllib.parse.quote_plus(password)
        
        # Force TCP connection with explicit host and port - NO SOCKET
        connection_string = f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{db}?host={host}&port={port}&sslmode=disable"
        
        engine = create_engine(connection_string, pool_pre_ping=True)
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Data fetching functions - PostgreSQL fallback
def get_ticker_list():
    """Get available tickers from PostgreSQL"""
    engine = get_db_connection()
    if not engine:
        return []
    
    try:
        # Prefer tickers that actually have realtime data with valid prices
        query_primary = text("""
            SELECT DISTINCT ticker
            FROM realtime_quotes
            WHERE price > 0
            ORDER BY ticker
        """)
        df = pd.read_sql(query_primary, engine)
        tickers = df['ticker'].tolist()
        if tickers:
            return tickers
        
        # Fallback to all tickers if no valid prices
        query_fallback = text("""
            SELECT DISTINCT ticker
            FROM realtime_quotes
            ORDER BY ticker
        """)
        df_fallback = pd.read_sql(query_fallback, engine)
        return df_fallback['ticker'].tolist()
    except Exception as e:
        st.error(f"Error fetching tickers: {e}")
        # Return hardcoded list as fallback
        return ['HPG', 'MSN', 'VCB', 'VHM', 'VIC']

def get_realtime_data(ticker=None, limit=1000):
    """Get real-time data from PostgreSQL"""
    engine = get_db_connection()
    if not engine:
        return pd.DataFrame()
    
    try:
        if ticker and ticker != "All":
            # Latest records for a specific ticker
            query = text("""
                SELECT time, price, volume, change_percent
                FROM realtime_quotes
                WHERE ticker = :ticker
                ORDER BY time DESC
                LIMIT :limit
            """)
            df = pd.read_sql(query, engine, params={"ticker": ticker, "limit": limit})
        else:
            # Latest record per ticker using DISTINCT ON (PostgreSQL)
            query = text("""
                SELECT DISTINCT ON (ticker)
                    ticker, time, price, volume, change_percent
                FROM realtime_quotes
                ORDER BY ticker, time DESC
            """)
            df = pd.read_sql(query, engine)
        
        return df
    except Exception as e:
        st.error(f"Error fetching realtime data: {e}")
        return pd.DataFrame()

def get_market_summary():
    """Get market summary from PostgreSQL"""
    engine = get_db_connection()
    if not engine:
        return {}
    
    try:
        query = text("""
            SELECT ticker, price, change, change_percent, volume
            FROM realtime_quotes 
            WHERE (ticker, time) IN (
                SELECT ticker, MAX(time)
                FROM realtime_quotes
                GROUP BY ticker
            )
            ORDER BY time DESC
        """)
        df = pd.read_sql(query, engine)
        
        market_data = {}
        for _, row in df.iterrows():
            market_data[row['ticker']] = {
                'price': row['price'],
                'change': row['change'],
                'change_percent': row['change_percent'],
                'volume': row['volume']
            }
        
        return market_data
    except Exception as e:
        st.error(f"Error fetching market summary: {e}")
        return {}

# Main dashboard
def main():
    st.markdown('<h1 class="main-header">📈 Vietnam Stock Dashboard - Hybrid</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎛️ Control Panel")
    
    # Get tickers from PostgreSQL
    tickers = get_ticker_list()
    if not tickers:
        st.error("❌ No tickers available from database")
        return
    
    # Ticker selection
    selected_ticker = st.sidebar.selectbox(
        "📊 Select Ticker",
        ["All"] + tickers,
        index=0
    )
    
    # Time range
    time_range = st.sidebar.selectbox(
        "⏰ Time Range",
        ["1 Hour", "4 Hours", "1 Day", "1 Week"],
        index=2
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Main content
    if selected_ticker == "All":
        st.subheader("📊 Market Overview")
        
        # Get market data from PostgreSQL
        market_data = get_market_summary()
        if market_data:
            # Display market metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📈 Total Tickers", len(market_data))
            
            with col2:
                avg_change = sum(data['change_percent'] for data in market_data.values()) / len(market_data)
                st.metric("📊 Avg Change %", f"{avg_change:.2f}%")
            
            with col3:
                total_volume = sum(data['volume'] for data in market_data.values())
                st.metric("📦 Total Volume", f"{total_volume:,}")
            
            with col4:
                st.metric("🕐 Last Update", datetime.now().strftime("%H:%M:%S"))
            
            # Market heatmap
            st.subheader("🔥 Market Heatmap")
            if market_data:
                heatmap_data = []
                for ticker, data in market_data.items():
                    heatmap_data.append({
                        'Ticker': ticker,
                        'Price': data['price'],
                        'Change %': data['change_percent'],
                        'Volume': data['volume']
                    })
                
                df_heatmap = pd.DataFrame(heatmap_data)
                st.dataframe(df_heatmap, use_container_width=True)
        else:
            st.warning("⚠️ No market data available from database")
    
    else:
        st.subheader(f"📈 {selected_ticker} Analysis")
        
        # Get ticker data from PostgreSQL
        ticker_data = get_realtime_data(selected_ticker, 100)
        
        if not ticker_data.empty:
            # Display ticker metrics
            col1, col2, col3, col4 = st.columns(4)
            
            latest = ticker_data.iloc[0]
            
            with col1:
                st.metric("💰 Current Price", f"${latest['price']:.2f}")
            
            with col2:
                st.metric("📊 Change", f"{latest['change']:.2f}")
            
            with col3:
                st.metric("📈 Change %", f"{latest['change_percent']:.2f}%")
            
            with col4:
                st.metric("📦 Volume", f"{latest['volume']:,}")
            
            # Price chart
            st.subheader("📊 Price Chart")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=ticker_data['time'],
                y=ticker_data['price'],
                mode='lines+markers',
                name=selected_ticker,
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig.update_layout(
                title=f"{selected_ticker} Price Movement",
                xaxis_title="Time",
                yaxis_title="Price",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            st.subheader("📦 Volume Analysis")
            fig_volume = go.Figure()
            fig_volume.add_trace(go.Bar(
                x=ticker_data['time'],
                y=ticker_data['volume'],
                name='Volume',
                marker_color='#ff7f0e'
            ))
            
            fig_volume.update_layout(
                title=f"{selected_ticker} Volume",
                xaxis_title="Time",
                yaxis_title="Volume"
            )
            
            st.plotly_chart(fig_volume, use_container_width=True)
            
        else:
            st.warning(f"⚠️ No data available for {selected_ticker} from database")
    
    # Footer
    st.markdown("---")
    st.markdown("**🔗 Data Source:** PostgreSQL Database")
    st.markdown("**⏰ Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()
