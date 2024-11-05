import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cicd.settings")
app = Celery("cicd")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


def get_acct_celery_app(acct):
    acct_app = Celery()
    if acct:
        acct_app.conf.update(broker_url=f'amqp://guest:bu11shit@localhost:5672/{acct}')
    else:
        acct_app.conf.update(broker_url=f'amqp://guest:bu11shit@localhost:5672//')
    return acct_app
