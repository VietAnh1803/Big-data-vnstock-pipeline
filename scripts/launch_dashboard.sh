#!/bin/bash

# Dashboard Launcher Script
# Provides options to launch different dashboard versions

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Dashboard Launcher - Vietnam Stock        ${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header

# Check if dashboard container is running
if ! docker ps | grep -q stock-dashboard; then
    print_info "Starting dashboard container..."
    cd /u01/Vanh_projects/vietnam-stock-pipeline
    docker compose up -d stock-dashboard
    sleep 5
fi

print_info "Dashboard container is running"
print_info "Available dashboard options:"
echo ""
echo "1. Demo Dashboard (with sample data) - RECOMMENDED"
echo "2. Hybrid Dashboard (with database connection)"
echo "3. Simple Dashboard (basic version)"
echo "4. Check dashboard status"
echo "5. View dashboard logs"
echo "6. Exit"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        print_info "Launching Demo Dashboard..."
        docker exec stock-dashboard streamlit run demo_dashboard.py --server.port 8501 --server.address 0.0.0.0
        print_success "Demo Dashboard launched at http://localhost:8501"
        ;;
    2)
        print_info "Launching Hybrid Dashboard..."
        docker exec stock-dashboard streamlit run dashboard_hybrid.py --server.port 8501 --server.address 0.0.0.0
        print_success "Hybrid Dashboard launched at http://localhost:8501"
        ;;
    3)
        print_info "Launching Simple Dashboard..."
        docker exec stock-dashboard streamlit run simple_dashboard.py --server.port 8501 --server.address 0.0.0.0
        print_success "Simple Dashboard launched at http://localhost:8501"
        ;;
    4)
        print_info "Dashboard Status:"
        docker ps | grep stock-dashboard
        ;;
    5)
        print_info "Dashboard Logs:"
        docker logs stock-dashboard --tail 20
        ;;
    6)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

print_success "Dashboard launcher completed!"
