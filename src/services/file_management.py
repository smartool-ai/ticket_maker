import os
from typing import List
from datetime import datetime

import boto3
import botocore
from fastapi import UploadFile


AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
AWS_SECRET_ACCESS = os.getenv("AWS_ACCESS_KEY", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_SECRET", "test")
s3 = boto3.resource("s3", region_name=AWS_REGION, 
    aws_access_key_id=AWS_SECRET_ACCESS,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,)
bucket = s3.Bucket(os.environ.get("ARTIST_IMAGES_BUCKET", "transcriptions-ai"))

def upload_file_to_s3(file_object: UploadFile) -> str:
    try:
        bucket.put_object(Key=file_object.filename, Body=file_object.file)
        print(
            f"Successfully uploaded file to S3 bucket  with key {file_object.filename}"
        )
        return file_object.filename
    except Exception as e:
        print(
            f"Failed to upload file to S3 bucket : {str(e)}"
        )
        print(e.__class__.__name__)


def download_file_from_s3(s3_key):
    try:
        obj = s3.Object(bucket.name, s3_key)
        obj.load()
        return {
            "bucket_name": bucket.name,
            "filename": obj.key,
            "url": f"https://{bucket.name}.s3.amazonaws.com/{obj.key}"
        }
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return {"error": "File not found", "status_code": 404}
        else:
            raise


if __name__ == "__main__":
    try:
        # get file object from f"{os.getcwd()}/example_transcription.txt" and send it to upload_file_to_s3
        file_object = open(f"{os.getcwd()}/example_transcription.txt", "rb")
        filename: str = upload_file_to_s3(file_object, "dev")
        file_object.close()
        # with open(f"{os.getcwd()}/example_transcription.txt") as f:

        #     filename: str = upload_file_to_s3(f, "dev")
        download_file_from_s3(filename)
    except Exception as e:
        print(e)