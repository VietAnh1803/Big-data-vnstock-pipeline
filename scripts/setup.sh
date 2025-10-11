#!/bin/bash

# Setup script for Vietnam Stock Pipeline
# This script helps with initial setup and validation

set -e

echo "=================================="
echo "Vietnam Stock Pipeline Setup"
echo "=================================="
echo ""

# Run comprehensive requirements check
if [ -f "./scripts/check-requirements.sh" ]; then
    echo "Running comprehensive requirements check..."
    echo ""
    ./scripts/check-requirements.sh
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "Requirements check failed. Please fix the issues above."
        exit 1
    fi
    
    echo ""
    echo "=================================="
    echo "All requirements satisfied!"
    echo "=================================="
    echo ""
    exit 0
fi

echo "Note: Running basic checks (check-requirements.sh not found)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

print_info() {
    echo -e "→ $1"
}

# Check if Docker is installed
print_info "Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    print_success "Docker is installed: $DOCKER_VERSION"
else
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
print_info "Checking Docker Compose installation..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    print_success "Docker Compose is installed: $COMPOSE_VERSION"
else
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker daemon is running
print_info "Checking if Docker daemon is running..."
if docker info &> /dev/null; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
print_info "Checking environment configuration..."
if [ -f .env ]; then
    print_success ".env file exists"
else
    print_warning ".env file not found"
    print_info "Creating .env from .env.example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        print_success ".env file created"
        print_warning "Please edit .env file with your configuration before starting the system"
    else
        print_error ".env.example not found"
        exit 1
    fi
fi

# Validate required environment variables
print_info "Validating environment variables..."
source .env

if [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    print_error "PostgreSQL configuration is incomplete in .env file"
    exit 1
else
    print_success "PostgreSQL configuration is valid"
fi

# Check available disk space
print_info "Checking available disk space..."
AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
print_success "Available disk space: $AVAILABLE_SPACE"

# Check available memory
print_info "Checking available memory..."
if command -v free &> /dev/null; then
    TOTAL_MEM=$(free -h | awk 'NR==2 {print $2}')
    AVAILABLE_MEM=$(free -h | awk 'NR==2 {print $7}')
    print_success "Total memory: $TOTAL_MEM, Available: $AVAILABLE_MEM"
    
    # Check if we have at least 4GB available
    AVAILABLE_MEM_GB=$(free -g | awk 'NR==2 {print $7}')
    if [ "$AVAILABLE_MEM_GB" -lt 4 ]; then
        print_warning "Less than 4GB memory available. System may be slow."
    fi
fi

# Check for port conflicts
print_info "Checking for port conflicts..."
PORTS=(8501 8080 8081 9092 5432 2181)
CONFLICTS=0

for PORT in "${PORTS[@]}"; do
    if command -v netstat &> /dev/null; then
        if netstat -tuln | grep ":$PORT " &> /dev/null; then
            print_warning "Port $PORT is already in use"
            CONFLICTS=1
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln | grep ":$PORT " &> /dev/null; then
            print_warning "Port $PORT is already in use"
            CONFLICTS=1
        fi
    fi
done

if [ $CONFLICTS -eq 0 ]; then
    print_success "No port conflicts detected"
fi

echo ""
echo "=================================="
echo "Setup validation complete!"
echo "=================================="
echo ""

if [ $CONFLICTS -eq 1 ]; then
    print_warning "Some ports are already in use. You may need to stop conflicting services."
    echo ""
fi

echo "Next steps:"
echo "1. Review and edit .env file with your configuration"
echo "2. Run: docker-compose up -d --build"
echo "3. Wait 2-3 minutes for all services to start"
echo "4. Access dashboard at: http://localhost:8501"
echo ""
echo "For more information, see README.md"

