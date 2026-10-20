#!/usr/bin/env bash
# Instala QuetzalMart (Odoo 18 + PostgreSQL 16 + HTTPS) en una VM Ubuntu de la nube.
#
# Uso (dentro de la VM, desde esta carpeta):
#   sudo ./instalar.sh                      # dominio automático <ip>.sslip.io
#   sudo ./instalar.sh mi-dominio.com       # dominio propio o etiqueta DNS de Azure
#
# Se puede ejecutar varias veces: no borra datos y solo crea lo que falta.
set -Eeuo pipefail
cd "$(dirname "$0")"

OCA_DMS_COMMIT=74931bd0aaa62b0c4a467d2571f2c86c4eec643c
MODULO_PRINCIPAL=qm_implementacion

[[ ${EUID} -eq 0 ]] || { echo "Ejecuta este script con sudo." >&2; exit 1; }

paso() { printf '\n\033[1;32m==> %s\033[0m\n' "$*"; }

paso "1/8 Paquetes del sistema"
if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y docker.io docker-compose-v2 git curl openssl
  systemctl enable --now docker
fi
command -v git >/dev/null 2>&1 || apt-get install -y git

paso "2/8 Variables y contraseñas (.env)"
if [[ ! -f .env ]]; then
  dominio=${1:-}
  if [[ -z ${dominio} ]]; then
    ip_publica=$(curl -fsS https://api.ipify.org)
    dominio="quetzalmart.${ip_publica//./-}.sslip.io"
  fi
  clave() { openssl rand -base64 24 | tr -d '/+=' | cut -c1-20; }
  umask 077
  cat > .env <<EOF
DOMINIO=${dominio}
BD_NOMBRE=quetzalmart
POSTGRES_PASSWORD=$(clave)
ODOO_MASTER_PASSWORD=$(clave)
ODOO_ADMIN_LOGIN=admin@quetzalmart.com
ODOO_ADMIN_PASSWORD=$(clave)
CONSULTA_PASSWORD=$(clave)
EOF
  umask 022
fi
set -a
# shellcheck disable=SC1091
source .env
set +a
echo "Dominio: ${DOMINIO}"

paso "3/8 Módulo OCA DMS (gestión documental)"
if [[ ! -d oca/dms/.git ]]; then
  mkdir -p oca
  git init -q oca/dms
  git -C oca/dms remote add origin https://github.com/OCA/dms.git
fi
if [[ $(git -C oca/dms rev-parse HEAD 2>/dev/null || true) != "${OCA_DMS_COMMIT}" ]]; then
  git -C oca/dms fetch -q --depth 1 origin "${OCA_DMS_COMMIT}"
  git -C oca/dms checkout -q FETCH_HEAD
fi

paso "4/8 Configuración de Odoo"
mkdir -p generado
sed -e "s|__CLAVE_MAESTRA__|${ODOO_MASTER_PASSWORD}|" \
    -e "s|__BD_NOMBRE__|${BD_NOMBRE}|" odoo.conf.plantilla > generado/odoo.conf
chmod 0644 generado/odoo.conf

paso "5/8 Base de datos PostgreSQL"
docker compose up -d --wait db

existe=$(docker compose exec -T db psql -U odoo -d postgres -tAc \
  "SELECT 1 FROM pg_database WHERE datname='${BD_NOMBRE}'")
if [[ ${existe} != "1" ]]; then
  paso "6/8 Creación de la base ${BD_NOMBRE} e instalación de módulos (tarda 5-10 min)"
  docker compose run --rm odoo odoo -d "${BD_NOMBRE}" -i base \
    --without-demo=all --load-language=es_419 --stop-after-init
  docker compose run --rm -T -e ODOO_ADMIN_LOGIN -e ODOO_ADMIN_PASSWORD odoo \
    odoo shell -d "${BD_NOMBRE}" --no-http < scripts/preparar_compania.py
  docker compose run --rm odoo odoo -d "${BD_NOMBRE}" -i "${MODULO_PRINCIPAL}" \
    --without-demo=all --stop-after-init
else
  paso "6/8 La base ${BD_NOMBRE} ya existe: se actualizan los módulos propios"
  docker compose stop odoo
  docker compose run --rm odoo odoo -d "${BD_NOMBRE}" -u "${MODULO_PRINCIPAL}" --stop-after-init
fi

paso "7/8 Usuario de solo lectura para consultas SQL"
docker compose exec -T db psql -q -U odoo -d "${BD_NOMBRE}" \
  -v clave="'${CONSULTA_PASSWORD}'" -v bd="${BD_NOMBRE}" < scripts/rol_consulta.sql

paso "8/8 Arranque de Odoo y HTTPS"
docker compose up -d
opciones_curl=(-fsS -o /dev/null)
# Con "localhost" (pruebas en la propia PC) Caddy usa un certificado interno.
[[ ${DOMINIO} == localhost ]] && opciones_curl+=(-k)
for intento in $(seq 1 60); do
  if curl "${opciones_curl[@]}" "https://${DOMINIO}/web/login"; then
    break
  fi
  if [[ ${intento} -eq 60 ]]; then
    echo "HTTPS aún no responde. Revisa: docker compose logs caddy odoo" >&2
    exit 1
  fi
  sleep 5
done

umask 077
cat > credenciales.txt <<EOF
URL:            https://${DOMINIO}
Base de datos:  ${BD_NOMBRE}
Usuario Odoo:   ${ODOO_ADMIN_LOGIN}
Clave Odoo:     ${ODOO_ADMIN_PASSWORD}
PostgreSQL (túnel SSH, puerto 5432 de la VM):
  usuario consulta / ${CONSULTA_PASSWORD}   (solo lectura)
  usuario odoo     / ${POSTGRES_PASSWORD}   (dueño de la base)
EOF
paso "Listo"
cat credenciales.txt
echo "(Guardado en $(pwd)/credenciales.txt; no lo subas al repositorio.)"
