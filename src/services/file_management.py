import datetime
import os
from typing import List, Optional

import boto3
import botocore
from fastapi import UploadFile

from src.lib.loggers import get_module_logger
from src.models.dynamo.documents import DocumentsModel

logger = get_module_logger()

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
s3 = boto3.resource("s3", region_name=AWS_REGION)
bucket = s3.Bucket(os.environ.get("ARTIST_IMAGES_BUCKET", "dev-transcriptions-ai"))


def upload_file_to_s3(file_object: UploadFile) -> dict:
    """
    Uploads a file to an S3 bucket.

    Args:
        file_object (UploadFile): The file object to be uploaded.

    Returns:
        dict: A dictionary containing the details of the uploaded file.

    Raises:
        Exception: If the file fails to upload to the S3 bucket.
    """
    try:
        # Append current datetime to the filename before the file extension
        file_name, file_extension = os.path.splitext(file_object.filename)
        filename = f"{file_name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"

        bucket.put_object(Key=filename, Body=file_object.file)
        print(
            f"Successfully uploaded file to S3 bucket with key {file_object.filename}"
        )
        return {
            "bucket": bucket.name,
            "files": {
                "0": {
                    "name": filename,
                    "url": f"https://{bucket.name}.s3.{AWS_REGION}.amazonaws.com/{file_object.filename}",
                    "extension": file_extension,
                    "size": file_object.size / 1000,
                }
            },
        }
    except Exception as e:
        print(f"Failed to upload file to S3 bucket: {str(e)}")
        raise


def get_file_details_from_s3(s3_key):
    """
    Retrieves the details of a file from an S3 bucket.

    Args:
        s3_key (str): The S3 key of the file.

    Returns:
        dict: A dictionary containing the details of the file.

    Raises:
        botocore.exceptions.ClientError: If the file is not found in the S3 bucket.
    """
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
    """
    Downloads a file from an S3 bucket and returns its contents.

    Args:
        s3_key (str): The S3 key of the file to download.

    Returns:
        str: The contents of the file, or None if the file is not found.

    Raises:
        botocore.exceptions.ClientError: If the file is not found in the S3 bucket.
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


async def get_all_files_from_documents(user_id: str) -> List[DocumentsModel]:
    """
    Retrieves all the files uploaded by a user.

    Args:
        user_id (str): The user ID.

    Returns:
        List[DocumentsModel]: A list of DocumentsModel objects representing the user's uploaded files.
    """
    try:
        documents = DocumentsModel.query(hash_key=user_id)
    except Exception as e:
        logger.error(f"Failed to retrieve files from DynamoDB: {str(e)}")
        raise e

    return [document for document in documents]


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
