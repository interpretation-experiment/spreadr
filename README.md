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
