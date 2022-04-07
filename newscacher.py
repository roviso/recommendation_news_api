from pydantic import BaseSettings
from fastapi import BackgroundTasks
from fastapi import Depends
from fastapi import FastAPI
from typing import List,Dict,Union
import functools
import aioredis
import ast
import asyncio
from pprint import pp
from config import cacheconfig
from repository.ncf_recommender.utils import content_filter
from collections import OrderedDict

NewsRecommended = List[Dict[str, Union[str, List[str]]]]
# redis = aioredis.from_url(cacheconfig.redis_url, decode_responses=True)
UrlRecommended = List[str]

class UrlCache():
    def __init__(self):
        self.redis = aioredis.from_url(cacheconfig.redis_url, decode_responses=True)
    
    async def add_to_cache(self,user_id: str,recommendedUrl : UrlRecommended):
        await self.redis.lpush(f'url_recommended:{user_id}',*recommendedUrl)
        await self.redis.expire(f'url_recommended:{user_id}',cacheconfig.URL_EXPIRY_TIME)

    async def read_from_cache(self,user_id: str):
        return await self.redis.lrange(f'url_recommended:{user_id}',0,-1)

    async def delete_from_cache(self,user_id: str,url_to_remove:str):
        print(f'url_recommended:{user_id}',0,url_to_remove)
        return await self.redis.lrem(f'url_recommended:{user_id}',0,url_to_remove)

    async def get_len(self,user_id: str):
        return await self.redis.llen(f'url_recommended:{user_id}')

    async def clear_cache_from_list(self,user_id, recommendedUrl : UrlRecommended):
        article_to_remove = [self.delete_from_cache(user_id,news) for news in recommendedUrl]

        await asyncio.gather(
            *article_to_remove
        )
        

urlcache = UrlCache()


class UserCache():
    def __init__(self):
        self.redis = aioredis.from_url(cacheconfig.redis_url, decode_responses=True)
        
    async def add_user(self,user_id: str):
        await self.redis.lpush(f'cached_user',user_id)
        # self.redis.expire(f'cached_user:{user_id}',cacheconfig.EXPIRY_TIME)

    async def clear_user_cache(self,):
        await self.redis.delete('cached_user')

    async def remove_cached_user(self,user_id: str):
        await self.redis.lrem(f'cached_user',0,user_id)

    async def get_users(self):
        return await self.redis.lrange(f'cached_user',0,-1)

usercache = UserCache()
class NewsCache(UserCache):
    def __init__(self):
        super().__init__()
    
    async def add_to_cache(self,user_id: str,news_index,recommendedNew ):
        await asyncio.gather(
            self.redis.hmset(f'recommended_news:{user_id}:{news_index}',recommendedNew),
            self.redis.expire(f'recommended_news:{user_id}:{news_index}',cacheconfig.EXPIRY_TIME),
        )

    async def remove_cached_news(self,user_id: str,news_index: int):
        await self.redis.delete(f'recommended_news:{user_id}:{news_index}')


    async def read_from_cache(self, user_id: str,news_index:str):
        cached_news =  await self.redis.hgetall(f'recommended_news:{user_id}:{news_index}')
        cached_news_changed = {key:ast.literal_eval(value) if key in ['content','additional_img'] else int(value) if key in ['likes','shares'] else value for key,value in cached_news.items()}
        # print(cached_news_changed)
        return cached_news_changed


    async def cache_news(self,user_id:str,recommended_news_list):
        news_set = [self.add_to_cache(user_id,i,{k: str(v) for k,v in news.items()}) for i,news in enumerate(recommended_news_list)]
        await asyncio.gather(
            self.add_user(user_id),
            *news_set
        )
        # await self.redis.close()

    
    async def read_cached_news(self, user_id:str,):
        cached_news = [(i,await self.read_from_cache(user_id,i)) for i in range(0,101) if await self.read_from_cache(user_id,i) ]
        cached_ordered = OrderedDict(cached_news)
        # cached_ordered = OrderedDict((i,news) for i,news in enumerate(cached_news))
        # cached_ordered = OrderedDict((index,news) for index,news in enumerate([await self.read_from_cache(user_id,i) for i in range(0,101)]) )
        return cached_ordered


    async def clear_cache_news(self,user_id:str,news_list_to_remove: List[int]):
        clear_news = [self.remove_cached_news(user_id,news_index) for news_index in news_list_to_remove]
        await asyncio.gather(
            *clear_news
        )
        
newscache = NewsCache()


