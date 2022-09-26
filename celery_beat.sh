#!/bin/bash
cd /home/admin/web/newstalk/recommendation_news_api
eval "$(conda shell.bash hook)"
conda activate py38
/root/miniconda3/envs/py38/bin/celery beat -A tasks --scheduler celery_pool_asyncio:PersistentScheduler
