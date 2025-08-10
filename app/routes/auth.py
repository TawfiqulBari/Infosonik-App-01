from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from app.config import settings
from urllib.parse import urlencode
import httpx

router = APIRouter(prefix="/auth")

@router.get("/google")
async def google_auth():
    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"auth_url": auth_url}

@router.get("/callback")
async def google_callback(code: str):
    try:
        # Exchange code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            token_data = response.json()
            
            # Get user info
            userinfo = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"}
            )
            user_data = userinfo.json()
            
            # Here you would typically create/update user in your database
            # and generate your own JWT token
            
            return RedirectResponse(
                url=f"/?token={token_data['access_token']}&user={user_data['name']}&email={user_data['email']}"
            )
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))