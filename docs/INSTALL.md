# 📦 Installation Guide - Vietnam Stock Pipeline

Hướng dẫn cài đặt đầy đủ cho Vietnam Stock Pipeline với các tùy chọn khác nhau.

## 🚀 **Quick Start (Recommended)**

### 1. Cài đặt nhanh (Minimal):
```bash
# Clone repository
git clone <repository-url>
cd vietnam-stock-pipeline

# Install minimal dependencies
pip install -r requirements-minimal.txt

# Start system
./manage.sh start
```

### 2. Cài đặt đầy đủ (Complete):
```bash
# Install all dependencies
pip install -r requirements.txt

# Start system
./manage.sh start
```

## 📋 **Requirements Files Overview**

| File | Purpose | Packages | Size | Use Case |
|------|---------|----------|------|----------|
| `requirements-minimal.txt` | Core functionality | 12 | ~500MB | Quick setup, basic features |
| `requirements.txt` | Complete system | 50+ | ~2GB | Full features, development |
| `requirements-dev.txt` | Development tools | 20+ | ~1GB | Testing, debugging, quality |
| `requirements-production.txt` | Production optimized | 40+ | ~1.5GB | Production deployment |

## 🔧 **System Requirements**

### **Minimum Requirements:**
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **Python**: 3.10+
- **RAM**: 4GB
- **Disk**: 5GB free space
- **Network**: Internet connection for data fetching

### **Recommended Requirements:**
- **OS**: Linux (Ubuntu 22.04+)
- **Python**: 3.11+
- **RAM**: 8GB+
- **Disk**: 20GB+ free space
- **CPU**: 4+ cores

## 📦 **Installation Options**

### **Option 1: Minimal Installation (Fastest)**
```bash
# For basic dashboard and data fetching
pip install -r requirements-minimal.txt
```

**Includes:**
- ✅ Streamlit Dashboard
- ✅ PostgreSQL connectivity
- ✅ VNStock API integration
- ✅ Basic data processing
- ✅ Kafka messaging

### **Option 2: Complete Installation (Recommended)**
```bash
# For full features and development
pip install -r requirements.txt
```

**Includes:**
- ✅ All minimal features
- ✅ Snowflake integration
- ✅ Spark processing
- ✅ Technical analysis
- ✅ Machine learning tools
- ✅ Advanced monitoring

### **Option 3: Development Installation**
```bash
# For development and testing
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Includes:**
- ✅ All complete features
- ✅ Testing frameworks
- ✅ Code quality tools
- ✅ Documentation tools
- ✅ Debugging tools

### **Option 4: Production Installation**
```bash
# For production deployment
pip install -r requirements-production.txt
```

**Includes:**
- ✅ Optimized packages
- ✅ Security tools
- ✅ Monitoring tools
- ✅ Performance optimization
- ✅ Process management

## 🐳 **Docker Installation (Recommended for Production)**

### **Using Docker Compose:**
```bash
# Clone repository
git clone <repository-url>
cd vietnam-stock-pipeline

# Start all services
docker compose up -d

# Check status
docker compose ps
```

### **Manual Docker Build:**
```bash
# Build dashboard
docker build -t stock-dashboard ./dashboard

# Build ETL services
docker build -t vnstock-fetcher ./etl

# Run services
docker run -d --name dashboard -p 8501:8501 stock-dashboard
docker run -d --name fetcher vnstock-fetcher
```

## 🔧 **System Dependencies**

### **Ubuntu/Debian:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
    python3.10 \
    python3.10-pip \
    python3.10-venv \
    build-essential \
    wget \
    curl \
    git \
    postgresql-client \
    openjdk-11-jdk

# Install TA-Lib
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
```

### **macOS:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 postgresql openjdk@11 ta-lib

# Install Python packages
pip3 install -r requirements.txt
```

### **Windows:**
```powershell
# Install Python 3.10+ from python.org
# Install Visual Studio Build Tools
# Install PostgreSQL

