import os
import sys

path = '/root/hidromed'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
os.environ['DJANGO_SECRET_KEY'] = '5bs(bg4yrv%=z66=pfpymbpbyf3w*p^b69j=j6=wu6(=(4jpdp'
os.environ['DJANGO_ALLOWED_HOSTS'] = '104.131.171.9'
os.environ['DJANGO_ADMIN_URL'] = '104.131.171.9/admin'
os.environ['DJANGO_MAILGUN_API_KEY'] = ''
os.environ['DJANGO_MAILGUN_SERVER_NAME'] = ''
os.environ['DJANGO_AWS_ACCESS_KEY_ID'] = ''
os.environ['DJANGO_AWS_SECRET_ACCESS_KEY'] = ''
os.environ['DJANGO_AWS_STORAGE_BUCKET_NAME'] = ''
os.environ['DATABASE_URL'] = 'mysql://root:root@localhost/hidromed'
os.environ['DJANGO_SECURE_SSL_REDIRECT'] = 'False'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
