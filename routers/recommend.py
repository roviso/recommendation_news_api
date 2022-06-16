from typing import Union
from crud.crud_user import UserCrud
from fastapi import APIRouter, status, HTTPException,Depends,Query
from starlette.responses import RedirectResponse
from config import pathconfig
import pickle
from schemas import clicks_schema
from schemas import article_schema
from crud.crud_redirect_clicks import ClicksCrud
from database import async_session
from crud.crud_article import ArticleCrud
from crud.crud_author import AuthorCrud
from repository.ncf_recommender.loader import load_pkl
from config import pathconfig
from repository.ncf_recommender import utils
import secrets
from models import article_model, author_model
import ast
from implicit.als import AlternatingLeastSquares
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import spsolve
from sklearn.preprocessing import MinMaxScaler
import database
from database import async_session
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from fastapi_pagination import Page, add_pagination, paginate,LimitOffsetPage;
import scipy.sparse as sparse;
from routers import utils
from collections import Counter
import operator
from routers.user import get_user_keywords


router = APIRouter(
    prefix = "/recommend",
    tags=['recommend']
)



### _______________________________ LOADING PREPROCESSING FILES _______________________________________________

print('----------Preprocessing(loading data)--------------------')
if pathconfig.PRE_PKL_PATH.is_file():
    pre = load_pkl(pathconfig.PRE_PKL_PATH)
    print('Successfully Loaded Pickle file')

if pathconfig.REDIRECT_DICT_PATH.is_file():
    with open(pathconfig.REDIRECT_DICT_PATH, 'rb') as f:
        redirect_dict = pickle.load(f)
    print('Successfully Loaded redirection url file')



### _______________________________ TFIDF SIMILARITIES CALCULATOR _______________________________________________
docs = pre.article_df.keywords_words.values
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(docs)

def get_similar_articles(q, pre):
    # print("query:", q)
    print("Articles with high cosine similarity are: ")
    q = [q]
    q_vec = vectorizer.transform(q).toarray().reshape(pre.tfidfVectors.shape[0],)
    sim = {}
    for i in range(pre.tfidfVectors.shape[1]):
        sim[i] = np.dot(pre.tfidfVectors.loc[:, i].values, q_vec) / np.linalg.norm(pre.tfidfVectors.loc[:, i]) * np.linalg.norm(q_vec)

    sim_sorted = sorted(sim.items(), key=lambda x: x[1], reverse=True)

    article_list = []

    for k, v in sim_sorted:
        if v >= 0.25:
            # print("Article Similarity:", v)
            # print(pre.article_df.article_id.iloc[k])
            article_list.append(pre.article_df.article_id.iloc[k])

    return article_list


### _______________________________ PREPARING RECOMMENDATION ENGINE _______________________________________________

print("_______________PREPARING RECOMMENDATION ENGINE_______________________________")
user_article_df = pre.df.groupby(['user','article_id']).size().reset_index(name='counts')
data = user_article_df.dropna()
data = data.copy()
data.rename(columns={"article_id": "article", "counts": "views"},inplace=True)

# Create a numeric user_id and article_id column
data['user'] = data['user'].astype("category")
data['article'] = data['article'].astype("category")
data['user_id'] = data['user'].cat.codes
data['article_id'] = data['article'].cat.codes

user_id_dict = pd.Series(data.user_id.values, index=data.user).to_dict()

article_id_dict = pd.Series(data.article_id.values, index=data.article).to_dict()


sparse_item_user = sparse.csr_matrix((data['views'].astype(float), (data['article_id'], data['user_id'])))


sparse_user_item = sparse_item_user.T.tocsr()

model = AlternatingLeastSquares(factors=64, regularization=0.05)
model.fit(2 * sparse_user_item)



