from fastapi import APIRouter,Depends
from typing import List
from crud.crud_keywords import KeywordsCrud
from crud.crud_latest import LatestCrud
from schemas import article_schema
from models import article_model
from repository.ncf_recommender.loader import load_pkl
from sqlalchemy.orm import Session
import database
from cacher.tfidf_cache import tfidfcache
from collections import Counter
import operator
from fastapi_pagination import paginate,LimitOffsetPage
import re
from helper import tfidf_generator
from operator import add
from functools import reduce
import pandas as pd
from database import async_session
import random

from io import StringIO
from html.parser import HTMLParser
from newscacher import keywordcache


router = APIRouter(
    prefix = "/keywords",
    tags=['keywords']
)


class HTMLFilter(HTMLParser):
    text = ""
    def handle_data(self, data):
        self.text += data.strip()


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def update_dictionary(old_dict, new_dict):
    for key in old_dict:
        if key in new_dict:
            new_dict[key] = new_dict[key] + old_dict[key]
        else:
            new_dict.update({key: old_dict[key]})
    
    return new_dict


stop_words = []
with open('helper/non-potential-topic-word-list.txt', 'r', encoding="utf8") as reader:
    for line in reader:
        line = line.strip('\n')
        stop_words.append(line)


def get_trending_keywords(recent_articles):
    # print(f"Using stopwords {stop_words}, {len(stop_words)}")

    keywords = [str(keyword.keyword.tag) for articles in  recent_articles for keyword in articles.keywords if str(keyword.keyword.tag) not in stop_words]
    keyword_count = Counter(keywords)

    keyword_popularity = {}

    for articles in  recent_articles:
        
        likes = articles.likes
        shares = articles.shares 
        views = articles.views 
        comments = articles.total_comments

        popularity = int(likes or 0)  + int(shares or 0) + int(views or 0) + int(comments or 0)
        
        keywords = [str(keyword.keyword.tag) for keyword in articles.keywords]

        article_keywords = {tag: popularity  for tag in keywords}

        keyword_popularity = update_dictionary(keyword_popularity, article_keywords)

    all_keywords = update_dictionary(keyword_popularity, keyword_count)
    trending_keywords = dict( sorted(all_keywords.items(), key=operator.itemgetter(1),reverse=True))
    return list(map(operator.itemgetter(0), trending_keywords.items()))[:20]



@router.get('/trending_keywords',)
async def trending_keywords(async_session: Session = Depends(database.get_session)):
    trending_len = await keywordcache.get_len("trending")
    if trending_len == 0:
        print("TRENDING KEYWORDS NOT IN CACHE")
        async with async_session as session:
            async with session.begin():
                latestcrud = LatestCrud(session)
                trending_articles = await latestcrud.get_trending_article()
                trending_keywords = get_trending_keywords(trending_articles)
                # print("keyword is ::: ", trending_keywords)
                await keywordcache.add_to_cache('trending',trending_keywords)
    else:
        print("TRENDING KEYWORDS IN CACHE")
        trending_keywords = await keywordcache.read_from_cache("trending")            
    return trending_keywords



@router.get('/add_stopword',)
async def add_stopword(stopword: str):
    stop_words_list = []
    with open('helper/non-potential-topic-word-list.txt', 'r', encoding="utf8") as reader:
        for line in reader:
            line = line.strip('\n')
            stop_words_list.append(line)

    if stopword in stop_words_list:
        print(f"stopword already in use")
        return 
    
    with open('helper/non-potential-topic-word-list.txt', 'a') as stopwords_file:
        stopwords_file.write(f'\n{stopword}')





