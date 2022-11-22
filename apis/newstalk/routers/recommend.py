from typing import Union
from crud.crud_user import UserCrud
from crud.crud_likes import Likes
from fastapi import APIRouter, status, HTTPException,Depends,Query
from implicit.als import AlternatingLeastSquares
from sklearn.feature_extraction.text import TfidfVectorizer
from config import pathconfig
from schemas import article_schema
from database import async_session
from models import user_model
from crud.crud_article import ArticleCrud
from crud.crud_latest import LatestCrud
from crud.crud_recommendation import RecommendationCrud
from repository.ncf_recommender.loader import load_pkl
from config import pathconfig
from repository.ncf_recommender import utils
import random
import database
from database import async_session
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from fastapi_pagination import paginate,LimitOffsetPage
import scipy.sparse as sparse
from routers import utils
from collections import Counter
import operator
from routers.user import get_user_keywords
from routers.keywords import update_articles_keywords
from newscacher import keywordcache, newscache, latestnewscache
import time
from apis.newstalk.routers.user import get_current_user
# from routers.recommend import *

router = APIRouter(
    prefix = "/recommend",
    tags=['recommend']
)

stop_words = []
with open('helper/non-potential-topic-word-list.txt', 'r', encoding="utf8") as reader:
    for line in reader:
        line = line.strip('\n')
        stop_words.append(line)



### _______________________________ PREPARING RECOMMENDATION ENGINE _______________________________________________
async def train_implicit_model():
    global user_id_dict,article_id_dict,sparse_user_item,model, data
    async with async_session() as session:
        async with session.begin():
            articlecrud = RecommendationCrud(session)

            user_articles_score_df = await articlecrud.get_user_article() 
            data = user_articles_score_df.dropna()
            data.rename(columns={"user_id":"user","article_id": "article"},inplace=True)

            # Create a numeric user_id and article_id column
            data['user'] = data['user'].astype("category")
            data['article'] = data['article'].astype("category")
            data['user_id'] = data['user'].cat.codes
            data['article_id'] = data['article'].cat.codes

            user_id_dict = pd.Series(data.user_id.values, index=data.user).to_dict()

            article_id_dict = pd.Series(data.article_id.values, index=data.article).to_dict()


            sparse_item_user = sparse.csr_matrix((data['score'].astype(float), (data['article_id'], data['user_id'])))


            sparse_user_item = sparse_item_user.T.tocsr()
            start = time.time()  

            model = AlternatingLeastSquares(factors=64, regularization=0.05, iterations=12, use_gpu = False)
            model.fit(2 * sparse_user_item)
            end = time.time()   
            print(f"Time Taken for TRAIN recommendation MODEL: {end - start}, ##########################################")

            # return user_id_dict,article_id_dict,sparse_user_item,model

@router.get('/train_model')
async def train_model():
    return await train_implicit_model()


class tfidf_obj():
    def __init__(self, article_keyword_df , vectorizer, X, tfidfVectors):
        self.article_keyword_df = article_keyword_df
        self.vectorizer = vectorizer
        self.X = X
        self.tfidfVectors = tfidfVectors



## function to update tfidf class object 
async def get_tfidf_verctorizer(tfidf):
    await update_articles_keywords()

    first_exists = await latestnewscache.check_news_exists(0)
    last_exists = await latestnewscache.check_news_exists(200)
    if not bool(first_exists) or not bool(last_exists):
        print("CACHING LATEST ARTICLE")
        async with async_session() as session:
            async with session.begin():
                articlecrud = ArticleCrud(session)
                all_latest_articles = await articlecrud.get_n_latest_articles(500)
                await latestnewscache.cache_news(all_latest_articles)
        
    articles = await latestnewscache.read_all_news_from_cache(0, 200)
    # print(f"articles in cache is: {articles}")

    article_keyword = {article['id'] : [str(keyword['keyword']['tag']) for keyword in article['keywords'] ] for article in  articles if article['keywords']}

    article_keyword_df = pd.DataFrame(list(article_keyword.items()), columns = ['article_id','keywords_words'])

    article_keyword_df.keywords_words = article_keyword_df.keywords_words.apply(lambda x: ' '.join([tags for tags in x]))

    keyword_values = article_keyword_df.keywords_words.values
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(keyword_values)
    tfidfVectors = pd.DataFrame(X.T.toarray(), index=vectorizer.get_feature_names())

    tfidf.article_keyword_df = article_keyword_df
    tfidf.vectorizer = vectorizer
    tfidf.X = X
    tfidf.tfidfVectors = tfidfVectors


    # return article_keyword_df, vectorizer, X, tfidfVectors


