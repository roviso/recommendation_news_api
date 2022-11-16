from typing import List,Dict,Union,Optional
import functools
import aioredis
import ast
import asyncio
from config import cacheconfig
import random
from collections import OrderedDict

# LatestNews = List[Dict[str, Union[str, List[str]]]]
Sources = List[Dict[str, Union[str, int]]]

Articles = List[Dict[str, Union[str, int]]]

class TopCache():
    def __init__(self):
        self.redis = aioredis.from_url(cacheconfig.redis_url, decode_responses=True)
    
    async def add_source_to_cache(self,rank,source ):
        await asyncio.gather(
            self.redis.hmset(f'top_source:{rank}',source),
            self.redis.expire(f'top_source:{rank}',cacheconfig.LATEST_EXPIRY_TIME),
        )
    # async def add_to_cache(self,news_index,recommendedNew ):
    #     await asyncio.gather(
    #         self.redis.hmset(f'latest_news:{news_index}',recommendedNew),
    #         self.redis.expire(f'latest_news:{news_index}',cacheconfig.LATEST_EXPIRY_TIME),
    #     )
    
    async def cache_source_exits(self,rank:Optional[int] = None):
        if not rank:
            rank = random.randint(0, 7)
        

        cached_source =  await self.redis.exists(f'top_source:{rank}')

        return cached_source


    async def read_source_from_cache(self, rank:int):
        if self.cache_source_exits(rank):
            cached_news =  await self.redis.hgetall(f'top_source:{rank}')
            # print(cached_news,999999999999999999999999999999999)
            # cached_news_changed = {key:int(value) if key in ['followers','total_articles','total_likes'] else value for key,value in cached_news.items()}
            return cached_news


    async def cache_source(self,top_sources_list):
        for i,source in enumerate(top_sources_list):
            print(f"source is :{source}.{i}")
            print(f"source is :{source.__dict__}.{dir(source)}")

        news_set = [self.add_source_to_cache(i,{k: v for k,v in source.__dict__.items()}) for i,source in enumerate(top_sources_list)]
        await asyncio.gather(
            *news_set
        )


    # async def cache_news(self,trending_news_list):
    #     news_set = [self.add_to_cache(i,{k: str(v) for k,v in news.items()}) for i,news in enumerate(trending_news_list)]
    #     await asyncio.gather(
    #         *news_set
    #     )
    #     # await self.redis.close()

    
    async def read_top_sources(self) -> Sources:
        cached_sources = [(i,await self.read_source_from_cache(i)) for i in range(0,7) if await self.cache_source_exits(i) ]
        cached_ordered = OrderedDict(cached_sources)
        # cached_ordered = OrderedDict((i,news) for i,news in enumerate(cached_news))
        # cached_ordered = OrderedDict((index,news) for index,news in enumerate([await self.read_from_cache(user_id,i) for i in range(0,101)]) )
        return cached_ordered

        
topcache = TopCache()
