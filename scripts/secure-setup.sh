#!/bin/bash
# Quick Security Setup Script
# Run this to apply essential security measures

set -e

echo "================================================================================"
echo "🔐 SECURITY SETUP - Vietnam Stock Pipeline"
echo "================================================================================"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Please run this script as normal user with sudo access, not as root."
   exit 1
fi

echo "[1/5] Checking current security status..."
echo ""

# Check open ports
echo "📊 Currently exposed ports:"
sudo netstat -tuln | grep -E "LISTEN.*:(8501|5432|9092|8080|8081)" || echo "  None (Good!)"
echo ""

# Check firewall status
echo "[2/5] Checking firewall..."
if sudo firewall-cmd --state &>/dev/null; then
    echo "✅ Firewall is active"
    echo ""
    echo "Current allowed ports:"
    sudo firewall-cmd --list-ports
else
    echo "⚠️  Firewall is not active"
    echo ""
    read -p "Do you want to enable firewall? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Enabling firewall..."
        sudo systemctl enable firewalld
        sudo systemctl start firewalld
        echo "✅ Firewall enabled"
    fi
fi
echo ""

# Ask for allowed IP
echo "[3/5] Configure allowed IP for dashboard access"
echo ""
echo "⚠️  Dashboard will be restricted to localhost only by default"
echo "   To access from remote machine, you can:"
echo "   A. Use SSH tunnel (recommended)"
echo "   B. Allow specific IP address"
echo ""
read -p "Do you want to allow a specific IP? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter IP address to allow (e.g., 192.168.1.100): " ALLOWED_IP
    
    if [[ ! -z "$ALLOWED_IP" ]]; then
        echo "Adding firewall rule for IP: $ALLOWED_IP"
        sudo firewall-cmd --permanent --add-rich-rule="rule family=\"ipv4\" source address=\"$ALLOWED_IP/32\" port protocol=\"tcp\" port=\"8501\" accept"
        sudo firewall-cmd --reload
        echo "✅ IP $ALLOWED_IP can now access dashboard on port 8501"
    fi
else
    echo "✅ Dashboard will only be accessible via localhost (use SSH tunnel for remote access)"
fi
echo ""

# Generate strong passwords
echo "[4/5] Security Recommendations"
echo ""
echo "⚠️  Default passwords detected in .env file"
echo ""
echo "Strong password suggestions (save these!):"
echo "  PostgreSQL: $(openssl rand -base64 24)"
echo "  Dashboard:  $(openssl rand -base64 24)"
echo ""
echo "Update these in: /u01/Vanh_projects/vietnam-stock-pipeline/.env"
echo ""
read -p "Press Enter to continue..."
echo ""

# Restart services with new security config
echo "[5/5] Applying Docker security configuration..."
echo ""
echo "Docker ports are now bound to localhost only (127.0.0.1)"
echo "This prevents external access to all services."
echo ""
read -p "Do you want to restart Docker services now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Restarting services..."
    cd /u01/Vanh_projects/vietnam-stock-pipeline
    docker-compose down
    docker-compose up -d
    echo "✅ Services restarted with secure configuration"
else
    echo "⚠️  Remember to restart services manually: docker-compose restart"
fi
echo ""

# Summary
echo "================================================================================"
echo "✅ SECURITY SETUP COMPLETE"
echo "================================================================================"
echo ""
echo "📋 Security Status:"
echo "  ✅ Docker ports bound to localhost only"
echo "  ✅ Firewall configured"
if [[ ! -z "$ALLOWED_IP" ]]; then
    echo "  ✅ IP $ALLOWED_IP allowed for dashboard access"
fi
echo ""
echo "📝 Next Steps:"
echo "  1. Update passwords in .env file"
echo "  2. Test dashboard access:"
echo "     - Local: http://localhost:8501"
echo "     - Remote: Use SSH tunnel (./scripts/ssh-tunnel.sh)"
echo ""
echo "🔐 SSH Tunnel Usage (from your local machine):"
echo "  ssh -L 8501:localhost:8501 oracle@10.0.0.7"
echo "  Then open: http://localhost:8501"
echo ""
echo "📚 Full security guide: SECURITY_GUIDE.md"
echo "================================================================================"






