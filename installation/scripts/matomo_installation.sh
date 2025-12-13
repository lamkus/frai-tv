#!/usr/bin/env bash
set -euo pipefail

# Matomo installer for Debian/Ubuntu (Strato VPS)
# Usage: sudo ./matomo_installation.sh --domain stats.YOUR_DOMAIN.de

DOMAIN=""
DB_NAME="matomo"
DB_USER="matomo"
MYSQL_ROOT_PW=""
MYSQL_NONINTERACTIVE=0
INSTALL_NGINX=1
DRY_RUN=0

print_usage() {
  echo "Usage: sudo $0 --domain stats.YOUR_DOMAIN.de [--no-nginx] [--db-root-pw ROOT_PW]"
  echo "  --no-nginx   : Don't touch nginx, only install Matomo files"
  echo "  --db-root-pw : Use provided mysql root password (for existing DB)"
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --domain)
      DOMAIN="$2"
      shift 2
      ;;
    --no-nginx)
      INSTALL_NGINX=0
      shift
      ;;
    --db-root-pw)
      MYSQL_ROOT_PW="$2"
      MYSQL_NONINTERACTIVE=1
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown arg: $1"
      print_usage
      exit 1
      ;;
  esac
done

if [[ -z "$DOMAIN" ]]; then
  echo "Domain is required. Use --domain stats.YOUR_DOMAIN.de"
  exit 1
fi

if [[ $(id -u) -ne 0 ]]; then
  echo "Please run as root, e.g., sudo $0 --domain $DOMAIN"
  exit 1
fi

run_cmd() {
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "DRY RUN: $*"
  else
    eval "$*"
  fi
}

run_cmd "apt update -y"
run_cmd "apt install -y nginx curl unzip wget gnupg2"

# PHP packages
run_cmd "apt install -y php-fpm php-cli php-mysql php-json php-common php-mbstring php-curl php-gd php-xml php-zip php-xmlrpc"

# MariaDB server (lightweight)
run_cmd "apt install -y mariadb-server"

# Create php-fpm pool config for Matomo if required
PHP_FPM_POOL_CONF="/etc/php/$(php -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')/fpm/pool.d/matomo.conf"
if [[ ! -f "$PHP_FPM_POOL_CONF" ]]; then
  cat > "$PHP_FPM_POOL_CONF" <<'EOF'
[matomo]
user = www-data
group = www-data
listen = /run/php/php-matomo-fpm.sock
listen.owner = www-data
listen.group = www-data
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3

EOF
  # Enable and restart php-fpm
  systemctl restart php*-fpm || true
fi

# Prepare DB
if [[ $MYSQL_NONINTERACTIVE -eq 0 ]]; then
  echo "Please enter MariaDB root password (press Enter for empty password):"
  read -s MYSQL_ROOT_PW || MYSQL_ROOT_PW=""
fi

# Create database and user
# Secure the password generation
DB_PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 22)

if [[ -z "$MYSQL_ROOT_PW" ]]; then
  # No root password (likely server default) - create DB
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "DRY RUN: mysql -u root <<'SQL'"
    echo "CREATE DATABASE IF NOT EXISTS \\`${DB_NAME}\\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';"
    echo "GRANT ALL PRIVILEGES ON \\`${DB_NAME}\\`.* TO '$DB_USER'@'localhost';"
    echo "FLUSH PRIVILEGES;"
    echo "SQL"
  else
    mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
  fi
else
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "DRY RUN: mysql -u root -p\"$MYSQL_ROOT_PW\" <<'SQL'"
    echo "CREATE DATABASE IF NOT EXISTS \\`${DB_NAME}\\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';"
    echo "GRANT ALL PRIVILEGES ON \\`${DB_NAME}\\`.* TO '$DB_USER'@'localhost';"
    echo "FLUSH PRIVILEGES;"
    echo "SQL"
  else
    mysql -u root -p"$MYSQL_ROOT_PW" <<EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
  fi
fi

# Download Matomo
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"
MATOMO_URL="https://builds.matomo.org/matomo.zip"
if [[ $DRY_RUN -eq 1 ]]; then
  echo "DRY RUN: wget -O matomo.zip \"$MATOMO_URL\""
  echo "DRY RUN: unzip matomo.zip"
else
  wget -O matomo.zip "$MATOMO_URL"
  unzip matomo.zip
fi

# Install to /var/www/matomo
if [[ $DRY_RUN -eq 1 ]]; then
  echo "DRY RUN: mkdir -p /var/www/matomo"
  echo "DRY RUN: cp -r matomo/* /var/www/matomo/"
  echo "DRY RUN: chown -R www-data:www-data /var/www/matomo"
else
  mkdir -p /var/www/matomo
  cp -r matomo/* /var/www/matomo/
  chown -R www-data:www-data /var/www/matomo
  chmod -R 755 /var/www/matomo
fi

# Create nginx vhost for domain if desired
if [[ $INSTALL_NGINX -ne 0 ]]; then
  NGINX_CONF=/etc/nginx/sites-available/matomo.conf
  cat > "$NGINX_CONF" <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    root /var/www/matomo;
    index index.php index.html;

    access_log /var/log/nginx/matomo.access.log;
    error_log /var/log/nginx/matomo.error.log;

    location / {
        try_files $uri $uri/ /index.php?$args;
    }

    location ~ \\.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/php-matomo-fpm.sock;
    }

    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
  run_cmd "ln -sf \"$NGINX_CONF\" /etc/nginx/sites-enabled/matomo.conf"
  run_cmd "nginx -t"
  run_cmd "systemctl reload nginx"
fi

# Setup cron job for Matomo archiving (hourly)
CRON_LINE="0 * * * * /usr/bin/php /var/www/matomo/console core:archive --url=https://${DOMAIN} > /dev/null 2>&1"
if [[ $DRY_RUN -eq 1 ]]; then
  echo "DRY RUN: ( crontab -l 2>/dev/null || true; echo \"$CRON_LINE\" ) | crontab -"
else
  ( crontab -l 2>/dev/null || true; echo "$CRON_LINE" ) | crontab -
fi

# Output DB password details
cat <<EOF
=== Matomo installation completed ===
- Visit: https://${DOMAIN}
- Database: ${DB_NAME}
- DB User: ${DB_USER}
- DB Password: ${DB_PASS}
- Please keep this password and use it during the Matomo web installation.

Note: If your domain is not yet pointing to this server, configure DNS first.
If you are using Plesk, prefer the Plesk GUI and do not run Nginx config step.
EOF

# Cleanup
cd /
rm -rf "$TMP_DIR"

exit 0
