from fastapi import FastAPI, File, UploadFile
import speech_recognition as sr
import nepali_roman as nr
from nepali_unicode_converter.convert import Converter
import requests
from kombu.utils.url import safequote
import boto3



sugaApi = FastAPI(title="Suga-RiRi", openapi_url="/openapi.json")

url = "https://riri.prixa.net/api/speak/"


headers = {
  'Authorization': 'Token r1YOqaiZ3ePjTUWJRgAP2fHUUMmMRQis7dA0MGcfAkKM5Wca3sXI72qV3tneSfdBRLh1bohRC7CrUTze77YK5pvGq3Z4jt5tUVcBUsFWJXRmRoqyEty7gt39qkHSDw5N'
}

####________________________AWS CODE_________________________________________________________________###

remote_url = 'https://riri.prixa.net/dashboard/submit-result/'
aws_access_key = safequote("AKIAT2O2SZBBDI4Q3EFJ")
aws_secret_key = safequote("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")

broker_url = "sqs://{aws_access_key}:{aws_secret_key}@".format(
    aws_access_key=aws_access_key, aws_secret_key=aws_secret_key,
)

session = boto3.Session(
    aws_access_key_id='AKIAT2O2SZBBDI4Q3EFJ',
    aws_secret_access_key='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',
)

s3 = session.resource('s3')
BUCKET = "riri.prixacdn.net"

bucket_session = s3.Bucket(BUCKET)

####___________________________________________________________________________________________________###





@sugaApi.post("/suga")
def suga( voice: str, file: UploadFile = File(...),):
    contents = file.file.read()
    recognizer = sr.Recognizer()


    # audio_source = sr.AudioData(contents, 22050, 2)
    audio_source = sr.AudioData(contents, 16000, 2)

    text = recognizer.recognize_google(audio_data=audio_source,language = 'ne-NP')
    if not nr.is_devanagari(text):
        converter = Converter()
        text = converter.convert(text)

    # return text

    payload= {'text': text, 'voice': voice}
    response = requests.request("POST", url, headers=headers, data=payload)
    # print("response: ", response, response.json())

    return response.json()


@sugaApi.get("/tts/{text}")
def tts(voice: str,text: str):
    if not nr.is_devanagari(text):
        converter = Converter()
        text = converter.convert(text)

    payload= {'text': text, 'voice': voice}
    response = requests.request("POST", url, headers=headers, data=payload)
    # print("response: ", response, response.json())

    return response.json()


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(sugaApi, host="0.0.0.0", port=8001, log_level="debug")
