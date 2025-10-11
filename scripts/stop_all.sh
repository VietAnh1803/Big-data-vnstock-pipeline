#!/bin/bash
################################################################################
# Stop All Services - Vietnam Stock Pipeline
################################################################################

set -e

echo "🛑 Stopping Vietnam Stock Pipeline..."
echo ""

# Stop systemd service if running
if systemctl is-active --quiet vietnam-stock-pipeline 2>/dev/null; then
    echo "Stopping systemd service: vietnam-stock-pipeline"
    sudo systemctl stop vietnam-stock-pipeline
elif systemctl is-active --quiet vietnam-stock-pipeline-with-snowflake 2>/dev/null; then
    echo "Stopping systemd service: vietnam-stock-pipeline-with-snowflake"
    sudo systemctl stop vietnam-stock-pipeline-with-snowflake
fi

# Stop docker-compose as well
echo "Stopping Docker containers..."
cd "$(dirname "$0")/.."
docker-compose --profile snowflake down

echo ""
echo "✅ All services stopped"

