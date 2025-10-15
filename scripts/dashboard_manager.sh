#!/bin/bash

# Dashboard Manager Script
# Manages dashboard container and provides access options

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Dashboard Manager - Vietnam Stock        ${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check dashboard status
check_dashboard_status() {
    print_header
    print_info "Checking dashboard status..."
    
    if docker ps | grep -q stock-dashboard; then
        print_success "Dashboard container is running"
        docker ps | grep stock-dashboard
        
        # Test access
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
            print_success "Dashboard is accessible at http://localhost:8501"
        else
            print_warning "Dashboard container running but not accessible"
        fi
    else
        print_warning "Dashboard container is not running"
    fi
}

# Function to start dashboard
start_dashboard() {
    print_header
    print_info "Starting dashboard..."
    
    if docker ps | grep -q stock-dashboard; then
        print_warning "Dashboard is already running"
        return 0
    fi
    
    cd /u01/Vanh_projects/vietnam-stock-pipeline
    docker compose up -d stock-dashboard
    
    print_info "Waiting for dashboard to start..."
    sleep 10
    
    if docker ps | grep -q stock-dashboard; then
        print_success "Dashboard started successfully"
        print_info "Access at: http://localhost:8501"
    else
        print_error "Failed to start dashboard"
    fi
}

# Function to stop dashboard
stop_dashboard() {
    print_header
    print_info "Stopping dashboard..."
    
    if ! docker ps | grep -q stock-dashboard; then
        print_warning "Dashboard is not running"
        return 0
    fi
    
    docker stop stock-dashboard
    print_success "Dashboard stopped"
}

# Function to restart dashboard
restart_dashboard() {
    print_header
    print_info "Restarting dashboard..."
    
    stop_dashboard
    sleep 2
    start_dashboard
}

# Function to switch dashboard version
switch_dashboard() {
    print_header
    print_info "Switching dashboard version..."
    
    echo "Available dashboard versions:"
    echo "1. Demo Dashboard (with sample data) - RECOMMENDED"
    echo "2. Hybrid Dashboard (with database connection)"
    echo "3. Simple Dashboard (basic version)"
    echo "4. Current Dashboard (keep running)"
    echo ""
    
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            print_info "Switching to Demo Dashboard..."
            docker exec stock-dashboard pkill -f streamlit
            sleep 2
            docker exec -d stock-dashboard streamlit run demo_dashboard.py --server.port 8501 --server.address 0.0.0.0
            print_success "Demo Dashboard started"
            ;;
        2)
            print_info "Switching to Hybrid Dashboard..."
            docker exec stock-dashboard pkill -f streamlit
            sleep 2
            docker exec -d stock-dashboard streamlit run dashboard_hybrid.py --server.port 8501 --server.address 0.0.0.0
            print_success "Hybrid Dashboard started"
            ;;
        3)
            print_info "Switching to Simple Dashboard..."
            docker exec stock-dashboard pkill -f streamlit
            sleep 2
            docker exec -d stock-dashboard streamlit run simple_dashboard.py --server.port 8501 --server.address 0.0.0.0
            print_success "Simple Dashboard started"
            ;;
        4)
            print_info "Keeping current dashboard running"
            ;;
        *)
            print_error "Invalid choice"
            ;;
    esac
}

# Function to view dashboard logs
view_logs() {
    print_header
    print_info "Dashboard logs (last 20 lines):"
    docker logs stock-dashboard --tail 20
}

# Function to open dashboard in browser
open_dashboard() {
    print_header
    print_info "Opening dashboard in browser..."
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 | grep -q "200"; then
        print_success "Dashboard is accessible"
        print_info "Opening http://localhost:8501"
        
        # Try to open in browser (if available)
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:8501
        elif command -v open &> /dev/null; then
            open http://localhost:8501
        else
            print_info "Please open http://localhost:8501 in your browser"
        fi
    else
        print_error "Dashboard is not accessible"
        print_info "Please check dashboard status first"
    fi
}

# Function to show dashboard info
show_info() {
    print_header
    print_info "Dashboard Information:"
    echo ""
    echo "🌐 **Access URL:** http://localhost:8501"
    echo "📊 **Available Versions:**"
    echo "   - Demo Dashboard (sample data)"
    echo "   - Hybrid Dashboard (real data)"
    echo "   - Simple Dashboard (basic)"
    echo ""
    echo "🎛️ **Features:**"
    echo "   - Market Overview"
    echo "   - Individual Analysis"
    echo "   - Volume Analysis"
    echo "   - Real-time Updates"
    echo ""
    echo "🛠️ **Management:**"
    echo "   - Auto-refresh every 30s"
    echo "   - Interactive charts"
    echo "   - Responsive design"
    echo ""
    echo "📞 **Support:**"
    echo "   - Use this script for management"
    echo "   - Check logs for issues"
    echo "   - Restart if needed"
}

# Main menu
show_menu() {
    print_header
    echo "Select an option:"
    echo "1. Check dashboard status"
    echo "2. Start dashboard"
    echo "3. Stop dashboard"
    echo "4. Restart dashboard"
    echo "5. Switch dashboard version"
    echo "6. View dashboard logs"
    echo "7. Open dashboard in browser"
    echo "8. Show dashboard info"
    echo "9. Exit"
    echo ""
    read -p "Enter your choice (1-9): " choice
    
    case $choice in
        1) check_dashboard_status ;;
        2) start_dashboard ;;
        3) stop_dashboard ;;
        4) restart_dashboard ;;
        5) switch_dashboard ;;
        6) view_logs ;;
        7) open_dashboard ;;
        8) show_info ;;
        9) echo "Goodbye!"; exit 0 ;;
        *) print_error "Invalid choice. Please try again." ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

# Run main menu
show_menu



