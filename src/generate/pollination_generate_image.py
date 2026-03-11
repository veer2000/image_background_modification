from fastapi import APIRouter
import requests
from PIL import Image
import io
import urllib.parse
import os
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["Pollination Image Generator"])
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

@router.get("/generate-product-scene")
def generate_background(prompt: str):
    """
    Generate background using Pollinations Flux model
    """

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
    img = Image.open(io.BytesIO(response.content)).convert("RGBA")

    # 2. Save image to a byte buffer
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    # 3. Return as a StreamingResponse
    return StreamingResponse(buf, media_type="image/png")
    # return Image.open(io.BytesIO(response.content)).convert("RGBA")