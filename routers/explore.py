from fastapi import APIRouter,status,Depends
from crud.crud_article import ArticleCrud

from repository.ncf_recommender.loader import load_pkl
from typing import List
import secrets
from database import async_session
from sqlalchemy.orm import Session
import database
from config import pathconfig
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
import scipy.sparse as sparse
from scipy.sparse.linalg import spsolve
import random
from sklearn.preprocessing import MinMaxScaler



from implicit.als import AlternatingLeastSquares



router = APIRouter(
    prefix = "/explore",
    tags=['explore']
)

print('----------Preprocessing(loading data)--------------------')
if pathconfig.PRE_PKL_PATH.is_file():
    pre = load_pkl(pathconfig.PRE_PKL_PATH)
    print('Successfully Loaded Pickle file')

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
        if v >= 0.3:
            # print("Article Similarity:", v)
            # print(pre.article_df.article_id.iloc[k])
            article_list.append(pre.article_df.article_id.iloc[k])

    return article_list


@router.post('/')
async def search_articles(keywords: str, async_session: Session = Depends(database.get_session)):
    article_list =  get_similar_articles(keywords,pre)
    # print(f"article_list: {article_list} 55555555555555555555555555555555555555555555555555555")
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            articles = [await articlecrud.search_article(article_id) for article_id in article_list]
            # for article_id in article_list:
            # return await articlecrud.get_article_by_id(article_liked)

    return articles

    
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

sparse_item_user = sparse.csr_matrix((data['views'].astype(float), (data['article_id'], data['user_id'])))


sparse_user_item = sparse_item_user.T.tocsr()

model = AlternatingLeastSquares(factors=64, regularization=0.05)
model.fit(2 * sparse_user_item)


@router.get('/recommend/{user_id}', status_code = 200)
async def get_recommendation(user_id: str,async_session: Session = Depends(database.get_session)):
    userid = user_id_dict.get(user_id)
    ids, scores = model.recommend(userid, sparse_user_item[userid], N=20, filter_already_liked_items=False)
    article_list = [pre.article_df.url.loc[pre.article_df.article_id == data.article.loc[data.article_id == id].iloc[0]].iloc[0] for id in ids]
    async with async_session as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            articles = [await articlecrud.search_article(article_id) for article_id in article_list]
    
    return articles