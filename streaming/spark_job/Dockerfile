FROM apache/spark:3.5.0

# Switch to root to install packages
USER root

# Create app directory
RUN mkdir -p /opt/app

# Download and install required JARs to avoid runtime dependency resolution
RUN curl -L -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.0.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.0/spark-sql-kafka-0-10_2.12-3.5.0.jar

RUN curl -L -o /opt/spark/jars/kafka-clients-3.5.1.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar

RUN curl -L -o /opt/spark/jars/commons-pool2-2.12.0.jar \
    https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.12.0/commons-pool2-2.12.0.jar

RUN curl -L -o /opt/spark/jars/postgresql-42.7.3.jar \
    https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.3/postgresql-42.7.3.jar

# Additional Kafka integration JARs
RUN curl -L -o /opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.0.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.0/spark-token-provider-kafka-0-10_2.12-3.5.0.jar

RUN curl -L -o /opt/spark/jars/kafka-clients-3.5.1.jar \
    https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar

# Copy the streaming job
COPY structured_streaming_quotes.py /opt/app/structured_streaming_quotes.py

# Switch back to spark user
USER spark

# Set working directory
WORKDIR /opt/app

# Default command
CMD ["/bin/bash", "-lc", "/opt/spark/bin/spark-submit --master local[*] /opt/app/structured_streaming_quotes.py"]
