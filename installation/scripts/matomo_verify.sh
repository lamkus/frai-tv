#!/usr/bin/env bash
# Matomo verification script (simple checks)
set -euo pipefail

DOMAIN=${1:-stats.YOUR_DOMAIN.de}

echo "Checking Matomo site: https://${DOMAIN}"
curl -I -s -S "https://${DOMAIN}" | head -n 10

echo "Checking Matomo archiving (dry-run):"
php /var/www/matomo/console core:archive --url=https://${DOMAIN} --force-non-ssl || true

echo "Checking DB connectivity for matomo user"
mysql -u matomo -p -e "SHOW DATABASES LIKE 'matomo'\;" || true

exit 0
