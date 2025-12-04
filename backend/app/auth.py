import os
import httpx
from fastapi import HTTPException, Depends, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from keycloak import KeycloakOpenID
from jose import jwt, JWTError
from typing import Optional

from .session_store import session_store

load_dotenv()

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
REALM = os.getenv("REALM")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=CLIENT_ID,
    realm_name=REALM,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
)

# security = HTTPBearer()

async def get_tokens_from_session(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="No session ID")
    tokens = session_store.get(session_id)
    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid session ID")
    return tokens


async def verify_token(tokens = Depends(get_tokens_from_session)):
    token = tokens.get("access_token")
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: No keyID",
            )
        jwks_url = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"
        async with httpx.AsyncClient() as client:
            jwks_response = await client.get(jwks_url)
            jwks = jwks_response.json()

        rsa_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = {
                    "kty": key.get("kty"),
                    "kid": key.get("kid"),
                    "use": key.get("use"),
                    "n": key.get("n"),
                    "e": key.get("e"),
                }
        print("rsa_key: ", rsa_key)

        if not rsa_key:
            raise HTTPException(
                status_code=401,
                detail="Public key not found in jwks",
        )

        # issuer = f"{KEYCLOAK_URL}/realms/{REALM}"
        issuer = "http://localhost:8080/realms/local-dev"

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            issuer=issuer,
            options= {
                "verify_signature": True,
                "verify_aud": False,
                "verify_exp": True,
            }
        )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid or expired token: {e}")


async def login_required(payload = Depends(verify_token)):
    return payload

def role_required(*required_roles: str):
    async def dependency(
            payload: dict = Depends(verify_token)
    ):
        roles = payload.get("resource_access", {}).get(CLIENT_ID).get("roles", [])
        if not any(r in roles for r in required_roles):
            raise HTTPException(status_code=403, detail="Forbidden")
        return payload
    return dependency



















