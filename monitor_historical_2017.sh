#!/bin/bash

echo "🔍 MONITORING HISTORICAL DATA FETCH FROM 2017"
echo "=============================================="

while true; do
    echo ""
    echo "📊 Current Status: $(date)"
    echo "----------------------------------------"
    
    # Check if container is running
    if docker ps | grep -q historical-2017-fetcher; then
        echo "✅ Container is running"
        
        # Show container logs (last 10 lines)
        echo ""
        echo "📝 Recent logs:"
        docker logs --tail 10 historical-2017-fetcher
    else
        echo "❌ Container is not running"
        break
    fi
    
    # Show database statistics
    echo ""
    echo "📈 Database Statistics:"
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT 
            MIN(trading_date) as earliest_date,
            MAX(trading_date) as latest_date,
            COUNT(DISTINCT ticker) as total_tickers,
            COUNT(*) as total_records
        FROM historical_prices;
    " 2>/dev/null || echo "   Database not accessible"
    
    echo ""
    echo "⏳ Waiting 30 seconds..."
    sleep 30
done

echo ""
echo "🎉 Monitoring completed!"
