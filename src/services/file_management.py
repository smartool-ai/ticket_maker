import os
import boto3
from datetime import datetime


AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
AWS_SECRET_ACCESS = os.getenv("AWS_ACCESS_KEY", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_SECRET", "test")


class S3CLI:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_SECRET_ACCESS, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    def upload_file(self, local_file_path, s3_key):
        try:
            self.s3.upload_file(local_file_path, self.bucket_name, s3_key)
            print(f"Successfully uploaded {local_file_path} to S3 bucket {self.bucket_name} with key {s3_key}")
        except Exception as e:
            print(f"Failed to upload {local_file_path} to S3 bucket {self.bucket_name}: {str(e)}")

    def download_file(self, s3_key, local_file_path):
        try:
            self.s3.download_file(self.bucket_name, s3_key, local_file_path)
            print(f"Successfully downloaded {s3_key} from S3 bucket {self.bucket_name} to {local_file_path}")
        except Exception as e:
            print(f"Failed to download {s3_key} from S3 bucket {self.bucket_name}: {str(e)}")


def upload_file_to_s3(file_object, app_name):
    """
    Uploads a file to an S3 bucket.

    Args:
        file_object (File): The file object received from a FastAPI endpoint.
        app_name (str): The name of the FastAPI app.

    Returns:
        bool: True if the file was successfully uploaded, False otherwise.
    """
    try:
        s3_client = boto3.client('s3')
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        object_name = f"{file_object.filename}_{current_datetime}"
        s3_client.upload_fileobj(file_object, app_name, object_name)
        return True
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return False
