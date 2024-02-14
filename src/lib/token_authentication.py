import os
from typing import Optional, Dict
from logging import getLogger

import jwt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

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
        try:
            logger.info("Getting signing key...")
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            logger.info("Signing key retrieved successfully")
            return signing_key.key
        except Exception as e:
            logger.error(e)
            raise unauthorized_error

    def require_any_user(
        self, token: Optional[HTTPAuthorizationCredentials] = Depends(token_auth_scheme)
    ) -> Dict:
        """Require the request to contain a valid Bearer token."""
        logger.info("Checking for valid Bearer token...")
        if not token:
            raise unauthorized_error

        # Decode the JWT and verify it using the JWKs from Auth0
        try:
            logger.info("Getting signing key...")
            logger.info(f"domain: {domain} and audience: {audience} and jwks_url: {jwks_url}")
            logger.info(f"token.credentials: {token.credentials}")
            key = self.get_signing_key_from_jwt(token.credentials)
            logger.info("Signing key retrieved successfully")
            
            logger.info("Decoding JWT...")
            payload = jwt.decode(
                token.credentials,
                key,
                algorithms=["RS256"],
                audience=audience,
                issuer=f"https://{domain}/",
            )
            logger.info("JWT decoded successfully")
        except Exception as e:
            logger.error(e)
            raise unauthorized_error

        logger.info("Checking JWT claims...")
        if payload.get("azp") != os.getenv("AUTH0_CLIENT_ID"):
            raise unauthorized_error

        # The JWT "sub" claim is prefixed with "auth0|"
        sub_prefix = payload.get("sub").split("|")[0]
        
        logger.info(f"Sub prefix: {sub_prefix}")

        if sub_prefix not in ["auth0", "google-oauth2"]:
            logger.error("User not authorized (sub prefix check)")
            raise unauthorized_error

        return payload

    def require_user_with_permission(self, permission: str) -> Dict:
        """Require the request to contain a valid Bearer token with a specific Auth0 permission."""
        def _require_user_with_permission(
            token: Optional[HTTPAuthorizationCredentials] = Depends(
                token_auth_scheme)
        ) -> Dict:
            payload = self.require_any_user(token)

            logger.info(f"Checking for permission: {permission}...")
            if permission not in payload.get("permissions", []):
                logger.error("User not authorized (permission check)")
                raise unauthorized_error

            return payload

        return _require_user_with_permission
