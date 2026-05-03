#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-.env}"
EXIT_CODE=0

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[FAIL] Missing $ENV_FILE. Copy from .env.sample first."
  exit 1
fi

required_vars=(
  POSTGRES_PASSWORD
  KAFKA_UI_PASSWORD
)

weak_patterns=(
  "change_me"
  "password"
  "123456"
  "qwerty"
  "admin"
  "<password>"
  "test"
)

get_var() {
  local key="$1"
  local value
  value="$(awk -F'=' -v k="$key" '$1==k {print substr($0, index($0,$2)); exit}' "$ENV_FILE" || true)"
  echo "${value:-}"
}

check_required() {
  local key="$1"
  local value
  value="$(get_var "$key")"
  if [[ -z "$value" ]]; then
    echo "[FAIL] $key is missing or empty."
    EXIT_CODE=1
    return
  fi

  if [[ ${#value} -lt 16 ]]; then
    echo "[FAIL] $key is too short (<16 chars)."
    EXIT_CODE=1
  fi

  local lowered
  lowered="$(echo "$value" | tr '[:upper:]' '[:lower:]')"
  for p in "${weak_patterns[@]}"; do
    if [[ "$lowered" == *"$p"* ]]; then
      echo "[FAIL] $key appears weak (contains '$p')."
      EXIT_CODE=1
      break
    fi
  done
}

echo "== Preflight security check for $ENV_FILE =="
for k in "${required_vars[@]}"; do
  check_required "$k"
done

sf_password="$(get_var SNOWFLAKE_PASSWORD)"
if [[ -n "$sf_password" ]]; then
  if [[ ${#sf_password} -lt 16 ]]; then
    echo "[FAIL] SNOWFLAKE_PASSWORD is too short (<16 chars)."
    EXIT_CODE=1
  fi
  sf_lower="$(echo "$sf_password" | tr '[:upper:]' '[:lower:]')"
  for p in "${weak_patterns[@]}"; do
    if [[ "$sf_lower" == *"$p"* ]]; then
      echo "[FAIL] SNOWFLAKE_PASSWORD appears weak (contains '$p')."
      EXIT_CODE=1
      break
    fi
  done
fi

if grep -q "^KAFKA_UI_USERNAME=admin$" "$ENV_FILE"; then
  echo "[WARN] KAFKA_UI_USERNAME is 'admin'. Consider changing it."
fi

if grep -q "localhost:9092" "$ENV_FILE"; then
  echo "[WARN] Found localhost Kafka settings in .env; verify exposure rules."
fi

if [[ $EXIT_CODE -eq 0 ]]; then
  echo "[PASS] Security preflight passed."
else
  echo "[FAIL] Security preflight failed. Fix values in $ENV_FILE."
fi

exit "$EXIT_CODE"
