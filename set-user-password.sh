#!/bin/bash

PASSWORD=${1:?Please provide the password you want to set as first parameter.}
DATABASE=${2:-production}
EMAIL=${3:-admin@ghu.edu.cw}

echo "Setting password ${PASSWORD} for user ${EMAIL} in database ${DATABASE}..."

HASHED_PASSWORD=`python3 -c "from passlib.context import CryptContext; print(CryptContext(schemes=['pbkdf2_sha512']).hash('test'))"`

docker-compose exec db psql --user odoo $DATABASE -c "UPDATE res_users SET password='${HASHED_PASSWORD}' where login='${EMAIL}';"
