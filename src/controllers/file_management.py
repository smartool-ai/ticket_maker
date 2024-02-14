from logging import getLogger
import os
from typing import Dict

from fastapi import APIRouter, Depends, File, UploadFile, Response
from src.lib.authorized_api_handler import authorized_api_handler
from src.lib.enums import AWSService

from src.lib.token_authentication import TokenAuthentication
from src.services.file_management import upload_file_to_s3, download_file_from_s3

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission("manage:upload_transcripts")


@router.post("/upload")
# @authorized_api_handler()
async def upload_file(
    upload: UploadFile, user: Dict = Depends(granted_user)
) -> Dict:
    return (
        Response(status_code=201, content="File uploaded successfully")
        if upload_file_to_s3(upload)
        else Response(status_code=400, content="Error uploading file to S3")
    )


@router.get("/file/{file_name}")
# @authorized_api_handler()
async def get_file(file_name: str, user: Dict = Depends(granted_user)) -> Response:
    """Get file from S3"""
    logger.info(f"Getting file from S3: {file_name}")
    resp: dict = download_file_from_s3(file_name)
    return (
        resp
        if not resp.get("error")
        else Response(status_code=resp.get("status_code"), content=resp.get("error"))
    )
