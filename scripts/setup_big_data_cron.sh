#!/bin/bash
# Setup cron jobs for BIG DATA pipeline
# Thiết lập cron jobs để fetch data tự động

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=================================================="
echo "  SETUP BIG DATA CRON JOBS"
echo "=================================================="
echo ""

# Create cron job script
cat > /tmp/big_data_fetch.sh << 'EOF'
#!/bin/bash
# Auto fetch data from vnstock

cd /u01/Vanh_projects/vietnam-stock-pipeline

# Log file
LOG_DIR=/var/log/vietnam-stock-pipeline
mkdir -p $LOG_DIR
LOG_FILE=$LOG_DIR/big_data_fetch_$(date +\%Y\%m\%d).log

echo "==================================================" >> $LOG_FILE
echo "BIG DATA FETCH - $(date)" >> $LOG_FILE
echo "==================================================" >> $LOG_FILE

# Run data fetcher
docker compose --profile data-fetch up --build data-fetcher >> $LOG_FILE 2>&1

# Cleanup old logs (keep 30 days)
find $LOG_DIR -name "big_data_fetch_*.log" -mtime +30 -delete

echo "Completed at $(date)" >> $LOG_FILE
EOF

chmod +x /tmp/big_data_fetch.sh
sudo mv /tmp/big_data_fetch.sh /usr/local/bin/

echo "✅ Created fetch script at /usr/local/bin/big_data_fetch.sh"
echo ""

# Setup cron jobs
echo "Setting up cron jobs..."
echo ""

# Create crontab entries
CRON_ENTRIES="# Vietnam Stock Pipeline - BIG DATA Cron Jobs
# Fetch all data weekly (every Sunday at 2 AM)
0 2 * * 0 /usr/local/bin/big_data_fetch.sh

# Fetch ticker info daily (every day at 1 AM)
0 1 * * * cd /u01/Vanh_projects/vietnam-stock-pipeline && docker compose --profile data-fetch run --rm data-fetcher python -c \"from fetch_all_data import fetch_ticker_info; fetch_ticker_info()\"

# Cleanup old Docker images monthly (first day of month at 3 AM)
0 3 1 * * docker system prune -af --filter \"until=720h\"
"

# Add to crontab
(crontab -l 2>/dev/null | grep -v "Vietnam Stock Pipeline - BIG DATA"; echo "$CRON_ENTRIES") | crontab -

echo "✅ Cron jobs installed:"
echo ""
crontab -l | grep -A 10 "Vietnam Stock Pipeline - BIG DATA"
echo ""

echo "=================================================="
echo "✅ BIG DATA CRON SETUP COMPLETED!"
echo "=================================================="
echo ""
echo "Scheduled jobs:"
echo "  • Weekly full fetch:  Sunday 2:00 AM"
echo "  • Daily ticker update: Every day 1:00 AM"  
echo "  • Monthly cleanup:    1st day 3:00 AM"
echo ""
echo "Logs: /var/log/vietnam-stock-pipeline/"
echo ""

