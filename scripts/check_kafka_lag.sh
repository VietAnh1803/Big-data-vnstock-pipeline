#!/bin/bash
# Script to check Kafka consumer lag for Spark Structured Streaming

echo "=== Kafka Topic: realtime_quotes ==="
echo ""

# Get latest offsets for all partitions
echo "Latest Offsets (end of log):"
docker exec vietnam-stock-kafka kafka-run-class kafka.tools.GetOffsetShell \
    --broker-list localhost:29092 \
    --topic realtime_quotes \
    --time -1 | sort -t: -k2 -n

echo ""
echo "Earliest Offsets (start of log):"
docker exec vietnam-stock-kafka kafka-run-class kafka.tools.GetOffsetShell \
    --broker-list localhost:29092 \
    --topic realtime_quotes \
    --time -2 | sort -t: -k2 -n

echo ""
echo "=== Spark Checkpoint Offsets ==="
echo "Checking checkpoint location: /tmp/spark-checkpoint"

# Check if checkpoint exists
if docker exec vietnam-stock-spark-consumer test -d /tmp/spark-checkpoint/sources/0; then
    echo "Checkpoint found"
    echo ""
    echo "Checkpoint offsets:"
    docker exec vietnam-stock-spark-consumer cat /tmp/spark-checkpoint/sources/0/*/metadata 2>/dev/null | grep -o '"latestOffset"[^}]*}' | head -5 || echo "WARNING: Could not read checkpoint offsets"
else
    echo "WARNING: Checkpoint directory not found"
fi

echo ""
echo "=== Database Records (Last 10 minutes) ==="
docker exec vietnam-stock-timescaledb psql -U stock_app -d stock_db -c "
SELECT 
    COUNT(*) as records_last_10min,
    MAX(time) as latest_record_time,
    NOW() - MAX(time) as age
FROM realtime_quotes 
WHERE time >= NOW() - INTERVAL '10 minutes';
"

echo ""
echo "=== Spark UI Streaming Info ==="
echo "Access Spark UI at: http://localhost:4041"
echo "Or via proxy: http://localhost:8080/spark/"





