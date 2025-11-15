#!/usr/bin/env python3
"""
VNStock Data Analysis - Identify Key Data for Big Data Pipeline
Senior Data Engineer Level - Data Source Analysis
"""

import vnstock
import pandas as pd
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_vnstock_data():
    """Analyze VNStock data sources for big data pipeline"""
    
    print("VNStock Data Analysis for Big Data Pipeline")
    print("=" * 60)
    
    # Test popular stocks
    test_tickers = ['VCB', 'VIC', 'VHM', 'HPG', 'VNM']
    
    # 1. Real-time Intraday Data
    print("\n1. REAL-TIME INTRADAY DATA")
    print("-" * 40)
    try:
        df_intraday = vnstock.stock_intraday_data(symbol='VCB')
        if not df_intraday.empty:
            print(f"OK: stock_intraday_data: {len(df_intraday)} records")
            print(f"   Columns: {list(df_intraday.columns)}")
            print(f"   Sample data:")
            print(df_intraday.head(2).to_string())
        else:
            print("ERROR: No intraday data available")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # 2. Historical Data
    print("\n2. HISTORICAL DATA")
    print("-" * 40)
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        df_hist = vnstock.stock_historical_data(
            symbol='VCB',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            resolution='1D',
            type='stock'
        )
        
        if not df_hist.empty:
            print(f"OK: stock_historical_data: {len(df_hist)} records")
            print(f"   Columns: {list(df_hist.columns)}")
            print(f"   Sample data:")
            print(df_hist.head(2).to_string())
        else:
            print("ERROR: No historical data available")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # 3. Price Board (Market Overview)
    print("\n3. PRICE BOARD (MARKET OVERVIEW)")
    print("-" * 40)
    try:
        df_price_board = vnstock.price_board()
        if not df_price_board.empty:
            print(f"OK: price_board: {len(df_price_board)} records")
            print(f"   Columns: {list(df_price_board.columns)}")
            print(f"   Sample data:")
            print(df_price_board.head(3).to_string())
        else:
            print("ERROR: No price board data available")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # 4. Company Information
    print("\n4. COMPANY INFORMATION")
    print("-" * 40)
    try:
        df_companies = vnstock.listing_companies()
        if not df_companies.empty:
            print(f"OK: listing_companies: {len(df_companies)} records")
            print(f"   Columns: {list(df_companies.columns)}")
            print(f"   Sample data:")
            print(df_companies.head(3).to_string())
        else:
            print("ERROR: No company data available")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # 5. Market Indices
    print("\n5. MARKET INDICES")
    print("-" * 40)
    try:
        df_indices = vnstock.indices_listing()
        if not df_indices.empty:
            print(f"OK: indices_listing: {len(df_indices)} records")
            print(f"   Columns: {list(df_indices.columns)}")
            print(f"   Sample data:")
            print(df_indices.head(3).to_string())
        else:
            print("ERROR: No indices data available")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # 6. Market Top Movers
    print("\n6. MARKET TOP MOVERS")
    print("-" * 40)
    try:
        df_top_movers = vnstock.market_top_mover()
        if not df_top_movers.empty:
            print(f"OK: market_top_mover: {len(df_top_movers)} records")
            print(f"   Columns: {list(df_top_movers.columns)}")
            print(f"   Sample data:")
            print(df_top_movers.head(3).to_string())
        else:
            print("ERROR: No top movers data available")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # 7. Financial Ratios
    print("\n7. FINANCIAL RATIOS")
    print("-" * 40)
    try:
        df_financial = vnstock.financial_ratio(symbol='VCB')
        if not df_financial.empty:
            print(f"OK: financial_ratio: {len(df_financial)} records")
            print(f"   Columns: {list(df_financial.columns)}")
            print(f"   Sample data:")
            print(df_financial.head(2).to_string())
        else:
            print("ERROR: No financial ratio data available")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # 8. Company Profile
    print("\n8. COMPANY PROFILE")
    print("-" * 40)
    try:
        df_profile = vnstock.company_profile(symbol='VCB')
        if not df_profile.empty:
            print(f"OK: company_profile: {len(df_profile)} records")
            print(f"   Columns: {list(df_profile.columns)}")
            print(f"   Sample data:")
            print(df_profile.head(2).to_string())
        else:
            print("ERROR: No company profile data available")
    except Exception as e:
        print(f"ERROR: {e}")

def recommend_data_strategy():
    """Recommend data collection strategy for big data pipeline"""
    
    print("\nRECOMMENDED DATA STRATEGY FOR BIG DATA PIPELINE")
    print("=" * 60)
    
    print("""
PRIORITY 1 - REAL-TIME STREAMING DATA (High Frequency):
├── stock_intraday_data() - Real-time price, volume, OHLC
├── price_board() - Market overview, top gainers/losers
└── market_top_mover() - Market movers analysis

PRIORITY 2 - HISTORICAL DATA (Daily Batch):
├── stock_historical_data() - OHLCV historical data
├── financial_ratio() - Financial metrics & ratios
└── company_profile() - Company fundamental data

PRIORITY 3 - REFERENCE DATA (Low Frequency):
├── listing_companies() - Company metadata
├── indices_listing() - Market indices information
└── company_profile() - Company details

KAFKA TOPICS RECOMMENDATION:
├── vnstock-realtime-quotes     - Real-time price data
├── vnstock-market-overview     - Market summary data
├── vnstock-historical-data     - Historical OHLCV data
├── vnstock-financial-ratios    - Financial metrics
├── vnstock-company-info        - Company metadata
└── vnstock-market-indices      - Index data

POSTGRESQL TABLES RECOMMENDATION:
├── realtime_quotes            - Real-time price data
├── historical_data            - Historical OHLCV data
├── market_summary             - Market overview
├── financial_ratios           - Financial metrics
├── company_info               - Company metadata
├── market_indices             - Index data
└── market_movers              - Top gainers/losers
""")

def data_collection_frequency():
    """Define data collection frequency"""
    
    print("\nDATA COLLECTION FREQUENCY STRATEGY")
    print("=" * 60)
    
    print("""
REAL-TIME STREAMING (Every 30 seconds):
├── stock_intraday_data() - Current price, volume
├── price_board() - Market overview
└── market_top_mover() - Top movers

DAILY BATCH (Once per day):
├── stock_historical_data() - Previous day OHLCV
├── financial_ratio() - Updated financial metrics
└── company_profile() - Company updates

REFERENCE DATA (Weekly/Monthly):
├── listing_companies() - New listings
├── indices_listing() - Index updates
└── company_profile() - Major changes

STREAMING PRIORITY:
1. Real-time quotes (30s) - Critical for trading
2. Market overview (1min) - Important for analysis
3. Historical data (1hour) - For trend analysis
4. Financial ratios (1day) - For fundamental analysis
5. Company info (1week) - For reference data
""")

if __name__ == "__main__":
    analyze_vnstock_data()
    recommend_data_strategy()
    data_collection_frequency()



