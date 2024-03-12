from typing import List 

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from schemas import GenerationRequest, GenerationResponse, TrainResponse   # 통신에 활용하는 자료 형태를 정의합니다.
from database import GenerationResult, TrainResult
from model import get_pipe, generate, patch_pipeline
from config import config, train_config
from env import env

from PIL import Image
from lora_diffusion.cli_lora_pti import train
import shutil
import io
import os 
import urllib.request 
import uuid 
import boto3


router = APIRouter()
s3 = boto3.client(
        's3',
        aws_access_key_id=env.access_key_id,
        aws_secret_access_key=env.access_key,
        region_name=env.region
    )

@router.post("/api/model/background/train")
def background_train(style_images: List[UploadFile] = File(...)) -> None:
    # set unique model name
    model_name = f"{uuid.uuid4()}"

    # clear dir
    try:
        shutil.rmtree(os.path.join(train_config.data_dir, model_name))
    except:
        pass
    
    # make dir
    os.makedirs(os.path.join(train_config.data_dir, model_name), exist_ok=True)
    
    # load & save style image
    for i, style_image in enumerate(style_images):
        request_object_content = style_image.file.read()
        style_image = Image.open(io.BytesIO(request_object_content)).convert("RGB").resize((512, 512))
        style_image.save(os.path.join(train_config.data_dir, model_name, f"{i}.jpg"))

    # train
    output_dir = os.path.join(train_config.model_dir, model_name+"_r"+str(train_config.rank))
    train(
        pretrained_model_name_or_path=train_config.pipeline_name,
        instance_data_dir=os.path.join(train_config.data_dir, model_name),
        output_dir=output_dir,
        train_text_encoder = True,
        resolution=train_config.resolution,
        train_batch_size=1,
        gradient_accumulation_steps=4,
        scale_lr = True,
        learning_rate_unet=train_config.lr_unet,
        learning_rate_text=train_config.lr_text,
        learning_rate_ti=train_config.lr_ti,
        color_jitter = True,
        lr_scheduler="linear",
        lr_warmup_steps=0,
        placeholder_tokens="<s1>|<s2>",
        use_template="style",
        save_steps=500,
        max_train_steps_ti=train_config.step_ti,
        max_train_steps_tuning=train_config.step_tuning,
        perform_inversion=True,
        clip_ti_decay = True,
        weight_decay_ti=0.000,
        weight_decay_lora=0.00,
        continue_inversion = True,
        continue_inversion_lr=1e-4,
        device="cuda:0",
        lora_rank=train_config.rank,
        seed=train_config.seed
    )
    
    # convert to response format
    generated_result = TrainResult(result = output_dir)
    
    # if we don't use train images, run this code.
    shutil.rmtree(os.path.join(train_config.data_dir, model_name)) 
    
    return TrainResponse(
        result = generated_result.result
    )


@router.post("/api/model/background/")
def background_inference(model_path: str = str(...), content_image: UploadFile = File(...)) -> GenerationResponse:
    # make dir
    os.makedirs('results', exist_ok=True)
    
    # patch pipeline
    result = patch_pipeline(model_path=model_path)
    if not result:
        generated_result = GenerationResult(result = "Error: There is no trained model.")
        return GenerationResponse(
            result = generated_result.result
        )

    # load pipeline
    pipe = get_pipe()
    
    # load content image
    request_object_content = content_image.file.read()
    content = io.BytesIO(request_object_content)

    # generate
    generated_images = generate(pipe, content)
    generated_image_bytes = []

    # save
    for i, img in enumerate(generated_images):        
        # convert image to bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        generated_image_bytes.append(buf.getvalue())
        
        # Local Save
        # background_file_name = f"{uuid.uuid4()}__result{i}.jpg"
        # img.save(f"results/{background_file_name}")
    
    # return StreamingResponse
    return StreamingResponse(generated_image_bytes, media_type="image/png")