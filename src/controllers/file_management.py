from logging import getLogger
from typing import Dict

from fastapi import APIRouter, File, UploadFile, Response

from src.lib.token_authentication import TokenAuthentication
from src.services.file_management import upload_file_to_s3

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:users")


# Create a route for uploading a file
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
    # file: UploadFile = File(...), user: Dict = Depends(granted_user)
) -> Dict:
    return Response(status_code=201, content="File uploaded successfully") if upload_file_to_s3(file, "app_name") else Response(status_code=400, content="Error uploading file to S3")
