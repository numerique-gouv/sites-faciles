postdeploy: python manage.py migrate && python manage.py update_index
web: gunicorn config.wsgi --log-file -
