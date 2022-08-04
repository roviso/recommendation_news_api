import json
import os
from pathlib import Path
from typing import List, Mapping
from crud.crud_article import ArticleCrud
from models.article_model import Article
from apis.tts.riri import inference
from apis.tts.riri.utils.util import mode, to_arr
from apis.tts.riri.utils.audio import save_wav, inv_melspectrogram

from database import async_session

from fastapi import Body, FastAPI, Query
from fastapi.responses import FileResponse
from starlette.requests import Request


ttsApi = FastAPI()

path = 'apis/tts/riri/'

model = inference.load_model('apis/tts/riri/ckpt/ckpt_riri_final')


@ttsApi.get('/')
async def root():
    return {'message': 'Text to Speech from Nepali text'}


@ttsApi.get('/tts/{text}', response_class=FileResponse)
async def get_tts(text: str):
    output = inference.infer(text, model)
    inference.audio(output, 'apis/tts/riri/wavdir/res')
    file_path = os.path.join(path,"wavdir/res.mp3")
    # wav_postnet = inv_melspectrogram(to_arr(output[0][0]))
    if os.path.exists(file_path):
        return FileResponse(file_path)
    # return FileResponse("")
    return {"Error": f"No wav file found at {file_path}"}





@ttsApi.get('/article/{article_id}', response_class=FileResponse)
async def search_article(article_id: str,request: Request) -> List[Article]:
    file_path = os.path.join(path,f"wavdir/{article_id}.mp3")
    if not os.path.exists(file_path):
        async with async_session() as session:
            async with session.begin():
                articlecrud = ArticleCrud(session)
                article =  await articlecrud.search_article(article_id)
                
                article_heading = article.heading
                headwords = article_heading.split()
                tts_text = article_heading + ' '.join(headwords[:int(0.2*len(headwords))])
                output = inference.infer(tts_text, model)
                inference.audio(output, f'apis/tts/riri/wavdir/{article_id}')
                

    # if os.path.exists(file_path):
    return FileResponse(file_path)

    # return {"Error": f"No wav file found at {file_path}"}

    # return article