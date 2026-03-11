from fastapi import APIRouter, UploadFile, File, HTTPException
import requests
from PIL import Image
import io
import urllib.parse
import os
from rembg import remove
from fastapi.responses import StreamingResponse
from src.services.mask_service import remove_background
from src.services.compose_service import compose_product_on_background

router = APIRouter(tags=["Pollination Image Generator"])
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

@router.post("/pollination_generate-product-scene")
async def generate_background(prompt: str, image: UploadFile = File(...)):
    """
    Generate background using Pollinations Flux model
    """
    image_bytes =  await image.read()

    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file.")

    # we are masking our image
    product = remove_background(image_bytes)

    encoded_prompt = urllib.parse.quote(prompt)

    url = f"https://gen.pollinations.ai/image/{encoded_prompt}"

    params = {
        "model": "flux",
        "width": 1024,
        "height": 1024,
        "quality": "medium",
        "negative_prompt": "worst quality, blurry"
    }

    headers = {
        "Authorization": f"Bearer {POLLINATIONS_API_KEY}"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(f"Background generation failed: {response.text}")

    background = Image.open(io.BytesIO(response.content)).convert("RGBA")
    final_image = compose_product_on_background(product, background)

    buffer = io.BytesIO()
    final_image.save(buffer, format="PNG")
    # product.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")