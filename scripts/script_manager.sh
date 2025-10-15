#!/bin/bash

# Script Manager - Quick access to all utility scripts
# Provides easy access to all organized scripts

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  Script Manager - Vietnam Stock Pipeline  ${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header

echo "Available scripts:"
echo ""
echo "📁 Root directory:"
echo "   ./manage.sh - Main system management"
echo ""
echo "📁 scripts/ directory:"
echo "   1. cleanup_workspace.sh - Clean workspace"
echo "   2. connect_postgres.sh - PostgreSQL connection"
echo "   3. cleanup_empty_tables.sh - Database cleanup"
echo "   4. cleanup_snowflake.sh - Snowflake cleanup"
echo "   5. manage_snowflake_credits.sh - Credits management"
echo "   6. optimize_snowflake.sh - Snowflake optimization"
echo ""
echo "Select a script to run:"
echo "1. Clean workspace"
echo "2. Connect to PostgreSQL"
echo "3. Clean database tables"
echo "4. Clean Snowflake"
echo "5. Manage Snowflake credits"
echo "6. Optimize Snowflake"
echo "7. Show all scripts"
echo "8. Exit"
echo ""

read -p "Enter your choice (1-8): " choice

case $choice in
    1) ./scripts/cleanup_workspace.sh ;;
    2) ./scripts/connect_postgres.sh ;;
    3) ./scripts/cleanup_empty_tables.sh ;;
    4) ./scripts/cleanup_snowflake.sh ;;
    5) ./scripts/manage_snowflake_credits.sh ;;
    6) ./scripts/optimize_snowflake.sh ;;
    7) 
        print_info "All available scripts:"
        find . -name "*.sh" -type f | sort
        ;;
    8) echo "Goodbye!"; exit 0 ;;
    *) echo "Invalid choice" ;;
esac
