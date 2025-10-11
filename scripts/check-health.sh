#!/bin/bash

# Health check script for Vietnam Stock Pipeline
# Checks the health of all services

set -e

echo "=================================="
echo "Vietnam Stock Pipeline Health Check"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_service() {
    SERVICE_NAME=$1
    CONTAINER_NAME=$2
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        echo -e "${GREEN}✓${NC} $SERVICE_NAME is running"
        return 0
    else
        echo -e "${RED}✗${NC} $SERVICE_NAME is not running"
        return 1
    fi
}

check_kafka() {
    echo "Checking Kafka topics..."
    TOPICS=$(docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list 2>/dev/null | grep -c "stock_quotes_topic" || echo "0")
    
    if [ "$TOPICS" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Kafka topic exists"
    else
        echo -e "${YELLOW}!${NC} Kafka topic not found (may be created on first message)"
    fi
}

check_postgres() {
    echo "Checking PostgreSQL data..."
    COUNT=$(docker exec postgres psql -U admin -d stock_db -t -c "SELECT COUNT(*) FROM realtime_quotes;" 2>/dev/null | xargs || echo "0")
    
    if [ "$COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} PostgreSQL has $COUNT records"
    else
        echo -e "${YELLOW}!${NC} PostgreSQL has no data yet"
    fi
}

# Check all services
check_service "Zookeeper" "zookeeper"
check_service "Kafka" "kafka"
check_service "PostgreSQL" "postgres"
check_service "Spark Master" "spark-master"
check_service "Spark Worker" "spark-worker"
check_service "Producer" "stock-producer"
check_service "Spark Processor" "spark-processor"
check_service "Dashboard" "stock-dashboard"

echo ""
check_kafka
check_postgres

echo ""
echo "=================================="
echo "Access points:"
echo "=================================="
echo "Dashboard:     http://localhost:8501"
echo "Spark Master:  http://localhost:8080"
echo "Spark Worker:  http://localhost:8081"
echo ""

