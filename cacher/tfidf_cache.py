
from typing import List,Dict,Union,Optional,Mapping
import functools
import aioredis
import ast
import asyncio
from config import cacheconfig
import random
from collections import OrderedDict
import time

TfidfDict = Mapping[str, float]



class TfidfCache():
    def __init__(self):
        self.redis = aioredis.from_url(cacheconfig.redis_url, decode_responses=True)
    

    async def cache_latest_tfidf(self, tfidf_dict: TfidfDict):
        expiryTime = time.time() + 60
        await asyncio.gather(
            self.redis.hmset('tfidf_dict',tfidf_dict),
        )
        await asyncio.gather(self.redis.expire('tfidf_dict',cacheconfig.TFIDF_EXPIRY_TIME))

    async def cache_exits(self):
        return await self.redis.exists(f'tfidf_dict')


    async def read_from_cache(self) -> TfidfDict:
        if await self.cache_exits():
            tfidf_dict =  await self.redis.hgetall(f'tfidf_dict')
        
            return tfidf_dict
    
tfidfcache = TfidfCache()