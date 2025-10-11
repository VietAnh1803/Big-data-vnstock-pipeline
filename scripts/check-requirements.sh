#!/bin/bash

# ========================================
# Requirements Checker for Vietnam Stock Pipeline
# Checks all prerequisites before starting the system
# ========================================

# Don't exit on error - we want to check everything
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║        Vietnam Stock Pipeline - Requirements Check            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
    ((WARNINGS++))
}

print_info() {
    echo -e "${BLUE}→${NC} $1"
}

print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# ========================================
# 1. Check Operating System
# ========================================
print_header "1. Operating System"

OS_TYPE=$(uname -s)
OS_VERSION=$(uname -r)

print_info "OS Type: $OS_TYPE"
print_info "OS Version: $OS_VERSION"

if [[ "$OS_TYPE" == "Linux" ]] || [[ "$OS_TYPE" == "Darwin" ]]; then
    print_success "Operating system is supported"
else
    print_warning "OS may not be fully supported. Recommended: Linux or macOS"
fi

# ========================================
# 2. Check Docker
# ========================================
print_header "2. Docker"

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | awk '{print $3}' | sed 's/,//')
    print_info "Docker version: $DOCKER_VERSION"
    
    # Check if version is >= 20.10
    DOCKER_MAJOR=$(echo $DOCKER_VERSION | cut -d. -f1)
    DOCKER_MINOR=$(echo $DOCKER_VERSION | cut -d. -f2)
    
    if [ "$DOCKER_MAJOR" -ge 20 ] && [ "$DOCKER_MINOR" -ge 10 ]; then
        print_success "Docker version is sufficient (>= 20.10)"
    else
        print_warning "Docker version is old. Recommended: 20.10 or higher"
    fi
    
    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        print_success "Docker daemon is running"
        
        # Get Docker info
        DOCKER_MEM=$(docker info 2>/dev/null | grep "Total Memory" | awk '{print $3 $4}')
        DOCKER_CPUS=$(docker info 2>/dev/null | grep "CPUs" | awk '{print $2}')
        
        if [ ! -z "$DOCKER_MEM" ]; then
            print_info "Docker Memory: $DOCKER_MEM"
        fi
        
        if [ ! -z "$DOCKER_CPUS" ]; then
            print_info "Docker CPUs: $DOCKER_CPUS"
        fi
    else
        print_error "Docker daemon is not running. Please start Docker first."
    fi
else
    print_error "Docker is not installed. Please install Docker first."
    echo ""
    echo "  Installation guide: https://docs.docker.com/get-docker/"
fi

# ========================================
# 3. Check Docker Compose
# ========================================
print_header "3. Docker Compose"

if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | awk '{print $4}' | sed 's/,//')
    print_info "Docker Compose version: $COMPOSE_VERSION"
    
    # Check if version is >= 2.0
    COMPOSE_MAJOR=$(echo $COMPOSE_VERSION | cut -d. -f1)
    
    if [ "$COMPOSE_MAJOR" -ge 2 ]; then
        print_success "Docker Compose version is sufficient (>= 2.0)"
    else
        print_warning "Docker Compose version is old. Recommended: 2.0 or higher"
    fi
else
    print_error "Docker Compose is not installed. Please install Docker Compose."
    echo ""
    echo "  Installation guide: https://docs.docker.com/compose/install/"
fi

# ========================================
# 4. Check System Resources
# ========================================
print_header "4. System Resources"

# Check RAM
if command -v free &> /dev/null; then
    TOTAL_MEM_GB=$(free -g | awk 'NR==2 {print $2}')
    AVAILABLE_MEM_GB=$(free -g | awk 'NR==2 {print $7}')
    
    print_info "Total RAM: ${TOTAL_MEM_GB}GB"
    print_info "Available RAM: ${AVAILABLE_MEM_GB}GB"
    
    if [ "$TOTAL_MEM_GB" -ge 8 ]; then
        print_success "Total RAM is sufficient (>= 8GB)"
    else
        print_warning "Total RAM is less than 8GB. System may be slow."
    fi
    
    if [ "$AVAILABLE_MEM_GB" -ge 4 ]; then
        print_success "Available RAM is sufficient (>= 4GB)"
    else
        print_warning "Available RAM is less than 4GB. Consider closing other applications."
    fi
