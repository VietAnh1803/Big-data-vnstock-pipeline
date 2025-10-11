FROM apache/spark:3.5.0

USER root

# Install Python dependencies
COPY requirements.txt /opt/app/
RUN pip install --no-cache-dir -r /opt/app/requirements.txt

# Create jars directory
RUN mkdir -p /opt/spark/jars-extra

# Copy application code
COPY *.py /opt/app/
COPY download_jars.sh /opt/app/

# Download required JAR files
WORKDIR /opt/app
RUN chmod +x download_jars.sh && ./download_jars.sh

WORKDIR /opt/app

