# from rembg import remove, new_session
# from PIL import Image, ImageFilter
# import io
#
# # load better model once (faster for repeated requests)
# session = new_session("u2net")
#
# def remove_background(image_bytes: bytes) -> Image.Image:
#     """
#     Remove background and return RGBA product image.
#     """
#
#     # run segmentation
#     output = remove(
#         image_bytes,
#         session=session,
#         alpha_matting=True,
#         alpha_matting_foreground_threshold=240,
#         alpha_matting_background_threshold=10,
#         alpha_matting_erode_size=10
#     )
#
#     # convert result to PIL image
#     image = Image.open(io.BytesIO(output)).convert("RGBA")
#
#     # refine alpha mask (smooth edges)
#     alpha = image.split()[3]
#     alpha = alpha.filter(ImageFilter.GaussianBlur(1))
#
#     image.putalpha(alpha)
#
#     return image

import io
from PIL import Image, ImageFilter, ImageEnhance
from rembg import remove, new_session
from fastapi import APIRouter, UploadFile, File

# 1. Use 'u2net'. It is much better at identifying 'solid' objects
# like this cooler compared to 'isnet'.
session = new_session("u2net")


def remove_background(image_bytes: bytes) -> Image.Image:
    # Load original image
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # --- STEP 1: PRE-PROCESS CONTRAST ---
    # We temporarily boost contrast so the light gray body
    # stands out from the white counter for the AI model.
    enhancer = ImageEnhance.Contrast(img)
    temp_img = enhancer.enhance(1.5)  # Increase contrast by 50%

    # Convert temp image back to bytes for rembg
    temp_buffer = io.BytesIO()
    temp_img.save(temp_buffer, format="PNG")
    temp_bytes = temp_buffer.getvalue()

    # --- STEP 2: REMOVE BACKGROUND ---
    # Lower thresholds allow the model to be 'braver' with light colors.
    output = remove(
        temp_bytes,
        session=session,
        alpha_matting=True,
        alpha_matting_foreground_threshold=130,  # Lower = more inclusive
        alpha_matting_background_threshold=15,
        alpha_matting_erode_size=5
    )

    # Convert rembg result to PIL
    result_img = Image.open(io.BytesIO(output)).convert("RGBA")

    # --- STEP 3: MASK REFINEMENT ---
    # We extract the mask and 'grow' it slightly to recover missing edges
    alpha = result_img.split()[3]

    # Dilation (MaxFilter) fills in the gaps at the bottom
    alpha = alpha.filter(ImageFilter.MaxFilter(3))
    # Erosion (MinFilter) brings the edge back to the correct spot
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    # Smooth out the jagged edges from the white counter
    alpha = alpha.filter(ImageFilter.GaussianBlur(1))

    # Apply the refined mask to the ORIGINAL image
    # (This ensures we keep the natural colors of the cooler)
    final_output = img.convert("RGBA")
    final_output.putalpha(alpha)

    return final_output
