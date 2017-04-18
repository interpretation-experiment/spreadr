Gistr Backend
=============

Works behind Gistr.

Get up and started
------------------

```shell
sudo apt-get install python3-dev libzmq-dev
mkvirtualenv -p $(which python3) spreadr
pip install -r requirements.txt
python -m nltk.downloader punkt  # And copy ~/nltk_data to /usr/local/share
                                 # when using a system user for spreadr
python manage.py runserver
```

Note that the `/trees/lock_random_tree` route uses SQL's `SELECT ... FOR
UPDATE` which is not supported by sqlite (calling it with sqlite will fail with
a 500 error), so you'll have to use the MySQL setup to run all routes.


Merging databases
-----------------

You might want to launch an experiment in batches to reduce the duration of the experiment for individual participants, and then merge the resulting databases into a single one for the analysis. To do that:

* For each batch `exp_Xa`, `exp_Xb`, `exp_Xc` (etc.), export the database of the individual batch to a json, using: `./export_db.sh spreadr_exp_Xa exp_Xa.json`
* Merge the json files, using: `python merge_dbs.py --outfile exp_X.json exp_Xa.json exp_Xb.json [ exp_Xc.json ... ]`
* Create a new database in MySQL to hold the merged batches: `echo "CREATE DATABASE spreadr_exp_X CHARACTER SET utf8;" | mysql -u root`
* Give all privileges to the analysis user on that database: `echo "GRANT ALL ON spreadr_exp_X.* TO 'spreadr_analysis'@'localhost';" | mysql -u root`
* Migrate the new database (the following is in the fish shell): `env DJANGO_SETTINGS_MODULE=spreadr.settings_analysis DB_NAME=spreadr_exp_X python manage.py migrate`
* And finally load the merged json in the new database: `env DJANGO_SETTINGS_MODULE=spreadr.settings_analysis DB_NAME=spreadr_exp_X python manage.py loaddata exp_X.json`

Finally, you can re-export the merged database with `mysqldump -u root --databases spreadr_exp_X > exp_X.sql` to get the result in SQL form, easily importable elsewhere.
