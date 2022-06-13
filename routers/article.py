from fastapi import APIRouter, status, HTTPException,Query
from crud.crud_article import ArticleCrud
from crud.crud_author import AuthorCrud
from crud.crud_comments import Comments
from models.article_model import Article,LatestArticle, RecommendedArticle
from models import author_model
from schemas import article_schema
from typing import List, Optional
import secrets
from database import async_session
from routers.comments import get_article_comments
from fastapi_pagination import Page, add_pagination, paginate,LimitOffsetPage
from sqlalchemy.future import select

router = APIRouter(
    prefix = "/articles",
    tags=['articles']
)


async def add_comments_and_replies(articles: List[Article]):
    for article in articles:
        article = article.__dict__
        comments = await get_article_comments(article['id'])
        article['comments'] = comments
    # async with async_session() as session:
    #     async with session.begin():
    #         comment = Comments(session)
    #         for article in articles:
    #             article = article.__dict__
    #             print(article)
    #             comments = await comment.get_comments_by_article(article['id'])
    #             article['comments'] = comments
    #             article['comments']['replies'] = "this is replies1 this is 2"
    
    return articles

@router.post('/create_articles/', status_code = 200)
async def create_articles(article: article_schema.RecommendedArticle):
    article_id = secrets.token_urlsafe(32)

    article_dict = article.dict()
    del article_dict['author'] 

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


@router.get('/get_all_articles', status_code = 200, response_model=LimitOffsetPage[article_schema.GetAllArticle])
async def get_all_articles() -> List[RecommendedArticle]:
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            articles =  await articlecrud.get_all_article()
            return paginate(articles)



@router.get('/get_recommended_articles', status_code = 200)
async def get_recommended_articles() -> List[RecommendedArticle]:
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            return await articlecrud.get_all_recommended_article()



@router.get('/search_article', status_code = 200)
async def search_article(article_id: str) -> List[Article]:
    async with async_session() as session:
        async with session.begin():
            articlecrud = ArticleCrud(session)
            return await articlecrud.search_article(article_id)
