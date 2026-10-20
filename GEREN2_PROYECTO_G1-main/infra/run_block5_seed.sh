#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Este script debe ejecutarse con sudo." >&2
  exit 1
fi

APP_DIR=/opt/quetzalmart
SOURCE_DIR=/tmp/quetzalmart-block5

cd "${APP_DIR}"
docker compose run --rm -T odoo odoo shell -d quetzalmart \
  < "${SOURCE_DIR}/seed_block5.py"

docker compose restart odoo

for attempt in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8069/web/login >/dev/null 2>&1; then
    break
  fi
  if [[ ${attempt} -eq 60 ]]; then
    docker compose logs --tail=100 odoo >&2
    echo "Odoo no estuvo listo después de generar las transacciones." >&2
    exit 1
  fi
  sleep 2
done

docker compose ps
