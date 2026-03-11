from rembg import remove
from PIL import Image
import io


def remove_background(image_bytes: bytes) -> Image.Image:
    """
    Remove background and return RGBA product image.
    """

    output = remove(
        image_bytes,
        alpha_matting=True,
        alpha_matting_foreground_threshold=240,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10
    )

    image = Image.open(io.BytesIO(output)).convert("RGBA")

    return image