import functools
import os
from contextlib import contextmanager
from typing import Any, Callable, ClassVar, Dict, Iterator, Optional

import boto3
import botocore
from boto3.session import Session

from src.lib.enums import AWSService


@contextmanager
def does_not_raise() -> Iterator[None]:
    """Used by pytest for cases that don't raise any exceptions."""
    yield None


def running_in_lambda_environment() -> bool:
    """Return True if this function gets executed in a lambda environment.

    Return False in all other cases, e.g. if run locally or in a gitlab runner.

    If the function is run in a lambda environment, the env var `AWS_LAMBDA_FUNCTION_NAME`
    will be set.
    """
    return "AWS_LAMBDA_FUNCTION_NAME" in os.environ


def only_run_in_lambda_env(func: Callable) -> Callable:
    """Wrapper to tell a function to only run if we are executing in the lambda environment."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not running_in_lambda_environment():
            return
        return func(*args, **kwargs)

    return wrapper


async def deep_merge(original: dict, body: dict):
    for key, value in body.items():
        if isinstance(value, dict):
            node = original.get(key)
            if node is None or not isinstance(node, dict):
                node = {}
                original[key] = node
            await deep_merge(node, value)
        else:
            original[key] = value
    return original


class BotoConnector:
    """Create and store boto3 connections to AWS services.

    The goal of the class is to only initialize a connection once per service,
    preferably during Lambda initialization.

    By storing the connections in a class variable, it's possible to share established
    connections between different instances of BotoConnector.
    """

    aws_connections: ClassVar[
        Dict[AWSService, Optional[botocore.client.BaseClient]]
    ] = {s: None for s in AWSService}

    @classmethod
    def get_client(cls, service: AWSService) -> botocore.client.BaseClient:
        """Return a boto3 client to the requested service."""

        if not cls.aws_connections[service]:
            cls.initialize_client(service=service)
        return cls.aws_connections[service]

    @classmethod
    def initialize_client(cls, service: AWSService) -> None:
        """Initialize a connection to the passed service with boto3."""
        cls.aws_connections[service]: Session.client = boto3.client(
            service, region_name=os.getenv("AWS_REGION")
        )
