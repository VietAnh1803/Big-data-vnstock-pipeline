#!/bin/bash
################################################################################
# Start All Services - Vietnam Stock Pipeline
################################################################################

set -e

echo "🚀 Starting Vietnam Stock Pipeline..."
echo ""

# Check if systemd service exists
if [ -f /etc/systemd/system/vietnam-stock-pipeline.service ]; then
    echo "Starting via systemd: vietnam-stock-pipeline"
    sudo systemctl start vietnam-stock-pipeline
elif [ -f /etc/systemd/system/vietnam-stock-pipeline-with-snowflake.service ]; then
    echo "Starting via systemd: vietnam-stock-pipeline-with-snowflake"
    sudo systemctl start vietnam-stock-pipeline-with-snowflake
else
    echo "No systemd service found, starting via docker-compose..."
    cd "$(dirname "$0")/.."
    
    # Ask if user wants Snowflake
    read -p "Enable Snowflake sync? (y/N) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose --profile snowflake up -d
    else
        docker-compose up -d
    fi
fi

echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "✅ Services started. Checking health..."
bash "$(dirname "$0")/healthcheck.sh" || echo "⚠️  Some services may still be initializing"

echo ""
echo "🌐 Access points:"
echo "   Dashboard: http://localhost:8501"
echo "   pgAdmin:   http://localhost:5050"

