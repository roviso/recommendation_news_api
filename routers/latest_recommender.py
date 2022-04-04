from fastapi import APIRouter, status,Depends, Response, WebSocket,Cookie,Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import database
from models import article_model
from typing import Optional
from fastapi.responses import HTMLResponse
import nepali_datetime
from starlette.requests import Request
from starlette.responses import Response
import time
from datetime import datetime
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend
import aioredis

router = APIRouter(
    prefix = "/latest_recommendation",
     tags=['Latest Recommendation']
)

# @router.on_event("startup")
# async def startup():
#     redis = aioredis.from_url(url="redis://localhost")
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


latest_recommendation = article_model.LatestArticle()

@cache(namespace="test", expire=5)
async def get_recommendation(db: Session):
    global latest_recommendation
    # time.sleep(3)
    latest_recommendation = db.query(article_model.LatestArticle).order_by(desc(article_model.LatestArticle.likes,)).limit(20).all()
    return latest_recommendation




@router.get('/get_latest_news/', status_code = 200)
@cache(namespace="test", expire=1*60)
async def get_already_recommended(request: Request, response: Response, db: Session = Depends(database.get_db)):
    start = datetime.now()
    # time.sleep(2)

    latest_aricles = await get_recommendation(db)
    # latest_aricles = db.query(article_model.LatestArticle).order_by(desc(article_model.LatestArticle.likes,)).limit(20).all()
    print('time taken to query: ',datetime.now() - start)
    # print(testt,"5555555555555555555555555555")
    # print(FastAPICache.get_prefix())
    return latest_aricles
    # recommended_user_article
    # stmt = select(users_table).order_by(users_table.c.name.asc())



html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>Item ID: <input type="text" id="itemId" autocomplete="off" value="foo"/></label>
            <label>Token: <input type="text" id="token" autocomplete="off" value="some-key-token"/></label>
            <button onclick="connect(event)">Connect</button>
            <hr>
            <label>Message: <input type="text" id="messageText" autocomplete="off"/></label>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
        var ws = null;
            function connect(event) {
                var itemId = document.getElementById("itemId")
                var token = document.getElementById("token")
                ws = new WebSocket("ws://localhost:9999/items/" + itemId.value + "/ws?token=" + token.value);
                ws.onmessage = function(event) {
                    var messages = document.getElementById('messages')
                    var message = document.createElement('li')
                    var content = document.createTextNode(event.data)
                    message.appendChild(content)
                    messages.appendChild(message)
                };
                event.preventDefault()
            }
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/latest_recommendation/")
async def get():
    return HTMLResponse(html)


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Optional[str] = Cookie(None),
    token: Optional[str] = Query(None),
):
    print('inside fun')
    if session is None and token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return session or token


@router.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    item_id: str,
    q: Optional[int] = None,
    cookie_or_token: str = Depends(get_cookie_or_token),
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # await websocket.send_text(
        #     f"Session cookie or query token value is: {cookie_or_token}"
        # )
        if q is not None:
            await websocket.send_text(f"Query parameter q is: {q}")
        await websocket.send_text(f"Message text was: {database.query(article_model.LatestArticle).order_by(desc(article_model.LatestArticle.likes)).limit(5).all()}, for item ID: {item_id}")