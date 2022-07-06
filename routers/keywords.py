from fastapi import APIRouter,Depends

from crud.crud_keywords import KeywordsCrud
from crud.crud_latest import LatestCrud

from schemas import article_schema, keywords_schema
from models import article_model
from repository.ncf_recommender.loader import load_pkl
from sqlalchemy.orm import Session
import database
# import secrets
from typing import List
from fastapi_pagination import paginate,LimitOffsetPage




router = APIRouter(
    prefix = "/keywords",
    tags=['keywords']
)


@router.get('/search_articles/{tags}', response_model = LimitOffsetPage[article_schema.SearchArticleByTag])
async def search_articles(tag: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            # print(f"searching the tag: {tag}")
            tagged_articles = await keywordcrud.search_articles_by_keywords(tag)
            # print(f"Searched Articles with tag: {tag} are : {tagged_articles}")
    print(tagged_articles[0].__dict__)
    return paginate(tagged_articles)


@router.get('/getkeyword/{keyword_id}')
async def search_keyword_by_id(keyword_id: int, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            keyword = await keywordcrud.get_keyword(keyword_id)
    return keyword


@router.get('/checkkeyword/{keyword_tag}')
async def checkkeyword(keyword_tag: str, async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            keywordcrud = KeywordsCrud(session)
            keyword = await keywordcrud.get_keyword_by_tag(keyword_tag)
    return keyword



@router.post('/create_keyword/', status_code = 200)
async def create_keyword(tag: str, async_session: Session = Depends(database.get_session)):
    # article_id = secrets.token_urlsafe(32)
    
    async with async_session as session:
        async with session.begin():
            
            new_keyword = article_model.Keywords(tag = tag)
            
            keywordcrud = KeywordsCrud(session)
            await keywordcrud.create_keywords(new_keyword)

            return await keywordcrud.get_keyword_by_tag(tag)


@router.post('/add_article_keywords',status_code = 200 )
async def add_article_keywords(keywords: List[str], article_id: str ,async_session: Session = Depends(database.get_session)):
    tagNotInDb = [tag  for tag in keywords if not await checkkeyword(tag,async_session)]

    for tag in tagNotInDb:
        await create_keyword(tag,async_session) 
    
    tagInDb = [await checkkeyword(tag,async_session) for tag in keywords]

    async with async_session as session:
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


# @router.get('/get_artical')
# async def get_article_with_no_keywords(async_session: Session = Depends(database.get_session)):

