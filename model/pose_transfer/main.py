from fastapi import FastAPI
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, Response, JSONResponse
from requests_toolbelt import MultipartEncoder
import fastapi as _fapi
from fastapi.middleware.cors import CORSMiddleware

from database import GenerationResult
from schemas import GenerationResponse
import services as _services
import io
from pathlib import Path
import uuid
import shutil
import os
import base64

from env import env
import uuid 
import boto3


s3 = boto3.client(
        's3',
        aws_access_key_id=env.access_key_id,
        aws_secret_access_key=env.access_key,
        region_name=env.region
    )

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Stable Diffussers API"}

# Endpoint to test the Front-end and backend
@app.get("/api")
async def root():
    return {"message": "Welcome to the Demo of StableDiffusers with FastAPI"}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    file_extension = Path(file.filename).suffix
    new_filename = f"{uuid.uuid4()}{file_extension}"
    file_location = f"uploads/{new_filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": new_filename, "location": file_location}

@app.post("/translate-pose")
async def translate_pose(file_source: UploadFile = File(...), file_target: UploadFile = File(...)):
    # save files
    source_path = f"uploads/{file_source.filename}"
    target_path = f"uploads/{file_target.filename}"

    if not os.path.exists(os.path.join(os.getcwd(), 'uploads')):
        os.mkdir(os.path.join(os.getcwd(), 'uploads'))

    if not os.path.exists(os.path.join(os.getcwd(), 'results')):
        os.mkdir(os.path.join(os.getcwd(), 'results'))

    with open(source_path, "wb") as buffer:
        shutil.copyfileobj(file_source.file, buffer)
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file_target.file, buffer)

    try:
        image_result, image_pose = await _services.generate_image(source=source_path, target=target_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"failed image generation: {str(e)}")


    image_result.save(os.path.join(os.getcwd(), 'results', 'result.png'), 'png')
    image_pose.save(os.path.join(os.getcwd(), 'results', 'pose.png'), 'png')

    images = [image_to_byte_array(image_result), image_to_byte_array(image_pose)]
    base64_images = [base64.b64encode(img).decode('utf-8') for img in images]
    print(len(base64_images))
    return JSONResponse(content={"images": base64_images})


def image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()
    # imgByteArr.seek(0)
    return imgByteArr

