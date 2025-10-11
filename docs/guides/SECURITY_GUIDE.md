# 🔐 SECURITY GUIDE - Bảo Mật Hệ Thống

**Last Updated**: 2025-10-08  
**Priority**: 🔴 CRITICAL

---

## ⚠️ CẢNH BÁO BẢO MẬT HIỆN TẠI

### 🔴 VẤN ĐỀ NGUY HIỂM

```
❌ Dashboard exposed trên 0.0.0.0:8501 (KHÔNG CÓ AUTHENTICATION)
❌ PostgreSQL port 5432 có thể bị scan
❌ Kafka, Spark ports đang exposed
❌ Không có SSL/HTTPS
❌ Không có rate limiting
```

---

## 🛡️ GIẢI PHÁP BẢO MẬT NGAY LẬP TỨC

### 1. GIỚI HẠN TRUY CẬP THEO IP (ƯU TIÊN CAO)

#### A. Firewall Rules (Khuyến nghị)

```bash
# 1. Xóa rule cho phép tất cả
sudo firewall-cmd --permanent --remove-port=8501/tcp
sudo firewall-cmd --permanent --remove-port=5432/tcp

# 2. Chỉ cho phép IP cụ thể truy cập dashboard
# Thay YOUR_IP bằng IP máy bạn (VD: 192.168.1.100)
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="YOUR_IP/32" port protocol="tcp" port="8501" accept'

# 3. Chỉ cho phép localhost truy cập PostgreSQL
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="127.0.0.1/32" port protocol="tcp" port="5432" accept'

# 4. Apply rules
sudo firewall-cmd --reload

# 5. Verify
sudo firewall-cmd --list-all
```

#### B. iptables Rules (Alternative)

```bash
# 1. Drop all connections to 8501 by default
sudo iptables -A INPUT -p tcp --dport 8501 -j DROP

# 2. Allow specific IP only (thay YOUR_IP)
sudo iptables -I INPUT -p tcp -s YOUR_IP --dport 8501 -j ACCEPT

# 3. Allow localhost
sudo iptables -I INPUT -p tcp -s 127.0.0.1 --dport 8501 -j ACCEPT

# 4. Save rules
sudo service iptables save

# 5. Verify
sudo iptables -L -n | grep 8501
```

---

### 2. THÊM AUTHENTICATION VÀO DASHBOARD

Tạo file `dashboard/.streamlit/secrets.toml`:

```toml
[passwords]
# Thay đổi username và password
admin = "your-strong-password-here-min-16-chars"
viewer = "another-strong-password-here"
```

Update `dashboard/dashboard.py` hoặc `dashboard_v2.py` để thêm authentication (tôi sẽ làm ngay).

---

### 3. SỬ DỤNG VPN (KHUYẾN NGHỊ MẠNH)

#### A. WireGuard VPN (Đơn giản nhất)

```bash
# Install WireGuard
sudo yum install wireguard-tools -y

# Generate keys
wg genkey | tee privatekey | wg pubkey > publickey

# Configure VPN server
sudo nano /etc/wireguard/wg0.conf
```

**Lợi ích**:
- ✅ Chỉ truy cập qua VPN
- ✅ Tất cả traffic được encrypt
- ✅ Không cần expose ports ra internet

---

### 4. NGINX REVERSE PROXY + SSL (Production)

```bash
# Install nginx
sudo yum install nginx -y

# Configure nginx
sudo nano /etc/nginx/conf.d/stock-dashboard.conf
```

**Config mẫu**:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Basic Auth
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=dashboard:10m rate=10r/s;
    limit_req zone=dashboard burst=20;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

**Tạo password file**:
```bash
# Install htpasswd
sudo yum install httpd-tools -y

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Start nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

---

### 5. GIỚI HẠN DOCKER PORTS (NGAY LẬP TỨC)

Update `docker-compose.yml` để chỉ bind localhost:

```yaml
# TRƯỚC (Nguy hiểm)
ports:
  - "8501:8501"    # Exposed to 0.0.0.0
  - "5432:5432"    # Exposed to 0.0.0.0

# SAU (An toàn)
ports:
  - "127.0.0.1:8501:8501"    # Chỉ localhost
  - "127.0.0.1:5432:5432"    # Chỉ localhost
```

Tôi sẽ update ngay file này!

---

### 6. THAY ĐỔI MẬT KHẨU MẶC ĐỊNH

```bash
# Update .env file
nano /u01/Vanh_projects/vietnam-stock-pipeline/.env
```

**Thay đổi**:
```bash
# TRƯỚC
POSTGRES_PASSWORD=admin
SNOWFLAKE_PASSWORD=Vanhdzai1803@!

