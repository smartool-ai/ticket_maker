import json
from src.lib.loggers import get_module_logger
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypedDict

logger = get_module_logger()

class HTTP_Response(TypedDict):
    """HTTP_Response that lambdas should return to get processed by the API Gateway.
    The API Gateway expects each response to have exactly these four keys. See
    https://aws.amazon.com/premiumsupport/knowledge-center/malformed-502-api-gateway/
    """
    statusCode: int
    headers: Dict[str, str]
    isBase64Encoded: bool
    body: str

class _HTTPError(Exception):
    """Base class for HTTP errors.
    Each HTTPError requires a status code and error message to generate an HTTP response.
    """
    status_code: int

    def generate_http_response(self) -> HTTP_Response:
        """Return an HTTP_Error_Response from the exception."""
        return {
            "statusCode": self.status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "isBase64Encoded": False,
            "body": json.dumps({"message": self.error_message}),
        }

    @property
    def error_message(self) -> str:  # type: ignore
        ...

class _400RangeHTTPError(_HTTPError):
    """Base class for all 400 range HTTP errors.
    All of these errors include user mistakes during input and require a descriptive error message.
    """
    @property
    def error_message(self) -> str:
        return str(self)

class BaseException(Exception):
    """
    Base exception class that we created so that we can just extend this whenever
    we want to make a custom exception.
    If you add the argument 'message' you may pass a string with
    placeholder brackets that can be filled with given args.
    Example:
        raise ExtraArgument("Invalid usage")
    This will create the string: SampleSet Some arg 2
    You can add more arguments and more placeholders to produce
    a more detailed message as well, just remember that the messages
    is formatted in the order resource_name, resource_identifier, kwargs[0],
    kwargs[1], etc..
    """
    def __init__(self, message: Optional[str] = None, **kwargs: Any):
        self._message = message
        self._kwargs = kwargs

    @property
    def message(self) -> str:
        return self.create_message()

    def create_message(self) -> str:
        if not self._message:
            ret = self.__class__.__name__
        else:
            ret = self._message

        notes = []
        for k in self._kwargs:
            v = repr(self._kwargs[k])
            note = " {}={}".format(k, v)
            notes.append(note)

        if notes:
            ret += ",".join(notes)

        return ret

    def __str__(self) -> str:
        return self.create_message()

class MissingRequiredData(BaseException):
    """
    Custom class for when add/updating row and some data that is required is missing
    """
    pass

class GeneralMissingDataError(BaseException):
    pass

class ObjectDoesNotExist(BaseException):
    pass

class InvalidInput(BaseException):
    """
    This exception is raised when the input that the api receives from the client
    is not the proper datatype
    """
    pass

class ResourceNotFoundException(BaseException):
    def __init__(
        self,
        message: Optional[str] = None,
        resource_name: Optional[str] = None,
        resource_identifier: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Initializer to create class values of resource name and resource indetifier
        """
        self._resource_name = resource_name
        self._resource_identifier = resource_identifier
        self._message = f"Resource {resource_name} was not found with given identifier {resource_identifier}"
        if message:
            # Prepend any message
            self._message = message + " " + self._message
        self._kwargs = kwargs

    @property
    def resource_name(self) -> str:
        return str(self._resource_name)

    @property
    def resource_identifier(self) -> str:
        return str(self._resource_identifier)

class InsufficientFunds(BaseException):
    """Raised when funds are insufficient to perform an action."""

class RedisCacheException(BaseException):
    """Raise when a read from or write to redis failed."""

class InvalidAddress(BaseException):
    """Raise when trying to store an invalid address."""

class UnprocessableEntity422(_400RangeHTTPError):
    """HTTP 422 Error"""
    status_code = 422

class ConflictError(BaseException):
    """Base conflict error."""

class ServerFailureError(BaseException):
    """Error when an integrated service fails."""

class IncompleteOnboardingError(BaseException):
    """Error when a user has not completed onboarding."""

class PlatformLinkError(BaseException):
    """Error when a user has not linked a platform."""

async def allow_exceptions(
    callable: Callable,
    exceptions: Tuple[Type[ResourceNotFoundException], Type[RedisCacheException]],
    *args: Any,
    **kwargs: Any,
) -> Optional[str]:
    """
    Wrapper method that catches specific exceptions, logs them, and returns None
    Args:
        callable (function)
        excpetions (List)
    """
    try:
        result = await callable(*args, **kwargs)
        return result
    except exceptions as err:
        logger.error(err)
        return None

async def allow_not_found(
    callable: Callable, *args: Any, **kwargs: Any
) -> Optional[str]:
    return await allow_exceptions(
        callable, (ResourceNotFoundException, RedisCacheException), *args, **kwargs
    )
