#!/bin/bash
set -e

APP_DIR="/opt/placeforbeauty"
SERVICE="placeforbeauty"
REPO="https://github.com/gusiev20033/barbershop-site.git"

echo "=== Place for Beauty — Deploy ==="

# Update system
apt-get update -y
apt-get install -y python3 python3-pip python3-venv nginx git

# Clone or update
if [ -d "$APP_DIR" ]; then
  echo "Обновление репозитория..."
  cd "$APP_DIR" && git pull
else
  echo "Клонирование репозитория..."
  git clone "$REPO" "$APP_DIR"
  cd "$APP_DIR"
fi

# Virtual env
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Generate PDF
python3 generate_pdf.py

# Copy PDF to static
cp admin_guide.pdf static/admin_guide.pdf

# Systemd service
cat > /etc/systemd/system/${SERVICE}.service << 'EOF'
[Unit]
Description=Place for Beauty FastAPI
After=network.target

[Service]
User=root
WorkingDirectory=/opt/placeforbeauty
ExecStart=/opt/placeforbeauty/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $SERVICE
systemctl restart $SERVICE

# Nginx config
cat > /etc/nginx/sites-available/${SERVICE} << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/${SERVICE} /etc/nginx/sites-enabled/${SERVICE}
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo ""
echo "=== Деплой завершён! ==="
echo "Сайт доступен по адресу: http://$(curl -s ifconfig.me)"
echo "Админка: http://$(curl -s ifconfig.me)/admin.html"
echo "Логин: admin | Пароль: beauty2024"