# SAU (tạo password mạnh)
POSTGRES_PASSWORD=StrongP@ssw0rd!2025_ComplexDB
SNOWFLAKE_PASSWORD=YourNewStr0ngP@ss_Here!2025
```

---

### 7. FAIL2BAN (Tự động block brute-force)

```bash
# Install fail2ban
sudo yum install fail2ban -y

# Configure
sudo nano /etc/fail2ban/jail.local
```

**Config**:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/secure

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
```

```bash
# Start fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

### 8. MONITORING & ALERTS

```bash
# Install monitoring
sudo yum install aide -y

# Initialize database
sudo aide --init
sudo mv /var/lib/aide/aide.db.new.gz /var/lib/aide/aide.db.gz

# Check for changes
sudo aide --check
```

---

## 🚨 HÀNH ĐỘNG NGAY LẬP TỨC (5 PHÚT)

### Bước 1: Giới hạn IP (Khuyến nghị cao)

```bash
# Lấy IP máy bạn
curl ifconfig.me

# Chặn tất cả, chỉ cho phép IP bạn
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="YOUR_IP/32" port protocol="tcp" port="8501" accept'
sudo firewall-cmd --permanent --remove-port=8501/tcp
sudo firewall-cmd --reload
```

### Bước 2: Change Localhost Binding

```bash
cd /u01/Vanh_projects/vietnam-stock-pipeline

# Tôi sẽ update docker-compose.yml để bind localhost only
```

### Bước 3: Restart Services

```bash
docker-compose down
docker-compose up -d
```

---

## 🔍 KIỂM TRA BẢO MẬT

```bash
# 1. Check open ports
sudo ss -tuln | grep -E "8501|5432|9092|8080"

# 2. Check firewall rules
sudo firewall-cmd --list-all

# 3. Scan from outside (from another machine)
nmap -p 8501,5432 YOUR_SERVER_IP

# 4. Check authentication
curl http://localhost:8501  # Should work from server
curl http://YOUR_IP:8501    # Should fail from outside
```

---

## 📋 SECURITY CHECKLIST

### Immediate (Do ngay - 5 phút)
- [ ] Bind ports to 127.0.0.1 trong docker-compose.yml
- [ ] Firewall: Chỉ allow IP cụ thể
- [ ] Change default passwords

### Short-term (1 giờ)
- [ ] Add authentication to dashboard
- [ ] Install fail2ban
- [ ] Setup monitoring

### Medium-term (1 ngày)
- [ ] Setup VPN (WireGuard recommended)
- [ ] Configure nginx reverse proxy
- [ ] Add SSL certificate (Let's Encrypt)
- [ ] Setup rate limiting

### Long-term (1 tuần)
- [ ] Implement proper user management
- [ ] Setup audit logging
- [ ] Configure backup encryption
- [ ] Penetration testing

---

## 🔐 MẬT KHẨU MẠNH

**Tạo password mạnh**:
```bash
# Random password generator
openssl rand -base64 32

# Hoặc
pwgen -s 32 1
```

**Yêu cầu**:
- ✅ Tối thiểu 16 ký tự
- ✅ Có chữ hoa, chữ thường, số, ký tự đặc biệt
- ✅ Không dùng từ điển
- ✅ Không dùng thông tin cá nhân

---

## ⚡ EMERGENCY RESPONSE

**Nếu nghi ngờ bị hack**:

```bash
# 1. Disconnect ngay
sudo firewall-cmd --panic-on

# 2. Stop all services
docker-compose down

# 3. Check logs
sudo grep -i "failed\|error\|attack" /var/log/secure
docker-compose logs | grep -i "error\|failed"

# 4. Check connections
sudo netstat -antp | grep ESTABLISHED

# 5. Restore firewall
sudo firewall-cmd --panic-off
```

---

## 📞 BEST PRACTICES

1. **Không bao giờ expose services ra internet trực tiếp**
2. **Luôn dùng VPN hoặc reverse proxy**
3. **Enable authentication cho mọi service**
4. **Thường xuyên update & patch**
5. **Monitor logs định kỳ**
6. **Backup thường xuyên (encrypted)**
7. **Use strong, unique passwords**
8. **Enable 2FA nếu có thể**

---

**QUAN TRỌNG**: Tôi sẽ update ngay docker-compose.yml để bind localhost và tạo authentication cho dashboard!



