from celery import Celery
from kombu.utils.url import safequote
import json
import os
from pathlib import Path
from typing import List, Mapping
import argparse
import torch
import boto3
from fastapi.responses import FileResponse
from starlette.requests import Request
import boto3
import uuid
import requests
import hashlib
import os

import whisper

    
    
remote_url = 'https://riri.prixa.net/dashboard/submit-result/'
aws_access_key = safequote("AKIAT2O2SZBBDI4Q3EFJ")
aws_secret_key = safequote("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")

broker_url = "sqs://{aws_access_key}:{aws_secret_key}@".format(
    aws_access_key=aws_access_key, aws_secret_key=aws_secret_key,
)

app = Celery('tasks', broker=broker_url)
session = boto3.Session(
    aws_access_key_id='AKIAT2O2SZBBDI4Q3EFJ',
    aws_secret_access_key='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',
)

s3 = session.resource('s3')
BUCKET = "riri.prixacdn.net"

bucket_session = s3.Bucket(BUCKET)



## ======================================== LOADING TTS MODEL =================================================== ##
model = whisper.load_model("large")
## ================================================================================================================================
    
@app.task(bind=True)
def add(self, x, y):
    print(self.request.id)
    return x + y

@app.task(bind=True, name="get_audio_text")
def get_audio_text(self, filename):
    audio_path = f"test_audio/{filename}"
    transcription = model.transcribe(audio_path,**transcribe_options)["text"]
    return transcription
    
    
    
    # req_name = self.request.id
    # filename = uuid.uuid4().hex
    # ntext = text + '_' + voice
    # filename_md5_encodded = hashlib.md5(ntext.encode())
    # filename =  filename_md5_encodded.hexdigest()
    
#     fname = f"{filename}.wav"
    
    
#     audio_path = args.output + f"/{filename}.wav"
#     if not os.path.exists(audio_path):
#         export_fastpitch_audio(text,fname, voice_calc)
    
    
#     op_path = "output/"+fname
#     if os.path.exists(audio_path):
#         print(f"Audio Created at {audio_path}")
#         bucket_session.upload_file(audio_path,op_path,ExtraArgs={'ContentType': "audio/wav", 'ACL': "public-read"} )
#         cdn_path = "https://riri.prixacdn.net/"+op_path
#         myobj = {'task_id': req_name, 'url':cdn_path}
#         requests.post(remote_url, myobj)
        

#         ## If file exists, delete it ##
#         if os.path.isfile(audio_path):
#             print(f"removing file: {audio_path}")
#             os.remove(audio_path)
#         else:    ## Show an error ##
#             print("Error: %s file not found" % audio_path)

#         return cdn_path
#     # return FileResponse("")

#     return {"Error": f"No wav file found at {audio_path}"}
    
