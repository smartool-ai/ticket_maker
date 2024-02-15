import datetime
import os
from typing import Optional

import boto3
import botocore
from fastapi import UploadFile

from src.lib.loggers import get_module_logger

logger = get_module_logger()

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
s3 = boto3.resource("s3", region_name=AWS_REGION)
bucket = s3.Bucket(os.environ.get("ARTIST_IMAGES_BUCKET", "transcriptions-ai"))


def upload_file_to_s3(file_object: UploadFile) -> dict:
    try:
        # Append current datetime to the filename before the file extension
        file_name, file_extension = os.path.splitext(file_object.filename)
        filename = f"{file_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"

        bucket.put_object(Key=filename, Body=file_object.file)
        print(
            f"Successfully uploaded file to S3 bucket  with key {file_object.filename}"
        )
        return {
            "bucket": bucket.name,
            "files": {
                "1": {
                    "name": filename,
                    "url": f"https://{bucket.name}.s3.{AWS_REGION}.amazonaws.com/{file_object.filename}",
                    "extension": file_extension,
                }
            },
        }
    except Exception as e:
        print(f"Failed to upload file to S3 bucket : {str(e)}")
        raise


def get_file_details_from_s3(s3_key):
    try:
        obj = s3.Object(bucket.name, s3_key)
        logger.info("Loading file...")
        obj.load()
        logger.info("File loaded")
        return {
            "bucket_name": bucket.name,
            "filename": obj.key,
            "url": f"https://{bucket.name}.s3.amazonaws.com/{obj.key}",
        }
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return {"error": "File not found", "status_code": 404}
        else:
            raise


def download_file_from_s3(s3_key) -> Optional[str]:
    """Download file and return its contents

    Args:
        s3_key (str): The S3 key of the file to download

    Returns:
        str: The contents of the file
    """
    try:
        obj = s3.Object(bucket.name, s3_key)
        logger.info("Loading file...")
        obj.load()
        logger.info("File loaded")
        return obj.get()["Body"].read().decode("utf-8")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return None
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
        get_file_details_from_s3(filename)
    except Exception as e:
        print(e)
