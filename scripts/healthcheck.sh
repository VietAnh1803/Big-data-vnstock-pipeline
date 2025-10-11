#!/bin/bash
################################################################################
# Quick Health Check - Vietnam Stock Pipeline
# 
# Fast health check script that can be used by external monitoring tools
# Returns 0 if healthy, non-zero if unhealthy
################################################################################

set -e

# Check if all critical containers are running
CRITICAL_CONTAINERS=(
    "kafka"
    "postgres"
    "stock-producer"
    "kafka-consumer"
)

failed=0

for container in "${CRITICAL_CONTAINERS[@]}"; do
    status=$(docker inspect -f '{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
    if [ "$status" != "running" ]; then
        echo "UNHEALTHY: $container is $status"
        failed=1
    fi
done

if [ $failed -eq 0 ]; then
    echo "HEALTHY: All critical services running"
    exit 0
else
    echo "UNHEALTHY: Some services are down"
    exit 1
fi

