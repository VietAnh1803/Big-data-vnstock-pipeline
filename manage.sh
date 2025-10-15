#!/bin/bash

# Vietnam Stock Pipeline - Management Script
# Script quản lý đơn giản cho toàn bộ hệ thống

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/u01/Vanh_projects/vietnam-stock-pipeline"

# Functions
print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Vietnam Stock Pipeline - Management      ${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Start all services
start_all() {
    print_header
    print_info "Starting Vietnam Stock Pipeline..."
    
    check_docker
    cd "$PROJECT_DIR"
    
    docker compose up -d
    print_success "All services started!"
    print_info "Dashboard: http://localhost:8501"
    print_info "pgAdmin: http://localhost:5050"
}

# Stop all services
stop_all() {
    print_header
    print_info "Stopping Vietnam Stock Pipeline..."
    
    check_docker
    cd "$PROJECT_DIR"
    
    docker compose down
    print_success "All services stopped!"
}

# Show status
show_status() {
    print_header
    print_info "System Status:"
    
    check_docker
    cd "$PROJECT_DIR"
    
    echo ""
    docker compose ps
}

# Show logs
show_logs() {
    print_header
    print_info "System Logs:"
    
    check_docker
    cd "$PROJECT_DIR"
    
    docker compose logs --tail=50
}

# Start VNStock data fetcher
start_vnstock() {
    print_header
    print_info "Starting VNStock Data Fetcher..."
    
    check_docker
    cd "$PROJECT_DIR"
    
    docker compose --profile vnstock-server up -d --build vnstock-server
    print_success "VNStock fetcher started!"
    print_info "Logs: docker compose --profile vnstock-server logs -f vnstock-server"
}

# Stop VNStock data fetcher
stop_vnstock() {
    print_header
    print_info "Stopping VNStock Data Fetcher..."
    
    check_docker
    cd "$PROJECT_DIR"
    
    docker compose --profile vnstock-server down vnstock-server
    print_success "VNStock fetcher stopped!"
}

# Clean up
cleanup() {
    print_header
    print_info "Cleaning up system..."
    
    check_docker
    cd "$PROJECT_DIR"
    
    docker compose down --volumes --remove-orphans
    docker system prune -f
    print_success "Cleanup completed!"
}

# Show help
show_help() {
    print_header
    echo "Usage: $0 {start|stop|status|logs|vnstock-start|vnstock-stop|cleanup|help}"
    echo ""
    echo "Commands:"
    echo "  start         - Start all services"
    echo "  stop          - Stop all services"
    echo "  status        - Show system status"
    echo "  logs          - Show system logs"
    echo "  vnstock-start - Start VNStock data fetcher"
    echo "  vnstock-stop  - Stop VNStock data fetcher"
    echo "  cleanup       - Clean up containers and images"
    echo "  help          - Show this help message"
    echo ""
    echo "Services:"
    echo "  - PostgreSQL Database"
    echo "  - Kafka Message Broker"
    echo "  - Streamlit Dashboard"
    echo "  - pgAdmin Web UI"
    echo "  - VNStock Data Fetcher (optional)"
    echo ""
    echo "Access URLs:"
    echo "  - Dashboard: http://localhost:8501"
    echo "  - pgAdmin: http://localhost:5050"
}

# Main script logic
case "$1" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    vnstock-start)
        start_vnstock
        ;;
    vnstock-stop)
        stop_vnstock
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Invalid command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac