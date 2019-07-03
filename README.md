# odoo

## Restoring a production dump on local development

All you need to do is to go to download a production dump which you can restore locally, you will get it at [https://www.odoo.sh/project/ghuedu/branches/master/backups](https://www.odoo.sh/project/ghuedu/branches/master/backups). **NOTE**: Do not download a automatic backup but a dump (you don't need to include filestore since it's downloaded from `fetch-production.sh` script)!

After downloading, place it into the root folder of the project (make sure its name is `ghuedu-master-306626.dump.zip`) and execute the `restore-production.sh` script.
You can then start docker-compose and login with `admin@ghu.edu.cw / test` at [http://localhost:8069](http://localhost:8069).
