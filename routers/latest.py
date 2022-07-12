from numpy import int16
import pandas as pd
from fastapi import APIRouter, status, HTTPException,Depends,Query
from crud.crud_latest import LatestCrud
from crud.crud_author import AuthorCrud
from models.article_model import Article,LatestArticle, RecommendedArticle
from models import author_model
from schemas import article_schema
from typing import List, Optional
import secrets
from database import async_session
from cacher.latest_cache import latestcache
from cacher.tfidf_cache import tfidfcache
from fastapi import BackgroundTasks
from crud.crud_article import ArticleCrud
from helper import tfidf_generator
from operator import add
from functools import reduce
from routers.keywords import add_article_keywords
from fastapi_pagination import paginate,LimitOffsetPage



router = APIRouter(
    prefix = "/latest",
    tags=['latest']
)


# @router.get('/get_keywords', status_code = 200)
# async def get_keywords(article_id: str, async_session: Session = Depends(database.get_session)) -> List[LatestArticle]:
#     CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
#     async with async_session as session:
#         async with session.begin():
#             latestcrud = LatestCrud(session)
#             if await tfidfcache.cache_exits():
#                 tfidf_dict = await tfidfcache.read_from_cache()
#             else:
#                 articles = await latestcrud.get_all_latest_article()
                


#                 article_text = [re.sub(CLEANR, '', article.heading + ' ' + reduce(add ,article.content))  for article in articles]

#                 train_df = pd.DataFrame(article_text, columns= ['text'])
#                 tfidf_dict = tfidf_generator.train_idfs(train_df)

#                 await tfidfcache.cache_latest_tfidf(tfidf_dict) ##Caching tfidf values in dictrionary 

#             article = await latestcrud.get_article_by_id(article_id)
#             content = [re.sub(CLEANR, '', article.heading + ' ' + reduce(add ,article.content)) ]
#             keywords = tfidf_generator.extract_keywords(content, tfidf_dict, 20)

#             final_keywords = reduce(add ,keywords)

#     return await add_article_keywords(final_keywords,article_id,async_session)

    # return await tfidfcache.read_from_cache()

async def cache_latest_news(latest_news):
    # print(latest_news,5555555555555555555555)
    await latestcache.cache_news(latest_news)

# async def cache_exits(news_index:int):
#     async with async_session() as session:
#         async with session.begin():
#             latestcrud = LatestCrud(session)


async def get_trending_news():
    async with async_session() as session:
        async with session.begin():
            latestcrud = LatestCrud(session)
            # authorcrud = AuthorCrud(session)
            trending_articles = await latestcrud.get_trending_article()
            # trending = []

            # for articles in trending_articles:
            #     article = articles.__dict__
            #     author_id = article['author_id']
            #     author = await authorcrud.get_author_by_id(author_id)
            #     author = author._mapping.Author
            #     # print(author,111111111111111, author.__dict__)
            #     # print(author.author_name, author.author_img)
            #     article['author'] = author.author_name
            #     article['author_img']  = author.author_img
            #     trending.append(article)
    return trending_articles


@router.post('/create_latest_article/', status_code = 200)
async def create_latest_article(article: article_schema.CreateLatestArticle):
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            
            article_exists = await articlecrud.get_article_by_url(article.url)
            if article_exists:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Article aleady exists")
            else:
                article_id = secrets.token_urlsafe(32)
                article_dict = article.dict()
                print(f"creating article: {article_dict}")
                new_article = Article(id = article_id,**article_dict)
                await articlecrud.create_article(new_article)
                return new_article



@router.get('/get_article_by_url/{article_url}', status_code = 200)
# , response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_article_by_url(article_url:str):
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            article =  await articlecrud.get_article_by_url(article_url)
            return article



@router.get('/get_latest_articles', status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_latest_articles(offset: int = 0, limit: int = Query(default=50)) -> List[LatestArticle]:
    async with async_session() as session:
        async with session.begin():
            latestcrud = LatestCrud(session)
            latest_articles = await latestcrud.get_latest_articles(offset,limit)

            return  paginate(latest_articles)


# @router.get('/get_latest_articles', status_code = 200)
# async def get_latest_articles(offset: int = 0, limit: int = Query(default=50)) -> List[LatestArticle]:
#     async with async_session() as session:
#         async with session.begin():
#             latestcrud = LatestCrud(session)
#             latest_articles = await latestcrud.get_latest_articles(offset,limit)

#             return  latest_articles




@router.get('/get_latest_article/article_id', status_code = 200)
async def get_latest_articles_by_id(article_id: str) -> List[LatestArticle]:
    async with async_session() as session:
        async with session.begin():
            latestcrud = LatestCrud(session)
            return await latestcrud.get_article_by_id(article_id)

@router.get('/get_trending_articles_test', status_code = 200)
async def get_trending_articles_test(id:int) -> List[LatestArticle]:
    trending =  await latestcache.cache_exits(id)
    if trending:
        return 'exists'
    else:
        return 'NOPE'



@router.get('/get_trending_articles')
async def get_trending_articles(background_tasks: BackgroundTasks):
    trending_news = [news for news in await get_trending_news()]

    # cache_exists = await latestcache.cache_exits()
    # if not cache_exists:
    #     print('Reading from db')
    #     # trending = await get_trending_news()
    #     trending_news = [news for news in await get_trending_news()]

    #     background_tasks.add_task(cache_latest_news,trending_news)
    # else:
    #     print('Reading from cache')
    #     trending_news_ordered = await latestcache.read_cached_news()
    #     trending_news = [dict(recommended_news) for recommended_news in trending_news_ordered.values()]
    return trending_news

    


@router.post('/create_articles/', status_code = 200)
async def create_latest_articles(article: article_schema.CreateLatestArticle):
    article_id = secrets.token_urlsafe(32)
    article_dict = article.dict()
    del article_dict['author'] 

    article_dict['type'] = 'latest'
    author_name = article.author.author_name
    
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            author = await authorcrud.get_author_by_name(author_name)
            if not author:
                author_id = secrets.token_urlsafe(32)
                new_author = author_model.Author(id = author_id,**article.author.dict())
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
            new_article = Article(id = article_id,**article_dict, author_id = author.id)
            
            latestcrud = LatestCrud(session)
            return await latestcrud.create_latest_article(new_article)
