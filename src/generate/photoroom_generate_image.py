from http.client import responses

from fastapi import APIRouter, UploadFile, HTTPException, Response
from dotenv import load_dotenv
from fastapi.params import File
from PIL import Image
import requests
import os

router = APIRouter()
load_dotenv()

api_key  = os.getenv("PHOTOROOM_API_KEY")
photoroomurl = os.getenv("PHOTOROOM_API_URL")
#def generate_image(prompt : str, file: UploadFile = File(...)):
@router.post('/generate')
async def generate_image(prompt : str, file: UploadFile | None = File(default=None)):
    try:
        # img = Image.open(file.file)
        # img.show()
        file_data = await file.read()

        files = {
            "imageFile": (file.filename, file_data , file.content_type)
        }

        data = {
            "background_detail": prompt
        }

        headers = {
            'x-api-key': api_key,
            "Accept": "image/png"
        }

        request_is = requests.post(photoroomurl, headers=headers, files=files, data=data)

        if request_is.status_code != 200:
            raise HTTPException(status_code=request_is.status_code, detail=request_is.text)

        return Response(content=request_is.content, media_type="image/png")

        # return {"Prompt" : prompt, "file": img}
    except HTTPException as ht:
        raise ht
    except Exception as e:
        raise e