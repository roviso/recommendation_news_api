## Start venv
.\apienv\Scripts\activate


## To restart postgress
systemctl restart postgresql

## to kill process

sudo kill -9 `sudo lsof -t -i:8000`

## to Start celery scrapping
celery worker -A tasks -P celery_pool_asyncio:TaskPool --scheduler celery_pool_asyncio:PersistentScheduler
celery beat -A tasks --scheduler celery_pool_asyncio:PersistentScheduler

## Required Files:
 - 

<!-- delete from "article" where type="latest" -->
<!-- git remote set-url origin https://roviso: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@github.com/roviso/recommendation_news_api.git -->