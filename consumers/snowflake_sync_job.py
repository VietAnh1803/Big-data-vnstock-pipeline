#!/usr/bin/env python3
"""
Incremental sync from local TimescaleDB to Snowflake DWH.
Source: public.realtime_quotes
Target: STOCK_DWH.BRONZE/SILVER/DW
"""

import os
import time
import logging
from pathlib import Path

import psycopg2
import snowflake.connector
from snowflake.connector.errors import ProgrammingError

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("snowflake_sync")


SYNC_INTERVAL_SECONDS = int(os.getenv("SNOWFLAKE_SYNC_INTERVAL_SECONDS", "120"))
BOOTSTRAP_LOOKBACK_HOURS = int(os.getenv("SNOWFLAKE_BOOTSTRAP_LOOKBACK_HOURS", "6"))
BATCH_LIMIT = int(os.getenv("SNOWFLAKE_SYNC_BATCH_LIMIT", "5000"))


def get_pg_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "timescaledb"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "stock_db"),
        user=os.getenv("POSTGRES_USER", "stock_app"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )


def get_sf_conn():
    account = os.environ["SNOWFLAKE_ACCOUNT"]
    user = os.environ["SNOWFLAKE_USER"]
    password = os.environ["SNOWFLAKE_PASSWORD"]
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "STOCK_WH")
    database = os.getenv("SNOWFLAKE_DATABASE", "STOCK_DWH")
    requested_role = os.getenv("SNOWFLAKE_ROLE", "").strip()

    # Try configured role first; fall back to default-role login when role is not granted.
    if requested_role:
        try:
            return snowflake.connector.connect(
                account=account,
                user=user,
                password=password,
                role=requested_role,
                warehouse=warehouse,
                database=database,
            )
        except Exception as e:
            logger.warning("Role '%s' is not usable, fallback to default role login: %s", requested_role, e)

    return snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        database=database,
    )


