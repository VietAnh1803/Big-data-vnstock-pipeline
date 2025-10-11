#!/bin/bash

# Download necessary JAR files for Spark

cd /opt/spark/jars-extra

# Kafka SQL connector for Spark 3.5
wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.0/spark-sql-kafka-0-10_2.12-3.5.0.jar

# Kafka clients
wget -q https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar

# Spark Token provider for Kafka
wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.0/spark-token-provider-kafka-0-10_2.12-3.5.0.jar

# Commons Pool
wget -q https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar

# Snowflake JDBC and Spark connector
wget -q https://repo1.maven.org/maven2/net/snowflake/snowflake-jdbc/3.14.4/snowflake-jdbc-3.14.4.jar
wget -q https://repo1.maven.org/maven2/net/snowflake/spark-snowflake_2.12/2.12.0-spark_3.5/spark-snowflake_2.12-2.12.0-spark_3.5.jar

# PostgreSQL JDBC driver
wget -q https://jdbc.postgresql.org/download/postgresql-42.6.0.jar

echo "All JAR files downloaded successfully!"

