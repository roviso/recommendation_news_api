from fastapi import APIRouter,Depends
from schemas import clicks_schema
from crud.crud_redirect_clicks import ClicksCrud
from database import async_session
from sqlalchemy.orm import Session
import database
from starlette.responses import RedirectResponse


router = APIRouter(
    prefix = "/redirect",
    tags=['redirect']
)


# if pathconfig.REDIRECT_DICT_PATH.is_file():
#     with open(pathconfig.REDIRECT_DICT_PATH, 'rb') as f:
#         redirect_dict = pickle.load(f)
#     print('Successfully Loaded redirection url file')



@router.get("/{article_id}")
async def redirect(article_id: str, user_id: str, referrer: str, async_session: Session = Depends(database.get_session)):
    # print(f"using user_id: {user_id}")

    article_clicked = clicks_schema.CreateUserArticleClicks(
        user_id =  user_id,
        article_id = article_id,
        referrer = referrer,
    )

    async with async_session as session:
            async with session.begin():
                clickscrud = ClicksCrud(session)
                article = await clickscrud.articledb.search_article(article_clicked.article_id)
                await clickscrud.click_article(article_clicked)
                


    response = RedirectResponse(url=article.url)
    return response