## initialize the tfidf object
tfidf = tfidf_obj(None,None,None,None)
user_id_dict,article_id_dict,sparse_user_item,model,data = None,None,None,None,None
## updating tfidf object on router startup
@router.on_event("startup")
async def startup_event():
    await get_tfidf_verctorizer(tfidf)
    await train_implicit_model()


## Function to get similar articles list using tfidf 
def get_similar_articles(q):
    # print("query:", q)
    print("Articles with high cosine similarity are: ")
    q = [q]
    q_vec = tfidf.vectorizer.transform(q).toarray().reshape(tfidf.tfidfVectors.shape[0],)
    sim = {}
    for i in range(tfidf.tfidfVectors.shape[1]):
        sim[i] = np.dot(tfidf.tfidfVectors.loc[:, i].values, q_vec) / np.linalg.norm(tfidf.tfidfVectors.loc[:, i]) * np.linalg.norm(q_vec)

    sim_sorted = sorted(sim.items(), key=lambda x: x[1], reverse=True)

    article_list = []

    for k, v in sim_sorted:
        if v >= 0.25:
            # print("Article Similarity:", v)
            # print(pre.article_df.article_id.iloc[k])
            article_list.append(tfidf.article_keyword_df.article_id.iloc[k])

    return article_list


## ____Function to extract keyword from recent articles provided____
def get_trending_keywords(recent_articles):
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


## this function returns similar articles based on Collaborative Filtering algorithm
def get_similar_cf_articles(article_list):
    similar_article_ids = []
    # similar_article_ids = [ids for article_id in article_list for ids,_ in model.similar_items(int(article_id_dict.get(article_id)))]
    for article_id in article_list:
        if article_id in article_id_dict:
            ids, scores= model.similar_items(int(article_id_dict.get(article_id)))
            similar_article_ids.extend(ids)

    similar_article_ids = [data.article.loc[data.article_id == id].iloc[0] for id in similar_article_ids if id in user_id_dict]
    return similar_article_ids

## this function returns recommended articles for certain user based on Collaborative Filtering algorithm
def get_recommended_cf_articles(user_id):
    # recommended_article_ids = [ids for ids, scores in model.recommend(user_id, sparse_user_item[user_id], N=10, filter_already_liked_items=False)]
    recommended_article_ids = []
    cf_user_id = user_id_dict.get(user_id)
    ids, scores = model.recommend(cf_user_id, sparse_user_item[cf_user_id], N=len(article_id_dict), filter_already_liked_items=False)

    recommended_article_ids.extend(ids)
    recommended_article_ids = [data.article.loc[data.article_id == id].iloc[0] for id in recommended_article_ids]

    return recommended_article_ids



## Router => RETURNS articles based on tags(back relationship method)
@router.get('/tags')
async def recommend_by_tags(tags: str, async_session: Session = Depends(database.get_session), current_user: user_model.User = Depends(get_current_user)):
    article_list =  get_similar_articles(tags)
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            articles = [await articlecrud.search_article(article_id) for article_id in article_list]

    return articles



