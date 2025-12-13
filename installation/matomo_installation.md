# Matomo Installation Automation (Strato VPS)

This document explains how to run the installer script on a Strato VPS (Debian/Ubuntu). It also describes Plesk steps if you prefer to use Plesk for hosting the Matomo site.

> WARNING: This script modifies system packages, installs PHP/MariaDB and Nginx configuration. Only run on a dedicated VPS you control. For Plesk, prefer the Plesk GUI steps instead of direct `nginx`/`php-fpm` edits.

Quick steps summary

1. SSH to your Strato VPS as root or sudo user:

```bash
ssh root@YOUR_SERVER_IP
```

2. Copy the script to `/tmp` and run it (confirm values when prompted):

```bash
# Dry-run first (safe):
curl -fsSL https://raw.githubusercontent.com/YOUR_REPO/installers/matomo_installation.sh -o /tmp/matomo_installation.sh
chmod +x /tmp/matomo_installation.sh
sudo /tmp/matomo_installation.sh --domain stats.YOUR_DOMAIN.de --dry-run

# If dry-run looks good, run for real:
sudo /tmp/matomo_installation.sh --domain stats.YOUR_DOMAIN.de
```

3. After the script finishes, open `https://stats.YOUR_DOMAIN.de` in a browser and complete the Matomo web installer (DB credentials recorded by the script).

4. Configure `VITE_MATOMO_URL` and `VITE_MATOMO_SITE_ID` in the frontend environment, rebuild and redeploy the frontend.

What the script does

- Ensures Debian/Ubuntu packages are installed (php, php-fpm, php extensions, nginx, mariadb-server, unzip).
- Creates a `matomo` MySQL database and a randomized secure password for the user `matomo`.
- Downloads Matomo, extracts it to `/var/www/matomo`, and sets permissions.
- Adds an `nginx` vhost for `stats.YOUR_DOMAIN.de` (if `--domain` flag used) and reloads `nginx`.
- Creates a cron job for Matomo archiving using `php` (hourly).

Plesk alternative: manual steps

If you are on Plesk (recommended), it's safer to perform these steps via the Plesk GUI:

1. Create a new subscription / domain `stats.YOUR_DOMAIN.de` and set the document root.
2. Use `Database` → `Add Database` in Plesk to create `matomo` DB and user.
3. Upload the Matomo zip via **File Manager** and extract under the domain's document root.
4. Ensure `PHP Settings` are set to use `php-fpm` and required modules are installed.
5. Use the Let's Encrypt extension to create an SSL cert.
6. Run the Matomo installer in the browser and configure archiving via cron (or Plesk scheduled tasks).

Limitations & notes

- The script assumes a Debian/Ubuntu VPS.
- The script will not change DNS or set up a reverse proxy port; you should have the domain already point to the server.
- For Plesk-managed hosts, prefer the manual Plesk GUI steps.
- Do not run the script on shared hosting.

---

If you want me to generate a version of the script requiring no editing (with DNS + domain args), I can create a safe prompt + script for you to run. Please confirm whether you want the script to automatically update nginx vhosts and run Let's Encrypt or prefer manual control.
