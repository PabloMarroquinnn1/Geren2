#!/usr/bin/env bash
set -euo pipefail

sudo docker cp /tmp/tag_dms_files.py quetzalmart-odoo:/tmp/tag_dms_files.py
DB_PASSWORD="$(sudo awk -F= '/^POSTGRES_PASSWORD=/{print substr($0,index($0,"=")+1)}' /opt/quetzalmart/.env)"
sudo docker exec -i -e DB_PASSWORD="$DB_PASSWORD" quetzalmart-odoo sh -lc \
  'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD" < /tmp/tag_dms_files.py'
