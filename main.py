from fastapi import FastAPI
from src.generate.photoroom_generate_image import router as photoroom_image_generator
from src.generate.claid_generate_image import router as claid_image_generator

app = FastAPI(title = "Image Generation")

app.include_router(photoroom_image_generator)
app.include_router(claid_image_generator)

