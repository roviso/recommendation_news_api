from numpy import int16
from fastapi import APIRouter, status, HTTPException
from crud.crud_latest import LatestCrud
from crud.crud_author import AuthorCrud
from models.article_model import Article,LatestArticle, RecommendedArticle
from models import author_model
from schemas import article_schema
from typing import List, Optional
import secrets
from database import async_session
from cacher.latest_cache import latestcache
from fastapi import BackgroundTasks


router = APIRouter(
    prefix = "/latest",
    tags=['latest']
)


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
            authorcrud = AuthorCrud(session)
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


@router.get('/get_latest_articles', status_code = 200)
async def get_latest_articles() -> List[LatestArticle]:
    async with async_session() as session:
        async with session.begin():
            latestcrud = LatestCrud(session)
            return await latestcrud.get_all_latest_article()

@router.get('/get_trending_articles_test', status_code = 200)
async def get_trending_articles_test(id:int) -> List[LatestArticle]:
    trending =  await latestcache.cache_exits(id)
    if trending:
        return 'exists'
    else:
        return 'NOPE'



@router.get('/get_trending_articles')
async def get_trending_articles(background_tasks: BackgroundTasks):
    # trending = await get_trending_news()
    # print(trending,dir(trending),555555555555555555555555555, )
    cache_exists = await latestcache.cache_exits()
    if not cache_exists:
        print('Reading from db')
        # trending = await get_trending_news()
        trending_news = [news for news in await get_trending_news()]

        background_tasks.add_task(cache_latest_news,trending_news)
    else:
        print('Reading from cache')
        trending_news_ordered = await latestcache.read_cached_news()
        trending_news = [dict(recommended_news) for recommended_news in trending_news_ordered.values()]
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
