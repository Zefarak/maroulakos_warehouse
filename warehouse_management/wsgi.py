import os
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_management.settings')

application = get_wsgi_application()
application = WhiteNoise(application)
