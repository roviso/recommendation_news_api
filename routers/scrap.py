from fastapi import APIRouter,Depends,  HTTPException
from worker import celery
from pydantic import BaseModel
import json
from crud import crud_scrap
from typing import Optional
from routers import source

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


@router.get("/test_source_scrape/")
async def test_source_scrape(source_id: int):
    sourceInDb = await source.getSourceById(source_id)
    if not sourceInDb:
        raise HTTPException(status_code=404, detail=f"Source Not Found In database: sourceId={source_id}")
    (sourceInDb,) = sourceInDb 

    print(f"Testing source RSS Link: {sourceInDb.link}")
    Newslinks = await test_rss_link(sourceInDb.link)
    
    if not Newslinks:
        raise HTTPException(status_code=404, detail=f"Source RSS Link Error with RSS={sourceInDb.link}")

    # print(Newslinks)
    # testLink = next(iter(Newslinks)) 
    testLink = list(Newslinks)[-1]
    
    print(f"Scrape Testing on Link: {testLink}")
    news_scrapper = crud_scrap.ScrapeLinkX(sourceInDb,testLink)
    title = news_scrapper.scrape_title()
    head_image = news_scrapper.scrape_img(sourceInDb.image_selector)
    author = news_scrapper.scrape_author(author_name_selector =sourceInDb.author_name_selector,author_img_selector =sourceInDb.author_img_selector)
    content, additional_img = news_scrapper.scrape_content(sourceInDb.content_selector, None)
    label = news_scrapper.scrape_label(sourceInDb.label_selector)

    reponse = {
        'rss_link': sourceInDb.link,
        'test_link': testLink,
        'title': title,
        'head_image': head_image,
        'author':author,
        'content': content,
        'additional_img': additional_img,
        'label': label
    }


    return reponse



@router.get("/test_rss/")
async def test_rss_link(rss_link: str):
    return await crud_scrap.scrape_normal_rss(rss_link)


@router.get("/test_title_scrape/")
async def test_title_scrape(link: str):
    title = crud_scrap.scrape_title(link)
    return title

@router.get("/test_headimage_scrape/")
async def test_headimage_scrape(link: str, image_selector:str):
    head_img = crud_scrap.scrape_img(link, image_selector)
    if not head_img:
        raise HTTPException(status_code=404, detail=f"Image not found... Please Check the image selector {image_selector}")
    return head_img



@router.get("/test_author_scrape/")
async def test_author_scrape(link: str, author_selector:str):
    author = crud_scrap.scrape_author(link, author_selector)
    if not author:
        raise HTTPException(status_code=404, detail=f"author not found... Please Check the author selector {author_selector}")
    return author


@router.get("/test_content_scrape/")
async def test_author_scrape(link: str, content_selector:str, content_unwanted_selector: Optional[str] = None):
    content = crud_scrap.scrape_content(link, content_selector, content_unwanted_selector)
    if not content:
        raise HTTPException(status_code=404, detail=f"content not found... Please Check the content selector {content_selector}")
    return content


@router.get("/test_label_scrape/")
async def test_label_scrape(link: str, label_selector:str):
    label = crud_scrap.scrape_label(link, label_selector)
    if not label:
        raise HTTPException(status_code=404, detail=f"label not found... Please Check the label selector {label_selector}")
    return label