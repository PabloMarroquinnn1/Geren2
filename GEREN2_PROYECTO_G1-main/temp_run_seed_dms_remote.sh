#!/bin/sh
set -eu
db_password="$(sudo docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' quetzalmart-db | sed -n 's/^POSTGRES_PASSWORD=//p')"
sudo docker exec quetzalmart-odoo sh -lc 'mkdir -p /tmp/dms_uploads_new'
sudo docker cp /tmp/dms_uploads/. quetzalmart-odoo:/tmp/dms_uploads_new/
sudo docker cp /tmp/temp_seed_dms_files.py quetzalmart-odoo:/tmp/temp_seed_dms_files.py
sudo docker exec -i -e DB_PASSWORD="$db_password" quetzalmart-odoo \
  sh -lc 'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD"' \
  < /tmp/temp_seed_dms_files.py
