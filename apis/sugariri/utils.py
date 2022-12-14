from fastapi import HTTPException
import boto3
import botocore
import hashlib
import requests

BUCKET = "riri.prixacdn.net"

# bucket_session = s3.Bucket(BUCKET)

def init_aws_session():
    session = boto3.Session(
                aws_access_key_id='AKIAT2O2SZBBDI4Q3EFJ',
                aws_secret_access_key='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',
            )
    s3 = session.resource('s3')
    
    return s3

url = "https://riri.prixa.net/api/speak/"


headers = {
  'Authorization': 'Token r1YOqaiZ3ePjTUWJRgAP2fHUUMmMRQis7dA0MGcfAkKM5Wca3sXI72qV3tneSfdBRLh1bohRC7CrUTze77YK5pvGq3Z4jt5tUVcBUsFWJXRmRoqyEty7gt39qkHSDw5N'
}

def check_and_infer(text: str, voice: str):
    ntext = text + '_' + voice
    filename_md5_encodded = hashlib.md5(ntext.encode())
    filename =  filename_md5_encodded.hexdigest()

    fname = f"output/{filename}.mp3"
    s3= init_aws_session()

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
    finally:
        # file_exists = True
        del s3
        print("file already exists in s3 bucket")
        return { 'status': "success",
                'text':text,
                'result_audio': f"https://{BUCKET}/{fname}"
        }