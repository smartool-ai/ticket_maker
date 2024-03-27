import os
from typing import Dict

from pixelum_core.dynamo.base_model import BaseModel
from pixelum_core.enums.enums import Role

from pynamodb.attributes import BooleanAttribute, UnicodeAttribute
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection


class UserManagementIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = "email-index"
        projection = AllProjection()

    email = UnicodeAttribute(hash_key=True)


class UserManagementModel(BaseModel):
    """Model representing a User.

    fields:
        user_id (str, hash_key): Primary Key auth0 created
        email (str): Email address
        password (str): UnicodeAttribute()
        authenticated (bool): BooleanAttribute()
        verified (bool): Wheter the account is email verified or not
    """

    class Meta:
        table_name = "UserManagement"
        region = os.getenv("AWS_REGION", "us-west-2")

    user_id = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute()
    password = UnicodeAttribute(null=True)
    name = UnicodeAttribute(null=True)
    authenticated = BooleanAttribute(null=True)
    verified = BooleanAttribute(null=True, default=False)
    created_datetime = UnicodeAttribute(null=True)

    plaid_access_token = UnicodeAttribute(null=True)
    _role = UnicodeAttribute(null=True, default=Role.GENERAL_USER, attr_name="role")

    email_index = UserManagementIndex()

    @property
    def role(self) -> Role:
        return Role(self._role)

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "authenticated": self.authenticated,
            "verified": self.verified,
            "role": self.role.value,
            "created_datetime": self.created_datetime,
        }