elif command -v sysctl &> /dev/null; then
    # macOS
    TOTAL_MEM_BYTES=$(sysctl -n hw.memsize)
    TOTAL_MEM_GB=$((TOTAL_MEM_BYTES / 1024 / 1024 / 1024))
    
    print_info "Total RAM: ${TOTAL_MEM_GB}GB"
    
    if [ "$TOTAL_MEM_GB" -ge 8 ]; then
        print_success "Total RAM is sufficient (>= 8GB)"
    else
        print_warning "Total RAM is less than 8GB. System may be slow."
    fi
else
    print_warning "Cannot determine RAM. Please ensure you have at least 8GB."
fi

# Check CPU cores
if command -v nproc &> /dev/null; then
    CPU_CORES=$(nproc)
elif command -v sysctl &> /dev/null; then
    CPU_CORES=$(sysctl -n hw.ncpu)
else
    CPU_CORES="Unknown"
fi

print_info "CPU Cores: $CPU_CORES"

if [ "$CPU_CORES" != "Unknown" ] && [ "$CPU_CORES" -ge 4 ]; then
    print_success "CPU cores are sufficient (>= 4)"
elif [ "$CPU_CORES" != "Unknown" ]; then
    print_warning "CPU cores are less than 4. Recommended: 4 or more cores."
fi

# Check disk space
DISK_AVAILABLE=$(df -h . | awk 'NR==2 {print $4}')
DISK_AVAILABLE_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')

print_info "Available disk space: $DISK_AVAILABLE"

if [ "$DISK_AVAILABLE_GB" -ge 10 ]; then
    print_success "Disk space is sufficient (>= 10GB)"
else
    print_warning "Disk space is less than 10GB. May not be enough for Docker images."
fi

# ========================================
# 5. Check Port Availability
# ========================================
print_header "5. Port Availability"

REQUIRED_PORTS=(8501 8080 8081 9092 9093 5432 2181)
PORT_CONFLICTS=0

for PORT in "${REQUIRED_PORTS[@]}"; do
    if command -v netstat &> /dev/null; then
        if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
            print_error "Port $PORT is already in use"
            PORT_CONFLICTS=1
        else
            print_success "Port $PORT is available"
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln 2>/dev/null | grep -q ":$PORT "; then
            print_error "Port $PORT is already in use"
            PORT_CONFLICTS=1
        else
            print_success "Port $PORT is available"
        fi
    elif command -v lsof &> /dev/null; then
        if lsof -i :$PORT &> /dev/null; then
            print_error "Port $PORT is already in use"
            PORT_CONFLICTS=1
        else
            print_success "Port $PORT is available"
        fi
    else
        print_warning "Cannot check port $PORT (no netstat/ss/lsof available)"
        break
    fi
done

if [ $PORT_CONFLICTS -eq 0 ]; then
    echo ""
    print_info "All required ports are available"
fi

# ========================================
# 6. Check Project Files
# ========================================
print_header "6. Project Files"

REQUIRED_FILES=(
    "docker-compose.yml"
    "producer/producer.py"
    "producer/Dockerfile"
    "spark-processor/streaming_app.py"
    "spark-processor/Dockerfile"
    "dashboard/dashboard.py"
    "dashboard/Dockerfile"
    "init-scripts/01-init-db.sql"
)

for FILE in "${REQUIRED_FILES[@]}"; do
    if [ -f "$FILE" ]; then
        print_success "$FILE exists"
    else
        print_error "$FILE is missing"
    fi
done

# ========================================
# 7. Check Environment Configuration
# ========================================
print_header "7. Environment Configuration"

