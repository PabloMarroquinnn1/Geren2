#!/bin/sh
set -eu

script_name="$1"
case "$script_name" in
  inspect_dms_sources.py|build_dms_records.py|log_dms_simulated_flow.py|archive_existing_invoices_to_dms.py|test_invoice_dms_auto_archive.py) ;;
  *) echo "Unsupported script" >&2; exit 2 ;;
esac

db_password="$(sudo docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' quetzalmart-db | sed -n 's/^POSTGRES_PASSWORD=//p')"
sudo docker exec -i -e DB_PASSWORD="$db_password" quetzalmart-odoo \
  sh -lc 'odoo shell -c /etc/odoo/odoo.conf -d quetzalmart --no-http --db_host=postgres --db_port=5432 --db_user=odoo --db_password="$DB_PASSWORD"' \
  < "/tmp/$script_name"
