#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Este script debe ejecutarse con sudo." >&2
  exit 1
fi

APP_DIR=/opt/quetzalmart
SOURCE_DIR=/tmp/quetzalmart-deploy
DOMAIN=quetzalmart.34-9-149-41.sslip.io
DATABASE=quetzalmart
ADMIN_LOGIN=admin@quetzalmart.local
DEPLOY_USER=${SUDO_USER:-root}
DEPLOY_HOME=$(getent passwd "${DEPLOY_USER}" | cut -d: -f6)

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx openssl curl
systemctl enable --now docker
systemctl enable --now nginx

install -d -m 0755 "${APP_DIR}" "${APP_DIR}/config" "${APP_DIR}/addons"
install -m 0644 "${SOURCE_DIR}/docker-compose.yml" "${APP_DIR}/docker-compose.yml"
install -m 0644 "${SOURCE_DIR}/nginx-quetzalmart.conf" /etc/nginx/sites-available/quetzalmart
ln -sfn /etc/nginx/sites-available/quetzalmart /etc/nginx/sites-enabled/quetzalmart
rm -f /etc/nginx/sites-enabled/default

if [[ ! -f "${APP_DIR}/.env" ]]; then
  POSTGRES_PASSWORD=$(openssl rand -hex 24)
  ODOO_MASTER_PASSWORD=$(openssl rand -hex 24)
  ODOO_ADMIN_PASSWORD=$(openssl rand -hex 16)
  umask 077
  printf 'POSTGRES_PASSWORD=%s\nODOO_MASTER_PASSWORD=%s\nODOO_ADMIN_PASSWORD=%s\n' \
    "${POSTGRES_PASSWORD}" "${ODOO_MASTER_PASSWORD}" "${ODOO_ADMIN_PASSWORD}" > "${APP_DIR}/.env"
fi

chmod 0600 "${APP_DIR}/.env"
set -a
source "${APP_DIR}/.env"
set +a

sed "s/__ODOO_MASTER_PASSWORD__/${ODOO_MASTER_PASSWORD}/" \
  "${SOURCE_DIR}/odoo.conf" > "${APP_DIR}/config/odoo.conf"
chown 100:101 "${APP_DIR}/config/odoo.conf"
chmod 0640 "${APP_DIR}/config/odoo.conf"

nginx -t
systemctl reload nginx

cd "${APP_DIR}"
docker compose pull
docker compose up -d postgres

for attempt in $(seq 1 30); do
  if docker compose exec -T postgres pg_isready -U odoo -d postgres >/dev/null 2>&1; then
    break
  fi
  if [[ ${attempt} -eq 30 ]]; then
    echo "PostgreSQL no estuvo listo a tiempo." >&2
    exit 1
  fi
  sleep 2
done

DB_EXISTS=$(docker compose exec -T postgres psql -U odoo -d postgres -tAc \
  "SELECT 1 FROM pg_database WHERE datname='${DATABASE}'")

if [[ "${DB_EXISTS}" != "1" ]]; then
  docker compose run --rm odoo odoo -d "${DATABASE}" -i base --stop-after-init --without-demo=all
  docker compose run --rm -T -e INIT_ADMIN_PASSWORD="${ODOO_ADMIN_PASSWORD}" odoo \
    odoo shell -d "${DATABASE}" <<'PY'
import os

admin = env.ref("base.user_admin")
admin.write({
    "name": "Administrador QuetzalMart",
    "login": "admin@quetzalmart.local",
    "password": os.environ["INIT_ADMIN_PASSWORD"],
})
admin.company_id.write({"name": "QuetzalMart"})
env.cr.commit()
PY
fi

docker compose up -d

for attempt in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8069/web/login >/dev/null 2>&1; then
    break
  fi
  if [[ ${attempt} -eq 60 ]]; then
    docker compose logs --tail=100 odoo >&2
    echo "Odoo no estuvo listo a tiempo." >&2
    exit 1
  fi
  sleep 2
done

if [[ ! -d "/etc/letsencrypt/live/${DOMAIN}" ]]; then
  certbot --nginx --non-interactive --agree-tos --register-unsafely-without-email \
    --redirect -d "${DOMAIN}"
else
  certbot install --nginx --non-interactive --cert-name "${DOMAIN}"
fi

systemctl reload nginx

CREDENTIAL_FILE="${DEPLOY_HOME}/quetzalmart-credentials.txt"
umask 077
printf 'URL=https://%s\nDATABASE=%s\nLOGIN=%s\nPASSWORD=%s\nMASTER_PASSWORD=%s\n' \
  "${DOMAIN}" "${DATABASE}" "${ADMIN_LOGIN}" "${ODOO_ADMIN_PASSWORD}" \
  "${ODOO_MASTER_PASSWORD}" > "${CREDENTIAL_FILE}"
chown "${DEPLOY_USER}:${DEPLOY_USER}" "${CREDENTIAL_FILE}"
chmod 0600 "${CREDENTIAL_FILE}"

curl -fsS "https://${DOMAIN}/web/login" >/dev/null
docker compose ps
echo "Despliegue completado en https://${DOMAIN}"
