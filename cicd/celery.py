import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cicd.settings")

# App for cheap customers
app = Celery("cicd")
app.config_from_object("django.conf:settings", namespace="CELERY")
