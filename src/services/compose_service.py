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




#
# from PIL import Image
#
# import cv2
# import numpy as np
#
# def detect_surface(background):
#
#     gray = cv2.cvtColor(np.array(background), cv2.COLOR_RGB2GRAY)
#
#     edges = cv2.Canny(gray, 50, 150)
#
#     lines = cv2.HoughLinesP(
#         edges,
#         1,
#         np.pi/180,
#         threshold=100,
#         minLineLength=200,
#         maxLineGap=20
#     )
#
#     surface_y = None
#
#     if lines is not None:
#         for line in lines:
#             x1, y1, x2, y2 = line[0]
#
#             if abs(y1 - y2) < 10:  # horizontal line
#                 if surface_y is None or y1 > surface_y:
#                     surface_y = y1
#
#     if surface_y is None:
#         surface_y = int(background.height * 0.75)
#
#     return surface_y
#
#
# def compose_product_on_background(product, background):
#
#     surface_y = detect_surface(background)
#
#     max_height = int(surface_y * 0.6)
#
#     ratio = max_height / product.height
#
#     product = product.resize(
#         (int(product.width * ratio), max_height)
#     )
#
#     x = (background.width - product.width) // 2
#     y = surface_y - product.height
#
#     background.paste(product, (x, y), product)
#
#     return background