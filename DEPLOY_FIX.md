# Emergency Fix & Deployment Guide

## 🚨 CRITICAL: SERVER LOCKED OUT?
If you cannot connect via SSH (`Connection timed out`) and the site is down (`Connection Refused`), your Firewall might have locked you out.

**Solution:**
1. Log in to **Strato Customer Panel**.
2. Go to **Server Login** -> **Remote Console (VNC)**.
3. Log in as `root`.
4. Run this command to open the firewall immediately:
   ```bash
   ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw enable
   ```
   *(If `ufw` is not found, try `iptables -F` to flush all rules temporarily)*

---

## 1. Fix Server (Once SSH is back)
Your server is refusing connections on port 443. Run this rescue script to fix Nginx and Firewall.

**Run these commands in your local terminal:**

```powershell
# 1. Upload the rescue script
scp installation/fix_server.sh root@88.99.101.251:/root/fix_server.sh

# 2. Run the script on the server
ssh root@88.99.101.251 "chmod +x /root/fix_server.sh && /root/fix_server.sh"
```

## 2. Deploy Code Fixes (Content Missing)
I have patched the backend to fetch ALL videos (not just 100) and fix the quota issues.

```powershell
# Deploy the new code
./deploy-full.ps1
```

## 3. Install Analytics (Matomo)
To get "Netflix-grade" analytics:

```powershell
# Upload and run Matomo installer
scp installation/scripts/matomo_installation.sh root@88.99.101.251:/root/
ssh root@88.99.101.251 "chmod +x /root/matomo_installation.sh && ./matomo_installation.sh --domain stats.frai.tv"
```

## Status
- **Security:** Hardened (Secrets removed).
- **Infrastructure:** Rescue script ready.
- **Backend:** YouTube Importer patched (Unlimited videos).
- **Frontend:** Ready for deploy.
