Matomo Installation Script

This script is for Debian/Ubuntu systems (Strato VPS). It installs required PHP modules, MariaDB and nginx, automatically creates a DB and sets up Matomo.

Usage:
```bash
sudo ./matomo_installation.sh --domain stats.YOUR_DOMAIN.de
```

Options:
- `--no-nginx`: Don't modify nginx config (recommended if you use Plesk).
- `--db-root-pw <ROOTPW>`: Provide the MariaDB root password in case it is set.

Notes:
- Plesk-managed systems: prefer the Plesk GUI and the Plesk instructions instead of using this script.
- If you want a `non-root` deploy, adjust permissions and user creation accordingly.
