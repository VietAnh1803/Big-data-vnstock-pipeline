#!/bin/bash

# PostgreSQL Connection Helper Script
# Provides multiple ways to connect to PostgreSQL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  PostgreSQL Connection Helper             ${NC}"
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

# Function to check PostgreSQL status
check_postgres_status() {
    print_header
    print_info "Checking PostgreSQL status..."
    
    if docker ps | grep -q postgres; then
        print_success "PostgreSQL container is running"
        docker ps | grep postgres
    else
        print_error "PostgreSQL container is not running"
        return 1
    fi
    
    echo ""
    print_info "Port mapping:"
    docker port postgres 2>/dev/null || echo "No port mapping found"
}

# Function to connect via Docker exec
connect_via_docker() {
    print_header
    print_info "Connecting to PostgreSQL via Docker exec..."
    
    echo "Available databases:"
    docker exec postgres psql -U admin -l
    
    echo ""
    print_info "Connecting to stock_db..."
    docker exec -it postgres psql -U admin -d stock_db
}

# Function to show connection info
show_connection_info() {
    print_header
    print_info "PostgreSQL Connection Information:"
    echo ""
    echo "📊 Connection Details:"
    echo "   Host: localhost"
    echo "   Port: 5432"
    echo "   Database: stock_db"
    echo "   Username: admin"
    echo "   Password: admin"
    echo ""
    echo "🔗 Connection Strings:"
    echo "   psql: psql -h localhost -p 5432 -U admin -d stock_db"
    echo "   URL: postgresql://admin:admin@localhost:5432/stock_db"
    echo ""
    echo "🌐 Web Interfaces:"
    echo "   pgAdmin: http://localhost:5050"
    echo "   Dashboard: http://localhost:8501"
    echo ""
    echo "📋 Quick Commands:"
    echo "   List databases: docker exec postgres psql -U admin -l"
    echo "   Connect to DB: docker exec -it postgres psql -U admin -d stock_db"
    echo "   Show tables: docker exec postgres psql -U admin -d stock_db -c '\dt'"
}

# Function to install PostgreSQL client
install_postgres_client() {
    print_header
    print_info "Installing PostgreSQL client..."
    
    if command -v yum &> /dev/null; then
        print_info "Installing via yum..."
        sudo yum install -y postgresql15
    elif command -v apt-get &> /dev/null; then
        print_info "Installing via apt-get..."
        sudo apt-get update && sudo apt-get install -y postgresql-client
    else
        print_warning "Package manager not found. Please install PostgreSQL client manually."
        return 1
    fi
    
    print_success "PostgreSQL client installed!"
    print_info "You can now use: psql -h localhost -p 5432 -U admin -d stock_db"
}

# Function to test connection
test_connection() {
    print_header
    print_info "Testing PostgreSQL connection..."
    
    # Test via Docker
    print_info "Testing via Docker exec..."
    if docker exec postgres psql -U admin -d stock_db -c "SELECT 1;" &>/dev/null; then
        print_success "Docker connection: OK"
    else
        print_error "Docker connection: FAILED"
    fi
    
    # Test port
    print_info "Testing port 5432..."
    if netstat -tlnp | grep -q ":5432 "; then
        print_success "Port 5432: LISTENING"
    else
        print_error "Port 5432: NOT LISTENING"
    fi
    
    # Test if psql client is available
    if command -v psql &> /dev/null; then
        print_info "Testing direct connection..."
        if timeout 5 psql -h localhost -p 5432 -U admin -d stock_db -c "SELECT 1;" &>/dev/null; then
            print_success "Direct connection: OK"
        else
            print_error "Direct connection: FAILED"
        fi
    else
        print_warning "psql client not installed. Use 'Install PostgreSQL client' option."
    fi
}

# Function to show database info
show_database_info() {
    print_header
    print_info "Database Information:"
    
    echo "📊 Database Size:"
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT 
            pg_size_pretty(pg_database_size('stock_db')) as database_size;
    "
    
    echo ""
    echo "📋 Tables:"
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    "
    
    echo ""
    echo "📈 Record Counts:"
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT 
            'realtime_quotes' as table_name, 
            COUNT(*) as record_count,
            MIN(time) as earliest,
            MAX(time) as latest
        FROM realtime_quotes
        UNION ALL
        SELECT 
            'historical_prices' as table_name, 
            COUNT(*) as record_count,
            MIN(trading_date) as earliest,
            MAX(trading_date) as latest
        FROM historical_prices;
    "
}

# Main menu
show_menu() {
    print_header
    echo "Select an option:"
    echo "1. Check PostgreSQL status"
    echo "2. Connect via Docker exec"
    echo "3. Show connection information"
    echo "4. Install PostgreSQL client"
    echo "5. Test connection"
    echo "6. Show database info"
    echo "7. Exit"
    echo ""
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1) check_postgres_status ;;
        2) connect_via_docker ;;
        3) show_connection_info ;;
        4) install_postgres_client ;;
        5) test_connection ;;
        6) show_database_info ;;
        7) echo "Goodbye!"; exit 0 ;;
        *) print_error "Invalid choice. Please try again." ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

# Run main menu
show_menu
