from fastapi import APIRouter,status,Depends
from crud.crud_article import ArticleCrud
from crud.crud_user import UserCrud
from crud.crud_author import AuthorCrud
from crud.crud_keywords import KeywordsCrud
from models.article_model import Article
from schemas import user_schema, author_schema, article_schema

from repository.ncf_recommender.loader import load_pkl
from typing import List, Optional, Any
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from config import pathconfig
from sklearn.feature_extraction.text import TfidfVectorizer

import scipy.sparse as sparse
from scipy.sparse.linalg import spsolve
import random
from sklearn.preprocessing import MinMaxScaler
from fastapi_pagination import paginate,LimitOffsetPage


from implicit.als import AlternatingLeastSquares



router = APIRouter(
    prefix = "/search",
    tags=['search']
)



# print('----------Preprocessing(loading data)--------------------')
# if pathconfig.PRE_PKL_PATH.is_file():
#     pre = load_pkl(pathconfig.PRE_PKL_PATH)
#     print('Successfully Loaded Pickle file')

# docs = pre.article_df.keywords_words.values
# vectorizer = TfidfVectorizer()
# X = vectorizer.fit_transform(docs)

# def get_similar_articles(q, pre):
#     print("query:", q)
#     print("Articles with high cosine similarity are: ")
#     q = [q]
#     q_vec = vectorizer.transform(q).toarray().reshape(pre.tfidfVectors.shape[0],)
#     sim = {}
#     for i in range(pre.tfidfVectors.shape[1]):
#         sim[i] = np.dot(pre.tfidfVectors.loc[:, i].values, q_vec) / np.linalg.norm(pre.tfidfVectors.loc[:, i]) * np.linalg.norm(q_vec)

#     sim_sorted = sorted(sim.items(), key=lambda x: x[1], reverse=True)

#     article_list = []

#     for k, v in sim_sorted:
#         if v != 0:
#             # print("Article Similarity:", v)
#             # print(pre.article_df.article_id.iloc[k])
#             article_list.append(pre.article_df.article_id.iloc[k])

#     return article_list


@router.get('/{tags}', response_model = LimitOffsetPage[article_schema.SearchArticleByTag])
async def search_articles(tag: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            # print(f"searching the tag: {tag}")
            tagged_articles = await keywordcrud.search_articles_by_keywords(tag)
            # print(f"Searched Articles with tag: {tag} are : {tagged_articles}")
    print(tagged_articles[0].__dict__)
    return paginate(tagged_articles)

@router.get('/author/{author_name}' , response_model = LimitOffsetPage[author_schema.GetAllAuthors])
async def search_author(author_name: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            authors = await authorcrud.search_author_by_name(author_name)
    # print(authors,authors[0].__dict__)
    return paginate(authors)
    # return authors



@router.get('/user/{user_name}', response_model = LimitOffsetPage[user_schema.SearchUsers])
async def search_users(user_name: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            usercrud = UserCrud(session)
            users = await usercrud.search_user_by_name(user_name)
    return paginate(users)
    # print(users)
    # return(users)


