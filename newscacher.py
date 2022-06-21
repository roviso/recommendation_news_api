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
import json


NewsRecommended = List[Dict[str, Union[str, List[str]]]]
# redis = aioredis.from_url(cacheconfig.redis_url, decode_responses=True)
UrlRecommended = List[str]

UserKeywords = List[str]


class KeywordsCache():
    def __init__(self):
        self.redis = aioredis.from_url(cacheconfig.redis_url, decode_responses=True)
    
    async def add_to_cache(self,user_id: str,userKeywords : UserKeywords):
        await self.redis.lpush(f'UserKeywords:{user_id}',*userKeywords)
        await self.redis.expire(f'UserKeywords:{user_id}',cacheconfig.KEYWORDS_EXPIRY_TIME)

    async def read_from_cache(self,user_id: str):
        return await self.redis.lrange(f'UserKeywords:{user_id}',0,-1)

    async def delete_from_cache(self,user_id: str,keyword:str):
        print(f'url_recommended:{user_id}',0,keyword)
        return await self.redis.lrem(f'UserKeywords:{user_id}',0,keyword)

    async def get_len(self,user_id: str):
        return await self.redis.llen(f'UserKeywords:{user_id}')

    async def clear_cache_from_list(self,user_id, userKeywords : UserKeywords):
        article_to_remove = [self.delete_from_cache(user_id,news) for news in userKeywords]

        await asyncio.gather(
            *article_to_remove
        )
        

keywordcache = KeywordsCache()





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



class LatestNewsCache(UserCache):
    def __init__(self):
        super().__init__()

    async def add_to_cache(self, news_index, latestNews):
        await self.redis.set(f'latest_news:{news_index}', json.dumps(latestNews)) ## saving nested dict as str to decode later when read
        await self.redis.expire(f'latest_news:{news_index}',cacheconfig.LATEST_EXPIRY_TIME)

    
    async def cache_news(self, latestNewsList):
        row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}
        news_list = []
        for i,news in enumerate(latestNewsList):
            news_dict = row2dict(news)
            news_dict.update({'author': row2dict(news.author)})
            keywords_list = []
            for key in news.keywords:
                keywords = row2dict(key)
                keywords.update({"keyword": row2dict(key.keyword)})
                keywords_list.append(keywords)
            # keywords_list = [row2dict(key).update({"keyword": row2dict(key.keyword)})  for key in news.keywords ]
            news_dict.update({'keywords': keywords_list})
            news_list.append(news_dict)
        latest_news_set = [self.add_to_cache(i,news) for i,news in enumerate(news_list)]

        await asyncio.gather(
            *latest_news_set
        )

    
    async def read_news_from_cache(self, news_index: int):
        latest_news_as_bytes = await self.redis.get(f'latest_news:{news_index}')
        # print(latest_news_as_bytes, type(latest_news_as_bytes))
        # latest_news_obj_as_str = latest_news_as_bytes.decode("utf-8")
        latest_news_obj_as_dict = json.loads(latest_news_as_bytes)
        latest_news_obj_as_dict.update({'content':ast.literal_eval(latest_news_obj_as_dict['content'])}) ##converting content as str to list
        latest_news_obj_as_dict.update({'additional_img':ast.literal_eval(latest_news_obj_as_dict['additional_img'])}) ##converting additional_img as str to list
        return latest_news_obj_as_dict

    async def read_all_news_from_cache(self, offset: int, limit: int):
        news_list = [await self.read_news_from_cache(i) for i in range(offset, offset+limit)]
        return news_list

    async def check_news_exists(self, news_index: int):
        return await self.redis.exists(f"latest_news:{news_index}")

latestnewscache = LatestNewsCache()


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


    async def cache_latest_news(self,user_id:str,recommended_news_list):
        # for i,news in enumerate(recommended_news_list):
        #     # print(i,news.__dict__.items())
        #     for k,v in news.__dict__.items():
        #         print(k,v)
        #     author = news.__dict__.get('author')
        #     print('author::: ',author.__dict__.items() )

        #     keywords = news.keywords
        #     # keywords = keyword.__dict__.get('keywords')
        #     for tag in keywords:

        #         print("tag is :::: ", tag.keyword.__dict__.items())

        news_set = [self.add_to_cache(user_id,i,{k: str(v) for k,v in news.items()}) for i,news in enumerate(recommended_news_list)]

        await asyncio.gather(
            self.add_user(user_id),
            *news_set
        )
    
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


