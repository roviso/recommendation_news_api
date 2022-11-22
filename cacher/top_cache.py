from typing import List,Dict,Union,Optional
from schemas import profile_schema
import functools
import aioredis
import ast
import asyncio
from config import cacheconfig
import random
from collections import OrderedDict
import json

# LatestNews = List[Dict[str, Union[str, List[str]]]]
Sources = List[Dict[str, Union[str, int]]]

Articles = List[Dict[str, Union[str, int]]]

class TopCache():
    def __init__(self):
        self.redis = aioredis.from_url(cacheconfig.redis_url, decode_responses=True)
    
    async def add_source_to_cache(self,rank,source ):
        await asyncio.gather(
            self.redis.hmset(f'top_source:{rank}',source),
            self.redis.expire(f'top_source:{rank}',cacheconfig.TOP_SOURCE_EXPIRY_TIME),
        )

    
    async def add_author_to_cache(self,rank,source ):
        await asyncio.gather(
            self.redis.hmset(f'top_author:{rank}',source),
            self.redis.expire(f'top_author:{rank}',cacheconfig.TOP_AUTHOR_EXPIRY_TIME),
        )

    
    async def cache_source_exits(self,rank:Optional[int] = None):
        if not rank:
            rank = random.randint(0, 7)
        cached_source =  await self.redis.exists(f'top_source:{rank}')
        return cached_source

    async def cache_author_exits(self,rank:Optional[int] = None):
        if not rank:
            rank = random.randint(0, 7)
        cached_source =  await self.redis.exists(f'top_author:{rank}')
        return cached_source


    async def read_source_from_cache(self, rank:int):
        if self.cache_source_exits(rank):
            cached_news =  await self.redis.hgetall(f'top_source:{rank}') 
            return cached_news

    async def read_author_from_cache(self, rank:int):
        if self.cache_author_exits(rank):
            cached_news =  await self.redis.hgetall(f'top_author:{rank}') 
            return cached_news


    async def cache_source(self,top_sources_list):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        source_list = []
        for i,source in enumerate(top_sources_list):
            source_dict = row2dict(source)
            source_dict.update({'followers': source.followers})
            source_dict.update({'total_articles': source.total_articles})
            source_dict.update({'total_likes': source.total_likes})
            source_dict.update({'total_views': source.total_views})
            source_list.append(source_dict)

        top_source_set = [self.add_source_to_cache(i,news) for i,news in enumerate(source_list)]

        await asyncio.gather(
            *top_source_set
        )

    
    async def cache_author(self,top_author_list):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        author_list = []
        for i,author in enumerate(top_author_list):
            author_dict = row2dict(author)
            author_dict.update({'followers': author.followers})
            author_dict.update({'following': author.following})
            author_dict.update({'total_articles': author.total_articles})
            author_dict.update({'total_likes': author.total_likes})
            author_dict.update({'total_views': author.total_views})
            author_list.append(author_dict)

        top_author_set = [self.add_author_to_cache(i,news) for i,news in enumerate(author_list)]

        await asyncio.gather(
            *top_author_set
        )

    
    async def read_source_from_cache(self, source_rank: int):
        top_source_as_bytes = await self.redis.hgetall(f'top_source:{source_rank}')

        return top_source_as_bytes

    async def read_author_from_cache(self, author_rank: int):
        top_author_as_bytes = await self.redis.hgetall(f'top_author:{author_rank}')
        return top_author_as_bytes

    async def read_top_sources(self,):
        top_source_list = [await self.read_source_from_cache(i) for i in range(0, 8)]
        return top_source_list

    async def read_top_authors(self,):
        top_author_list = [await self.read_author_from_cache(i) for i in range(0, 8)]
        return top_author_list


    
        
topcache = TopCache()
