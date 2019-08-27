#!/bin/bash -e

DUMP_FILE=${1:-ghuedu-master-306626.dump.zip}
SSH_LOGIN=306626@ghuedu.odoo.com

# ./fetch-enterprise.sh ${SSH_LOGIN}

# echo "############################################################"
# echo "Reset containers and restore dump at ${DUMP_FILE}..."
# echo "############################################################"

# docker-compose down -v
# docker-compose build
docker-compose up -d
sleep 20

# curl -s -w "${http_code}" -L -F "master_pwd=admin" -F "name=production" http://localhost:8069/web/database/drop
echo "Restoring database..."
curl -o /dev/null -s -w "\${http_code}" -L -F "master_pwd=admin" -F "backup_file=@$DUMP_FILE" -F 'copy=true' -F 'name=production' http://localhost:8069/web/database/restore
echo "Done..."
echo

# sync production filestore
rsync -azvhP ${SSH_LOGIN}:/home/odoo/data/filestore/ghuedu-master-306626/ ./enterprise/filestore/production
docker cp ./enterprise/filestore/production odoo_web_1:/var/lib/odoo/filestore
docker exec -u root odoo_web_1 chown -R odoo:odoo /var/lib/odoo/filestore

. set-user-password.sh test

docker-compose stop
