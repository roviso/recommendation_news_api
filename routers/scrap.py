from fastapi import APIRouter,Depends
from worker import celery
from pydantic import BaseModel
import json



router = APIRouter(
    prefix = "/scrap",
    tags=['scrap']
)



class Item(BaseModel):
    name: str

@router.post("/task_hello_world/")
async def create_item(item: Item):
    task_name = "hello.task"
    task = celery.send_task(task_name, args=[item.name])
    return dict(id=task.id, url='localhost:8000/check_task/{}'.format(task.id))


@router.post("/scrapenews/")
async def scrape_news():
    # news: NewsResponse):
    task_name = "tasks.refresh_sources"
    # task = celery.send_task(task_name, args=[news.pk,news.category_id,news.link,news.prefix,news.selector,
    # news.image_selector,news.exception_selector,news.default_image,news.pubDate,news.debug,])
    task = await celery.send_task(task_name)
    return dict(id=task.id, url='localhost:8000/check_task/{}'.format(task.id))


@router.get("/check_task/{id}")
def check_task(id: str):

    task = celery.AsyncResult(id)

    print(type(task), task.state)
    if task.state == 'SUCCESS':
        response = {
            'status': task.state,
            'result': task.result,
            'task_id': id
        }
    elif task.state == 'FAILURE':
        response = json.loads(task.backend.get(task.backend.get_key_for_task(task.id)).decode('utf-8'))
        del response['children']
        del response['traceback']
    else:
        response = {
            'status': task.state,
            'result': task.info,
            'task_id': id
        }
    return response