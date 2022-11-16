from fastapi import APIRouter,Depends
from crud.crud_author import AuthorCrud
from crud.crud_source import SourceCrud
from crud.crud_latest import LatestCrud
from crud.crud_user import UserCrud
from models.author_model import Author
from models.user_model import RegisteredUser, User
from schemas import author_schema,article_schema,profile_schema
from typing import List, Optional
import secrets
from database import async_session
from fastapi_pagination import paginate,LimitOffsetPage
from cacher.top_cache import topcache
from fastapi import BackgroundTasks
from apis.newstalk.routers.user import get_current_user


router = APIRouter(
    prefix = "/top",
    tags=['top']
)

async def cache_top_sources(top_sources):
    await topcache.cache_source(top_sources)


@router.get('/top_articles', status_code = 200 , response_model= LimitOffsetPage[article_schema.GetAllArticle])
async def get_top_articles(n_days: int,current_user: User = Depends(get_current_user)) -> List[Author]:
    async with async_session() as session:
        async with session.begin():
            latestcrud = LatestCrud(session)
            top_sources = await latestcrud.get_top_article(n_days)
    return paginate(top_sources)



@router.get('/top_source', status_code = 200 , response_model= LimitOffsetPage[profile_schema.SourceProfile])
async def get_top_source(background_tasks: BackgroundTasks,current_user: User = Depends(get_current_user)) -> List[Author]:
    cache_exists = await topcache.cache_source_exits(1)

    if not cache_exists:
        print('Reading Top source from db ')
        async with async_session() as session:
            async with session.begin():
                sourcecrud = SourceCrud(session)
                top_sources = await sourcecrud.get_top_sources()
                background_tasks.add_task(cache_top_sources,top_sources)
    else:
        print('Reading from cache')
        top_sources_ordered = await topcache.read_top_sources()
        top_sources = [dict(source) for source in top_sources_ordered.values()]
    return paginate(top_sources)

    
    
            

    # return paginate(top_sources)



@router.get('/top_author', status_code = 200 , response_model= LimitOffsetPage[profile_schema.AuthorProfile])
async def get_top_author(current_user: User = Depends(get_current_user)) -> List[Author]:
    async with async_session() as session:
        async with session.begin():
            authorcrud = AuthorCrud(session)
            top_authors = await authorcrud.get_top_authors()
            

    return paginate(top_authors)



@router.get('/top_users', status_code = 200 , response_model= LimitOffsetPage[profile_schema.UserProfile])
async def get_top_users(current_user: User = Depends(get_current_user)) -> List[RegisteredUser]:
    async with async_session() as session:
        async with session.begin():
            usercrud = UserCrud(session)
            top_users = await usercrud.get_top_users()
            

    return paginate(top_users)