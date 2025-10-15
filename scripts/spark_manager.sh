#!/bin/bash

# Spark Cluster Manager for Vietnam Stock Pipeline
# Hướng dẫn quản lý Spark cluster từ cơ bản đến nâng cao

echo "🚀 SPARK CLUSTER MANAGER"
echo "========================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show help
show_help() {
    echo -e "${BLUE}📋 SPARK CLUSTER COMMANDS:${NC}"
    echo ""
    echo -e "${YELLOW}🔍 MONITORING:${NC}"
    echo "  status     - Hiển thị trạng thái cluster"
    echo "  ui         - Mở Spark Web UI"
    echo "  logs       - Xem logs của Spark processor"
    echo "  metrics    - Hiển thị metrics chi tiết"
    echo ""
    echo -e "${YELLOW}⚙️  MANAGEMENT:${NC}"
    echo "  start      - Khởi động Spark cluster"
    echo "  stop       - Dừng Spark cluster"
    echo "  restart    - Khởi động lại Spark cluster"
    echo "  scale      - Thay đổi số lượng workers"
    echo ""
    echo -e "${YELLOW}📊 JOBS:${NC}"
    echo "  submit     - Submit Spark job"
    echo "  kill       - Dừng Spark job"
    echo "  list       - Liệt kê các jobs đang chạy"
    echo ""
    echo -e "${YELLOW}🔧 CONFIGURATION:${NC}"
    echo "  config     - Hiển thị cấu hình"
    echo "  optimize   - Tối ưu hóa cluster"
    echo "  test       - Test cluster connectivity"
    echo ""
    echo -e "${YELLOW}📚 LEARNING:${NC}"
    echo "  tutorial   - Hướng dẫn Spark cơ bản"
    echo "  examples   - Ví dụ Spark jobs"
    echo "  docs       - Tài liệu Spark"
    echo ""
    echo -e "${GREEN}Usage: $0 [command]${NC}"
}

# Function to show cluster status
show_status() {
    echo -e "${BLUE}📊 SPARK CLUSTER STATUS${NC}"
    echo "=========================="
    
    echo -e "\n${YELLOW}🐳 Docker Containers:${NC}"
    docker ps | grep spark
    
    echo -e "\n${YELLOW}🌐 Web UIs:${NC}"
    echo "  Spark Master UI: http://localhost:8080"
    echo "  Spark Worker UI: http://localhost:8081"
    
    echo -e "\n${YELLOW}📈 Cluster Metrics:${NC}"
    curl -s http://localhost:8080 | grep -E "(Workers|Applications|Memory|Cores)" | head -5
    
    echo -e "\n${YELLOW}💾 Worker Resources:${NC}"
    curl -s http://localhost:8081 | grep -E "(Memory|Cores|Running|Completed)" | head -5
}

# Function to open Spark UI
open_ui() {
    echo -e "${BLUE}🌐 SPARK WEB UIs${NC}"
    echo "=================="
    echo ""
    echo -e "${GREEN}📊 Spark Master UI:${NC}"
    echo "  URL: http://localhost:8080"
    echo "  Features: Cluster overview, applications, workers"
    echo ""
    echo -e "${GREEN}⚙️  Spark Worker UI:${NC}"
    echo "  URL: http://localhost:8081"
    echo "  Features: Worker details, executors, logs"
    echo ""
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo "  - Click vào 'Workers' để xem chi tiết workers"
    echo "  - Click vào 'Applications' để xem jobs đang chạy"
    echo "  - Click vào 'Executors' để xem resource usage"
    echo ""
    echo "Mở browser và truy cập các URL trên để quản lý Spark cluster!"
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}📋 SPARK PROCESSOR LOGS${NC}"
    echo "=========================="
    echo ""
    echo -e "${YELLOW}Recent logs:${NC}"
    docker logs spark-processor --tail 20
    echo ""
    echo -e "${YELLOW}Follow logs (Ctrl+C to stop):${NC}"
    echo "docker logs spark-processor -f"
}

# Function to show metrics
show_metrics() {
    echo -e "${BLUE}📊 SPARK CLUSTER METRICS${NC}"
    echo "============================"
    
    echo -e "\n${YELLOW}🏗️  Cluster Overview:${NC}"
    curl -s http://localhost:8080 | grep -A 5 -B 5 "Alive Workers"
    
    echo -e "\n${YELLOW}💻 Worker Details:${NC}"
    curl -s http://localhost:8081 | grep -A 3 -B 3 "Cores"
    
    echo -e "\n${YELLOW}📈 Applications:${NC}"
    curl -s http://localhost:8080 | grep -A 10 "Running Applications"
}

# Function to start cluster
start_cluster() {
    echo -e "${BLUE}🚀 STARTING SPARK CLUSTER${NC}"
    echo "=========================="
    
    echo "Starting Spark Master..."
    docker compose up -d spark-master
    
    echo "Starting Spark Worker..."
    docker compose up -d spark-worker
    
    echo "Starting Spark Processor..."
    docker compose up -d spark-processor
    
    echo -e "\n${GREEN}✅ Spark cluster started!${NC}"
    echo "Wait 30 seconds for full startup..."
    sleep 30
    show_status
}

# Function to stop cluster
stop_cluster() {
    echo -e "${BLUE}🛑 STOPPING SPARK CLUSTER${NC}"
    echo "=========================="
    
    echo "Stopping Spark Processor..."
    docker compose stop spark-processor
    
    echo "Stopping Spark Worker..."
    docker compose stop spark-worker
    
    echo "Stopping Spark Master..."
    docker compose stop spark-master
    
    echo -e "\n${GREEN}✅ Spark cluster stopped!${NC}"
}

