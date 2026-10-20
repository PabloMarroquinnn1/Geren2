#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Este script debe ejecutarse con sudo." >&2
  exit 1
fi

APP_DIR=/opt/quetzalmart
SOURCE_DIR=/tmp/quetzalmart-block4
OCA_DMS_DIR=${APP_DIR}/addons/oca-dms
MODULES=sale_management,purchase_stock,stock,account,hr,hr_contract,crm,website_sale,mass_mailing,l10n_gt,dms,payment_demo

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y git

if [[ ! -d "${OCA_DMS_DIR}/.git" ]]; then
  git clone --depth=1 --branch 18.0 https://github.com/OCA/dms.git "${OCA_DMS_DIR}"
else
  git -C "${OCA_DMS_DIR}" pull --ff-only
fi

if ! grep -q '/mnt/extra-addons/oca-dms' "${APP_DIR}/config/odoo.conf"; then
  sed -i 's#^addons_path = .*#addons_path = /mnt/extra-addons,/mnt/extra-addons/oca-dms,/usr/lib/python3/dist-packages/odoo/addons#' \
    "${APP_DIR}/config/odoo.conf"
fi
chown 100:101 "${APP_DIR}/config/odoo.conf"
chmod 0640 "${APP_DIR}/config/odoo.conf"

cd "${APP_DIR}"
docker compose stop odoo

restore_odoo() {
  cd "${APP_DIR}"
  docker compose up -d odoo >/dev/null 2>&1 || true
}
trap restore_odoo EXIT

docker compose run --rm -T odoo odoo shell -d quetzalmart \
  < "${SOURCE_DIR}/preconfigure_quetzalmart.py"

docker compose run --rm odoo odoo -d quetzalmart -i "${MODULES}" \
  --stop-after-init --without-demo=all

trap - EXIT
docker compose up -d odoo

for attempt in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8069/web/login >/dev/null 2>&1; then
    break
  fi
  if [[ ${attempt} -eq 60 ]]; then
    docker compose logs --tail=100 odoo >&2
    echo "Odoo no estuvo listo después de instalar los módulos." >&2
    exit 1
  fi
  sleep 2
done

docker compose ps
