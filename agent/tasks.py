from celery import shared_task


@shared_task()
def put_on_queue(data):
    pass
