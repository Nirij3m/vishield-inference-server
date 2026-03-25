#!/bin/sh
set -e

# ── 1. Détection IP hôte ─────────────────────────────────────────────────────
HOST_IP=$(getent hosts host.docker.internal | awk '{print $1}')
if [ -z "$HOST_IP" ]; then
    echo ">>> Failed to resolve docker host IP address, fallback to gateway"
    HOST_IP=$(ip route | awk '/default/ {print $3}')
fi
echo ">>> IP hôte : $HOST_IP"
export HOST_IP

DOMAIN="${HOST_IP}.nip.io"
CERT_PATH="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"

# ── 2. Génère une config HTTP-only temporaire ────────────────────────────────
cat > /etc/nginx/conf.d/default.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN};
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://\$host\$request_uri; }
}
EOF

# ── 3. Démarre nginx en HTTP pour le challenge ACME ──────────────────────────
nginx

# ── 4. Obtient le certificat si pas encore présent ───────────────────────────
if [ ! -f "$CERT_PATH" ]; then
    echo ">>> Certificat absent, lancement de Certbot..."
    certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "${CERTBOT_EMAIL}" \
        --agree-tos \
        --no-eff-email \
        --non-interactive \
        -d "${DOMAIN}"
    echo ">>> Certificat obtenu."
else
    echo ">>> Certificat déjà présent, skip Certbot."
fi

# ── 5. Génère la config HTTPS complète et recharge nginx ────────────────────
envsubst '${HOST_IP}' < /etc/nginx/templates/nginx.conf.template \
    > /etc/nginx/conf.d/default.conf

nginx -s reload
echo ">>> nginx rechargé en HTTPS."

# ── 6. Garde nginx au premier plan ───────────────────────────────────────────
nginx -s quit
exec nginx -g "daemon off;"