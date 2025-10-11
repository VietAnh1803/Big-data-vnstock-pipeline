# 🌐 Dashboard Access Guide

**Last Updated**: 2025-10-08  
**Status**: ✅ Dashboard Running

---

## 🔗 Access URLs

### From Local Machine (Same Server)
```
http://localhost:8501
```

### From Other Machines (Network)
```
http://10.0.0.7:8501
```

### From Your Workstation
Replace `10.0.0.7` with your server IP or hostname:
```
http://<your-server-ip>:8501
```

---

## ✅ Current Status

**Dashboard Container**: ✅ Running
```
Container: stock-dashboard
Status: Up 13 minutes
Port: 0.0.0.0:8501 -> 8501/tcp
```

**Port Status**: ✅ Listening
```
tcp    0.0.0.0:8501    LISTEN
tcp6   :::8501         LISTEN
```

**HTTP Response**: ✅ 200 OK
```
HTTP/1.1 200 OK
Server: TornadoServer/6.5.2
Content-Type: text/html
```

---

## 🔍 Quick Checks

### Check if Dashboard is Running
```bash
docker ps | grep dashboard
```

Expected output:
```
stock-dashboard   Up XX minutes   0.0.0.0:8501->8501/tcp
```

### Check Dashboard Logs
```bash
docker logs stock-dashboard --tail 20
```

### Test Local Connection
```bash
curl http://localhost:8501
```

---

## 🚧 Firewall Configuration

If you're accessing from **another machine**, ensure port `8501` is open:

### Check Firewall Status
```bash
sudo firewall-cmd --list-ports
```

### Open Port (if needed)
```bash
# Temporary (until reboot)
sudo firewall-cmd --add-port=8501/tcp

# Permanent
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

### Alternative: iptables
```bash
# Check current rules
sudo iptables -L -n

# Add rule (if needed)
sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
```

---

## 🖥️ Accessing Dashboard

### Browser Recommendations
- ✅ Chrome/Chromium (Best performance)
- ✅ Firefox
- ✅ Edge
- ⚠️ Safari (May have WebSocket issues)

### Features Available
1. **Market Overview**
   - Heatmap of all stocks
   - Price distribution
   - Volume distribution
   - Top gainers/losers

2. **Trends Analysis**
   - Market trends over time
   - Stock comparison charts
   - Historical trends

3. **Stock Details**
   - MA5/MA10 indicators
   - RSI (Relative Strength Index)
   - Momentum analysis
   - Bullish/Bearish signals

### Auto-Refresh
Dashboard auto-refreshes every **3 seconds** by default.

---

## 🔧 Troubleshooting

### Cannot Access from Local Machine

**Problem**: `Connection refused` when accessing `http://localhost:8501`

**Solutions**:
1. Check if container is running:
   ```bash
   docker ps | grep dashboard
   ```

2. Restart dashboard:
   ```bash
   docker-compose restart dashboard
   ```

3. Check logs for errors:
   ```bash
   docker logs stock-dashboard
   ```

---

### Cannot Access from Remote Machine

**Problem**: Timeout when accessing `http://<server-ip>:8501`

**Solutions**:
1. **Check Server IP**:
   ```bash
   hostname -I
   ```
   Use the first IP address shown.

2. **Test from Server**:
   ```bash
   curl http://localhost:8501
   ```
   If this works, it's a network/firewall issue.

3. **Check Firewall**:
   ```bash
   sudo firewall-cmd --list-ports
   ```
   Should show `8501/tcp`.

4. **Open Port** (if not shown):
   ```bash
   sudo firewall-cmd --permanent --add-port=8501/tcp
   sudo firewall-cmd --reload
   ```

5. **Test Again**:
   ```bash
   telnet <server-ip> 8501
   # or
   nc -zv <server-ip> 8501
   ```

---

### Dashboard Shows "Connecting..."

**Problem**: Dashboard loads but shows "Connecting to server..."

**Solutions**:
1. **Check WebSocket Connection**:
   - Open browser DevTools (F12)
   - Look for WebSocket errors in Console

2. **Restart Dashboard**:
   ```bash
   docker-compose restart dashboard
   ```

3. **Check Database Connection**:
   ```bash
   docker logs stock-dashboard | grep -i error
   ```

---

### Dashboard Shows No Data

**Problem**: Dashboard loads but shows empty charts

**Solutions**:
1. **Check PostgreSQL**:
   ```bash
   docker exec -it postgres psql -U admin -d stock_db -c "SELECT COUNT(*) FROM realtime_quotes;"
   ```
   Should show 2,551,663+ records.

2. **Check Database Connection in Dashboard**:
   ```bash
   docker logs stock-dashboard | grep -i "database\|postgres"
   ```

3. **Restart Dashboard**:
   ```bash
   docker-compose restart dashboard
   ```

---

## 📱 Mobile Access

Dashboard is **mobile-responsive**. Access from your phone/tablet:

1. Ensure your device is on the **same network** as the server
2. Open browser and go to: `http://<server-ip>:8501`
3. For best experience, use landscape mode on tablets

---

## 🔐 Security Notes

**Current Setup**: Dashboard is **publicly accessible** on port 8501 (no authentication)

### Production Recommendations

1. **Add Authentication** (if needed):
   - Use Streamlit Cloud (with built-in auth)
   - Add nginx reverse proxy with basic auth
   - Use VPN for access

2. **Restrict Access by IP**:
   ```bash
   # Allow only specific IP
   sudo iptables -A INPUT -p tcp -s <allowed-ip> --dport 8501 -j ACCEPT
   sudo iptables -A INPUT -p tcp --dport 8501 -j DROP
   ```

3. **Use HTTPS** (recommended):
   - Set up nginx reverse proxy with SSL
   - Use Let's Encrypt for free SSL certificate

---

## 📊 Current Data

```
Total Records: 2,551,663
Unique Stocks: 1,558
Date Range: 2017-01-03 → 2025-10-08
Database Size: 570 MB
Update Status: ✅ UP TO DATE
```

---

## 🎯 Quick Links

- **Dashboard**: http://10.0.0.7:8501
- **Server IP**: 10.0.0.7
- **Port**: 8501
- **Protocol**: HTTP (WebSocket enabled)

---

**Need Help?** Check the logs:
```bash
docker logs stock-dashboard --follow
```

**Stop Dashboard**:
```bash
docker-compose stop dashboard
```

**Start Dashboard**:
```bash
docker-compose start dashboard
```

**Rebuild Dashboard** (if code changed):
```bash
docker-compose up -d --build dashboard
```



