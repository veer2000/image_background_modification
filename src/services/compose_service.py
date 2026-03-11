from PIL import Image


def compose_product_on_background(product: Image.Image, background: Image.Image) -> Image.Image:
    """
    Place product onto background using alpha mask.
    """

    # resize product relative to background
    max_width = int(background.width * 0.4)

    ratio = max_width / product.width

    product = product.resize(
        (max_width, int(product.height * ratio))
    )

    # center bottom placement
    x = (background.width - product.width) // 2
    y = background.height - product.height - 40

    background.paste(product, (x, y), product)

    return background