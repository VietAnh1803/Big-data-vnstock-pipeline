#!/bin/bash
# Calculate Kafka consumer lag for Spark Structured Streaming

echo "=== 📊 Kafka Consumer Lag Analysis ==="
echo ""

# Get latest Kafka offsets
echo "Getting latest Kafka offsets..."
LATEST_OFFSETS=$(docker exec vietnam-stock-kafka kafka-run-class kafka.tools.GetOffsetShell \
    --broker-list localhost:29092 \
    --topic realtime_quotes \
    --time -1 | sort -t: -k2 -n)

# Get Spark checkpoint offsets
echo "Getting Spark checkpoint offsets..."
CHECKPOINT_FILE="/tmp/spark-checkpoint/sources/0/0"
CHECKPOINT_DATA=$(docker exec vietnam-stock-spark-consumer cat "$CHECKPOINT_FILE" 2>/dev/null)

if [ -z "$CHECKPOINT_DATA" ]; then
    echo "⚠️  Could not read checkpoint offsets"
    exit 1
fi

# Parse checkpoint JSON (Spark stores offsets in JSON format)
# Extract offsets from JSON
CHECKPOINT_OFFSETS=$(echo "$CHECKPOINT_DATA" | grep -o '"realtime_quotes":{[^}]*}' | sed 's/.*{\(.*\)}.*/\1/')

echo ""
echo "=== Partition Lag Details ==="
echo ""
printf "%-10s %-15s %-15s %-15s %-10s\n" "Partition" "Latest Offset" "Checkpoint" "Lag" "Status"
echo "--------------------------------------------------------------------------------"

TOTAL_LAG=0

# Process each partition
for i in {0..11}; do
    # Get latest offset for this partition
    LATEST=$(echo "$LATEST_OFFSETS" | grep ":$i:" | cut -d: -f3)
    
    # Get checkpoint offset for this partition
    CHECKPOINT=$(echo "$CHECKPOINT_OFFSETS" | grep -o "\"$i\":[0-9]*" | cut -d: -f2)
    
    if [ -z "$CHECKPOINT" ]; then
        CHECKPOINT="0"
    fi
    
    # Calculate lag
    if [ -n "$LATEST" ] && [ -n "$CHECKPOINT" ]; then
        LAG=$((LATEST - CHECKPOINT))
        TOTAL_LAG=$((TOTAL_LAG + LAG))
        
        if [ $LAG -lt 10000 ]; then
            STATUS="✅ Good"
        elif [ $LAG -lt 100000 ]; then
            STATUS="⚠️  Warning"
        else
            STATUS="🔴 High"
        fi
        
        printf "%-10s %-15s %-15s %-15s %-10s\n" "$i" "$LATEST" "$CHECKPOINT" "$LAG" "$STATUS"
    fi
done

echo "--------------------------------------------------------------------------------"
echo ""
echo "📈 Total Lag: $TOTAL_LAG messages"
echo ""

# Calculate lag percentage
TOTAL_MESSAGES=$(echo "$LATEST_OFFSETS" | awk -F: '{sum+=$3} END {print sum}')
if [ $TOTAL_MESSAGES -gt 0 ]; then
    LAG_PERCENT=$(echo "scale=2; $TOTAL_LAG * 100 / $TOTAL_MESSAGES" | bc)
    echo "📊 Lag Percentage: $LAG_PERCENT%"
fi

echo ""
echo "=== Recent Processing Status ==="
docker exec vietnam-stock-timescaledb psql -U stock_app -d stock_db -c "
SELECT 
    COUNT(*) as records_last_5min,
    MAX(time) as latest_record,
    NOW() - MAX(time) as age
FROM realtime_quotes 
WHERE time >= NOW() - INTERVAL '5 minutes';
"

echo ""
echo "💡 Tips:"
echo "  - Lag < 10,000: ✅ Good"
echo "  - Lag 10,000-100,000: ⚠️  Monitor"
echo "  - Lag > 100,000: 🔴 Action needed"
echo ""
echo "🔧 To reduce lag:"
echo "  - Increase MAX_OFFSETS_PER_TRIGGER"
echo "  - Increase STREAM_TRIGGER frequency"
echo "  - Check Spark resource usage"





