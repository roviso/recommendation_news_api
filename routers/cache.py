from fastapi import APIRouter
from newscacher import newscache, urlcache,usercache
from typing import List

router = APIRouter(
    prefix = "/cache",
    tags=['cache']
)



@router.get('/remove_cached_user/{user_id}', status_code = 200)
async def get_cached_user(user_id: str):
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await newscache.remove_cached_user(user_id)


@router.get('/cached_user/', status_code = 200)
async def get_cached_user():
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await newscache.get_users()


@router.get('/cached_news/{user_id}', status_code = 200)
async def get_recommendation_cache(user_id: str):
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await newscache.read_cached_news(user_id)
    

@router.post('/remove_cached_news/{user_id}', status_code = 200)
async def remove_cached_news(user_id: str, url_indices : List[int]):
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await newscache.clear_cache_news(user_id, url_indices)

@router.get('/clear_user_cache/', status_code = 200)
async def clear_user_cache():
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await usercache.clear_user_cache()


@router.get('/cached_url/{user_id}', status_code = 200)
async def get_url_cache(user_id: str):
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await urlcache.read_from_cache(user_id)

@router.post('/remove_cached_urls/{user_id}', status_code = 200)
async def remove_cached_urls(user_id: str, urls_to_remove: List[str]):
    # return await get_recommendation_cache_func(db, user_id,site,time)
    return await urlcache.clear_cache_from_list(user_id,urls_to_remove)
