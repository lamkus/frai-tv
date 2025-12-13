#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== remAIke.TV Server Rescue Script ===${NC}"

# 1. Check Nginx Status
echo -e "\n[1] Checking Nginx Status..."
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx is running${NC}"
else
    echo -e "${RED}✗ Nginx is NOT running${NC}"
    echo "Attempting to start Nginx..."
    systemctl start nginx
fi

# 2. Check Firewall (UFW)
echo -e "\n[2] Checking Firewall (UFW)..."
if command -v ufw >/dev/null; then
    ufw_status=$(ufw status | grep -i "active")
    echo "UFW Status: $ufw_status"
    
    # Ensure ports are open
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    echo -e "${GREEN}✓ Ports 80, 443, 22 allowed${NC}"
else
    echo "UFW not installed (skipping)"
fi

# 3. Test Nginx Configuration
echo -e "\n[3] Testing Nginx Configuration..."
nginx -t
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
    echo "Reloading Nginx..."
    systemctl reload nginx
else
    echo -e "${RED}✗ Nginx configuration has errors!${NC}"
    echo "Please fix the errors above."
    exit 1
fi

# 4. Check SSL Certificates
echo -e "\n[4] Checking SSL Certificates..."
if command -v certbot >/dev/null; then
    certbot certificates
else
    echo "Certbot not found."
fi

# 5. Check Node.js Backend
echo -e "\n[5] Checking Backend (Port 4000)..."
if lsof -i :4000 >/dev/null; then
    echo -e "${GREEN}✓ Backend is listening on port 4000${NC}"
else
    echo -e "${RED}✗ Backend is NOT listening on port 4000${NC}"
    echo "Check PM2 status:"
    pm2 status
    echo "Attempting to restart backend..."
    pm2 restart all
fi

echo -e "\n${GREEN}=== Rescue Complete ===${NC}"
echo "Try accessing https://frai.tv now."