def get_trending_keywords(recent_articles):
    keywords = [str(keyword.keyword.tag) for articles in  recent_articles for keyword in articles.keywords]
    keyword_count = Counter(keywords)

    keyword_popularity = {}

    for articles in  recent_articles:
        
        likes = articles.likes
        shares = articles.shares 
        views = articles.views 
        comments = articles.total_comments

        popularity = int(likes) + int(shares) + int(views) + int(comments)
        
        keywords = [str(keyword.keyword.tag) for keyword in articles.keywords]

        article_keywords = {tag: popularity  for tag in keywords}

        keyword_popularity = update_dictionary(keyword_popularity, article_keywords)

    all_keywords = update_dictionary(keyword_popularity, keyword_count)
    # print(all_keywords)
    trending_keywords = dict( sorted(all_keywords.items(), key=operator.itemgetter(1),reverse=True))
    return list(map(operator.itemgetter(0), trending_keywords.items()))[:20]





def get_similar_cf_articles(article_list):
    similar_article_ids = []
    # similar_article_ids = [ids for article_id in article_list for ids,_ in model.similar_items(int(article_id_dict.get(article_id)))]
    for article_id in article_list:
        ids, scores= model.similar_items(int(article_id_dict.get(article_id)))
        similar_article_ids.extend(ids)

    similar_article_ids = [data.article.loc[data.article_id == id].iloc[0] for id in similar_article_ids]
    return similar_article_ids


def get_recommended_cf_articles(user_id):
    # recommended_article_ids = [ids for ids, scores in model.recommend(user_id, sparse_user_item[user_id], N=10, filter_already_liked_items=False)]
    recommended_article_ids = []
    cf_user_id = user_id_dict.get(user_id)
    ids, scores = model.recommend(cf_user_id, sparse_user_item[cf_user_id], N=10, filter_already_liked_items=False)
    recommended_article_ids.extend(ids)
    recommended_article_ids = [data.article.loc[data.article_id == id].iloc[0] for id in recommended_article_ids]
    return recommended_article_ids


@router.get('/tags')
async def search_articles(tags: str, async_session: Session = Depends(database.get_session)):
    article_list =  get_similar_articles(tags,pre)
    # print(f"article_list: {article_list} 55555555555555555555555555555555555555555555555555555")
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            articles = [await articlecrud.search_article(article_id) for article_id in article_list]
            # for article_id in article_list:
            # return await articlecrud.get_article_by_id(article_liked)

    return articles

