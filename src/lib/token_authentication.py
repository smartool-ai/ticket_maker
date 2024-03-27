import os
from typing import Optional, Dict
from logging import getLogger

import jwt
from auth0.authentication import GetToken
from auth0.management import Auth0
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED
from src.models.dynamo.user_metadata import UserMetadataModel

from src.services.user import get_user_metadata


logger = getLogger(__name__)
token_auth_scheme = HTTPBearer()

# Fetch the JWKS from Auth0 during startup
domain = os.getenv("AUTH0_DOMAIN", "test")
audience = os.getenv("AUTH0_AUDIENCE", "test")
jwks_url = f"https://{domain}/.well-known/jwks.json"
jwks_client = jwt.PyJWKClient(jwks_url, timeout=15)

unauthorized_error = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class TokenAuthentication:
    def get_signing_key_from_jwt(self, token: str) -> str:
        """
        Get the signing key from the JWT token.

        Args:
            token (str): The JWT token.

        Returns:
            str: The signing key.

        Raises:
            HTTPException: If the signing key cannot be retrieved.
        """
        try:
            logger.debug("Getting signing key...")
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            logger.debug("Signing key retrieved successfully")
            return signing_key.key
        except Exception as e:
            logger.error(e)
            raise unauthorized_error

    def require_any_user(
        self, token: Optional[HTTPAuthorizationCredentials] = Depends(token_auth_scheme)
    ) -> Dict:
        """
        Require the request to contain a valid Bearer token.

        Args:
            token (Optional[HTTPAuthorizationCredentials], optional): The Bearer token. Defaults to Depends(token_auth_scheme).

        Returns:
            Dict: The decoded JWT payload.

        Raises:
            HTTPException: If the request does not contain a valid Bearer token or if the JWT cannot be decoded or verified.
        """
        logger.debug("Checking for valid Bearer token...")
        if not token:
            raise unauthorized_error

        # Decode the JWT and verify it using the JWKs from Auth0
        try:
            logger.debug("Getting signing key...")
            logger.debug(
                f"domain: {domain} and audience: {audience} and jwks_url: {jwks_url}"
            )
            key = self.get_signing_key_from_jwt(token.credentials)
            logger.debug("Signing key retrieved successfully")

            logger.debug("Decoding JWT...")
            payload = jwt.decode(
                token.credentials,
                key,
                algorithms=["RS256"],
                audience=audience,
                issuer=f"https://{domain}/",
            )
            logger.debug("JWT decoded successfully")
        except Exception as e:
            logger.error(e)
            raise unauthorized_error

        logger.debug("Checking JWT claims...")
        if payload.get("azp") != os.getenv("AUTH0_CLIENT_ID"):
            raise unauthorized_error

        # The JWT "sub" claim is prefixed with "auth0|"
        sub_prefix = payload.get("sub").split("|")[0]

        logger.debug(f"Sub prefix: {sub_prefix}")

        if sub_prefix not in ["auth0", "google-oauth2"]:
            logger.error("User not authorized (sub prefix check)")
            raise unauthorized_error

        return payload

    def get_user_details(self, user_id: str) -> dict:
        """Get the user details from the auth0."""
        get_token = GetToken(
            domain,
            client_id=os.getenv("AUTH0_MGMT_CLIENT_ID", "test"),
            client_secret=os.getenv("AUTH0_MGMT_CLIENT_SECRET", "test"),
        )

        token = get_token.client_credentials("https://{}/api/v2/".format(domain))
        api_token = token["access_token"]

        auth0 = Auth0(domain, api_token)

        try:
            user = auth0.users.get(user_id)
            return user
        except Exception as e:
            logger.error(f"Error getting user details with user id: {user_id} \n{e}")
            return {}

    def require_user_with_permission(self, permission: str) -> Dict:
        """
        Require the request to contain a valid Bearer token with a specific Auth0 permission.

        Args:
            permission (str): The required permission.

        Returns:
            Dict: The decoded JWT payload.

        Raises:
            HTTPException: If the request does not contain a valid Bearer token, if the JWT cannot be decoded or verified,
                           or if the user does not have the required permission.
        """
        def _require_user_with_permission(
            token: Optional[HTTPAuthorizationCredentials] = Depends(token_auth_scheme),
        ) -> Dict:
            payload = self.require_any_user(token)

            logger.debug(f"Checking for permission: {permission}...")
            if permission not in payload.get("permissions", []):
                logger.error("User not authorized (permission check)")
                raise unauthorized_error

            # Check if user metadata is in our db, if not add it
            user_metadata: Optional[UserMetadataModel] = get_user_metadata(payload.get("sub", "").split("|")[1])

            if not user_metadata:
                user_details = self.get_user_details(payload.get("sub"))

                user_metadata = UserMetadataModel.synchronous_initialize(
                    user_id=payload.get("sub", "").split("|")[1],
                    email=user_details.get("email"),
                    signup_method=payload.get("sub", "").split("|")[0],
                    permissions=payload.get("permissions", []),
                )
                user_metadata.synchronous_save()

            return user_metadata

        return _require_user_with_permission
