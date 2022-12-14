from fastapi import APIRouter, Depends
import nepali_roman as nr
from nepali_unicode_converter.convert import Converter
from apis.sugariri.utils import check_and_infer
from pydantic import BaseModel
import database
from sqlalchemy.orm import Session
from crud.crud_article import ArticleCrud
import html2text
from bs4 import BeautifulSoup
import re
import random

router = APIRouter(
    prefix = "/tts",
    tags=['text to speach']
)


class suga_request(BaseModel):
    id: str
    voice: str 
    

    class Config:
        orm_mode = True



def func(value):
    return ''.join(value.splitlines())


riri_voices = ['np_rija','np_prasanna']

@router.post("/heading")
async def heading(suga_request: suga_request, async_session: Session = Depends(database.get_session)):
    article_id = suga_request.id
    async with async_session as session:
        async with session.begin():
            articleCrud = ArticleCrud(session)
            article = await articleCrud.get_article_by_id(article_id)
            text = article.heading
            voice = random.choice(riri_voices)

            if not nr.is_devanagari(text):
                converter = Converter()
                text = converter.convert(text)

            # return check_and_infer(text, suga_request.voice)
            return check_and_infer(text, voice)
            


@router.post("/content")
async def heading(suga_request: suga_request, async_session: Session = Depends(database.get_session)):
    article_id = suga_request.id
    async with async_session as session:
        async with session.begin():
            articleCrud = ArticleCrud(session)
            article = await articleCrud.get_article_by_id(article_id)

            parsed_html = BeautifulSoup(article.content[0],  'html5lib')
            paragraphs = parsed_html.find_all(['p', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if article.source.name == "फरक धार" :
                content = ''.join(str(p) for p in paragraphs[:-1]) 
            else:
                content = ''.join(str(p) for p in paragraphs) 

            text = html2text.html2text(content)
            text =  func(text)

            if not nr.is_devanagari(text):
                converter = Converter()
                text = converter.convert(text)

            return check_and_infer(text, suga_request.voice)
            # return content
            # return