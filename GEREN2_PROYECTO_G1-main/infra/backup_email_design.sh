#!/bin/sh
set -eu
stamp=$(date -u +%Y%m%dT%H%M%SZ)
target="/opt/quetzalmart/backups/email-design-${stamp}"
sudo mkdir -p "$target"
sudo sh -c "docker exec quetzalmart-db pg_dump -U odoo -d quetzalmart -Fc > '$target/quetzalmart.dump'"
echo "BACKUP $target"
