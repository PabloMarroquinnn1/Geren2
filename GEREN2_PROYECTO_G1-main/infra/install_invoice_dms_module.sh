#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Este script debe ejecutarse con sudo." >&2
  exit 1
fi

APP_DIR=/opt/quetzalmart
MODULE_PATH=${APP_DIR}/addons/quetzalmart_invoice_dms/__manifest__.py
[[ -f ${MODULE_PATH} ]] || {
  echo "No se encuentra el módulo ${MODULE_PATH}." >&2
  exit 1
}

cd "${APP_DIR}"
MODULE_STATE=$(docker compose exec -T postgres psql -U odoo -d quetzalmart -tAc \
  "SELECT state FROM ir_module_module WHERE name='quetzalmart_invoice_dms'")
if [[ ${MODULE_STATE} == "installed" ]]; then
  MODULE_OPERATION=(-u quetzalmart_invoice_dms)
else
  MODULE_OPERATION=(-i quetzalmart_invoice_dms)
fi

docker compose stop odoo

restore_odoo() {
  cd "${APP_DIR}"
  docker compose up -d odoo >/dev/null 2>&1 || true
}
trap restore_odoo EXIT

docker compose run --rm -T odoo odoo -d quetzalmart \
  "${MODULE_OPERATION[@]}" --stop-after-init

trap - EXIT
docker compose up -d odoo

for attempt in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8069/web/login >/dev/null 2>&1; then
    docker compose ps
    exit 0
  fi
  if [[ ${attempt} -eq 60 ]]; then
    docker compose logs --tail=100 odoo >&2
    echo "Odoo no estuvo listo después de instalar el archivado de facturas." >&2
    exit 1
  fi
  sleep 2
done
