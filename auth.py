from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from database import get_db
from models import User, UserSession
from utils import (
    create_access_token, get_current_user_from_token,
    get_google_oauth_flow, verify_infosonik_domain,
    get_credentials_from_session, get_gmail_service
)
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    profile_picture: str = None
    preferences: dict = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserPreferences(BaseModel):
    theme: str = "light"
    language: str = "en"
    notifications: bool = True
    backup_frequency: str = "daily"

# Dependency functions
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    return get_current_user_from_token(token, db)

def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.email != 'tawfiqul.bari@infosonik.com':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Authentication endpoints
@router.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    flow = get_google_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return {"auth_url": auth_url}

@router.get("/auth/callback")
async def google_callback(code: str, state: str = None, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    flow = get_google_oauth_flow()
    try:
        # Fetch the token with the authorization code
        flow.fetch_token(code=code)
    except Exception as e:
        error_msg = str(e).lower()
        print(f"OAuth error details: {e}")

        # Handle specific OAuth errors
        if "invalid_grant" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="OAuth grant expired or invalid. Please try logging in again."
            )
        elif "invalid_request" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth request. Please try logging in again."
            )
        elif "unauthorized_client" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="OAuth client not authorized. Please contact administrator."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="OAuth authentication failed. Please try again."
            )

    credentials = flow.credentials

    # Get user info from Google
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()

    email = user_info.get('email')
    if not verify_infosonik_domain(email):
        raise HTTPException(
            status_code=403,
            detail="Access restricted to infosonik.com domain users only"
        )

    # Create or update user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Set admin status for the specified admin email
        is_admin = email == 'tawfiqul.bari@infosonik.com'
        user = User(
            email=email,
            name=user_info.get('name'),
            google_id=user_info.get('id'),
            profile_picture=user_info.get('picture'),
            is_admin=is_admin,
            preferences=json.dumps({"theme": "light", "language": "en"})
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Store user session
    session = UserSession(
        user_id=user.id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        expires_at=credentials.expiry
    )
    db.add(session)
    db.commit()

    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Redirect to the main app with token in URL fragment for React to handle
    redirect_url = f"/?token={access_token}&user={user.name}&email={user.email}"
    return RedirectResponse(url=redirect_url)

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    preferences = json.loads(current_user.preferences) if current_user.preferences else {}
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        profile_picture=current_user.profile_picture,
        preferences=preferences,
        created_at=current_user.created_at
    )

@router.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user by removing sessions"""
    # Remove user sessions
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Successfully logged out"}

@router.put("/user/preferences")
async def update_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    current_user.preferences = json.dumps(preferences.dict())
    db.commit()
    return {"message": "Preferences updated successfully"}

# Test endpoint
@router.get("/test/auth")
async def test_auth(current_user: User = Depends(get_current_user)):
    """Test authentication endpoint"""
    return {"message": f"Hello {current_user.name}, your ID is {current_user.id}"}

# Helper functions for role-based access
def get_user_role(user: User, db: Session):
    """Get the role assigned to a user"""
    from models import Role
    if user.role_id:
        return db.query(Role).filter(Role.id == user.role_id).first()
    return None

def user_has_permission(user: User, permission: str, db: Session) -> bool:
    """Check if user has a specific permission through their role"""
    role = get_user_role(user, db)
    if role and role.permissions:
        permissions = json.loads(role.permissions)
        return permission in permissions
    return False

def require_permission(permission: str):
    """Dependency factory to require specific permission"""
    def permission_dependency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # Admins have all permissions
        if current_user.is_admin or current_user.email == 'tawfiqul.bari@infosonik.com':
            return current_user

        if not user_has_permission(current_user, permission, db):
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission}' required"
            )
        return current_user

    return permission_dependency