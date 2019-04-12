#!/bin/bash -e

SSH_LOGIN=${1:?"Please provide the ssh login to the production server to fetch the enterprise modules and themes from (e.g. 306626@ghuedu.odoo.com)..."}

rsync -azvhP --exclude .git --exclude .gitignore ${1}:/home/odoo/src/enterprise/ ./enterprise/addons/
rsync -azvhP --exclude .git --exclude .gitignore ${1}:/home/odoo/src/themes/ ./enterprise/themes/
