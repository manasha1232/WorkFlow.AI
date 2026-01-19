import os
# from dotenv import load_dotenv
# load_dotenv()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow

import requests

router = APIRouter(prefix="/api/auth")

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def get_google_flow():
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")

    if not client_id or not client_secret or not redirect_uri:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth env variables not set"
        )

    return Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=[
            "openid",
            "email",
            "https://www.googleapis.com/auth/userinfo.email",
        ],
        redirect_uri=redirect_uri,
    )


@router.get("/login")
def google_login():
    flow = get_google_flow()
    auth_url, _ = flow.authorization_url(
        prompt="consent",
        access_type="offline",
    )
    return RedirectResponse(auth_url)


@router.get("/callback")
def google_callback(request: Request):
    flow = get_google_flow()
    flow.fetch_token(authorization_response=str(request.url))

    credentials = flow.credentials

    userinfo = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {credentials.token}"},
    ).json()

    email = userinfo.get("email")

    frontend = os.getenv("FRONTEND_URL")

    return RedirectResponse(f"{frontend}/dashboard?email={email}")