from fastapi import FastAPI, File, UploadFile
import speech_recognition as sr
import nepali_roman as nr
from nepali_unicode_converter.convert import Converter
import requests
from pydantic import BaseModel

class suga_request(BaseModel):
    voice: str 
    text: str

    class Config:
        orm_mode = True



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





@sugaApi.post("/tts/{text}")
def tts(suga_request: suga_request):
    if not nr.is_devanagari(text):
        converter = Converter()
        text = converter.convert(text)

    payload= {'text': suga_request.text, 'voice': suga_request.voice}
    response = requests.request("POST", url, headers=headers, data=payload)
    # print("response: ", response, response.json())

    return response.json()


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(sugaApi, host="0.0.0.0", port=8001, log_level="debug")
