postdeploy: python manage.py migrate && python manage.py import_dsfr_pictograms && python manage.py import_page_templates && python manage.py update_index
web: gunicorn config.wsgi --log-file -
