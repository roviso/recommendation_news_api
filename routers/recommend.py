from fastapi import APIRouter, status, HTTPException,Depends
from starlette.responses import RedirectResponse
from config import pathconfig
import pickle
from schemas import clicks_schema
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
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.linalg import spsolve
from sklearn.preprocessing import MinMaxScaler
import database
from database import async_session
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd

router = APIRouter(
    prefix = "/recommend",
    tags=['recommend']
)





print('----------Preprocessing(loading data)--------------------')
if pathconfig.PRE_PKL_PATH.is_file():
    pre = load_pkl(pathconfig.PRE_PKL_PATH)
    print('Successfully Loaded Pickle file')

if pathconfig.REDIRECT_DICT_PATH.is_file():
    with open(pathconfig.REDIRECT_DICT_PATH, 'rb') as f:
        redirect_dict = pickle.load(f)
    print('Successfully Loaded redirection url file')

docs = pre.article_df.keywords_words.values
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(docs)

def get_similar_articles(q, pre):
    print("query:", q)
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
async def search_articles(article_id: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            article = await articlecrud.search_article(article_id)
            keywords = ' '.join([str(keyword.keyword.tag) for keyword in article.keywords])
            article_list =  get_similar_articles(keywords,pre)
            similar_articles = [await articlecrud.search_article(article_id) for article_id in article_list]


    return similar_articles



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

