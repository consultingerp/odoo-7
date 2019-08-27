#!/bin/bash -e

DB_NAME=${1:-production}

docker-compose exec web odoo shell --shell-interface ipython -d ${DB_NAME} --db_host db --db_pass odoo
