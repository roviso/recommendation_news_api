from datetime import date, datetime

import aioredis
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

app = FastAPI()

ret = 0
viewed_user_article = dict()

@cache(namespace="test", expire=5)
async def get_ret():
    global ret
    ret = ret + 1
    return ret


@cache(namespace="test", expire=5)
async def store_viewed_already(user_id: str, url_list: list):
    viewed_user_article[user_id] = url_list
    return viewed_user_article

    
@app.post('/view_test/{user_id}', status_code = 200)
async def view_test(user_id: str, url: list):
    urls = ['aa','bb','cc']
    all_urls = urls + url
    global viewed_user_article
    viewed_user_article.update(await store_viewed_already(user_id,all_urls))
    return viewed_user_article

    
@app.get('/view_all', status_code = 200)
async def view_test_all():
    return viewed_user_article


@app.get('/view_s', status_code = 200)
async def view_test_s(user_id: str):
    return viewed_user_article[user_id]


@app.get('/test_exist', status_code = 200)
async def view_test_s(user_id: str):
    if user_id in viewed_user_article:
        return viewed_user_article[user_id]
    else:
        return 'npuser'


    
@cache(namespace="viewed_url", expire=10)
async def store_viewed_already(user_id: str, url_list: list):
    viewed_user_article = {}
    viewed_user_article[user_id] = url_list
    return viewed_user_article



@app.get("/")
async def index(request: Request, response: Response):
    return dict(ret=await get_ret())


@app.get("/clear")
async def clear():
    return await FastAPICache.clear(namespace="test")


@app.get("/date")
@cache(namespace="test", expire=20)
async def get_data(request: Request, response: Response):
    # return date.today()
    global ret
    local_ret = str(ret + 55) + "helli"
    return local_ret


@app.get("/datetime")
@cache(namespace="test", expire=20)
async def get_datetime(request: Request, response: Response):
    return datetime.now()


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(url="redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


if __name__ == "__main__":
    uvicorn.run("main:app", debug=True, reload=True)