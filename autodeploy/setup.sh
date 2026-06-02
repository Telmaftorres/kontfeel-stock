#!/bin/bash
# Lance ce script UNE SEULE FOIS sur le VPS :
#   bash ~/kontfeel-stock/autodeploy/setup.sh

set -e

REPO="/home/ubuntu/kontfeel-stock"
SERVICE_SRC="$REPO/autodeploy/autodeploy.service"
SERVICE_DST="/etc/systemd/system/autodeploy.service"

# Générer un secret aléatoire
SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo ""
echo "========================================"
echo "SECRET GitHub webhook (note-le !) :"
echo "  $SECRET"
echo "========================================"
echo ""

# Installer le service systemd avec le secret
sed "s/REMPLACER_PAR_SECRET/$SECRET/" "$SERVICE_SRC" | sudo tee "$SERVICE_DST" > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable autodeploy
sudo systemctl start autodeploy
echo "✅ Service autodeploy démarré"

# Ajouter la route webhook dans le Nginx du host
NGINX_CONF="/etc/nginx/sites-available/stock.calculateur-kontfeel.tech"
if grep -q "webhook" "$NGINX_CONF"; then
  echo "ℹ️  Route webhook déjà présente dans Nginx"
else
  sudo sed -i '/location \/ {/i\    location /webhook/ {\n        proxy_pass http://127.0.0.1:9000;\n    }\n' "$NGINX_CONF"
  sudo nginx -t && sudo systemctl reload nginx
  echo "✅ Nginx mis à jour"
fi

echo ""
echo "========================================"
echo "Configuration GitHub webhook :"
echo "  URL     : https://stock.calculateur-kontfeel.tech/webhook/deploy"
echo "  Secret  : $SECRET"
echo "  Content : application/json"
echo "  Event   : Just the push event"
echo "========================================"
