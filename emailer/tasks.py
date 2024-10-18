import os
from celery import Celery
from django.conf import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@app.task(name='tasks.process_email_task')
def process_email_task(email_data):
    logger.info(f"Processing email to: {email_data['email']}, collection_name: {email_data['collection_name']}, operation_type: {email_data['operation_type']}, entity_id: {email_data['entity_id']}")
    # Simulate email sending (replace with actual email sending logic)
    # send_email(email_data['email'], email_data['subject'], email_data['body'])

if __name__ == "__main__":
    logger.info("Starting Celery worker...")
    app.worker_main(['worker', '--loglevel=info'])
