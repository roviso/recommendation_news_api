#!/bin/bash
cd /home/admin/web/newstalk/recommendation_news_api
eval "$(conda shell.bash hook)"
conda activate py38
/root/miniconda3/envs/py38/bin/celery worker -A tasks -P celery_pool_asyncio:TaskPool --scheduler celery_pool_asyncio:PersistentScheduler
