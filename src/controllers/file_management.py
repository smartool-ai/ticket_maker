from logging import getLogger
from typing import Dict

from fastapi import APIRouter, Depends, File, UploadFile, Response
from src.lib.authorized_api_handler import authorized_api_handler

from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.documents import DocumentsModel
from src.services.file_management import upload_file_to_s3, get_file_details_from_s3

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:upload_transcripts"
)


@router.post("/upload")
@authorized_api_handler(initialize_dynamo_tables=[DocumentsModel])
async def upload_file(
    file: UploadFile = File(...), user: Dict = Depends(granted_user)
) -> Dict:
    resp: dict = upload_file_to_s3(file)
    user_id: str = user.get("sub").split("|")[1]

    for k, item in resp.get("files").items():
        logger.info(f"item: {item}")
        document: DocumentsModel = await DocumentsModel.initialize(
            user_id=user_id,
            document_id=item.get("name"),
            document_type=item.get("extension"),
            memo=f"Transcript with filename: {item.get('name')} and extension: {item.get('extension')}",
        )

        await document.save()

    return resp


@router.get("/file/{file_name}")
@authorized_api_handler()
async def get_file(file_name: str, _: Dict = Depends(granted_user)) -> Response:
    """Get file from S3"""
    logger.info(f"Getting file from S3: {file_name}")
    resp: dict = get_file_details_from_s3(file_name)
    return (
        resp
        if not resp.get("error")
        else Response(status_code=resp.get("status_code"), content=resp.get("error"))
    )
