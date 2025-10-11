#!/usr/bin/env python3
"""
Fetch ALL available data from vnstock3 for BIG DATA pipeline - VERSION 2
Fixed for actual vnstock3 API column names
"""

import os
import sys
import time
import logging
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database config
PG_HOST = os.getenv('POSTGRES_HOST', 'postgres')
PG_PORT = os.getenv('POSTGRES_PORT', '5432')
PG_DB = os.getenv('POSTGRES_DB', 'stock_db')
PG_USER = os.getenv('POSTGRES_USER', 'admin')
PG_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin')


def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )


def fetch_ticker_info():
    """Fetch company information for all tickers."""
    logger.info("Fetching ticker information...")
    
    try:
        from vnstock import Listing
        
        listing = Listing()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        total_inserted = 0
        
        for exchange in ['HSX', 'HNX', 'UPCOM']:
            logger.info(f"Fetching tickers from {exchange}...")
            
            try:
                tickers_df = listing.all_symbols(exchange=exchange)
                
                if tickers_df is None or tickers_df.empty:
                    logger.warning(f"No data from {exchange}")
                    continue
                
                for idx, row in tickers_df.iterrows():
                    ticker = row.get('ticker', row.get('symbol', ''))
                    
                    if not ticker:
                        continue
                    
                    try:
                        cursor.execute("""
                            INSERT INTO ticker_info (
                                ticker, company_name, exchange, 
                                listing_date, updated_at
                            ) VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (ticker) DO UPDATE SET
                                company_name = EXCLUDED.company_name,
                                exchange = EXCLUDED.exchange,
                                listing_date = EXCLUDED.listing_date,
                                updated_at = EXCLUDED.updated_at
                        """, (
                            ticker,
                            row.get('organ_name', row.get('company_name', '')),
                            exchange,
                            row.get('listing_date', None),
                            datetime.now()
                        ))
                        
                        total_inserted += 1
                        
                        if total_inserted % 100 == 0:
                            conn.commit()
                            logger.info(f"Inserted {total_inserted} tickers...")
                        
                    except Exception as e:
                        logger.debug(f"Error inserting {ticker}: {e}")
                        continue
                
            except Exception as e:
                logger.error(f"Error fetching {exchange}: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Fetched {total_inserted} ticker info records")
        return total_inserted
        
    except Exception as e:
        logger.error(f"Error in fetch_ticker_info: {e}")
        return 0


def fetch_historical_prices(ticker, start_date=None, end_date=None):
    """Fetch historical prices using vnstock3."""
    try:
        from vnstock import Vnstock
        
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        stock = Vnstock().stock(symbol=ticker, source='VCI')
        df = stock.quote.history(start=start_date, end=end_date, interval='1D')
        
        if df is None or df.empty:
            return 0
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        inserted = 0
        for idx, row in df.iterrows():
            try:
                trading_date = row.get('time', idx)
                if isinstance(trading_date, str):
                    trading_date = datetime.strptime(trading_date, '%Y-%m-%d').date()
                elif isinstance(trading_date, pd.Timestamp):
                    trading_date = trading_date.date()
                    
                # Calculate change percent
                change_pct = None
                if pd.notna(row.get('open')) and pd.notna(row.get('close')) and row.get('open') > 0:
                    change_pct = ((row.get('close') - row.get('open')) / row.get('open')) * 100
                
                cursor.execute("""
                    INSERT INTO historical_prices (
                        ticker, trading_date, open_price, high_price,
                        low_price, close_price, volume, change_percent
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (ticker, trading_date) DO NOTHING
                """, (
                    ticker,
                    trading_date,
                    float(row.get('open', 0)) if pd.notna(row.get('open')) else None,
                    float(row.get('high', 0)) if pd.notna(row.get('high')) else None,
                    float(row.get('low', 0)) if pd.notna(row.get('low')) else None,
                    float(row.get('close', 0)) if pd.notna(row.get('close')) else None,
                    int(row.get('volume', 0)) if pd.notna(row.get('volume')) else 0,
                    float(change_pct) if change_pct is not None else None
                ))
                inserted += 1
            except Exception as e:
                logger.debug(f"Error inserting price for {ticker}: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return inserted
        
    except Exception as e:
        logger.debug(f"Error fetching historical prices for {ticker}: {e}")
        return 0


def main():
    """Main function to fetch all data."""
    logger.info("=" * 70)
    logger.info("FETCHING DATA FROM VNSTOCK3 - BIG DATA PIPELINE V2")
    logger.info("=" * 70)
    
    # Step 1: Fetch ticker info
    logger.info("\n📊 Step 1: Fetching ticker information...")
    ticker_count = fetch_ticker_info()
    
    # Step 2: Get all tickers from database
    logger.info("\n📊 Step 2: Fetching historical prices for each ticker...")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ticker FROM ticker_info ORDER BY ticker")
    tickers = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    
    logger.info(f"Found {len(tickers)} tickers to process")
    
    # Step 3: Fetch historical prices only (financials have format issues)
    logger.info("\n📊 Step 3: Fetching historical prices (2 years)...")
    logger.info("⚠️  This will take 30-60 minutes with 1.5s delay per ticker")
    logger.info("⚠️  Processing all {} tickers...".format(len(tickers)))
    
    processed = 0
    failed = 0
    total_prices = 0
    rate_limit_hits = 0
    
    for i, ticker in enumerate(tickers, 1):
        try:
            if i % 50 == 0:
                logger.info(f"Progress: {i}/{len(tickers)} ({i*100//len(tickers)}%) - Prices: {total_prices:,} - Success: {processed} - Failed: {failed}")
            
            # Delay to avoid rate limit (slower is safer)
            time.sleep(1.5)
            
            # Historical prices
            prices_count = fetch_historical_prices(ticker)
            total_prices += prices_count
            
            if prices_count > 0:
                processed += 1
            else:
                failed += 1
                
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "quá nhiều request" in error_msg:
                rate_limit_hits += 1
                logger.warning(f"⚠️  Rate limit hit at ticker {i}/{len(tickers)}. Waiting 65 seconds...")
                time.sleep(65)
                # Retry current ticker
                try:
                    prices_count = fetch_historical_prices(ticker)
                    total_prices += prices_count
                    if prices_count > 0:
                        processed += 1
                    else:
                        failed += 1
                except:
                    failed += 1
            else:
                logger.debug(f"Error processing {ticker}: {e}")
                failed += 1
            continue
    
    logger.info("\n" + "=" * 70)
    logger.info(f"✅ COMPLETED - HISTORICAL PRICES COLLECTION!")
    logger.info(f"   Ticker info: {ticker_count} companies")
    logger.info(f"   Successfully processed: {processed} tickers")
    logger.info(f"   Failed: {failed} tickers")
    logger.info(f"   Historical prices: {total_prices:,} records")
    logger.info(f"   Rate limit hits: {rate_limit_hits}")
    logger.info("=" * 70)
    logger.info("\nℹ️  Note: Financial data (balance sheet, income, etc.) requires")
    logger.info("   different approach due to vnstock3 API format changes.")
    logger.info("   Historical prices collection is complete!")


if __name__ == "__main__":
    main()

