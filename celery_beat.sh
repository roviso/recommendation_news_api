#!/bin/bash
cd /home/admin/web/newstalk/recommendation_news_api
eval "$(conda shell.bash hook)"
conda activate scrapenv
/root/miniconda3/envs/scrapenv/bin/celery beat -A tasks --scheduler celery_pool_asyncio:PersistentScheduler