@router.get('/similar/{article_id}', response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def recommend_similar_articles(article_id: str, user_id: str, async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            article = await articlecrud.search_article(article_id)
            keywords = ' '.join([str(keyword.keyword.tag) for keyword in article.keywords])

            tfidf_similar_article_list =  get_similar_articles(keywords)

            cf_similar_article_list = get_similar_cf_articles(tfidf_similar_article_list)


            all_article_list = list(set([article.id] +tfidf_similar_article_list + cf_similar_article_list))

            similar_articles = await articlecrud.get_all_articles_by_id(all_article_list)

    for article in similar_articles:
        article.url =  f"http://newstalk.prixa.net/redirect/{article.id}?user_id={user_id}&referrer=from_web"

    return  paginate(similar_articles)
    # return {"item": articles,
    #         "total": len(articles),
    #         "limit": limit,
    #         "offset": offset}


@router.get('/user', response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def recommend_user_articles(current_user: user_model.User = Depends(get_current_user),async_session: Session = Depends(database.get_session)):
    user_id = current_user.id
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            likes = Likes(session)
            ### ____________-- Getting user keyword from model dataframe -- ____________________
            # user = pre.user_df.query(f'user == "{user_id}"')
            # keyword_list = [str(keyword) for keyword in user['user_keywords']]

            ### ___________ -- GETTING USER KEYWORD FROM HISTORY -- __________________
            keywords_len = await keywordcache.get_len(user_id)
            if keywords_len == 0:
                print("USER NOT IN CACHE")
                keyword_list = await get_user_keywords(user_id)
                print("keyword_list is ::: ", keyword_list)
                if not keyword_list:
                    keyword_list = await keywordcache.read_from_cache("trending")
                    if not keyword_list:
                        recent_articles = await articlecrud.get_all_article(0, 100)
                        keyword_list = get_trending_keywords(recent_articles)
                await keywordcache.add_to_cache(user_id,keyword_list)
            else:
                print("USER ALREADY CACHED")
                keyword_list = await keywordcache.read_from_cache(user_id)
                
            keywords = ' '.join([str(keyword) for keyword in keyword_list]) 

            
            tfidf_similar_article_list =  get_similar_articles(keywords)



            cf_similar_article_list = get_similar_cf_articles(tfidf_similar_article_list)

            if user_id not in user_id_dict:
                user_id = random.choice(list(user_id_dict))

            cf_recommended_article_list = get_recommended_cf_articles(user_id)

            all_recommended_article_list = list(set(cf_recommended_article_list + cf_similar_article_list + tfidf_similar_article_list))
            # + cf_similar_article_list))
            all_liked_articles = await likes.get_all_liked_articles(user_id=user_id)

            liked_ids = [liked_articles.id for liked_articles in all_liked_articles]
            recommended_article_list = [id for id in all_recommended_article_list if id not in liked_ids]

            recommended_articles = await articlecrud.get_all_articles_by_id(recommended_article_list)

        ## Replacing with redirect url
        for article in recommended_articles:
            article.url =  f"http://newstalk.prixa.net/redirect/{article.id}?user_id={user_id}&referrer=from_web"

        return  paginate(recommended_articles)



def update_dictionary(old_dict, new_dict):
    for key in old_dict:
        if key in new_dict:
            new_dict[key] = new_dict[key] + old_dict[key]
        else:
            new_dict.update({key: old_dict[key]})
    
    return new_dict



@router.get('/latest_news', response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def latest_news(offset: int = 0, limit: int = Query(default=50), async_session: Session = Depends(database.get_session),current_user: user_model.User = Depends(get_current_user)):
    first_exists = await latestnewscache.check_news_exists(offset)
    last_exists = await latestnewscache.check_news_exists(offset+limit)
    if not bool(first_exists) or not bool(last_exists):
        print("CACHING LATEST ARTICLE")
        async with async_session as session:
            async with session.begin():
                articlecrud = ArticleCrud(session)
                all_latest_articles = await articlecrud.get_n_latest_articles(50+offset+limit)
                await latestnewscache.cache_news(all_latest_articles)

    latest_articles = await latestnewscache.read_all_news_from_cache(0, limit + offset)

    return paginate(latest_articles)
