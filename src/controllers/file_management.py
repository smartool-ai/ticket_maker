from logging import getLogger
from typing import Dict

from fastapi import APIRouter, Depends, File, UploadFile, Response
from pixelum_core.api.authorized_api_handler import authorized_api_handler
from pixelum_core.errors.custom_exceptions import FileUploadLimitReachedError

from src.lib.token_authentication import TokenAuthentication
from src.models.dynamo.documents import DocumentsModel
from src.models.dynamo.user_metadata import UserMetadataModel
from src.schemas.file import FileListSchema
from src.services.file_management import (
    upload_file_to_s3,
    get_file_details_from_s3,
    get_all_files_from_documents,
)

router = APIRouter()
logger = getLogger(__name__)
token_authentication = TokenAuthentication()
granted_user = token_authentication.require_user_with_permission(
    "manage:upload_transcripts"
)


@router.post("/upload")
@authorized_api_handler(initialize_dynamo_tables=[DocumentsModel])
async def upload_file(
    file: UploadFile = File(...), user: UserMetadataModel = Depends(granted_user)
) -> Dict:
    """
    Uploads a file to S3 and saves the file details to DynamoDB.

    Args:
        file (UploadFile): The file to be uploaded.
        user (Dict): The user details.

    Returns:
        Dict: The response containing the uploaded file details.
    """
    logger.info(f"User has {user.file_uploads_count} file uploads remaining")
    if user.file_uploads_count == 0:
        logger.error("User has reached the maximum number of file uploads.")
        raise FileUploadLimitReachedError(
            message="User has reached the maximum number of file uploads."
        )

    resp: dict = upload_file_to_s3(file)
    user_id: str = user.user_id

    for k, item in resp.get("files").items():
        logger.info(f"item: {item}")
        document: DocumentsModel = await DocumentsModel.initialize(
            user_id=user_id,
            document_id=item.get("name"),
            document_type=item.get("extension"),
            memo=f"Transcript with filename: {item.get('name')} and extension: {item.get('extension')}",
        )

        await document.save()

    # Decrement the file uploads count for the user
    logger.info("Decrementing the file uploads count for the user")
    user.file_uploads_count -= 1
    await user.save()
    logger.info(f"User has {user.file_uploads_count} file uploads remaining")

    return resp


@router.get("/file/{file_name}")
@authorized_api_handler()
async def get_file(file_name: str, _: Dict = Depends(granted_user)) -> dict:
    """
    Retrieves a file from S3.

    Args:
        file_name (str): The name of the file to retrieve.

    Returns:
        Response: The response containing the file content or error message.
    """
    logger.info(f"Getting file from S3: {file_name}")
    resp: dict = get_file_details_from_s3(file_name)
    return (
        resp
        if not resp.get("error")
        else {"status_code": resp.get("status_code"), "content": resp.get("error")}
    )


@router.get("/file/{file_name}/content")
@authorized_api_handler()
async def get_file_content(file_name: str, _: Dict = Depends(granted_user)) -> Response:
    """
    Retrieves a files content from S3.

    Args:
        file_name (str): The name of the file to retrieve.

    Returns:
        Response: The response containing the file content or error message.
    """
    logger.info(f"Getting file from S3: {file_name}")
    resp: dict = get_file_details_from_s3(file_name, return_content=True)
    return (
        resp
        if not resp.get("error")
        else {"status_code": resp.get("status_code"), "content": resp.get("error")}
    )


@router.get("/file")
@authorized_api_handler()
async def get_all_user_uploads(
    user: UserMetadataModel = Depends(granted_user),
) -> FileListSchema:
    """
    Retrieves all the files uploaded by a user.

    Args:
        user (Dict): The user details.

    Returns:
        Dict: The response containing the user's uploaded files.
    """
    user_id: str = user.user_id
    documents: list = await get_all_files_from_documents(user_id)
    return {"documents": documents}