if [ -f ".env" ]; then
    print_success ".env file exists"
    
    # Check required variables
    REQUIRED_VARS=(
        "POSTGRES_DB"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "KAFKA_BOOTSTRAP_SERVERS"
        "KAFKA_TOPIC"
    )
    
    for VAR in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${VAR}=" .env; then
            VALUE=$(grep "^${VAR}=" .env | cut -d= -f2)
            if [ ! -z "$VALUE" ]; then
                print_success "$VAR is configured"
            else
                print_warning "$VAR is empty"
            fi
        else
            print_error "$VAR is not configured"
        fi
    done
    
    # Check Snowflake configuration (optional)
    if grep -q "^SNOWFLAKE_URL=" .env && [ ! -z "$(grep "^SNOWFLAKE_URL=" .env | cut -d= -f2)" ]; then
        print_info "Snowflake configuration detected"
        
        SNOWFLAKE_VARS=(
            "SNOWFLAKE_USER"
            "SNOWFLAKE_PASSWORD"
            "SNOWFLAKE_DATABASE"
            "SNOWFLAKE_WAREHOUSE"
        )
        
        for VAR in "${SNOWFLAKE_VARS[@]}"; do
            if grep -q "^${VAR}=" .env; then
                VALUE=$(grep "^${VAR}=" .env | cut -d= -f2)
                if [ ! -z "$VALUE" ] && [ "$VALUE" != "your_"* ]; then
                    print_success "$VAR is configured"
                else
                    print_warning "$VAR is not configured or using default value"
                fi
            fi
        done
    else
        print_info "Snowflake not configured (optional - system will work with PostgreSQL only)"
    fi
    
else
    print_error ".env file not found"
    print_info "Creating .env from .env.example..."
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created from .env.example"
        print_warning "Please edit .env file with your configuration"
    else
        print_error ".env.example not found"
    fi
fi

# ========================================
# 8. Check Network Connectivity
# ========================================
print_header "8. Network Connectivity"

# Check internet connection
if ping -c 1 8.8.8.8 &> /dev/null; then
    print_success "Internet connection is available"
else
    print_warning "Cannot verify internet connection. May have issues downloading images."
fi

# Check Docker Hub connectivity
if ping -c 1 hub.docker.com &> /dev/null; then
    print_success "Docker Hub is reachable"
else
    print_warning "Cannot reach Docker Hub. May have issues pulling images."
fi

# ========================================
# 9. Check Python (Optional)
# ========================================
print_header "9. Python (Optional - for local development)"

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_info "Python version: $PYTHON_VERSION"
    print_success "Python 3 is installed"
else
    print_info "Python 3 not found (not required - runs in Docker)"
fi

# ========================================
# 10. Check Git (Optional)
# ========================================
print_header "10. Git (Optional)"

if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    print_info "Git version: $GIT_VERSION"
    print_success "Git is installed"
else
    print_info "Git not found (optional)"
fi

# ========================================
# Summary
# ========================================
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                         SUMMARY                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

print_info "Checks passed: $PASSED"
if [ $FAILED -gt 0 ]; then
    print_info "Checks failed: $FAILED"
fi
if [ $WARNINGS -gt 0 ]; then
    print_info "Warnings: $WARNINGS"
fi

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical requirements are met!${NC}"
    echo ""
    echo "You can now start the pipeline:"
    echo "  docker-compose up -d --build"
    echo ""
    
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}Note: There are some warnings. The system should work but may not be optimal.${NC}"
        echo ""
    fi
    
    exit 0
else
    echo -e "${RED}✗ Some critical requirements are not met.${NC}"
    echo ""
    echo "Please fix the errors above before starting the pipeline."
    echo ""
    
    if [ $FAILED -eq 1 ] && ! command -v docker &> /dev/null; then
        echo "Quick fix: Install Docker"
        echo "  https://docs.docker.com/get-docker/"
    fi
    
    if [ $FAILED -eq 1 ] && ! command -v docker-compose &> /dev/null; then
        echo "Quick fix: Install Docker Compose"
        echo "  https://docs.docker.com/compose/install/"
    fi
    
    echo ""
    exit 1
fi
