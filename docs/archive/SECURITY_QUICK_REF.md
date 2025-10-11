# 🔐 SECURITY QUICK REFERENCE

## 🚨 ĐÃ APPLIED (Secure by default)

✅ **Docker Ports**: Tất cả ports chỉ bind `127.0.0.1` (localhost only)
✅ **No External Exposure**: Không có service nào exposed ra internet
✅ **Network Isolation**: All services trong private Docker network

---

## 🔗 TRUY CẬP DASHBOARD

### Từ Server (Local)
```bash
http://localhost:8501
```

### Từ Máy Khác (Remote) - PHẢI DÙNG SSH TUNNEL

#### Option 1: Manual SSH Tunnel
```bash
# Trên máy bạn (laptop/desktop):
ssh -L 8501:localhost:8501 oracle@10.0.0.7

# Sau đó mở browser:
http://localhost:8501
```

#### Option 2: Dùng Script (Đã có sẵn)
```bash
# Download script về máy:
scp oracle@10.0.0.7:/u01/Vanh_projects/vietnam-stock-pipeline/scripts/ssh-tunnel.sh .

# Chạy:
./ssh-tunnel.sh 10.0.0.7 oracle
```

#### Option 3: SSH Config (Tiện lợi nhất)
Thêm vào `~/.ssh/config` trên máy bạn:
```
Host stock-server
    HostName 10.0.0.7
    User oracle
    LocalForward 8501 localhost:8501
    LocalForward 8080 localhost:8080  # Spark UI (optional)
    LocalForward 8081 localhost:8081  # Spark Worker UI (optional)
```

Sau đó chỉ cần:
```bash
ssh stock-server
# Dashboard tự động available tại http://localhost:8501
```

---

## 🛡️ BẢO MẬT CƠ BẢN ĐÃ CÓ

| Service | Port | Binding | Status |
|---------|------|---------|--------|
| Dashboard | 8501 | 127.0.0.1 | ✅ Secure |
| PostgreSQL | 5432 | 127.0.0.1 | ✅ Secure |
| Kafka | 9092, 9093 | 127.0.0.1 | ✅ Secure |
| Spark Master | 8080, 7077 | 127.0.0.1 | ✅ Secure |
| Spark Worker | 8081 | 127.0.0.1 | ✅ Secure |
| Zookeeper | 2181 | 127.0.0.1 | ✅ Secure |

---

## ⚡ QUICK COMMANDS

### Check Security Status
```bash
# Check port bindings
docker ps | grep -E "stock|kafka|spark|postgres"

# Check listening ports
sudo netstat -tuln | grep -E "8501|5432|9092"

# Should see "127.0.0.1:PORT" NOT "0.0.0.0:PORT"
```

### Restart with Security Config
```bash
cd /u01/Vanh_projects/vietnam-stock-pipeline
docker-compose down
docker-compose up -d
```

### Run Security Setup (Interactive)
```bash
./scripts/secure-setup.sh
```

---

## 🔐 MẬT KHẨU

### Mật khẩu hiện tại (THAY ĐỔI NGAY!)
```
PostgreSQL: admin (⚠️ WEAK)
Snowflake: [see .env] (⚠️ EXPOSED IN CODE)
```

### Tạo mật khẩu mạnh
```bash
# Generate random password
openssl rand -base64 32

# Update trong file .env:
nano /u01/Vanh_projects/vietnam-stock-pipeline/.env
```

---

## 🚧 FIREWALL (Optional - Extra Layer)

```bash
# Block all external access to dashboard port
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" port protocol="tcp" port="8501" reject'
sudo firewall-cmd --reload

# Dashboard chỉ accessible qua SSH tunnel
```

---

## ❌ NHỮNG GÌ KHÔNG NÊN LÀM

❌ **KHÔNG** mở port 8501 ra firewall (`firewall-cmd --add-port=8501/tcp`)
❌ **KHÔNG** change binding từ `127.0.0.1` thành `0.0.0.0`
❌ **KHÔNG** expose PostgreSQL port ra internet
❌ **KHÔNG** dùng password yếu
❌ **KHÔNG** commit `.env` file lên git
❌ **KHÔNG** share credentials qua email/chat không mã hóa

---

## ✅ NHỮNG GÌ NÊN LÀM

✅ **LUÔN** dùng SSH tunnel để truy cập remote
✅ **LUÔN** dùng strong passwords (min 16 chars)
✅ **LUÔN** update system thường xuyên
✅ **LUÔN** monitor logs
✅ **LUÔN** backup dữ liệu (encrypted)
✅ **LUÔN** check security trước khi expose

---

## 🔍 KIỂM TRA NGAY

Chạy commands sau để verify security:

```bash
# 1. Check Docker ports (phải thấy 127.0.0.1)
docker ps --format "table {{.Names}}\t{{.Ports}}"

# 2. Check netstat (phải thấy 127.0.0.1, KHÔNG thấy 0.0.0.0)
sudo netstat -tuln | grep -E "8501|5432|9092|8080"

# 3. Test từ bên ngoài (phải FAIL)
# Từ máy khác:
telnet 10.0.0.7 8501  # Should: Connection refused

# 4. Test từ localhost (phải SUCCESS)
curl http://localhost:8501  # Should: HTTP 200
```

---

## 📞 TROUBLESHOOTING

### "Cannot access dashboard from my laptop"
✅ **EXPECTED** - Đây là intended behavior! Dùng SSH tunnel.

### "Connection refused to port 8501"
✅ **GOOD** - Ports are secure. Use SSH tunnel.

### "I see 0.0.0.0:8501 in docker ps"
❌ **BAD** - Restart Docker Compose to apply secure config.

### "SSH tunnel not working"
Check:
1. SSH access to server: `ssh oracle@10.0.0.7`
2. Dashboard running: `docker ps | grep dashboard`
3. Port not in use locally: `lsof -i :8501`

---

## 📚 MORE INFO

- Full guide: `SECURITY_GUIDE.md`
- Access guide: `ACCESS_DASHBOARD.md`
- Setup script: `./scripts/secure-setup.sh`

---

**Last Updated**: 2025-10-08  
**Security Level**: 🟢 HIGH (Localhost only + SSH tunnel required)



