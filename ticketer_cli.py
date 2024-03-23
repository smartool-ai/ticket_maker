import argparse
import os

import boto3


AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
AWS_SECRET_ACCESS = os.getenv("AWS_ACCESS_KEY", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_SECRET", "test")


class S3CLI:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_SECRET_ACCESS,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

    def upload_file(self, local_file_path, s3_key):
        try:
            self.s3.upload_file(local_file_path, self.bucket_name, s3_key)
            print(
                f"Successfully uploaded {local_file_path} to S3 bucket {self.bucket_name} with key {s3_key}"
            )
        except Exception as e:
            print(
                f"Failed to upload {local_file_path} to S3 bucket {self.bucket_name}: {str(e)}"
            )

    def download_file(self, s3_key, local_file_path):
        try:
            self.s3.download_file(self.bucket_name, s3_key, local_file_path)
            print(
                f"Successfully downloaded {s3_key} from S3 bucket {self.bucket_name} to {local_file_path}"
            )
        except Exception as e:
            print(
                f"Failed to download {s3_key} from S3 bucket {self.bucket_name}: {str(e)}"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AWS S3 CLI")
    parser.add_argument(
        "command", choices=["upload", "download"], help="Command to execute"
    )
    parser.add_argument("local_file_path", help="Local file path")
    parser.add_argument("s3_key", help="S3 key")
    parser.add_argument("--bucket", default="dev-transcriptions-ai", help="S3 bucket name")

    args = parser.parse_args()

    s3_cli = S3CLI(args.bucket)

    if args.command == "upload":
        s3_cli.upload_file(args.local_file_path, args.s3_key)
    elif args.command == "download":
        s3_cli.download_file(args.s3_key, args.local_file_path)
