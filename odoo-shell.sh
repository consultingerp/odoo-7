#!/bin/bash -e

DB_NAME=${1:?"Please provide the database name you want to connect to..."}

docker-compose exec web odoo shell -d ${DB_NAME} --db_host db --db_pass odoo
