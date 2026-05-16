#!/bin/bash
set -e

APP_DIR="/opt/placeforbeauty"
SERVICE="placeforbeauty"
REPO="https://github.com/SergeyGusev1/barbershop-site.git"

echo "=== Place for Beauty — Deploy ==="

apt-get update -y
apt-get install -y python3 python3-pip python3-venv nginx git curl fonts-dejavu-core

if [ -d "$APP_DIR" ]; then
  echo "Updating repo..."
  cd "$APP_DIR" && git pull
else
  echo "Cloning repo..."
  git clone "$REPO" "$APP_DIR"
  cd "$APP_DIR"
fi

cd "$APP_DIR"
python3 -m venv venv
venv/bin/pip install --upgrade pip -q
venv/bin/pip install -r requirements.txt -q
venv/bin/python generate_pdf.py || true
cp admin_guide.pdf static/admin_guide.pdf 2>/dev/null || true

# Test that main.py can be imported (catches syntax/import errors early)
echo "--- Testing app import ---"
venv/bin/python -c "import main; print('Import OK')"

# Stop existing service before port detection so its port is freed
systemctl stop "$SERVICE" 2>/dev/null || true
sleep 2

# Find a free port starting at 8001
APP_PORT=8001
while ss -tlnp | grep -q ":$APP_PORT "; do
  APP_PORT=$((APP_PORT + 1))
done
echo "Using app port: $APP_PORT"

# Write systemd service
cat > /etc/systemd/system/${SERVICE}.service << SVCEOF
[Unit]
Description=Place for Beauty FastAPI
After=network.target

[Service]
User=root
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/venv/bin/uvicorn main:app --host 127.0.0.1 --port ${APP_PORT}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SVCEOF

systemctl daemon-reload
systemctl enable "$SERVICE"
systemctl restart "$SERVICE"

# Wait up to 30s for service to become active
for i in $(seq 1 10); do
  sleep 3
  ST=$(systemctl is-active "$SERVICE" || true)
  echo "  [${i}] service: $ST"
  [ "$ST" = "active" ] && break
done

# Always print last journal lines for diagnostics
echo "--- Journal (last 20 lines) ---"
journalctl -u "$SERVICE" -n 20 --no-pager || true
echo "---"

# Nginx — clear all existing catch-all sites, take over port 80
rm -f /etc/nginx/sites-enabled/default
for f in /etc/nginx/sites-enabled/*; do
  [ "$(basename "$f")" != "$SERVICE" ] && rm -f "$f"
done

cat > /etc/nginx/sites-available/${SERVICE} << NGINXEOF
server {
    listen 80 default_server;
    server_name _;
    client_max_body_size 10M;
    location / {
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_read_timeout 60s;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/${SERVICE} /etc/nginx/sites-enabled/${SERVICE}
nginx -t && systemctl reload nginx

sleep 3
STATUS=$(systemctl is-active "$SERVICE" || true)
echo "=== Service status: $STATUS ==="
curl -s -o /dev/null -w "HTTP %{http_code}" http://127.0.0.1:${APP_PORT}/api/services || true
echo ""
echo "=== Site: http://193.164.150.235 ==="
echo "=== Deploy complete! ==="
