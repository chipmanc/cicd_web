from celery import shared_task


@shared_task
def put_on_queue(data):
    print(__name__)
    print(data)
    return
