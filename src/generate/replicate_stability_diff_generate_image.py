from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, File, UploadFile
from rembg import remove
import replicate
import os
import dotenv
from PIL import Image
import io

load_dotenv()

router =APIRouter()

STABILITY_DIFF_API_KEY = os.getenv('STABILITY_DIFF_API_KEY')

if not STABILITY_DIFF_API_KEY:
    raise RuntimeError("Please set the STABILITY_DIFF_API_KEY environment variable.")

@router.post('/replicate_stability_diff_generate_image')
async def replicate_stabality_diff_generate_image(prompt : str, file:UploadFile = File(...)):
    try:
        # -------- Step 1: Read uploaded image --------
        image_bytes = await file.read()

        # -------- Step 2: Remove background --------
        output_image = remove(image_bytes)

        # Convert to file-like object
        product_image = io.BytesIO(output_image)
        product_image.name = "product.png"


    except Exception as e:
        raise e