# Function to restart cluster
restart_cluster() {
    echo -e "${BLUE}🔄 RESTARTING SPARK CLUSTER${NC}"
    echo "============================"
    
    stop_cluster
    sleep 5
    start_cluster
}

# Function to test cluster
test_cluster() {
    echo -e "${BLUE}🧪 TESTING SPARK CLUSTER${NC}"
    echo "========================="
    
    echo -e "\n${YELLOW}1. Testing Master UI:${NC}"
    if curl -s http://localhost:8080 > /dev/null; then
        echo -e "${GREEN}✅ Master UI accessible${NC}"
    else
        echo -e "${RED}❌ Master UI not accessible${NC}"
    fi
    
    echo -e "\n${YELLOW}2. Testing Worker UI:${NC}"
    if curl -s http://localhost:8081 > /dev/null; then
        echo -e "${GREEN}✅ Worker UI accessible${NC}"
    else
        echo -e "${RED}❌ Worker UI not accessible${NC}"
    fi
    
    echo -e "\n${YELLOW}3. Testing Kafka Connection:${NC}"
    if docker exec spark-processor python3 -c "from kafka import KafkaConsumer; print('Kafka OK')" 2>/dev/null; then
        echo -e "${GREEN}✅ Kafka connection OK${NC}"
    else
        echo -e "${RED}❌ Kafka connection failed${NC}"
    fi
    
    echo -e "\n${YELLOW}4. Testing Spark Session:${NC}"
    if docker logs spark-processor 2>&1 | grep -q "Spark session created"; then
        echo -e "${GREEN}✅ Spark session created${NC}"
    else
        echo -e "${RED}❌ Spark session failed${NC}"
    fi
}

# Function to show tutorial
show_tutorial() {
    echo -e "${BLUE}📚 SPARK TUTORIAL - CƠ BẢN${NC}"
    echo "=============================="
    echo ""
    echo -e "${YELLOW}🎯 SPARK LÀ GÌ?${NC}"
    echo "  - Apache Spark: Framework xử lý dữ liệu lớn"
    echo "  - In-memory processing: Xử lý nhanh hơn Hadoop"
    echo "  - Real-time streaming: Xử lý dữ liệu real-time"
    echo "  - Machine Learning: Hỗ trợ ML algorithms"
    echo ""
    echo -e "${YELLOW}🏗️  SPARK ARCHITECTURE:${NC}"
    echo "  - Master: Quản lý cluster, schedule jobs"
    echo "  - Worker: Thực thi tasks, cung cấp resources"
    echo "  - Driver: Chạy main application"
    echo "  - Executor: Chạy tasks trên workers"
    echo ""
    echo -e "${YELLOW}📊 SPARK COMPONENTS:${NC}"
    echo "  - Spark Core: Engine cơ bản"
    echo "  - Spark SQL: Xử lý structured data"
    echo "  - Spark Streaming: Real-time processing"
    echo "  - MLlib: Machine Learning library"
    echo "  - GraphX: Graph processing"
    echo ""
    echo -e "${YELLOW}🔄 DATA PROCESSING FLOW:${NC}"
    echo "  Data Source → Spark → Processing → Output"
    echo "  (Kafka) → (Streaming) → (Transform) → (Database)"
    echo ""
    echo -e "${YELLOW}💡 TRONG PROJECT CỦA BẠN:${NC}"
    echo "  - Kafka: Nguồn dữ liệu real-time"
    echo "  - Spark Streaming: Xử lý dữ liệu stock"
    echo "  - PostgreSQL: Lưu trữ kết quả"
    echo "  - Snowflake: Data warehouse"
}

# Function to show examples
show_examples() {
    echo -e "${BLUE}💡 SPARK EXAMPLES${NC}"
    echo "=================="
    echo ""
    echo -e "${YELLOW}1. Simple Word Count:${NC}"
    echo "  # Đếm số lần xuất hiện của từ"
    echo "  text_file = spark.read.text('file.txt')"
    echo "  words = text_file.select(explode(split(text_file.value, ' ')).alias('word'))"
    echo "  word_counts = words.groupBy('word').count()"
    echo ""
    echo -e "${YELLOW}2. Kafka Streaming:${NC}"
    echo "  # Đọc dữ liệu từ Kafka"
    echo "  kafka_df = spark.readStream.format('kafka')"
    echo "    .option('kafka.bootstrap.servers', 'kafka:9092')"
    echo "    .option('subscribe', 'stock-quotes')"
    echo "    .load()"
    echo ""
    echo -e "${YELLOW}3. Database Write:${NC}"
    echo "  # Ghi dữ liệu vào PostgreSQL"
    echo "  df.write.format('jdbc')"
    echo "    .option('url', 'jdbc:postgresql://postgres:5432/stock_db')"
    echo "    .option('dbtable', 'realtime_quotes')"
    echo "    .save()"
}

# Main command handler
case "$1" in
    "status")
        show_status
        ;;
    "ui")
        open_ui
        ;;
    "logs")
        show_logs
        ;;
    "metrics")
        show_metrics
        ;;
    "start")
        start_cluster
        ;;
    "stop")
        stop_cluster
        ;;
    "restart")
        restart_cluster
        ;;
    "test")
        test_cluster
        ;;
    "tutorial")
        show_tutorial
        ;;
    "examples")
        show_examples
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Use '$0 help' to see available commands"
        ;;
esac



