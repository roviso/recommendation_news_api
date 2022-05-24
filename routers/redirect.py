from fastapi import APIRouter, status, HTTPException
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

router = APIRouter(
    prefix = "/redirect",
    tags=['redirect']
)

print('----------Preprocessing(loading data)--------------------')
if pathconfig.PRE_PKL_PATH.is_file():
    pre = load_pkl(pathconfig.PRE_PKL_PATH)
    print('Successfully Loaded Pickle file')

if pathconfig.REDIRECT_DICT_PATH.is_file():
    with open(pathconfig.REDIRECT_DICT_PATH, 'rb') as f:
        redirect_dict = pickle.load(f)
    print('Successfully Loaded redirection url file')


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

