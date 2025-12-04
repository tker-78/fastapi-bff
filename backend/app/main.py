import os
import uuid
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from .auth import keycloak_openid, verify_token, login_required, role_required, KEYCLOAK_URL
from .session_store import session_store

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.urandom(24),
    max_age=3600,
)

@app.get("/api/login")
async def login(request: Request, state="/"):
    request.session["state"] = state
    request.session["nonce"] = str(uuid.uuid4())

    request_uri = keycloak_openid.auth_url(
        redirect_uri=os.getenv("CALLBACK_URL"),
        scope="openid email roles",
        state=state,
        nonce=request.session["nonce"],
    )

    return RedirectResponse(request_uri)


@app.get("/api/callback")
async def callback( request: Request, code: str, state: str) -> Response:
    # stateの検証
    saved_state = request.session.get("state")
    saved_nonce = request.session.get("nonce")

    if not saved_state or saved_state != state:
        raise HTTPException(status_code=400, detail="Invalid state")

    # 認可コードでtokenを取得
    tokens = keycloak_openid.token(
        code=code,
        grant_type="authorization_code",
        redirect_uri=os.getenv("CALLBACK_URL"),
    )

    session_id = str(uuid.uuid4())
    session_store[session_id] = tokens

    print(session_store)

    # レスポンス先とcookieの設定
    redirect_response = RedirectResponse(url=os.getenv("FRONTEND_URL"))
    redirect_response.set_cookie("session_id", session_id, httponly=True, samesite="lax", secure=False)

    return redirect_response


@app.get("/api/logout")
async def logout(request: Request, response: Response):
    session_id = request.cookies.get("session_id")

    if session_id in session_store:
        del session_store[session_id]

    logout_url = (f"http://localhost:8080/realms/local-dev/protocol/openid-connect/logout"
        f"?post_logout_redirect_uri={os.getenv('FRONTEND_URL')}"
        f"&client_id={os.getenv('CLIENT_ID')}"
        )

    redirect_response = RedirectResponse(url=logout_url)
    redirect_response.delete_cookie("session_id")

    return redirect_response

@app.get("/api/verify-token")
async def verify_token(payload = Depends(verify_token)):
    return payload


@app.get("/api/protected")
async def protected(payload = Depends(login_required)):
    return {"message": "Hello World. This is protected."}


@app.get("/api/protected-by-role")
async def protected_by_role(payload = Depends(role_required("general"))):
    return {"message": "Hello World. This is protected and allowed for general role."}








