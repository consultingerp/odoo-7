#!/bin/bash -e

# SSH_LOGIN=${1:?"Please provide the ssh login to the production server to fetch the enterprise modules and themes from (e.g. 306626@ghuedu.odoo.com)..."}
SSH_LOGIN=${1:-306626@ghuedu.odoo.com}

echo "Fetching enterprise addons and themes from ${SSH_LOGIN}..."

rsync -azvhP --exclude .git --exclude .gitignore ${SSH_LOGIN}:/home/odoo/src/enterprise/ ./enterprise/addons/
rsync -azvhP --exclude .git --exclude .gitignore ${SSH_LOGIN}:/home/odoo/src/odoo/ ./enterprise/odoo/
rsync -azvhP --exclude .git --exclude .gitignore ${SSH_LOGIN}:/home/odoo/src/themes/ ./enterprise/themes/

# fetch installed packages
mkdir -p ./_/odoo/apt
ssh ${SSH_LOGIN} -C "dpkg --get-selections" > ./_/odoo/apt/package.list
rsync -azvhP ${SSH_LOGIN}:/etc/apt/sources.list* ./_/odoo/apt/sources
ssh ${SSH_LOGIN} -C "apt-key exportall" > ./_/odoo/apt/repo.keys
ssh ${SSH_LOGIN} -C "pip freeze" | sed "/==0.0.0/d" > ./_/odoo/apt/requirements.txt
