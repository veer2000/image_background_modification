# src/services/background_service.py
import os

from google import genai
from google.genai import types
import io
from PIL import Image

# Initialize the client (ensure your API key is in your env)
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))


def generate_background(prompt: str):
    # Use the 2026 Flash Image model for the daily free tier
    model_id = "gemini-3.1-flash-image-preview"

    # Refine prompt for background generation
    refined_prompt = f"Professional product photography background: {prompt}. High resolution, 8k, bokeh, no people."

    try:
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
            return Image.open(io.BytesIO(image_bytes))
        else:
            raise Exception("No image data returned from Gemini API")

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise