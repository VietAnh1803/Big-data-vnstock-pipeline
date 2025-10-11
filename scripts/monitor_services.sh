#!/bin/bash
################################################################################
# Monitor Services - Vietnam Stock Pipeline
# 
# This script monitors all Docker containers and alerts if any are down
# Can be run manually or via cron job
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/vietnam-stock-pipeline-monitor.log"
ALERT_EMAIL="${ALERT_EMAIL:-}"  # Set this in .env or environment

# Timestamp
timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# Log function
log() {
    echo "[$(timestamp)] $1" | tee -a "$LOG_FILE"
}

# Check if container is running
check_container() {
    local container_name=$1
    local status=$(docker inspect -f '{{.State.Status}}' "$container_name" 2>/dev/null || echo "not_found")
    
    if [ "$status" == "running" ]; then
        echo -e "${GREEN}✅ $container_name: Running${NC}"
        log "✅ $container_name: Running"
        return 0
    else
        echo -e "${RED}❌ $container_name: $status${NC}"
        log "❌ $container_name: $status"
        return 1
    fi
}

# Check container health
check_health() {
    local container_name=$1
    local health=$(docker inspect -f '{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no_health_check")
    
    if [ "$health" == "healthy" ]; then
        echo -e "${GREEN}  ❤️  Health: Healthy${NC}"
        log "  ❤️  $container_name Health: Healthy"
        return 0
    elif [ "$health" == "no_health_check" ]; then
        echo -e "${YELLOW}  ⚠️  Health: No health check configured${NC}"
        return 0
    else
        echo -e "${RED}  💔 Health: $health${NC}"
        log "  💔 $container_name Health: $health"
        return 1
    fi
}

# Get container uptime
get_uptime() {
    local container_name=$1
    local started=$(docker inspect -f '{{.State.StartedAt}}' "$container_name" 2>/dev/null)
    if [ -n "$started" ]; then
        echo "  ⏱️  Uptime: $(docker inspect -f '{{.State.StartedAt}}' "$container_name" | xargs -I {} date -d {} +'%Y-%m-%d %H:%M:%S')"
    fi
}

# Send alert (email or webhook)
send_alert() {
    local message=$1
    log "🚨 ALERT: $message"
    
    # Send email if configured
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "Vietnam Stock Pipeline Alert" "$ALERT_EMAIL" 2>/dev/null || true
    fi
    
    # You can add webhook notification here (Slack, Discord, etc.)
    # curl -X POST -H 'Content-type: application/json' \
    #     --data "{\"text\":\"$message\"}" \
    #     YOUR_WEBHOOK_URL
}

# Main monitoring function
main() {
    echo "=========================================="
    echo "🔍 Monitoring Vietnam Stock Pipeline"
    echo "$(timestamp)"
    echo "=========================================="
    log "========== Monitoring Start =========="
    
    cd "$PROJECT_DIR"
    
    # List of critical containers
    CONTAINERS=(
        "zookeeper"
        "kafka"
        "postgres"
        "stock-producer"
        "kafka-consumer"
        "stock-dashboard"
    )
    
    # Optional containers
    OPTIONAL_CONTAINERS=(
        "spark-master"
        "spark-worker"
        "snowflake-sync"
        "pgadmin"
    )
    
    failed_containers=()
    unhealthy_containers=()
    
    echo ""
    echo "📦 Critical Services:"
    echo "--------------------"
    
    # Check critical containers
    for container in "${CONTAINERS[@]}"; do
        if ! check_container "$container"; then
            failed_containers+=("$container")
        else
            check_health "$container"
            get_uptime "$container"
        fi
        echo ""
    done
    
    echo "📦 Optional Services:"
    echo "--------------------"
    
    # Check optional containers
    for container in "${OPTIONAL_CONTAINERS[@]}"; do
        if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
            if ! check_container "$container"; then
                log "⚠️  Optional container $container is not running"
            else
                check_health "$container"
                get_uptime "$container"
            fi
            echo ""
        else
            echo -e "${YELLOW}⚠️  $container: Not deployed${NC}"
        fi
    done
    
    # Check disk space
    echo "💾 Disk Space:"
    echo "--------------------"
    df -h "$PROJECT_DIR" | tail -1
    echo ""
    
    # Check Docker volumes
    echo "📊 Docker Volumes:"
    echo "--------------------"
    docker volume ls --filter name=vietnam-stock-pipeline 2>/dev/null || true
    echo ""
    
    # Summary
    echo "=========================================="
    if [ ${#failed_containers[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ All critical services are running${NC}"
        log "✅ All critical services are running"
    else
        echo -e "${RED}❌ Failed containers: ${failed_containers[*]}${NC}"
        send_alert "Failed containers: ${failed_containers[*]}"
        
        # Auto-restart if systemd is managing the service
        if systemctl is-active --quiet vietnam-stock-pipeline; then
            log "🔄 Attempting to restart service via systemd..."
            echo "🔄 Attempting to restart service..."
            systemctl restart vietnam-stock-pipeline
        else
            log "🔄 Attempting to restart failed containers..."
            echo "🔄 Attempting to restart failed containers..."
            cd "$PROJECT_DIR"
            docker-compose up -d "${failed_containers[@]}"
        fi
    fi
    echo "=========================================="
    
    log "========== Monitoring End =========="
}

# Run main function
main "$@"

