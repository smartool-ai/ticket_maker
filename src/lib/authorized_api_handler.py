from datetime import datetime
from functools import wraps
from typing import Any, List, Optional, Type

from fastapi import Response, status

from src.lib.custom_exceptions import (
    ConflictError,
    FileUploadLimitReachedError,
    IncompleteOnboardingError,
    InsufficientFunds,
    InvalidInput,
    MissingRequiredData,
    ObjectDoesNotExist,
    PlatformLinkError,
    ServerFailureError,
    TicketGenerationLimitReachedError
)
from src.lib.dynamo_connector import initialize_dynamo_tables
from src.lib.dynamo_utils import BaseModel
from src.lib.enums import AWSService
from src.lib.lambda_utils import initialize_boto_connections
from src.lib.loggers import get_module_logger

BAD_REQUEST_ERRORS = (
    ConflictError,
    FileUploadLimitReachedError,
    IncompleteOnboardingError,
    InsufficientFunds,
    InvalidInput,
    MissingRequiredData,
    ObjectDoesNotExist,
    PlatformLinkError,
    TicketGenerationLimitReachedError,
)
SERVICE_UNAVAILABLE_ERRORS = ServerFailureError


class AuthorizedApiHandler:
    """This class handles dependency injection."""

    def __init__(self) -> None:
        self.dependencies = {
            "logger": get_module_logger(),
        }

    def __call__(
        self,
        boto_clients_to_initialize: Optional[List[AWSService]] = None,
        models_to_initialize: Optional[List[Type[BaseModel]]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        This method is called when an instance of the class is called as a function.
        It initializes the necessary dependencies and returns a decorator function.
        """
        self.dependencies["logger"].debug(
            f"Initializing Dynamo Tables: {models_to_initialize}"
        )
        try:
            initialize_dynamo_tables(models_to_initialize=models_to_initialize)
            initialize_boto_connections(
                boto_clients_to_initialize=boto_clients_to_initialize
            )
        except Exception as e:
            self.dependencies["logger"].error(
                f"Failed to initialize Dynamo Tables: {e}"
            )
            raise e

        def decorator(func: Any) -> Any:
            """
            This decorator function wraps the route function and handles exceptions.
            """

            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    self.dependencies["logger"].info("Calling route function")
                    self.dependencies["logger"].debug(
                        f"Here are the kwargs passed to route function: {kwargs}"
                    )
                    self.dependencies["logger"].debug(
                        f"Here are the args passed to route function: {args}"
                    )
                    return await func(*args, **kwargs)
                except BAD_REQUEST_ERRORS as e:
                    self.dependencies["logger"].exception(e)
                    return Response(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content=e.message,
                        headers={"Content-Type": "text/plain"},
                    )
                except SERVICE_UNAVAILABLE_ERRORS as e:
                    self.dependencies["logger"].exception(e)
                    return Response(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        content=f"Unexpected error has occured. Please try again later.\n{e}",
                        headers={"Content-Type": "text/plain"},
                    )
                except Exception as e:
                    self.dependencies["logger"].exception(e)
                    return Response(
                        status_code=500,
                        content=f"An unexpected error has occured: {datetime.now()}",
                        headers={"Content-Type": "text/plain"},
                    )

            return wrapper

        return decorator


authorized_api_handler = AuthorizedApiHandler()
