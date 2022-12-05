from celery import Celery
from kombu.utils.url import safequote
from pathlib import Path
from typing import List, Mapping
import boto3
import os
from celery import shared_task
# import whisper

    
    
remote_url = 'https://riri.prixa.net/dashboard/submit-result/'
aws_access_key = safequote("AKIA5BJRLA5THBMHDDKZ")
aws_secret_key = safequote("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")

broker_url = "sqs://{aws_access_key}:{aws_secret_key}@".format(
    aws_access_key=aws_access_key, aws_secret_key=aws_secret_key,
)

app = Celery('tasks_ref', broker=broker_url,broker_transport_options = {'region': 'ap-southeast-1'} )
session = boto3.Session(
    aws_access_key_id='AKIAT2O2SZBBDI4Q3EFJ',
    aws_secret_access_key='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',
)

s3 = session.resource('s3')
BUCKET = "riri.prixacdn.net"

bucket_session = s3.Bucket(BUCKET)



## ======================================== LOADING TTS MODEL =================================================== ##
# model = whisper.load_model("large")
## ================================================================================================================================
    
@shared_task(name= 'add2')
def add2(x, y):
    # print(self.request.id)
    return x + y


@app.task(bind=True, name = "fixed_data")
def fixed_data(self,x):
    print(self.request.id)
    print(x)
    


# @app.task(name="srec")
@shared_task(name="srec2")
def srec2(url):
    # print(self.request.id)
    print(url)
    # audio_path = f"test_audio/{filename}"
    # transcription = model.transcribe(audio_path,**transcribe_options)["text"]
    return "server not hit"
    # return transcription
    

# @app.task(bind=True, name="process_audio")
# def process_audio(self, text, voice):
#     print('processing audio')
#     return "server not HITTTT!!!"
    
    
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
    
