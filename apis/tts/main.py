import json
import os
from pathlib import Path
from typing import List, Mapping
from crud.crud_article import ArticleCrud
from models.article_model import Article
from apis.tts.riri_tts import inference_glow as inference
from apis.tts.riri_tts.utils.util import mode, to_arr
from apis.tts.riri_tts.utils.audio import save_wav, inv_melspectrogram
import torch
from database import async_session

from fastapi import Body, FastAPI, Query
from fastapi.responses import FileResponse
from starlette.requests import Request


ttsApi = FastAPI()

path = 'apis/tts/riri_tts/'
sigma = 0.6
output_dir = 'apis/tts/riri_tts/wavdir/'
sampling_rate = 22050

# model_name = 'ckpt_riri_24k_16bs_421244'
model_name = 'ckpt_male_453000'
waveglow_model = 'waveglow_56000'

model = inference.load_model(f'apis/tts/riri_tts/ckpt/{model_name}')
waveglow = torch.load(f'apis/tts/riri_tts/waveglow_ckpt/{waveglow_model}', map_location=torch.device('cpu'))['model']
waveglow = waveglow.remove_weightnorm(waveglow)
# waveglow.cuda().eval()
waveglow.eval()

@ttsApi.get('/')
async def root():
    return {'message': 'Text to Speech from Nepali text'}


@ttsApi.get('/tts/{text}', response_class=FileResponse)
async def get_tts(text: str):
    output = inference.infer(text, model)
    npy_ary = output[1]
    filename = 'response'
    
    audio_path = inference.save_waveglow(npy_ary,filename, waveglow,sigma, output_dir, sampling_rate, False)
    
    # output = inference.infer(text, model)
    # inference.audio(output, 'apis/tts/riri_tts/wavdir/res')
    # file_path = os.path.join(path,"wavdir/res.mp3")
    # wav_postnet = inv_melspectrogram(to_arr(output[0][0]))
    if os.path.exists(audio_path):
        return FileResponse(audio_path)
    # return FileResponse("")
    return {"Error": f"No wav file found at {audio_path}"}





@ttsApi.get('/article/{article_id}', response_class=FileResponse)
async def search_article(article_id: str,request: Request) -> List[Article]:
    file_path = os.path.join(output_dir,f"{article_id}.wav")
    print(f"file path: {file_path}, 55555555555555555")
    if not os.path.exists(file_path):
        async with async_session() as session:
            async with session.begin():
                articlecrud = ArticleCrud(session)
                article =  await articlecrud.search_article(article_id)
                
                article_heading = article.heading + '।'
                # headwords = article_heading.split()
                # tts_text = article_heading + ' '.join(headwords[:int(0.2*len(headwords))])

                # output = inference.infer(article_heading, model)
                # inference.audio(output, f'apis/tts/riri/wavdir/{article_id}')
                output = inference.infer(article_heading, model)
                npy_ary = output[1]
                filename = article_id
                
                audio_path = inference.save_waveglow(npy_ary,filename, waveglow,sigma, output_dir, sampling_rate, False)
                
                assert audio_path == file_path
    # if os.path.exists(file_path):
    return FileResponse(file_path)

    # return {"Error": f"No wav file found at {file_path}"}

    # return article
