from fastapi import HTTPException, File, UploadFile, Form, APIRouter
import requests
import os
import json
from rembg import remove
from PIL import Image
import io

CLAID_API_KEY = os.getenv("CLAID_API_KEY")
if not CLAID_API_KEY:
    raise RuntimeError("Please set the CLAID_API_KEY environment variable.")

router = APIRouter()

UPLOAD_URL = "https://api.claid.ai/v1/image/edit/upload"
SCENE_URL = "https://api.claid.ai/v1/scene/create"


@router.post("/add-background")
async def add_background(
    prompt: str = Form(...),
    image_file: UploadFile = File(...)
):
    """
    Removes background using rembg, uploads product PNG to Claid,
    then generates AI background.
    """

    try:
        # -------- Step 1: Read uploaded image --------
        image_bytes = await image_file.read()

        # -------- Step 2: Remove background --------
        output_image = remove(image_bytes)

        # Convert to file-like object
        product_image = io.BytesIO(output_image)
        product_image.name = "product.png"

        # -------- Step 3: Upload image to Claid --------
        upload_headers = {"Authorization": f"Bearer {CLAID_API_KEY}"}

        files = {
            "file": ("product.png", product_image, "image/png"),
            "data": (
                None,
                json.dumps({
                    "operations": [],
                    "output": {"format": "png"}
                }),
                "application/json"
            )
        }

        upload_resp = requests.post(
            UPLOAD_URL,
            headers=upload_headers,
            files=files,
            timeout=30
        )

        if upload_resp.status_code != 200:
            raise HTTPException(status_code=upload_resp.status_code, detail=upload_resp.text)

        resp_json = upload_resp.json()

        uploaded_image_url = resp_json.get("data", {}).get("output", {}).get("tmp_url")

        if not uploaded_image_url:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get uploaded image URL from Claid. Response: {resp_json}"
            )

        # -------- Step 4: Generate background scene --------
        scene_payload = {
            "object": {
                "image_url": uploaded_image_url,
                "rotation_degree": 0.0,
                "scale": 0.55,
                "position": {"x": 0.35, "y": 0.5}
            },
            "scene": {
                "template_url": "https://images.claid.ai/photoshoot-templates/docs/scene.png",
                "template_mode": "transform",
                "view": "front",
                "prompt": prompt
            },
            "output": {
                "number_of_images": 1,
                "format": "png"
            }
        }

        scene_headers = {
            "Authorization": f"Bearer {CLAID_API_KEY}",
            "Content-Type": "application/json"
        }

        scene_resp = requests.post(
            SCENE_URL,
            json=scene_payload,
            headers=scene_headers,
            timeout=30
        )

        if scene_resp.status_code != 200:
            raise HTTPException(status_code=scene_resp.status_code, detail=scene_resp.text)

        return scene_resp.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")