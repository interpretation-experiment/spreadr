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
