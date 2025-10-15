#!/bin/bash

# Database Cleanup Script - Remove Empty Tables
# This script removes tables with 0 records to optimize database

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Database Cleanup - Remove Empty Tables   ${NC}"
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

# Function to check empty tables
check_empty_tables() {
    print_header
    print_info "Checking for empty tables..."
    
    echo ""
    echo "📊 Tables with 0 records:"
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT table_name, (xpath('/row/cnt/text()', xml_count))[1]::text::int AS row_count 
        FROM (
            SELECT table_name, 
                   query_to_xml(format('select count(*) as cnt from %I.%I', table_schema, table_name), false, true, '') AS xml_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        ) t 
        WHERE (xpath('/row/cnt/text()', xml_count))[1]::text::int = 0
        ORDER BY table_name;
    "
    
    echo ""
    echo "📈 Tables with data:"
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT table_name, (xpath('/row/cnt/text()', xml_count))[1]::text::int AS row_count 
        FROM (
            SELECT table_name, 
                   query_to_xml(format('select count(*) as cnt from %I.%I', table_schema, table_name), false, true, '') AS xml_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        ) t 
        WHERE (xpath('/row/cnt/text()', xml_count))[1]::text::int > 0
        ORDER BY (xpath('/row/cnt/text()', xml_count))[1]::text::int DESC;
    "
}

# Function to show table sizes
show_table_sizes() {
    print_header
    print_info "Table sizes and storage usage..."
    
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
    "
}

# Function to backup before cleanup
backup_database() {
    print_header
    print_info "Creating backup before cleanup..."
    
    backup_file="backup_before_cleanup_$(date +%Y%m%d_%H%M%S).sql"
    print_info "Backing up to: $backup_file"
    
    docker exec postgres pg_dump -U admin stock_db > "$backup_file"
    
    if [ -f "$backup_file" ]; then
        print_success "Backup created: $backup_file"
        print_info "Backup size: $(du -h "$backup_file" | cut -f1)"
    else
        print_error "Backup failed!"
        return 1
    fi
}

# Function to remove empty tables
remove_empty_tables() {
    print_header
    print_warning "This will remove ALL tables with 0 records!"
    print_warning "Make sure you have a backup before proceeding."
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_info "Operation cancelled."
        return 0
    fi
    
    print_info "Removing empty tables..."
    
    # Get list of empty tables
    empty_tables=$(docker exec postgres psql -U admin -d stock_db -t -c "
        SELECT table_name 
        FROM (
            SELECT table_name, 
                   query_to_xml(format('select count(*) as cnt from %I.%I', table_schema, table_name), false, true, '') AS xml_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        ) t 
        WHERE (xpath('/row/cnt/text()', xml_count))[1]::text::int = 0;
    " | tr -d ' ' | tr '\n' ' ')
    
    if [ -z "$empty_tables" ]; then
        print_info "No empty tables found."
        return 0
    fi
    
    print_info "Empty tables to remove: $empty_tables"
    
    # Remove each empty table
    for table in $empty_tables; do
        if [ -n "$table" ]; then
            print_info "Removing table: $table"
            docker exec postgres psql -U admin -d stock_db -c "DROP TABLE IF EXISTS $table CASCADE;"
            print_success "Removed: $table"
        fi
    done
    
    print_success "Cleanup completed!"
}

# Function to remove specific empty tables
remove_specific_tables() {
    print_header
    print_info "Remove specific empty tables..."
    
    # List of known empty tables
    empty_tables=(
        "company_news"
        "company_profiles" 
        "market_indicators"
        "balance_sheet"
        "income_statement"
        "cash_flow_statement"
        "financial_ratios"
        "trading_statistics"
        "company_events"
        "index_data"
        "insider_trading"
        "news_announcements"
        "market_indices"
        "financial_statements"
        "ownership_structure"
    )
    
    print_warning "Tables to be removed:"
    for table in "${empty_tables[@]}"; do
        echo "  - $table"
    done
    
    echo ""
    read -p "Remove these empty tables? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_info "Operation cancelled."
        return 0
    fi
    
    print_info "Removing specific empty tables..."
    
    for table in "${empty_tables[@]}"; do
        # Check if table exists and is empty
        count=$(docker exec postgres psql -U admin -d stock_db -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null || echo "0")
        count=$(echo $count | tr -d ' ')
        
        if [ "$count" = "0" ]; then
            print_info "Removing empty table: $table"
            docker exec postgres psql -U admin -d stock_db -c "DROP TABLE IF EXISTS $table CASCADE;"
            print_success "Removed: $table"
        else
            print_warning "Skipping $table (has $count records)"
        fi
    done
    
    print_success "Specific cleanup completed!"
}

# Function to optimize database after cleanup
optimize_database() {
    print_header
    print_info "Optimizing database after cleanup..."
    
    print_info "Running VACUUM ANALYZE..."
    docker exec postgres psql -U admin -d stock_db -c "VACUUM ANALYZE;"
    
    print_info "Checking database size..."
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT 
            pg_size_pretty(pg_database_size('stock_db')) as database_size;
    "
    
    print_success "Database optimization completed!"
}

# Function to show final status
show_final_status() {
    print_header
    print_info "Final database status..."
    
    echo ""
    echo "📊 Remaining tables:"
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT table_name, (xpath('/row/cnt/text()', xml_count))[1]::text::int AS row_count 
        FROM (
            SELECT table_name, 
                   query_to_xml(format('select count(*) as cnt from %I.%I', table_schema, table_name), false, true, '') AS xml_count 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        ) t 
        ORDER BY (xpath('/row/cnt/text()', xml_count))[1]::text::int DESC;
    "
    
    echo ""
    echo "💾 Database size:"
    docker exec postgres psql -U admin -d stock_db -c "
        SELECT pg_size_pretty(pg_database_size('stock_db')) as database_size;
    "
}

# Main menu
show_menu() {
    print_header
    echo "Select an option:"
    echo "1. Check empty tables"
    echo "2. Show table sizes"
    echo "3. Backup database"
    echo "4. Remove specific empty tables (recommended)"
    echo "5. Remove ALL empty tables (dangerous)"
    echo "6. Optimize database"
    echo "7. Show final status"
    echo "8. Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice
    
    case $choice in
        1) check_empty_tables ;;
        2) show_table_sizes ;;
        3) backup_database ;;
        4) remove_specific_tables ;;
        5) remove_empty_tables ;;
        6) optimize_database ;;
        7) show_final_status ;;
        8) echo "Goodbye!"; exit 0 ;;
        *) print_error "Invalid choice. Please try again." ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    show_menu
}

# Run main menu
show_menu
