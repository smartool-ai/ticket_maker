import os

from pynamodb.attributes import UTCDateTimeAttribute
from pynamodb.models import Model


class BaseModel(Model):
    """The shared model underlying all Dynamo models."""

    class Meta:
        region = os.environ.get("AWS_REGION", "us-west-2")
        host = os.environ.get(
            "DYNAMO_ENDPOINT", f"https://dynamodb.{region}.amazonaws.com"
        )

    created_datetime = UTCDateTimeAttribute()

    @classmethod
    def initialize_connection(cls) -> None:
        """Initialize connection and fetch table description, indexes, and attributes.

        By running `initialize_connection` in the global namespace, the initial connection
        and the DescribeTable call get executed when the lambda gets initialized / "warmed"
        up rather than during the actual call. This saves about 150ms every time a new instance
        of the lambda gets started up (usually every few minutes).
        """
        cls.describe_table()
        cls.get_attributes()
