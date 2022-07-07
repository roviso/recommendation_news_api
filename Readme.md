## To restart postgress
systemctl restart postgresql


## to Start celery scrapping
celery worker -A tasks -P celery_pool_asyncio:TaskPool --scheduler celery_pool_asyncio:PersistentScheduler
celery beat -A tasks --scheduler celery_pool_asyncio:PersistentScheduler

## Required Files:
 - 
