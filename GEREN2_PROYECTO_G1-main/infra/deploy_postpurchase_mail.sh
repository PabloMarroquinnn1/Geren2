#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR=/opt/quetzalmart
STAGED_COMPOSE=/tmp/qm-postpurchase-compose.yml
STAGED_ADDON=/tmp/quetzalmart_website_crm

[[ ${EUID} -eq 0 ]] || { echo 'Run with sudo.' >&2; exit 1; }
[[ -f ${STAGED_COMPOSE} ]] || { echo 'Compose file was not staged.' >&2; exit 1; }
[[ -f ${STAGED_ADDON}/__manifest__.py ]] || { echo 'Addon was not staged.' >&2; exit 1; }

cd "${PROJECT_DIR}"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
BACKUP_DIR="${PROJECT_DIR}/backups/postpurchase-${STAMP}"
mkdir -p "${BACKUP_DIR}"
cp -a docker-compose.yml "${BACKUP_DIR}/docker-compose.yml"
cp -a addons/quetzalmart_website_crm "${BACKUP_DIR}/quetzalmart_website_crm"
docker exec quetzalmart-db pg_dump -U odoo -d quetzalmart -Fc > "${BACKUP_DIR}/quetzalmart.dump"

install -m 0644 "${STAGED_COMPOSE}" docker-compose.yml
cp -a "${STAGED_ADDON}/." addons/quetzalmart_website_crm/
docker compose config --quiet

# The former stand-alone Mailpit container had temporary storage and no
# restart policy. Keep it as a recoverable stopped container while Compose
# creates the persistent replacement.
if docker ps -a --format '{{.Names}}' | grep -Fxq quetzalmart-mailpit; then
  docker stop quetzalmart-mailpit >/dev/null
  docker rename quetzalmart-mailpit "quetzalmart-mailpit-legacy-${STAMP}"
fi
docker compose up -d mailpit
docker exec quetzalmart-odoo getent hosts quetzalmart-mailpit >/dev/null

restore_odoo() {
  cd "${PROJECT_DIR}"
  docker compose up -d odoo >/dev/null 2>&1 || true
}
docker compose stop odoo
trap restore_odoo EXIT
docker compose run --rm -T odoo odoo -d quetzalmart \
  -u quetzalmart_website_crm --stop-after-init
docker compose up -d odoo
trap - EXIT

for attempt in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8069/web/login >/dev/null 2>&1; then
    echo "Backup: ${BACKUP_DIR}"
    docker compose ps
    exit 0
  fi
  sleep 2
done
echo 'Odoo did not become ready after the module upgrade.' >&2
exit 1