def ensure_snowflake_setup(cur):
    def execute_with_privilege_fallback(stmt: str):
        try:
            cur.execute(stmt)
        except ProgrammingError as exc:
            msg = str(exc)
            # App role may not have full DDL privileges in shared Snowflake accounts.
            # Skip non-critical setup statements and continue with incremental sync.
            if "Insufficient privileges" in msg:
                logger.warning("Skipping setup statement due to limited role privileges")
                return
            raise

    for p in [
        "/app/scripts/snowflake/01_setup.sql",
        "/app/scripts/snowflake/02_tables.sql",
        "/app/scripts/snowflake/04_seed_dim_date.sql",
        "/app/scripts/snowflake/05_bi_views.sql",
    ]:
        sql = Path(p).read_text(encoding="utf-8")
        for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
            execute_with_privilege_fallback(stmt)

    cur.execute("USE DATABASE STOCK_DWH")
    cur.execute("USE WAREHOUSE STOCK_WH")
    cur.execute("CREATE SCHEMA IF NOT EXISTS DW")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS DW.ETL_STATE (
          STATE_KEY STRING PRIMARY KEY,
          WATERMARK TIMESTAMP_TZ,
          UPDATED_AT TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
        )
        """
    )
    cur.execute(
        """
        MERGE INTO DW.ETL_STATE t
        USING (
          SELECT 'TS_TO_SF_BRONZE' AS STATE_KEY,
                 DATEADD(hour, -%s, CURRENT_TIMESTAMP()) AS WATERMARK
        ) s
        ON t.STATE_KEY = s.STATE_KEY
        WHEN NOT MATCHED THEN INSERT (STATE_KEY, WATERMARK, UPDATED_AT)
        VALUES (s.STATE_KEY, s.WATERMARK, CURRENT_TIMESTAMP())
        """,
        (BOOTSTRAP_LOOKBACK_HOURS,),
    )


def get_watermark(cur):
    cur.execute("SELECT WATERMARK FROM DW.ETL_STATE WHERE STATE_KEY = 'TS_TO_SF_BRONZE'")
    row = cur.fetchone()
    return row[0]


def set_watermark(cur, wm):
    cur.execute(
        """
        UPDATE DW.ETL_STATE
        SET WATERMARK = %s, UPDATED_AT = CURRENT_TIMESTAMP()
        WHERE STATE_KEY = 'TS_TO_SF_BRONZE'
        """,
        (wm,),
    )


def sync_once(pg_cur, sf_cur):
    wm = get_watermark(sf_cur)

    pg_cur.execute(
        """
        SELECT time, COALESCE(ingest_time, now()), ticker, price, volume, change,
               percent_change, high, low, open_price, close_price, quote_time, data_source
        FROM public.realtime_quotes
        WHERE time > %s
        ORDER BY time ASC
        LIMIT %s
        """,
        (wm, BATCH_LIMIT),
    )
    rows = pg_cur.fetchall()
    if not rows:
        return 0, 0, 0, wm

    sf_cur.executemany(
        """
        INSERT INTO BRONZE.RAW_QUOTES (
          EVENT_TIME, INGEST_TIME, TICKER, PRICE, VOLUME, CHANGE, PERCENT_CHANGE,
          HIGH, LOW, OPEN_PRICE, CLOSE_PRICE, QUOTE_TIME, DATA_SOURCE
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        rows,
    )

    sf_cur.execute(
        """
        MERGE INTO SILVER.REALTIME_QUOTES_CLEAN t
        USING (
          SELECT
            EVENT_TIME,
            COALESCE(INGEST_TIME, CURRENT_TIMESTAMP()) AS INGEST_TIME,
            UPPER(TICKER) AS TICKER,
            PRICE, VOLUME, CHANGE, PERCENT_CHANGE, HIGH, LOW, OPEN_PRICE, CLOSE_PRICE,
            COALESCE(DATA_SOURCE, 'vnstock') AS DATA_SOURCE,
            SHA2(CONCAT_WS('|', UPPER(TICKER), TO_VARCHAR(EVENT_TIME), TO_VARCHAR(PRICE), TO_VARCHAR(VOLUME)), 256) AS RECORD_HASH
          FROM BRONZE.RAW_QUOTES
          WHERE EVENT_TIME > %s
            AND TICKER IS NOT NULL
            AND REGEXP_LIKE(TICKER, '^[A-Z]{2,5}$')
            AND PRICE > 0
            AND VOLUME >= 0
          QUALIFY ROW_NUMBER() OVER (
            PARTITION BY UPPER(TICKER), EVENT_TIME
            ORDER BY COALESCE(INGEST_TIME, CURRENT_TIMESTAMP()) DESC
          ) = 1
        ) s
        ON t.TICKER = s.TICKER AND t.EVENT_TIME = s.EVENT_TIME
        WHEN MATCHED THEN UPDATE SET
          INGEST_TIME = s.INGEST_TIME, PRICE = s.PRICE, VOLUME = s.VOLUME, CHANGE = s.CHANGE,
          PERCENT_CHANGE = s.PERCENT_CHANGE, HIGH = s.HIGH, LOW = s.LOW, OPEN_PRICE = s.OPEN_PRICE,
          CLOSE_PRICE = s.CLOSE_PRICE, DATA_SOURCE = s.DATA_SOURCE, RECORD_HASH = s.RECORD_HASH
        WHEN NOT MATCHED THEN INSERT (
          EVENT_TIME, INGEST_TIME, TICKER, PRICE, VOLUME, CHANGE, PERCENT_CHANGE,
          HIGH, LOW, OPEN_PRICE, CLOSE_PRICE, DATA_SOURCE, RECORD_HASH
        ) VALUES (
          s.EVENT_TIME, s.INGEST_TIME, s.TICKER, s.PRICE, s.VOLUME, s.CHANGE, s.PERCENT_CHANGE,
          s.HIGH, s.LOW, s.OPEN_PRICE, s.CLOSE_PRICE, s.DATA_SOURCE, s.RECORD_HASH
        )
        """,
        (wm,),
    )

    sf_cur.execute(
        """
        MERGE INTO DW.DIM_TICKER d
        USING (
          SELECT DISTINCT TICKER
          FROM SILVER.REALTIME_QUOTES_CLEAN
          WHERE EVENT_TIME > %s
        ) s
        ON d.TICKER_CODE = s.TICKER AND d.IS_CURRENT = TRUE
        WHEN NOT MATCHED THEN INSERT (TICKER_CODE, IS_ACTIVE, VALID_FROM, IS_CURRENT)
        VALUES (s.TICKER, TRUE, CURRENT_TIMESTAMP(), TRUE)
        """,
        (wm,),
    )

    sf_cur.execute(
        """
        MERGE INTO DW.FACT_QUOTE_1M f
        USING (
          WITH base AS (
            SELECT DATE_TRUNC('MINUTE', EVENT_TIME) AS BUCKET_MINUTE, TICKER,
                   MIN(EVENT_TIME) AS MIN_ET, MAX(EVENT_TIME) AS MAX_ET,
                   MAX(HIGH) AS HIGH_PRICE, MIN(LOW) AS LOW_PRICE,
                   SUM(VOLUME) AS VOLUME, SUM(PRICE * VOLUME) AS TURNOVER,
                   COUNT(*) AS SOURCE_ROWS
            FROM SILVER.REALTIME_QUOTES_CLEAN
            WHERE EVENT_TIME > %s
            GROUP BY 1, 2
          )
          SELECT d.TICKER_SK,
                 TO_NUMBER(TO_CHAR(CAST(b.BUCKET_MINUTE AS DATE), 'YYYYMMDD')) AS DATE_SK,
                 b.BUCKET_MINUTE,
                 o.PRICE AS OPEN_PRICE,
                 b.HIGH_PRICE,
                 b.LOW_PRICE,
                 c.PRICE AS CLOSE_PRICE,
                 b.VOLUME,
                 b.TURNOVER,
                 b.SOURCE_ROWS
          FROM base b
          JOIN SILVER.REALTIME_QUOTES_CLEAN o ON o.TICKER = b.TICKER AND o.EVENT_TIME = b.MIN_ET
          JOIN SILVER.REALTIME_QUOTES_CLEAN c ON c.TICKER = b.TICKER AND c.EVENT_TIME = b.MAX_ET
          JOIN DW.DIM_TICKER d ON d.TICKER_CODE = b.TICKER AND d.IS_CURRENT = TRUE
        ) s
        ON f.TICKER_SK = s.TICKER_SK AND f.BUCKET_MINUTE = s.BUCKET_MINUTE
        WHEN MATCHED THEN UPDATE SET
          DATE_SK = s.DATE_SK, OPEN_PRICE = s.OPEN_PRICE, HIGH_PRICE = s.HIGH_PRICE, LOW_PRICE = s.LOW_PRICE,
          CLOSE_PRICE = s.CLOSE_PRICE, VOLUME = s.VOLUME, TURNOVER = s.TURNOVER, SOURCE_ROWS = s.SOURCE_ROWS,
          LOAD_TS = CURRENT_TIMESTAMP()
        WHEN NOT MATCHED THEN INSERT (
          TICKER_SK, DATE_SK, BUCKET_MINUTE, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME, TURNOVER, SOURCE_ROWS
        ) VALUES (
          s.TICKER_SK, s.DATE_SK, s.BUCKET_MINUTE, s.OPEN_PRICE, s.HIGH_PRICE, s.LOW_PRICE, s.CLOSE_PRICE, s.VOLUME, s.TURNOVER, s.SOURCE_ROWS
        )
        """,
        (wm,),
    )

    new_wm = rows[-1][0]
    set_watermark(sf_cur, new_wm)
    return len(rows), len(rows), len(rows), new_wm


def run():
    logger.info("Starting Snowflake sync worker")
    setup_checked = False
    while True:
        try:
            pg = get_pg_conn()
            sf = get_sf_conn()
            pg_cur = pg.cursor()
            sf_cur = sf.cursor()
            if not setup_checked:
                try:
                    ensure_snowflake_setup(sf_cur)
                except ProgrammingError as exc:
                    if "Insufficient privileges" in str(exc):
                        logger.warning("Skipping Snowflake setup step due to limited role privileges")
                    else:
                        raise
                setup_checked = True
            bronze_rows, silver_rows, fact_rows, wm = sync_once(pg_cur, sf_cur)
            sf.commit()
            logger.info(
                "Snowflake sync completed: bronze=%s silver=%s fact=%s watermark=%s",
                bronze_rows,
                silver_rows,
                fact_rows,
                wm,
            )
            pg_cur.close()
            sf_cur.close()
            pg.close()
            sf.close()
        except Exception as e:
            logger.exception("Snowflake sync failed: %s", e)
        time.sleep(SYNC_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
