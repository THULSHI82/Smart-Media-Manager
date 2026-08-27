from celery import Celery
from config import Config

celery = Celery('smart_media_manager', broker=Config.REDIS_URL, backend=Config.REDIS_URL)
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    task_track_started=True,
    task_always_eager=Config.CELERY_TASK_ALWAYS_EAGER,
)


@celery.task(name='tasks.process_image_task')
def process_image_task(image_id: str, job_id: str):
    from tasks import process_image
    return process_image(image_id, job_id)
