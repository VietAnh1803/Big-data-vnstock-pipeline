#!/bin/bash
################################################################################
# Setup Cron Jobs - Vietnam Stock Pipeline
# 
# This script sets up cron jobs to monitor and maintain the pipeline
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "⏰ Setting up Cron Jobs"
echo "=========================================="

# Get project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 Project directory: $PROJECT_DIR"

# Make scripts executable
chmod +x "$PROJECT_DIR/scripts/monitor_services.sh"

# Create cron job entries
CRON_FILE="/tmp/vietnam-stock-cron"

cat > "$CRON_FILE" << EOF
# Vietnam Stock Pipeline - Automated Monitoring & Maintenance
# Generated on $(date)

# Monitor services every 5 minutes
*/5 * * * * $PROJECT_DIR/scripts/monitor_services.sh >> /var/log/vietnam-stock-monitor-cron.log 2>&1

# Daily health check at 6 AM
0 6 * * * $PROJECT_DIR/scripts/monitor_services.sh >> /var/log/vietnam-stock-daily-check.log 2>&1

# Weekly restart to clear any memory leaks (Sunday 3 AM)
0 3 * * 0 systemctl restart vietnam-stock-pipeline >> /var/log/vietnam-stock-weekly-restart.log 2>&1

# Clean up old logs every month (1st day of month at 4 AM)
0 4 1 * * find /var/log -name "vietnam-stock-*.log" -mtime +30 -delete 2>&1

# Check disk space daily at 7 AM and alert if > 80%
0 7 * * * df -h /u01 | awk 'NR==2 {if (int(\$5) > 80) print "WARNING: Disk usage is " \$5}' | grep WARNING && echo "Disk space warning on Vietnam Stock Pipeline server" | mail -s "Disk Space Alert" ${ALERT_EMAIL:-root} || true

EOF

echo ""
echo "📝 Cron jobs to be installed:"
echo "-----------------------------"
cat "$CRON_FILE"
echo "-----------------------------"
echo ""

# Install cron jobs
echo "💾 Installing cron jobs..."

# Backup existing crontab
crontab -l > /tmp/crontab-backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

# Remove old vietnam-stock cron entries if they exist
(crontab -l 2>/dev/null | grep -v "vietnam-stock" | grep -v "Vietnam Stock Pipeline" || true) | crontab -

# Add new cron entries
(crontab -l 2>/dev/null; cat "$CRON_FILE") | crontab -

echo -e "${GREEN}✅ Cron jobs installed successfully${NC}"
echo ""

# Verify
echo "🔍 Current cron jobs:"
crontab -l | grep -i "vietnam" || echo "No Vietnam Stock cron jobs found"

echo ""
echo -e "${YELLOW}📌 Note:${NC}"
echo "  - Monitoring runs every 5 minutes"
echo "  - Daily health check at 6 AM"
echo "  - Weekly restart on Sunday at 3 AM"
echo "  - Old logs cleaned up monthly"
echo "  - Disk space checked daily at 7 AM"
echo ""
echo "To view logs:"
echo "  tail -f /var/log/vietnam-stock-monitor-cron.log"
echo ""

# Cleanup
rm -f "$CRON_FILE"

echo "✅ Setup complete!"

