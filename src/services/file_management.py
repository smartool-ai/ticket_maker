import boto3
from datetime import datetime


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
