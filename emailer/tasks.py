import os
from celery import Celery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_HOST = 'redis-11857.c276.us-east-1-2.ec2.cloud.redislabs.com'
REDIS_PORT = 11857
REDIS_USERNAME = 'default'  # Use the correct Redis user
REDIS_PASSWORD = 'Fw82cxCVcMZED9ubfJVxeuSqcCb1vFqi'  # Use your Redis password

CELERY_BROKER_URL = f'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0'

app = Celery('tasks', broker=CELERY_BROKER_URL)

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
