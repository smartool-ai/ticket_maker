import os

from src.lib.dynamo_utils import BaseModel

from pynamodb.attributes import UnicodeAttribute


class UserMetadataModel(BaseModel):
    """Model representing a User and their metadata.

    fields:
        email (str, hash_key): Email address
    """

    class Meta:
        table_name = "UserMetadata"
        region = os.getenv("AWS_REGION", "us-west-2")

    email = UnicodeAttribute(hash_key=True)
