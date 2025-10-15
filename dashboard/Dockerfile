FROM python:3.10-slim

WORKDIR /app

# System deps for building some wheels (e.g., cryptography, TA-Lib wrappers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    cargo \
    curl \
    wget \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    ( \
      cd /tmp && \
      wget -q https://deac-riga.dl.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz && \
      tar -xzf ta-lib-0.4.0-src.tar.gz && \
      cd ta-lib && \
      ./configure --prefix=/usr && make && make install \
    ) || true && \
    (pip install --no-cache-dir ta-lib==0.4.28) || true

# Copy application code (from root context)
COPY dashboard/*.py ./
COPY dashboard/styles.css ./

# Expose Streamlit port
EXPOSE 8501

# Configure Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Run the dashboard
CMD ["streamlit", "run", "dashboard_hybrid.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--server.runOnSave=true", "--server.fileWatcherType=poll"]

