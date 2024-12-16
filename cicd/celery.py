from celery import Celery


def get_acct_celery_app(acct):
    acct_app = Celery()
    if acct:
        acct_app.conf.update(broker_url=f'amqp://guest:bu11shit@localhost:5672/{acct}')
    else:
        acct_app.conf.update(broker_url=f'amqp://guest:bu11shit@localhost:5672/agent')
    return acct_app
