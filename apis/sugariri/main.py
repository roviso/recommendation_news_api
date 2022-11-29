from fastapi import FastAPI, File, UploadFile,HTTPException,Depends
import speech_recognition as sr
import nepali_roman as nr
from nepali_unicode_converter.convert import Converter
import requests
from pydantic import BaseModel
import boto3
import botocore
import hashlib
from celery.result import AsyncResult
from fastapi.responses import JSONResponse
import database
from sqlalchemy.orm import Session
from models import tasks_model
from schemas import tasks_schema
from sqlalchemy.future import select
from kombu.utils.url import safequote
from celery import Celery
from celery import shared_task
import time

class suga_request(BaseModel):
    voice: str 
    text: str

    class Config:
        orm_mode = True


session = boto3.Session(
    aws_access_key_id='AKIAT2O2SZBBDI4Q3EFJ',
    aws_secret_access_key='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',
)

s3 = session.resource('s3')
BUCKET = "riri.prixacdn.net"

bucket_session = s3.Bucket(BUCKET)




sugaApi = FastAPI(title="Suga-RiRi", openapi_url="/openapi.json")

url = "https://riri.prixa.net/api/speak/"


headers = {
  'Authorization': 'Token r1YOqaiZ3ePjTUWJRgAP2fHUUMmMRQis7dA0MGcfAkKM5Wca3sXI72qV3tneSfdBRLh1bohRC7CrUTze77YK5pvGq3Z4jt5tUVcBUsFWJXRmRoqyEty7gt39qkHSDw5N'
}



# def get_audio_text(wavfilepath):
#     rObject = sr.Recognizer()
#     wavFile = sr.AudioFile(wavfilepath)
#     with wavFile as source:
#         audio = rObject.record(source)
#     try:
#         text = rObject.recognize_google(audio, language ='ne-NP')
#         print("You : ", text)
#         return text
#     except:
#         print("Could not understand your audio, PLease try again !")
#         return 0

class riri_reponse(BaseModel):
    status: str 
    text: str
    result_audio: str

    class Config:
        orm_mode = True



def check_and_infer(text: str, voice: str):
    ntext = text + '_' + voice
    filename_md5_encodded = hashlib.md5(ntext.encode())
    filename =  filename_md5_encodded.hexdigest()

    fname = f"output/{filename}.wav"

    try:
        s3.Object(BUCKET, fname).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("Object Does not exists")
        else:
            print("Something else has gone wrong.")
        # file_exists = False
        print("Np file exists in bucket so inferecing the text")
        try:
            payload= {'text': text, 'voice': voice}
            response = requests.request("POST", url, headers=headers, data=payload)
            # print("response: ", response, response.json())

            return response.json()
        except:
            raise HTTPException(status_code=404, detail="RIRI Server connection error!!!")
    else:
        # file_exists = True
        print("file already exists in s3 bucket")
        return riri_reponse(
            status= "success",
            text = text,
            result_audio = f"https://{BUCKET}/{fname}")


@sugaApi.post("/suga")
def suga( voice: str, file: UploadFile = File(...),):
    try:
        contents = file.file.read()
        recognizer = sr.Recognizer()
        # audio_source = sr.AudioData(contents, 22050, 2)
        audio_source = sr.AudioData(contents, 16000, 2)

        text = recognizer.recognize_google(audio_data=audio_source,language = 'ne-NP')
        if not nr.is_devanagari(text):
            converter = Converter()
            text = converter.convert(text)
    except Exception:
        return {"message": "There was an error Reading/Uploading the wav file"}
        # return text
    finally:
        file.file.close()

    
    return check_and_infer(text, voice)


aws_access_key = safequote("AKIA5BJRLA5THBMHDDKZ")
aws_secret_key = safequote("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")

broker_url = "sqs://{aws_access_key}:{aws_secret_key}@".format(
    aws_access_key=aws_access_key, aws_secret_key=aws_secret_key,
)

app = Celery('tasks_ref', broker=broker_url,broker_transport_options = {'region': 'ap-southeast-1'} )

# @app.task(name="srec")
@app.task(name="srec2")
def srec2(url):
    # print(self.request.id)
    print(url)
    # audio_path = f"test_audio/{filename}"
    # transcription = model.transcribe(audio_path,**transcribe_options)["text"]
    return "server not hit"
    # return transcription

async def wait_until(task_id, timeout,async_session, period=0.25,):
    print("waiting")
    mustend = time.time() + timeout
    while time.time() < mustend:
        status  =await get_status(task_id,async_session)
        if status: 
            return True
        time.sleep(period)
    return False


@sugaApi.get("/whisper")
async def whisper( url: str,  async_session: Session = Depends(database.get_session)):
    task = await srec2.delay(url)
    # id = url
    print(task)
    # await wait_until(task.id,10,async_session)

    # task_sucess =  await get_task(id, async_session)

    # return check_and_infer(task_sucess.result, 'np_rija')
    return task.id




@sugaApi.post("/update_tasks")
async def update_tasks(task:tasks_schema.tasks,  async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            new_task = tasks_model.Tasks(
            id = task.id, 
            status = task.status,
            result = task.result
            )
            session.add(new_task)
            await session.flush()
            return task


@sugaApi.get("/test_task")
def test_task():
    url = 'https://newstalk.prixa.net/api/sugariri/update_tasks'
    payload={'id': 'test_id', 'status': 'sucess', 'result': 'transcription'}
    response = requests.request("POST", url, json=payload)
    return response.text


@sugaApi.get("/get_tasks_status/{task_id}")
async def get_status(task_id: str,async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            query = select(tasks_model.Tasks).where(tasks_model.Tasks.id == task_id)
            results = await session.execute(query)
            result = results.fetchone()
            if result:
                return True 
            else:          
                return False


@sugaApi.get("/get_tasks/{task_id}")
async def get_task(task_id: str,async_session: Session = Depends(database.get_session)):
    async with async_session as session:
        async with session.begin():
            query = select(tasks_model.Tasks).where(tasks_model.Tasks.id == task_id)
            results = await session.execute(query)
            result = results.scalars().one()
            return result



@sugaApi.post("/tts")
def tts(suga_request: suga_request):
    text = suga_request.text
    if not nr.is_devanagari(text):
        converter = Converter()
        text = converter.convert(text)

    return check_and_infer(text, suga_request.voice)

    # ntext = text + '_' + suga_request.voice

    # filename_md5_encodded = hashlib.md5(ntext.encode())
    # filename =  filename_md5_encodded.hexdigest()

    
    # fname = f"output/{filename}.wav"

    # try:
    #     s3.Object(BUCKET, fname).load()
    # except botocore.exceptions.ClientError as e:
    #     if e.response['Error']['Code'] == "404":
    #         print("Object Does not exists")
    #     else:
    #         print("Something else has gone wrong.")
    #     file_exists = False
    # else:
    #     file_exists = True
        
    # if file_exists:
    #     print("file already exists in s3 bucket")
    #     return riri_reponse(
    #         status= "success",
    #         text = text,
    #         result_audio = f"https://{BUCKET}/{fname}"
    #     )
    # else:
    #     print("Np file exists in bucket so inferecing the text")
    #     payload= {'text': text, 'voice': suga_request.voice}
    #     response = requests.request("POST", url, headers=headers, data=payload)
    #     # print("response: ", response, response.json())

    #     return response.json()


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(sugaApi, host="0.0.0.0", port=8001, log_level="debug")
