#!/bin/bash

# Spark Job Submitter for Vietnam Stock Pipeline
# Hướng dẫn submit và quản lý Spark jobs

echo "🚀 SPARK JOB SUBMITTER"
echo "======================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to show help
show_help() {
    echo -e "${BLUE}📋 SPARK JOB COMMANDS:${NC}"
    echo ""
    echo -e "${YELLOW}📤 SUBMIT JOBS:${NC}"
    echo "  submit-simple    - Submit simple Spark job"
    echo "  submit-streaming - Submit streaming job"
    echo "  submit-sql       - Submit Spark SQL job"
    echo "  submit-ml        - Submit ML job"
    echo ""
    echo -e "${YELLOW}📊 MONITOR JOBS:${NC}"
    echo "  list-jobs        - List running jobs"
    echo "  job-status       - Check job status"
    echo "  job-logs         - View job logs"
    echo "  kill-job         - Kill running job"
    echo ""
    echo -e "${YELLOW}🧪 TEST JOBS:${NC}"
    echo "  test-wordcount   - Test word count job"
    echo "  test-pi          - Test Pi calculation"
    echo "  test-kafka       - Test Kafka streaming"
    echo ""
    echo -e "${GREEN}Usage: $0 [command]${NC}"
}

# Function to submit simple job
submit_simple() {
    echo -e "${BLUE}📤 SUBMITTING SIMPLE SPARK JOB${NC}"
    echo "================================"
    
    # Create a simple test job
    cat > /tmp/simple_spark_job.py << 'EOF'
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Create Spark session
spark = SparkSession.builder \
    .appName("SimpleTestJob") \
    .getOrCreate()

# Create sample data
data = [("VIC", 100.5), ("VCB", 95.2), ("VHM", 88.7), ("HPG", 45.3)]
df = spark.createDataFrame(data, ["ticker", "price"])

# Show data
print("=== Sample Stock Data ===")
df.show()

# Calculate statistics
print("=== Price Statistics ===")
df.select(
    avg("price").alias("avg_price"),
    max("price").alias("max_price"),
    min("price").alias("min_price"),
    count("ticker").alias("total_tickers")
).show()

spark.stop()
EOF

    echo "Submitting simple job..."
    docker exec spark-master /opt/spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --deploy-mode client \
        /tmp/simple_spark_job.py
    
    echo -e "\n${GREEN}✅ Simple job submitted!${NC}"
}

# Function to submit streaming job
submit_streaming() {
    echo -e "${BLUE}📤 SUBMITTING STREAMING JOB${NC}"
    echo "=============================="
    
    # Create streaming job
    cat > /tmp/streaming_job.py << 'EOF'
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Create Spark session
spark = SparkSession.builder \
    .appName("StockStreamingJob") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
    .getOrCreate()

# Read from Kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "stock-quotes") \
    .option("startingOffsets", "latest") \
    .load()

# Process data
processed_df = kafka_df.select(
    col("key").cast("string").alias("ticker"),
    col("value").cast("string").alias("json_data"),
    col("timestamp").alias("kafka_timestamp")
)

# Write to console
query = processed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime='10 seconds') \
    .start()

print("Streaming job started...")
query.awaitTermination()
EOF

    echo "Submitting streaming job..."
    docker exec spark-master /opt/spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --deploy-mode client \
        --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 \
        /tmp/streaming_job.py
    
    echo -e "\n${GREEN}✅ Streaming job submitted!${NC}"
}

# Function to test word count
test_wordcount() {
    echo -e "${BLUE}🧪 TESTING WORD COUNT JOB${NC}"
    echo "============================"
    
    # Create word count job
    cat > /tmp/wordcount_job.py << 'EOF'
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Create Spark session
spark = SparkSession.builder \
    .appName("WordCountTest") \
    .getOrCreate()

# Sample text data
text_data = [
    "Vietnam Stock Market Analysis",
    "Stock prices are rising today",
    "Market analysis shows positive trends",
    "Stock market performance is good"
]

# Create DataFrame
df = spark.createDataFrame(text_data, ["text"])

# Word count
words = df.select(explode(split(col("text"), " ")).alias("word"))
word_counts = words.groupBy("word").count().orderBy(desc("count"))

print("=== Word Count Results ===")
word_counts.show()

spark.stop()
EOF

    echo "Running word count test..."
    docker exec spark-master /opt/spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --deploy-mode client \
        /tmp/wordcount_job.py
    
    echo -e "\n${GREEN}✅ Word count test completed!${NC}"
}

# Function to test Pi calculation
test_pi() {
    echo -e "${BLUE}🧪 TESTING PI CALCULATION${NC}"
    echo "============================"
    
    # Create Pi calculation job
    cat > /tmp/pi_job.py << 'EOF'
from pyspark.sql import SparkSession
import random

# Create Spark session
spark = SparkSession.builder \
    .appName("PiCalculation") \
    .getOrCreate()

sc = spark.sparkContext

# Pi calculation using Monte Carlo method
def inside(p):
    x, y = random.random(), random.random()
    return x*x + y*y < 1

# Calculate Pi
n = 100000
count = sc.parallelize(range(0, n)).filter(inside).count()
pi = 4.0 * count / n

print(f"Pi is roughly {pi}")

spark.stop()
EOF

    echo "Running Pi calculation..."
    docker exec spark-master /opt/spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --deploy-mode client \
        /tmp/pi_job.py
    
    echo -e "\n${GREEN}✅ Pi calculation completed!${NC}"
}

# Function to list jobs
list_jobs() {
    echo -e "${BLUE}📊 LISTING SPARK JOBS${NC}"
    echo "======================"
    
    echo -e "\n${YELLOW}Running Applications:${NC}"
    curl -s http://localhost:8080 | grep -A 10 "Running Applications"
    
    echo -e "\n${YELLOW}Completed Applications:${NC}"
    curl -s http://localhost:8080 | grep -A 10 "Completed Applications"
}

# Function to check job status
job_status() {
    echo -e "${BLUE}📈 JOB STATUS${NC}"
    echo "============="
    
    echo -e "\n${YELLOW}Cluster Status:${NC}"
    curl -s http://localhost:8080 | grep -E "(Workers|Applications|Memory|Cores)" | head -5
    
    echo -e "\n${YELLOW}Worker Status:${NC}"
    curl -s http://localhost:8081 | grep -E "(Memory|Cores|Running|Completed)" | head -5
}

# Main command handler
case "$1" in
    "submit-simple")
        submit_simple
        ;;
    "submit-streaming")
        submit_streaming
        ;;
    "test-wordcount")
        test_wordcount
        ;;
    "test-pi")
        test_pi
        ;;
    "list-jobs")
        list_jobs
        ;;
    "job-status")
        job_status
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo "Use '$0 help' to see available commands"
        ;;
esac


