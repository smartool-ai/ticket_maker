from io import BytesIO
from logging import getLogger
from typing import Dict
import os

from PIL import Image
from fastapi import APIRouter, UploadFile, Depends, Response
import botocore
import boto3

from src.lib.token_authentication import TokenAuthentication

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:artist_images")

region_name = os.environ.get("AWS_REGION", "us-west-2")
s3 = boto3.resource("s3", region_name=region_name)
bucket = s3.Bucket(os.environ.get("ARTIST_IMAGES_BUCKET", "artist-images-dev"))
image_sizes = {"small": 0.158, "medium": 0.41728, "large": 0.66667}


def upload_image(filename, file_obj):
    bucket.put_object(Key=filename, Body=file_obj)
    return filename


def resize_image(file_obj, ratio):
    file_obj.seek(0)
    image = Image.open(file_obj)
    height, width = image.size

    resized_image = image.resize(
        (
            int(height * ratio),
            int(width * ratio),
        )
    )

    byte_arr = BytesIO()
    resized_image.save(byte_arr, format=image.format)
    byte_arr.seek(0)
    return byte_arr


@router.get("/artist_image/{filename}")
async def get_artist_image(
    filename: str, response: Response, user: Dict = Depends(granted_user)
) -> Dict:
    try:
        obj = s3.Object(bucket.name, filename)
        obj.load()
        return {
            "bucket": bucket.name,
            "filename": obj.key,
            "url": f"https://{bucket.name}.s3.{region_name}.amazonaws.com/{obj.key}",
        }
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            response.status_code = 404
            return {"error": "File not found"}
        else:
            raise


@router.post("/artist_image")
async def upload_artist_image(
    upload: UploadFile, user: Dict = Depends(granted_user)
) -> Dict:
    uploaded_files = {}

    # Upload original image
    xlarge_image_name = upload_image(upload.filename, upload.file)
    uploaded_files["xlarge"] = {
        "name": xlarge_image_name,
        "url": f"https://{bucket.name}.s3.{region_name}.amazonaws.com/{xlarge_image_name}"
    }

    # Resize and upload other image sizes
    for image_size, size in image_sizes.items():
        resized_image = resize_image(upload.file, size)
        if "xlarge" in upload.filename:
            resized_name = upload.filename.replace("xlarge", image_size)
        else:
            filename, extension = os.path.splitext(upload.filename)
            resized_name = f"{filename}_{image_size}{extension}"
        upload_image(resized_name, resized_image)
        uploaded_files[image_size] = {
            "name": resized_name,
            "url": f"https://{bucket.name}.s3.{region_name}.amazonaws.com/{resized_name}",
        }

    return {"bucket": bucket.name, "files": uploaded_files}
