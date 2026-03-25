#!/bin/bash
# Deploy MapSearch to VPS
set -euo pipefail

VPS_HOST="${VPS_HOST:-82.21.4.94}"
VPS_DIR="/var/www/mapsearch"
COMMAND="${1:-help}"

case "$COMMAND" in
  app)
    echo "Deploying MapSearch app..."
    rsync -avz --delete --exclude='__pycache__' app/ "root@$VPS_HOST:$VPS_DIR/app/"
    rsync -avz requirements.txt "root@$VPS_HOST:$VPS_DIR/"
    ssh "root@$VPS_HOST" "$VPS_DIR/venv/bin/pip install -q -r $VPS_DIR/requirements.txt"
    ssh "root@$VPS_HOST" "systemctl restart mapsearch"
    ;;
  quick)
    FILE="${2:?Usage: deploy.sh quick <relative-path>}"
    echo "Quick deploy: $FILE"
    scp "$FILE" "root@$VPS_HOST:$VPS_DIR/$FILE"
    ssh "root@$VPS_HOST" "systemctl restart mapsearch"
    ;;
  deps)
    echo "Installing dependencies..."
    rsync -avz requirements.txt "root@$VPS_HOST:$VPS_DIR/"
    ssh "root@$VPS_HOST" "$VPS_DIR/venv/bin/pip install -q -r $VPS_DIR/requirements.txt"
    ;;
  setup)
    echo "First-time setup..."
    ssh "root@$VPS_HOST" "mkdir -p $VPS_DIR"
    ssh "root@$VPS_HOST" "python3 -m venv $VPS_DIR/venv"
    rsync -avz --delete --exclude='__pycache__' app/ "root@$VPS_HOST:$VPS_DIR/app/"
    rsync -avz requirements.txt "root@$VPS_HOST:$VPS_DIR/"
    ssh "root@$VPS_HOST" "$VPS_DIR/venv/bin/pip install -q -r $VPS_DIR/requirements.txt"
    echo ""
    echo "Next steps:"
    echo "  1. Copy .env.example to $VPS_DIR/.env and fill in values"
    echo "  2. Run: ./deploy.sh db-setup"
    echo "  3. Run: ./deploy.sh service-install"
    echo "  4. Add Caddy block: ./deploy.sh caddy-add"
    echo "  5. Add DNS A record: mapsearch.allwk.com → $VPS_HOST"
    ;;
  db-setup)
    echo "Setting up PostgreSQL database..."
    echo "Enter a password for the mapsearch DB user:"
    read -rs DB_PASSWORD
    ssh "root@$VPS_HOST" "sudo -u postgres psql -c \"CREATE USER mapsearch WITH PASSWORD '$DB_PASSWORD';\""
    ssh "root@$VPS_HOST" "sudo -u postgres psql -c \"CREATE DATABASE mapsearch OWNER mapsearch;\""
    cat app/database/schema.sql | ssh "root@$VPS_HOST" "sudo -u postgres psql mapsearch"
    ssh "root@$VPS_HOST" "sudo -u postgres psql -c \"GRANT ALL ON ALL TABLES IN SCHEMA public TO mapsearch;\" mapsearch"
    echo "Database ready. Update MAPSEARCH_DATABASE_URL in $VPS_DIR/.env"
    ;;
  service-install)
    echo "Installing systemd service..."
    cat <<'SERVICE' | ssh "root@$VPS_HOST" "cat > /etc/systemd/system/mapsearch.service"
[Unit]
Description=MapSearch FastAPI
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/var/www/mapsearch
ExecStart=/var/www/mapsearch/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8200
Restart=always
RestartSec=5
EnvironmentFile=/var/www/mapsearch/.env

[Install]
WantedBy=multi-user.target
SERVICE
    ssh "root@$VPS_HOST" "systemctl daemon-reload && systemctl enable mapsearch && systemctl start mapsearch"
    echo "Service installed and started on port 8200"
    ;;
  caddy-add)
    echo "Adding Caddy reverse proxy block..."
    cat <<'CADDY' | ssh "root@$VPS_HOST" "cat >> /root/caddy/Caddyfile"

mapsearch.allwk.com {
    reverse_proxy 172.18.0.1:8200
    encode gzip
}
CADDY
    ssh "root@$VPS_HOST" "ufw allow from 172.18.0.0/16 to any port 8200 2>/dev/null; cd /root/caddy && docker compose restart caddy"
    echo "Caddy updated. Make sure DNS A record points mapsearch.allwk.com → $VPS_HOST"
    ;;
  status)
    echo "Service status:"
    ssh "root@$VPS_HOST" "systemctl status mapsearch --no-pager -l"
    ;;
  logs)
    echo "Recent logs:"
    ssh "root@$VPS_HOST" "journalctl -u mapsearch -n 50 --no-pager"
    ;;
  restart)
    ssh "root@$VPS_HOST" "systemctl restart mapsearch"
    echo "Restarted."
    ;;
  *)
    echo "Usage: deploy.sh {setup|app|quick <file>|deps|db-setup|service-install|caddy-add|status|logs|restart}"
    echo ""
    echo "  setup            First-time: create venv, deploy code"
    echo "  app              Deploy app code + restart"
    echo "  quick <file>     Deploy single file + restart"
    echo "  deps             Install/update dependencies"
    echo "  db-setup         Create PostgreSQL database + user"
    echo "  service-install  Install systemd service (port 8200)"
    echo "  caddy-add        Add Caddy reverse proxy block"
    echo "  status           Show service status"
    echo "  logs             Show recent logs"
    echo "  restart          Restart service"
    ;;
esac

echo ""
echo "Checking health..."
sleep 2
curl -sf "https://mapsearch.allwk.com/health" && echo " ✓ OK" || echo " ✗ FAILED (may need DNS propagation)"