# Install TA-Lib
pip install --find-links https://www.lfd.uci.edu/~gohlke/pythonlibs/ ta-lib

# Install other packages
pip install -r requirements.txt
```

## 🗄️ **Database Setup**

### **PostgreSQL:**
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb stock_db

# Create user
sudo -u postgres createuser --interactive

# Restore data (if available)
psql -U admin -d stock_db < data/stock_db_full.sql
```

### **Snowflake (Optional):**
```bash
# Install Snowflake connector
pip install snowflake-connector-python

# Configure connection
export SNOWFLAKE_ACCOUNT="your-account"
export SNOWFLAKE_USER="your-user"
export SNOWFLAKE_PASSWORD="your-password"
```

## 🚀 **First Run**

### **1. Start Services:**
```bash
# Start all services
./manage.sh start

# Or using Makefile
make up
```

### **2. Check Status:**
```bash
# Check system status
./manage.sh status

# Or using Makefile
make status
```

### **3. Access Dashboard:**
- **Dashboard**: http://localhost:8501
- **pgAdmin**: http://localhost:5050

### **4. Start Data Fetching:**
```bash
# Start VNStock data fetcher
./etl/vnstock_manager.sh start

# Or using Makefile
make start-vnstock-fetcher
```

## 🔍 **Verification**

### **Check Installation:**
```bash
# Test Python packages
python -c "import streamlit, pandas, psycopg2, vnstock; print('✅ All packages installed')"

# Test database connection
python -c "import psycopg2; conn = psycopg2.connect('postgresql://admin:admin@localhost:5432/stock_db'); print('✅ Database connected')"

# Test VNStock API
python -c "import vnstock; print('✅ VNStock API available')"
```

### **Check Services:**
```bash
# Check Docker services
docker compose ps

# Check logs
docker compose logs

# Check specific service
docker compose logs dashboard
```

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **1. TA-Lib Installation Error:**
```bash
# Ubuntu/Debian
sudo apt install build-essential
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# macOS
brew install ta-lib

# Windows
pip install --find-links https://www.lfd.uci.edu/~gohlke/pythonlibs/ ta-lib
```

#### **2. PostgreSQL Connection Error:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check connection
psql -U admin -d stock_db -h localhost
```

#### **3. VNStock API Error:**
```bash
# Update VNStock
pip install --upgrade vnstock

# Test API
python -c "import vnstock; print(vnstock.listing_companies().head())"
```

#### **4. Docker Issues:**
```bash
# Clean Docker
docker system prune -a

# Rebuild containers
docker compose down
docker compose up -d --build
```

## 📊 **Performance Optimization**

### **For Large Datasets:**
```bash
# Increase PostgreSQL memory
# Edit postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### **For High Frequency Updates:**
```bash
# Use Redis for caching
pip install redis

# Configure Redis
export REDIS_URL="redis://localhost:6379"
```

## 🔒 **Security Setup**

### **Production Security:**
```bash
# Use environment variables
cp .env.example .env
# Edit .env with secure passwords

# Enable SSL
# Configure nginx with SSL certificates

# Set up firewall
sudo ufw allow 8501
sudo ufw allow 5432
sudo ufw enable
```

## 📞 **Support**

### **Getting Help:**
1. Check logs: `./manage.sh logs`
2. Check status: `./manage.sh status`
3. Check documentation: `README.md`
4. Check issues: GitHub Issues

### **Useful Commands:**
```bash
# System management
./manage.sh start|stop|status|logs

# VNStock fetcher
./etl/vnstock_manager.sh start|stop|status|logs

# Database operations
make backup|restore

# Cleanup
make clean
```

---

**🎯 Ready to go!** Your Vietnam Stock Pipeline is now installed and ready to use.

**Next steps:**
1. Start the system: `./manage.sh start`
2. Access dashboard: http://localhost:8501
3. Start data fetching: `./etl/vnstock_manager.sh start`
4. Monitor system: `./manage.sh status`
