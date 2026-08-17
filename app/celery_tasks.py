import time

from app.celery_worker import celery


@celery.task
def long_running_task(name: str):

    print(f"Task Started for {name}")

    time.sleep(10)

    print(f"Task Completed for {name}")

    return f"Hello {name}"