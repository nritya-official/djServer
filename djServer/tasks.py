from celery import shared_task
from djApi.processor import update_cache

rc = redis.Redis(
    host="redis-11857.c276.us-east-1-2.ec2.cloud.redislabs.com", port=11857,
    username="default", # use your Redis user. More info https://redis.io/docs/management/security/acl/
    password="Fw82cxCVcMZED9ubfJVxeuSqcCb1vFqi", # use your Redis password
    )
rc.set("foo","bar")

@shared_task
def keep_updating_redis():
    update_cache(rc)
    pass