from fastapi import APIRouter,Depends
from typing import List

from crud.crud_keywords import KeywordsCrud
from crud.crud_latest import LatestCrud
from crud.crud_recommendation import RecommendationCrud

from schemas import article_schema, keywords_schema, recommendation_schema
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
import time
import random
import scipy.sparse as sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from implicit.als import AlternatingLeastSquares
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



# if keywords_len == 0:
#                 print("USER NOT IN CACHE")
#                 keyword_list = await get_user_keywords(user_id)
#                 print("keyword_list is ::: ", keyword_list)
#                 if not keyword_list:
#                     keyword_list = await keywordcache.read_from_cache("trending")
#                     if not keyword_list:
#                         # recent_articles = await articlecrud.get_all_article(0, 100)
#                         # keyword_list = get_trending_keywords(recent_articles)
                        
#                         top_articles = await latestcrud.get_top_article(5)
#                         keyword_list = get_trending_keywords(top_articles)
#                 await keywordcache.add_to_cache(user_id,keyword_list)
                


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




@router.get('/search_articles/{tags}', response_model = LimitOffsetPage[article_schema.SearchArticleByTag])
async def search_articles(tag: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            # print(f"searching the tag: {tag}")
            tagged_articles = await keywordcrud.search_articles_by_keywords(tag)
            # print(f"Searched Articles with tag: {tag} are : {tagged_articles}")
    # print(tagged_articles[0].__dict__)
    return paginate(tagged_articles)


@router.get('/getkeyword/{keyword_id}')
async def search_keyword_by_id(keyword_id: int, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            keyword = await keywordcrud.get_keyword(keyword_id)
    return keyword


@router.get('/checkkeyword/{keyword_tag}')
async def checkkeyword(keyword_tag: str):
    async with async_session() as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            keyword = await keywordcrud.get_keyword_by_tag(keyword_tag)
    return keyword



@router.post('/create_keyword/', status_code = 200)
async def create_keyword(tag: str):
    # article_id = secrets.token_urlsafe(32)
    
    async with async_session() as session:
        async with session.begin():
            
            new_keyword = article_model.Keywords(tag = tag)
            
            keywordcrud = KeywordsCrud(session)
            await keywordcrud.create_keywords(new_keyword)

            return await keywordcrud.get_keyword_by_tag(tag)

@router.post('/delete_keywords/')
async def delete_keywords(keyword_ids: List[int], async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            for id in keyword_ids:
                keyword = await keywordcrud.get_keyword(id)
                if keyword:
                
                    print(f"Removing keyword: {keyword_ids}: {keyword}")
                    await keywordcrud.delete_keyword(id)  
                else:
                    print(f"NO KEYWORD OF ID: {id} FOUND")

@router.post('/add_article_keywords',status_code = 200 )
async def add_article_keywords(keywords: List[str], article_id: str ):
    tagNotInDb = [tag  for tag in keywords if not await checkkeyword(tag)]

    for tag in tagNotInDb:
        await create_keyword(tag) 
    
    tagInDb = [await checkkeyword(tag) for tag in keywords]

    async with async_session() as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            latestcrud = LatestCrud(session)
            for tag in tagInDb:
                articlekeyword = article_model.AricleKeywords(
                    article_id = article_id,
                    keywords_id = tag.Keywords.id
                )
                await keywordcrud.link_article_keyword(articlekeyword)
            return await latestcrud.get_article_by_id(article_id)


@router.get('/update_keywords', status_code = 200)
async def update_keywords(article, tfidf_dict):
# -> List[article_model.LatestArticle]:
    CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    # html_filter = HTMLFilter()
    # html_filter.feed(article.content[0])
    content = [re.sub(CLEANR, '', article.heading + ' ' + strip_tags(article.content[0])) ]
    # print(content,1111111111111111111)
    try:
        keywords = tfidf_generator.extract_keywords(content, tfidf_dict, 20)
        final_keywords = reduce(add ,keywords)
    except:
        try:
            keywords = tfidf_generator.extract_keywords(content, tfidf_dict, 10)
            final_keywords = reduce(add ,keywords)
        except:
            keywords = [key for key in random.sample(list(content[0].split()),int(0.2 * len(content[0].split()))) if len(key)>=5]
            final_keywords = keywords
    

    return await add_article_keywords(final_keywords,article.id)


#     CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
#     async with async_session() as session:
#         async with session.begin():
#             latestcrud = LatestCrud(session)
#             keywordcrud = KeywordsCrud(session)
#             #if await tfidfcache.cache_exits():
#             #    tfidf_dict = await tfidfcache.read_from_cache()
#             #else:
#             # articles = await latestcrud.get_all_latest_article()
#             articles = await keywordcrud.get_article_no_keyword()
#             print(articles)
                


#             article_text = [re.sub(CLEANR, '', article.heading + ' ' + reduce(add ,article.content))  for article in articles if article.content]

#             train_df = pd.DataFrame(article_text, columns= ['text'])
#             tfidf_dict = tfidf_generator.train_idfs(train_df)

#  #           await tfidfcache.cache_latest_tfidf(tfidf_dict) ##Caching tfidf values in dictrionary 

#             article = await latestcrud.get_article_by_id(article_id)
    #         content = [re.sub(CLEANR, '', article.heading + ' ' + reduce(add ,article.content)) ]
    #         # print(content,1111111111111111111)
    #         try:
    #             keywords = tfidf_generator.extract_keywords(content, tfidf_dict, 20)
    #         except:
    #             keywords = tfidf_generator.extract_keywords(content, tfidf_dict, 10)
    #         final_keywords = reduce(add ,keywords)

    # return await add_article_keywords(final_keywords,article_id)
    # return final_keywords



@router.get('/get_article_with_no_keywords')
async def get_article_with_no_keywords(async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            article_with_no_keywords =  await keywordcrud.get_article_no_keyword()
            article_ids_with_no_keywords = [article.id for article in article_with_no_keywords]

    return article_ids_with_no_keywords


@router.get('/update_articles_keywords')
async def update_articles_keywords():
    print(f"Updating Latest Article Keywords...")
    CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    async with async_session() as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            article_with_no_keywords =  await keywordcrud.get_article_no_keyword()
            if not article_with_no_keywords:
                print("ALL ARTICLES HAS KEYWORDS :)")
                return 
            # article_ids_with_no_keywords = [article.id for article in article_with_no_keywords]
            html_filter = HTMLFilter()
            # article_text = [re.sub(CLEANR, '', article.heading + ' ' + reduce(add ,article.content))  for article in article_with_no_keywords if article.content]


            article_text = [re.sub(CLEANR, '', article.heading + ' ' + strip_tags(article.content[0]))  for article in article_with_no_keywords if article.content]

            train_df = pd.DataFrame(article_text, columns= ['text'])
            tfidf_dict = tfidf_generator.train_idfs(train_df)


    updated_articles = [await update_keywords(article,tfidf_dict) for article in article_with_no_keywords]
    return updated_articles
