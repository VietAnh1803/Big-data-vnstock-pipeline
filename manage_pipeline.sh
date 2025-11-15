#!/bin/bash
# Vietnam Stock Big Data Pipeline Management Script
# Senior Data Engineer Level - Complete Pipeline Management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Vietnam Stock Big Data Pipeline"
COMPOSE_FILE="docker-compose.yml"
LOG_DIR="./logs"
CHECKPOINT_DIR="./checkpoints"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}================================${NC}"
    echo -e "${CYAN} $1${NC}"
    echo -e "${CYAN}================================${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_status "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_status "Docker Compose is installed"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    print_status "Python 3 is installed"
    
    # Create necessary directories
    mkdir -p $LOG_DIR
    mkdir -p $CHECKPOINT_DIR
    print_status "Created necessary directories"
    
    print_status "All prerequisites are satisfied!"
}

# Function to build images
build_images() {
    print_header "Building Docker Images"
    
    print_status "Building Kafka Producer image..."
    docker-compose -f $COMPOSE_FILE build kafka-producer
    
    print_status "Building Spark Consumer image..."
    docker-compose -f $COMPOSE_FILE build spark-consumer
    
    print_status "Building Dashboard image..."
    docker-compose -f $COMPOSE_FILE build dashboard
    
    print_status "All images built successfully!"
}

# Function to start the pipeline
start_pipeline() {
    print_header "Starting Vietnam Stock Big Data Pipeline"
    
    print_status "Starting infrastructure services..."
    docker-compose -f $COMPOSE_FILE up -d zookeeper kafka postgres
    
    print_status "Waiting for services to be ready..."
    sleep 30
    
    print_status "Creating Kafka topics..."
    docker-compose -f $COMPOSE_FILE up kafka-topics
    
    print_status "Starting data processing services..."
    docker-compose -f $COMPOSE_FILE up -d kafka-producer spark-consumer
    
    print_status "Starting dashboard..."
    docker-compose -f $COMPOSE_FILE up -d dashboard
    
    print_status "Pipeline started successfully!"
    print_status "Dashboard available at: http://localhost:8501"
    print_status "Kafka available at: localhost:9092"
    print_status "PostgreSQL available at: localhost:5432"
}

# Function to stop the pipeline
stop_pipeline() {
    print_header "Stopping Vietnam Stock Big Data Pipeline"
    
    print_status "Stopping all services..."
    docker-compose -f $COMPOSE_FILE down
    
    print_status "Pipeline stopped successfully!"
}

# Function to restart the pipeline
restart_pipeline() {
    print_header "Restarting Vietnam Stock Big Data Pipeline"
    
    stop_pipeline
    sleep 5
    start_pipeline
}

# Function to show pipeline status
show_status() {
    print_header "Pipeline Status"
    
    echo -e "${BLUE}Service Status:${NC}"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    echo -e "${BLUE}Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    
    echo ""
    echo -e "${BLUE}Recent Logs:${NC}"
    echo "Kafka Producer:"
    docker-compose -f $COMPOSE_FILE logs --tail=5 kafka-producer
    echo ""
    echo "Spark Consumer:"
    docker-compose -f $COMPOSE_FILE logs --tail=5 spark-consumer
    echo ""
    echo "Dashboard:"
    docker-compose -f $COMPOSE_FILE logs --tail=5 dashboard
    echo ""
    echo "Spark UI Manager:"
    docker-compose -f $COMPOSE_FILE logs --tail=5 spark-ui-manager
    
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo -e "Spark UI: http://localhost:4040"
    echo -e "Dashboard: http://localhost:8501"
    echo -e "Kafka Topics: http://localhost:9092"
    echo -e "PostgreSQL: localhost:5432"
}

# Function to show logs
show_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        print_header "All Services Logs"
        docker-compose -f $COMPOSE_FILE logs -f
    else
        print_header "$service Logs"
        docker-compose -f $COMPOSE_FILE logs -f $service
    fi
}

# Function to clean up
cleanup() {
    print_header "Cleaning Up Pipeline"
    
    print_warning "This will remove all containers, volumes, and data. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Stopping all services..."
        docker-compose -f $COMPOSE_FILE down -v
        
        print_status "Removing images..."
        docker-compose -f $COMPOSE_FILE down --rmi all
        
        print_status "Cleaning up volumes..."
        docker volume prune -f
        
        print_status "Cleaning up networks..."
        docker network prune -f
        
        print_status "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to monitor pipeline
monitor_pipeline() {
    print_header "Pipeline Monitoring"
    
    while true; do
        clear
        print_header "Vietnam Stock Big Data Pipeline - Live Monitor"
        echo ""
        
        # Service status
        echo -e "${BLUE}Service Status:${NC}"
        docker-compose -f $COMPOSE_FILE ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
        
        echo ""
        
        # Resource usage
        echo -e "${BLUE}Resource Usage:${NC}"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
        
        echo ""
        
        # Recent activity
        echo -e "${BLUE}Recent Activity:${NC}"
        echo "Kafka Producer (last 3 lines):"
        docker-compose -f $COMPOSE_FILE logs --tail=3 kafka-producer 2>/dev/null || echo "No logs available"
        echo ""
        echo "Spark Consumer (last 3 lines):"
        docker-compose -f $COMPOSE_FILE logs --tail=3 spark-consumer 2>/dev/null || echo "No logs available"
        
        echo ""
        echo -e "${YELLOW}Press Ctrl+C to exit monitor${NC}"
        sleep 10
    done
}

# Function to show help
show_help() {
    print_header "Vietnam Stock Big Data Pipeline Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the entire pipeline"
    echo "  stop        Stop the entire pipeline"
    echo "  restart     Restart the entire pipeline"
    echo "  status      Show pipeline status"
    echo "  logs        Show logs (optionally specify service name)"
    echo "  monitor     Monitor pipeline in real-time"
    echo "  build       Build Docker images"
    echo "  cleanup     Clean up all resources (DESTRUCTIVE)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start the pipeline"
    echo "  $0 logs kafka-producer      # Show kafka-producer logs"
    echo "  $0 monitor                  # Monitor pipeline in real-time"
    echo ""
    echo "Service URLs:"
    echo "Spark UI: http://localhost:4040"
    echo "Dashboard: http://localhost:8501"
    echo "Kafka Topics: http://localhost:9092"
    echo "PostgreSQL: localhost:5432"
    echo ""
    echo "Services:"
    echo "  zookeeper         Kafka coordination"
    echo "  kafka             Message streaming platform"
    echo "  postgres          Data warehouse"
    echo "  kafka-producer    Data ingestion"
    echo "  spark-consumer    Big data processing"
    echo "  spark-ui-manager  Spark job and cluster management"
    echo "  dashboard         Real-time analytics"
    echo ""
    echo "Access Points:"
    echo "  Spark UI:        http://localhost:4040"
    echo "  Dashboard:       http://localhost:8501"
    echo "  Kafka:           localhost:9092"
    echo "  PostgreSQL:      localhost:5432"
    echo ""
}

# Main script logic
main() {
    case "${1:-help}" in
        "start")
            check_prerequisites
            build_images
            start_pipeline
            ;;
        "stop")
            stop_pipeline
            ;;
        "restart")
            restart_pipeline
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "monitor")
            monitor_pipeline
            ;;
        "build")
            check_prerequisites
            build_images
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"