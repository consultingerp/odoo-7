# odoo

## Restoring a production dump on local development

First you need to make sure you get all the enterprise modules to your working copy by executing `fetch-enterprise.sh` script from the repository root. It will ask for a ssh login you will find at [https://www.odoo.sh/project/ghuedu/branches/master/settings](https://www.odoo.sh/project/ghuedu/branches/master/settings).

You also need to download a production dump which you can restore locally, you will get it at [https://www.odoo.sh/project/ghuedu/branches/master/backups](https://www.odoo.sh/project/ghuedu/branches/master/backups). **NOTE**: Do not download a automatic backup but a dump!

After downloading, go to http://localhost:8069/web/database/manager and restore your database from the dump (e.g. ghuedu-master-306626.dump.zip). Please remember the database name you've chosen to be able to update the password of the user you want to access.

Gain access to whatever user you want by executing the `./set-user-password.sh` script, e.g. 
```
./set-user-password.sh {DATABASE_NAME} {PASSWORD} {USERNAME - defaults to admin@ghu.edu.cw}
```
