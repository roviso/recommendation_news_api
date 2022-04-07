from fastapi import APIRouter
from crud.crud_article import ArticleCrud
from models.article_model import Article
from schemas import article_schema
from typing import List, Optional
import secrets
from database import async_session

router = APIRouter(
    prefix = "/articles",
    tags=['articles']
)




@router.post('/create_articles', status_code = 200)
async def create_articles(article: article_schema.CreateArticle):
    article_id = secrets.token_urlsafe(32)
    # author_id = 'IXg3IFtmGOGeIKffh3iAKWGFjrPmnvjy4wOuNLso-rM'
    new_article = Article(id = article_id,**article.dict())
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            return await articlecrud.create_article(new_article)


@router.put('/update_articles/{article_id}', status_code = 200)
async def update_articles(article_id: str, url: Optional[str] = None, head_image: Optional[str] = None, heading: Optional[str] = None,
        date: Optional[str] = None, content: Optional[str] = None, additional_img: Optional[str] = None,
        source: Optional[str] = None, author_id: Optional[str] = None):
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            return await articlecrud.update_article(article_id, url, head_image, heading,
                date, content, additional_img,source, author_id)


@router.get('/get_articles', status_code = 200)
async def get_articles() -> List[Article]:
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            return await articlecrud.get_all_article()

@router.get('/search_article', status_code = 200)
async def search_article(article_ur: str) -> List[Article]:
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            return await articlecrud.get_article(article_ur)
