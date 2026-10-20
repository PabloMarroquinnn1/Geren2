#!/usr/bin/env bash
set -euo pipefail

sudo docker cp /tmp/seed_block7_ga4.py quetzalmart-odoo:/tmp/seed_block7_ga4.py
DB_PASSWORD="$(sudo awk -F= '/^POSTGRES_PASSWORD=/{print substr($0,index($0,"=")+1)}' /opt/quetzalmart/.env)"
sudo docker exec -i -e DB_PASSWORD="$DB_PASSWORD" quetzalmart-odoo sh -lc \
  'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD" < /tmp/seed_block7_ga4.py'
