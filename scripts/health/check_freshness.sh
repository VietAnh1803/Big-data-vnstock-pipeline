#!/usr/bin/env bash
# Freshness of staging data in TimescaleDB (public.realtime_quotes).
# Snowflake SILVER/DWH freshness is not checked here — use Snowflake queries or the dashboard BI health panel.
set -euo pipefail

DB_CONTAINER="${DB_CONTAINER:-vietnam-stock-timescaledb}"
DB_USER="${DB_USER:-stock_app}"
DB_NAME="${DB_NAME:-stock_db}"
MAX_STAGING_LAG_MINUTES="${MAX_STAGING_LAG_MINUTES:-15}"

echo "== Freshness check (TimescaleDB staging: public.realtime_quotes) =="

staging_lag="$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c \
  "SELECT COALESCE(EXTRACT(EPOCH FROM (NOW() - MAX(\"time\"))) / 60, 1e9) FROM public.realtime_quotes;")"

staging_ok=1
awk "BEGIN {exit !($staging_lag <= $MAX_STAGING_LAG_MINUTES)}" || staging_ok=0

printf "staging lag: %.2f min (threshold: %s)\n" "$staging_lag" "$MAX_STAGING_LAG_MINUTES"

if [[ $staging_ok -eq 1 ]]; then
  echo "[PASS] Freshness check passed."
  exit 0
fi

echo "[FAIL] Freshness check failed (no recent rows in public.realtime_quotes, or market closed — interpret with context)."
exit 1
