"""
WSGI config for monithorsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
#from monithor.models import Source
#from monithor.backend import SNMP
from monithor.engine import Engine
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monithorsite.settings')

application = get_wsgi_application()

# ToDo comment out for now
engine = Engine()
#snmp = SNMP()
