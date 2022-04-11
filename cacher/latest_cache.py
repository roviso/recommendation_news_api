from typing import List,Dict,Union,Optional
import functools
import aioredis
import ast
import asyncio
from config import cacheconfig
import random
from collections import OrderedDict

LatestNews = List[Dict[str, Union[str, List[str]]]]

class LatestCache():
    def __init__(self):
        self.redis = aioredis.from_url(cacheconfig.redis_url, decode_responses=True)
    
    async def add_to_cache(self,news_index,recommendedNew ):
        await asyncio.gather(
            self.redis.hmset(f'latest_news:{news_index}',recommendedNew),
            self.redis.expire(f'latest_news:{news_index}',cacheconfig.LATEST_EXPIRY_TIME),
        )
    
    async def cache_exits(self,news_index:Optional[int] = None):
        if not news_index:
            news_index = random.randint(0, 10)
        

        cached_news =  await self.redis.exists(f'latest_news:{news_index}')

        return cached_news


    async def read_from_cache(self, news_index:int):
        if self.cache_exits(news_index):
            cached_news =  await self.redis.hgetall(f'latest_news:{news_index}')
            # print(cached_news,999999999999999999999999999999999)
            cached_news_changed = {key:ast.literal_eval(value) if key in ['content','additional_img'] else int(value) if key in ['likes','shares'] else value for key,value in cached_news.items()}
            return cached_news_changed


    async def cache_news(self,trending_news_list):
        news_set = [self.add_to_cache(i,{k: str(v) for k,v in news.items()}) for i,news in enumerate(trending_news_list)]
        await asyncio.gather(
            *news_set
        )
        # await self.redis.close()

    
    async def read_cached_news(self) -> LatestNews:
        cached_news = [(i,await self.read_from_cache(i)) for i in range(0,101) if await self.cache_exits(i) ]
        cached_ordered = OrderedDict(cached_news)
        # cached_ordered = OrderedDict((i,news) for i,news in enumerate(cached_news))
        # cached_ordered = OrderedDict((index,news) for index,news in enumerate([await self.read_from_cache(user_id,i) for i in range(0,101)]) )
        return cached_ordered

        
latestcache = LatestCache()
