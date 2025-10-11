# 🌐 ACCESS ALL WEB UIs - Quick Guide

**Last Updated**: 2025-10-08  
**Status**: ✅ ALL RUNNING

---

## 🎯 AVAILABLE WEB INTERFACES

### 1. 📊 Streamlit Dashboard (Stock Market)
```
URL: http://localhost:8501
Purpose: Real-time stock market visualization
Features: 
  - Market overview & heatmap
  - Trends analysis (8 years)
  - Stock details with indicators
  - Auto-refresh every 3s
```

### 2. 🐘 pgAdmin (PostgreSQL UI)
```
URL: http://localhost:5050
Login: admin@example.com / admin
Purpose: PostgreSQL database management
Features:
  - Browse 2.55M stock records
  - Run SQL queries
  - Export data
  - Database admin tools
```

### 3. ⚡ Spark Master UI
```
URL: http://localhost:8080
Purpose: Monitor Spark cluster
Features:
  - View running applications
  - Worker nodes status
  - Execution metrics
```

### 4. ⚡ Spark Worker UI
```
URL: http://localhost:8081
Purpose: Monitor Spark worker
Features:
  - Worker resource usage
  - Executor logs
  - Task details
```

---

## 🔗 LOCAL ACCESS (From Server)

```bash
# Dashboard
http://localhost:8501

# pgAdmin
http://localhost:5050

# Spark Master
http://localhost:8080

# Spark Worker
http://localhost:8081
```

---

## 🔗 REMOTE ACCESS (SSH Tunnel)

### Forward All Ports (Recommended)

```bash
# Single command to forward all UIs
ssh -L 8501:localhost:8501 \
    -L 5050:localhost:5050 \
    -L 8080:localhost:8080 \
    -L 8081:localhost:8081 \
    oracle@10.0.0.7
```

**After connecting, access:**
- Dashboard: http://localhost:8501
- pgAdmin: http://localhost:5050
- Spark Master: http://localhost:8080
- Spark Worker: http://localhost:8081

### Or Use SSH Config

Add to `~/.ssh/config`:
```
Host stock
    HostName 10.0.0.7
    User oracle
    LocalForward 8501 localhost:8501  # Dashboard
    LocalForward 5050 localhost:5050  # pgAdmin
    LocalForward 8080 localhost:8080  # Spark Master
    LocalForward 8081 localhost:8081  # Spark Worker
```

Then just:
```bash
ssh stock
```

---

## 📊 QUICK COMPARISON

| UI | Purpose | Best For | Port |
|----|---------|----------|------|
| **Dashboard** | Stock visualization | Traders, analysts | 8501 |
| **pgAdmin** | Database management | Data engineers, admins | 5050 |
| **Spark Master** | Cluster monitoring | DevOps, troubleshooting | 8080 |
| **Spark Worker** | Worker monitoring | Performance tuning | 8081 |

---

## 🔐 SECURITY STATUS

All ports are **localhost-only** (127.0.0.1):

```
✅ 8501 - Dashboard      - Localhost only
✅ 5050 - pgAdmin        - Localhost only
✅ 8080 - Spark Master   - Localhost only
✅ 8081 - Spark Worker   - Localhost only
```

**Remote access REQUIRES SSH tunnel** ✅

---

## 🚀 COMMON WORKFLOWS

### For Traders/Analysts
```bash
# 1. SSH tunnel to dashboard only
ssh -L 8501:localhost:8501 oracle@10.0.0.7

# 2. Open browser
http://localhost:8501

# 3. Monitor real-time stocks
```

### For Data Engineers
```bash
# 1. SSH tunnel to dashboard + pgAdmin
ssh -L 8501:localhost:8501 -L 5050:localhost:5050 oracle@10.0.0.7

# 2. View data in dashboard
http://localhost:8501

# 3. Query database in pgAdmin
http://localhost:5050

# 4. Run SQL queries, export data
```

### For DevOps/Admins
```bash
# 1. SSH tunnel to all services
ssh -L 8501:localhost:8501 \
    -L 5050:localhost:5050 \
    -L 8080:localhost:8080 \
    -L 8081:localhost:8081 \
    oracle@10.0.0.7

# 2. Monitor everything:
# - Dashboard: http://localhost:8501
# - Database: http://localhost:5050
# - Spark: http://localhost:8080
# - Worker: http://localhost:8081
```

---

## 📱 MOBILE ACCESS

All UIs are responsive and work on mobile:

1. Setup SSH tunnel from mobile (Termius, JuiceSSH)
2. Forward ports 8501, 5050
3. Access via mobile browser
4. Dashboard works great on tablets!

---

## 🔍 TROUBLESHOOTING

### Cannot Access UI

```bash
# 1. Check container status
docker ps | grep -E "dashboard|pgadmin|spark"

# 2. Check if port is listening
sudo netstat -tuln | grep -E "8501|5050|8080|8081"

# 3. Test local access
curl http://localhost:8501
curl http://localhost:5050
curl http://localhost:8080
curl http://localhost:8081
```

### SSH Tunnel Not Working

```bash
# 1. Check SSH connection
ssh oracle@10.0.0.7 echo "Connected"

# 2. Check if port already in use locally
lsof -i :8501
lsof -i :5050

# 3. Kill process using port
kill -9 <PID>

# 4. Retry SSH tunnel
```

### UI Shows Error

```bash
# Check container logs
docker logs stock-dashboard --tail 50
docker logs pgadmin --tail 50
docker logs spark-master --tail 50
docker logs spark-worker --tail 50

# Restart if needed
docker-compose restart dashboard
docker-compose restart pgadmin
```

---

## ⚡ QUICK COMMANDS

```bash
# Check all UI status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | \
  grep -E "dashboard|pgadmin|spark"

# Restart all UIs
docker-compose restart dashboard pgadmin spark-master spark-worker

# View all UI logs
docker-compose logs -f dashboard pgadmin

# Stop all UIs (keep data)
docker-compose stop dashboard pgadmin spark-master spark-worker

# Start all UIs
docker-compose start dashboard pgadmin spark-master spark-worker
```

---

## 📚 DETAILED GUIDES

| UI | Guide |
|----|-------|
| Dashboard | `ACCESS_DASHBOARD.md` |
| pgAdmin | `PGADMIN_GUIDE.md` |
| Security | `SECURITY_GUIDE.md`, `SECURITY_QUICK_REF.md` |
| Full Docs | `README.md`, `INDEX.md` |

---

## 🎯 SUMMARY

**All Web UIs Ready!**

✅ **4 Web Interfaces** running
✅ **All secured** (localhost only)
✅ **SSH tunnel** for remote access
✅ **Full documentation** available
✅ **2.55M records** ready to explore

**Access Matrix**:
```
From Server:  http://localhost:[PORT]
From Remote:  SSH tunnel + http://localhost:[PORT]
```

---

**Last Verified**: 2025-10-08 09:54 UTC  
**All Services**: 🟢 RUNNING  
**Security Level**: 🟢 HIGH (Localhost only)