@router.get('/similar/{article_id}')
async def search_articles(article_id: str,offset: Union[int, None] = None, limit: Union[int, None] = None, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            article = await articlecrud.search_article(article_id)
            keywords = ' '.join([str(keyword.keyword.tag) for keyword in article.keywords])
            tfidf_similar_article_list =  get_similar_articles(keywords,pre)

            cf_similar_article_list = get_similar_cf_articles(tfidf_similar_article_list)


            articles = await articlecrud.get_all_articles_by_id(cf_similar_article_list,offset,limit)


    return {"item": articles,
            "total": len(articles),
            "limit": limit,
            "offset": offset}


@router.get('/user/{user_id}', response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def user_recommendation(user_id: str,offset: int = 0, limit: int = Query(default=50), async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            # article = await articlecrud.search_article(article_id)

            ### ____________-- Getting user keyword from model dataframe -- ____________________
            # user = pre.user_df.query(f'user == "{user_id}"')
            # keyword_list = [str(keyword) for keyword in user['user_keywords']]

            ### ___________ -- GETTING USER KEYWORD FROM HISTORY -- __________________
            keyword_list = await get_user_keywords(user_id)

            print(f"userkeyword is : {keyword_list}")

            if not keyword_list:
                recent_articles = await articlecrud.get_all_article(offset, limit)
                trending_keywords = get_trending_keywords(recent_articles)
                keywords = ' '.join([str(keyword) for keyword in trending_keywords])

                tfidf_similar_article_list =  get_similar_articles(keywords,pre)

                cf_similar_article_list = get_similar_cf_articles(tfidf_similar_article_list)

                recommended_articles = await articlecrud.get_all_articles_by_id(cf_similar_article_list,offset,limit)
                return paginate(recommended_articles)

            else:
                # keywords = ' '.join([str(keyword) for keyword in user['user_keywords']])
                keywords = ' '.join([str(keyword) for keyword in keyword_list])
                tfidf_similar_article_list =  get_similar_articles(keywords,pre)

                cf_similar_article_list = get_similar_cf_articles(tfidf_similar_article_list)
                
                if user_id not in user_id_dict:
                    user_id = random.choice(list(user_id_dict))

                cf_recommended_article_list = get_recommended_cf_articles(user_id)

                recommended_article_list = list(set(cf_recommended_article_list + cf_similar_article_list))

                recommended_articles = await articlecrud.get_all_articles_by_id(recommended_article_list,offset,limit)

                return  paginate(recommended_articles)





@router.get('/web/{user_id}')
async def user_web_recommendation(user_id: str,offset: int = 0, limit: int = Query(default=20), async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            # article = await articlecrud.search_article(article_id)
            user = pre.user_df.query(f'user == "{user_id}"')
            keywords = ' '.join([str(keyword) for keyword in user['user_keywords']])
            tfidf_similar_article_list =  get_similar_articles(keywords,pre)

            cf_similar_article_list = get_similar_cf_articles(tfidf_similar_article_list)

            cf_recommended_article_list = get_recommended_cf_articles(user_id)

            recommended_article_list = list(set(cf_recommended_article_list + cf_similar_article_list))

            articles = await articlecrud.get_all_articles_by_id(recommended_article_list,offset,limit)
            
            html_content = utils.hori_html_formate(articles)

    return  html_content



def update_dictionary(old_dict, new_dict):
    for key in old_dict:
        if key in new_dict:
            new_dict[key] = new_dict[key] + old_dict[key]
        else:
            new_dict.update({key: old_dict[key]})
    
    return new_dict


@router.get('/trending_keywords',)
async def trending_keywords(offset: int = 0, limit: int = Query(default=20), async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            recent_articles = await articlecrud.get_all_article(offset, limit)
            trending_keywords = get_trending_keywords(recent_articles)
            
    return trending_keywords




async def get_article(article_url: str):
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            authorcrud = AuthorCrud(session)
            article =  await articlecrud.get_article(article_url)
    
            if article:
                article = article._mapping.Article
                author = await authorcrud.get_author_by_id(article.author_id)
                author = author._mapping.Author
            else:
                item_df = pre.df[pre.df.url == article_url].iloc[0]
                author_name = item_df.author
                author_img = item_df.author_img
                author = await authorcrud.get_author_by_name(author_name)
                if not author:
                    author_id = secrets.token_urlsafe(32)
                    new_author = author_model.Author(id = author_id,author_name = author_name, author_img = author_img)
                    print('no author found in db... Adding the author in db.')
                    try:
                        await authorcrud.create_author(new_author)

                        author = new_author
                        print("Successfully added article in db")
                    except:
                        print("Unable to add author in db")
                        # return JSONResponse(status_code=status.HTTP_201_CREATED, content=item)
                        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Author not added in database")
                else:
                    author = author._mapping.Author
              
                    
                article_id = secrets.token_urlsafe(32)
                likes = 0
                shares = 0
                article_dict = {
                    "id": article_id,
                    "url": item_df.url,
                    "head_image": item_df.head_image,
                    "heading": item_df.heading,
                    "date": item_df.date.split()[0],
                    "label": item_df.label,
                    # "content": content_filter(ast.literal_eval(item_df.content)),
                    "content": list(filter(None, ast.literal_eval(item_df.content))),
                    "additional_img": ast.literal_eval(item_df.additional_images),
                    "source": item_df.source,
                    "likes": likes,
                    "shares": shares,
                    "author_id": author.id,
                    "type": 'recommended'
                }

                article = article_model.Article(**article_dict)
                await articlecrud.create_article(article)
    return article, author


@router.get("/{redirect_str}")
async def redirect(redirect_str:str,id:str,current_page:str):
    # print(f"using user_id: {user_id}")
    article_url = redirect_dict[redirect_str]
    article,author = await get_article(article_url)

    article_liked = clicks_schema.CreateUserArticleClicks(
        user_id =  id,
        article_url = article.url,
        author_name = author.author_name,
        referrer = current_page,
    )
    async with async_session() as session:
            async with session.begin():
                clickscrud = ClicksCrud(session)
                await clickscrud.click_article(article_liked)


    response = RedirectResponse(url=redirect_dict[redirect_str])
    return response

