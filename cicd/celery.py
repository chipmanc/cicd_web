import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cicd.settings")

# App for cheap customers
basic_tier = Celery("basic")
basic_tier.config_from_object("django.conf:settings", namespace="CELERY")
basic_tier.autodiscover_tasks()

# # App for paying customers
# premium_tier = Celery("premium")
# premium_tier.config_from_object("django.conf:settings", namespace="CELERY.PREMIUM")
# premium_tier.autodiscover_tasks()
#
# # App for enterprise customers
# bespoke_tier = Celery("bespoke")
# bespoke_tier.config_from_object("django.conf:settings", namespace="CELERY.BESPOKE")
# bespoke_tier.autodiscover_tasks()
