# Need to have this in both SCM and API.  So one point for another app
# that resides elsewhere, like oslo
from celery import shared_task


@shared_task
def task():
    """
    This is where the defined tasks in pipeline will get run
    :return:
    """
    print('I DID IT')
