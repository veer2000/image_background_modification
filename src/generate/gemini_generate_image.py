from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import io
import os
from google import genai
from google.genai import types
from PIL import Image
from src.services.mask_service import remove_background
from src.services.background_service import generate_background
from src.services.compose_service import compose_product_on_background

router = APIRouter(tags=["Gimini AI"])
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

@router.post("/generate-product-scene")
async def generate_product_scene(
        image: UploadFile = File(...),
        prompt: str = Form(...)
):
    try:
        model_id = "gemini-3.1-flash-image-preview"
        image_bytes = await image.read()

        # we are masking our image
        product = remove_background(image_bytes)


        # Refine prompt for background generation
        refined_prompt = f"Professional product photography background: {prompt}. High resolution, 8k, bokeh, no people."


        response = client.models.generate_content(
            model=model_id,
            contents=refined_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                candidate_count=1
            ),
        )

        # Extract the image bytes from the response parts
        image_part = response.candidates[0].content.parts[0]

        if image_part.inline_data:
            image_bytes = image_part.inline_data.data
            background = Image.open(io.BytesIO(image_bytes))
        else:
            raise Exception("No image data returned from Gemini API")

        # compose
        final_image = compose_product_on_background(product, background)

        buffer = io.BytesIO()
        final_image.save(buffer, format="PNG")
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise