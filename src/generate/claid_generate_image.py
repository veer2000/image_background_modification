# from fastapi import HTTPException, File, UploadFile, Form, APIRouter
# import requests
# import os
# import json
# from rembg import remove
# from PIL import Image
# import io
#
# CLAID_API_KEY = os.getenv("CLAID_API_KEY")
# if not CLAID_API_KEY:
#     raise RuntimeError("Please set the CLAID_API_KEY environment variable.")
#
# router = APIRouter()
#
# UPLOAD_URL = "https://api.claid.ai/v1/image/edit/upload"
# SCENE_URL = "https://api.claid.ai/v1/scene/create"
#
#
# @router.post("/add-background")
# async def add_background(
#     prompt: str = Form(...),
#     image_file: UploadFile = File(...)
# ):
#     """
#     Removes background using rembg, uploads product PNG to Claid,
#     then generates AI background.
#     """
#
#     try:
#         # -------- Step 1: Read uploaded image --------
#         image_bytes = await image_file.read()
#
#         # -------- Step 2: Remove background --------
#         output_image = remove(image_bytes)
#
#         # Convert to file-like object
#         product_image = io.BytesIO(output_image)
#         product_image.name = "product.png"
#
#         # -------- Step 3: Upload image to Claid --------
#         upload_headers = {"Authorization": f"Bearer {CLAID_API_KEY}"}
#
#         files = {
#             "file": ("product.png", product_image, "image/png"),
#             "data": (
#                 None,
#                 json.dumps({
#                     "operations": [],
#                     "output": {"format": "png"}
#                 }),
#                 "application/json"
#             )
#         }
#
#         upload_resp = requests.post(
#             UPLOAD_URL,
#             headers=upload_headers,
#             files=files,
#             timeout=30
#         )
#
#         if upload_resp.status_code != 200:
#             raise HTTPException(status_code=upload_resp.status_code, detail=upload_resp.text)
#
#         resp_json = upload_resp.json()
#
#         uploaded_image_url = resp_json.get("data", {}).get("output", {}).get("tmp_url")
#
#         if not uploaded_image_url:
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Failed to get uploaded image URL from Claid. Response: {resp_json}"
#             )
#
#         # -------- Step 4: Generate background scene --------
#         scene_payload = {
#             "object": {
#                 "image_url": uploaded_image_url,
#                 "rotation_degree": 0.0,
#                 "scale": 0.55,
#                 "position": {"x": 0.35, "y": 0.5}
#             },
#             "scene": {
#                 "template_url": "https://images.claid.ai/photoshoot-templates/docs/scene.png",
#                 "template_mode": "transform",
#                 "view": "front",
#                 "prompt": prompt
#             },
#             "output": {
#                 "number_of_images": 1,
#                 "format": "png"
#             }
#         }
#
#         scene_headers = {
#             "Authorization": f"Bearer {CLAID_API_KEY}",
#             "Content-Type": "application/json"
#         }
#
#         scene_resp = requests.post(
#             SCENE_URL,
#             json=scene_payload,
#             headers=scene_headers,
#             timeout=30
#         )
#
#         if scene_resp.status_code != 200:
#             raise HTTPException(status_code=scene_resp.status_code, detail=scene_resp.text)
#
#         return scene_resp.json()
#
#     except requests.exceptions.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
from fastapi import HTTPException, File, UploadFile, Form, APIRouter
from fastapi.responses import StreamingResponse
import requests
import os
import json
from rembg import remove
from PIL import Image
import io

CLAID_API_KEY = os.getenv("CLAID_API_KEY")

if not CLAID_API_KEY:
    raise RuntimeError("Please set the CLAID_API_KEY environment variable.")

router = APIRouter(tags=['CLAID AI'])

UPLOAD_URL = "https://api.claid.ai/v1/image/edit/upload"
SCENE_URL = "https://api.claid.ai/v1/scene/create"


@router.post("/add-background")
async def add_background(
        prompt: str = Form(...),
        image_file: UploadFile = File(...)
):
    """
    Upload product image, remove background, generate AI background,
    then overlay original product on generated background.
    """

    try:


        # Step 1: Read uploaded image

        image_bytes = await image_file.read()

        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty image file.")


        # Step 2: Remove background

        transparent_product = remove(image_bytes)

        product_buffer = io.BytesIO(transparent_product)
        product_buffer.name = "product.png"


        # Step 3: Upload product to Claid

        upload_headers = {
            "Authorization": f"Bearer {CLAID_API_KEY}"
        }

        files = {
            "file": ("product.png", product_buffer, "image/png"),
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
            raise HTTPException(
                status_code=upload_resp.status_code,
                detail=upload_resp.text
            )

        upload_json = upload_resp.json()

        uploaded_image_url = upload_json.get("data", {}).get("output", {}).get("tmp_url")

        if not uploaded_image_url:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve uploaded image URL: {upload_json}"
            )

        # -----------------------------
        # Step 4: Generate background scene
        # -----------------------------
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

        scene_data = scene_resp.json()

        if scene_resp.status_code != 200:
            raise HTTPException(
                status_code=scene_resp.status_code,
                detail=scene_data
            )

        # -----------------------------
        # Step 5: Extract background URL safely
        # -----------------------------
        background_url = scene_data.get("data", {}).get("output", [{}])[0].get("tmp_url")

        if not background_url:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected Claid response format: {scene_data}"
            )

        # -----------------------------
        # Step 6: Download generated background
        # -----------------------------
        bg_response = requests.get(background_url)

        if bg_response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Failed to download generated background."
            )

        background = Image.open(io.BytesIO(bg_response.content)).convert("RGBA")

        # -----------------------------
        # Step 7: Load product image
        # -----------------------------
        product_buffer.seek(0)
        product = Image.open(product_buffer).convert("RGBA")

        # Resize product (optional)
        max_width = background.width // 2
        ratio = max_width / product.width
        new_height = int(product.height * ratio)

        product = product.resize((max_width, new_height))

        # -----------------------------
        # Step 8: Compute position
        # -----------------------------
        x = (background.width - product.width) // 2
        y = background.height - product.height - 50

        # -----------------------------
        # Step 9: Paste product on background
        # -----------------------------
        background.paste(product, (x, y), product)

        # -----------------------------
        # Step 10: Return final image
        # -----------------------------
        output_buffer = io.BytesIO()
        background.save(output_buffer, format="PNG")
        output_buffer.seek(0)

        return StreamingResponse(
            output_buffer,
            media_type="image/png"
        )

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"External request error: {str(e)}"
        )