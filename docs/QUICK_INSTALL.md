# 🚀 Quick Install Guide - Vietnam Stock Pipeline

Hướng dẫn cài đặt nhanh cho Linux và Windows.

## 🐧 **Linux (Ubuntu/Debian) - 5 phút**

### 1. Cài đặt system dependencies:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.10 python3.10-pip python3.10-venv build-essential wget curl git postgresql-client openjdk-11-jdk
```

### 2. Cài đặt TA-Lib (REQUIRED):
```bash
# Download and build TA-Lib
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
cd ..
rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
```

### 3. Cài đặt Python packages:
```bash
# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify installation:
```bash
python -c "import streamlit, pandas, psycopg2, vnstock, ta; print('✅ All packages installed successfully')"
```

---

## 🪟 **Windows - 10 phút**

### 1. Cài đặt system dependencies:

#### **Python 3.10+:**
- Download từ: https://python.org
- ✅ Check "Add Python to PATH" during installation

#### **Visual Studio Build Tools:**
- Download từ: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install "C++ build tools" workload

#### **PostgreSQL:**
- Download từ: https://postgresql.org/download/windows/
- Install với default settings
- Nhớ password cho user 'postgres'

#### **Java 11+:**
- Download từ: https://adoptium.net/
- Install và set JAVA_HOME environment variable

### 2. Cài đặt TA-Lib (REQUIRED):
```cmd
# Method 1: Pre-compiled wheel (recommended)
pip install --find-links https://www.lfd.uci.edu/~gohlke/pythonlibs/ ta-lib

# Method 2: Using conda (if you have Anaconda)
conda install -c conda-forge ta-lib
```

### 3. Cài đặt Python packages:
```cmd
# Open Command Prompt as Administrator

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install packages
pip install -r requirements.txt
```

### 4. Verify installation:
```cmd
python -c "import streamlit, pandas, psycopg2, vnstock, ta; print('✅ All packages installed successfully')"
```

---

## 🐳 **Docker (All Platforms) - 2 phút**

### 1. Install Docker Desktop:
- **Linux**: https://docs.docker.com/engine/install/
- **Windows**: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
- **macOS**: https://desktop.docker.com/mac/main/amd64/Docker.dmg

### 2. Start system:
```bash
# Clone repository
git clone <repository-url>
cd vietnam-stock-pipeline

# Start with Docker Compose
docker compose up -d
```

### 3. Access dashboard:
- **Dashboard**: http://localhost:8501
- **pgAdmin**: http://localhost:5050

---

## 🚀 **Start System**

### After installation, start the system:

```bash
# Start all services
./manage.sh start          # Linux/macOS
manage.sh start            # Windows (with Git Bash)
docker compose up -d       # Docker

# Check status
./manage.sh status

# Access dashboard
# http://localhost:8501
```

---

## 🔧 **Troubleshooting**

### **TA-Lib Installation Error:**
```bash
# Linux
sudo apt install build-essential
# Then retry TA-Lib installation

# Windows
# Use pre-compiled wheel from lfd.uci.edu
pip install --find-links https://www.lfd.uci.edu/~gohlke/pythonlibs/ ta-lib
```

### **PostgreSQL Connection Error:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql    # Linux
# Start PostgreSQL service          # Windows

# Check connection
psql -U postgres -h localhost
```

### **Memory Issues:**
- Close unnecessary applications
- Increase virtual memory (Windows)
- Use swap file (Linux)

### **Permission Errors (Linux):**
```bash
# Use virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Avoid using sudo with pip
pip install -r requirements.txt
```

---

## 📊 **System Requirements**

### **Minimum:**
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 10.15+
- **Python**: 3.10+
- **RAM**: 4GB
- **Disk**: 5GB free space

### **Recommended:**
- **OS**: Linux (Ubuntu 22.04+)
- **Python**: 3.11+
- **RAM**: 8GB+
- **Disk**: 20GB+ free space
- **CPU**: 4+ cores

---

## 🎯 **Next Steps**

1. **Start system**: `./manage.sh start`
2. **Access dashboard**: http://localhost:8501
3. **Start data fetching**: `./etl/vnstock_manager.sh start`
4. **Monitor system**: `./manage.sh status`

---

## 📞 **Support**

If you encounter issues:
1. Check logs: `./manage.sh logs`
2. Check status: `./manage.sh status`
3. Read full documentation: `README.md`, `INSTALL.md`
4. Check system requirements
5. Verify all dependencies are installed

**🎉 Ready to go!** Your Vietnam Stock Pipeline is now installed and ready to use.
