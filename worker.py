import os
from celery import Celery

import celery_pool_asyncio 

celery_pool_asyncio.__package__

CELERY_BROKER_URL = os.getenv("BROKER_URI", "redis://localhost:6379")
CELERY_RESULT_BACKEND = os.getenv("BACKEND_URI", "redis://localhost:6379")

celery = Celery("celery", backend=CELERY_BROKER_URL, broker=CELERY_RESULT_BACKEND)



celery.conf.beat_schedule = {
    'add-every-60-seconds': {
        'task': 'tasks.refresh_sources',
        'schedule': 60.0,
        # 'args': (16, 16)
    },
}
 
celery.conf.timezone = 'UTC'