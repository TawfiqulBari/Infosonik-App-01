from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from jose import JWTError, jwt
import speech_recognition as sr
import os
import json
import io
import aiofiles
from typing import Optional, List
import uuid
from pathlib import Path

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://infsnk-app-01.tawfiqulbari.work/auth/callback")
ALLOWED_DOMAIN = "infosonik.com"

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Security
security = HTTPBearer()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    google_id = Column(String, unique=True)
    profile_picture = Column(String)
    is_active = Column(Boolean, default=True)
    preferences = Column(Text)  # JSON string for user preferences
    created_at = Column(DateTime, default=datetime.utcnow)

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    language = Column(String)
    theme = Column(String, default="light")
    attachments = Column(Text)  # JSON string for file attachments
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    google_event_id = Column(String)
    attachments = Column(Text)  # JSON string for file attachments
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FileAttachment(Base):
    __tablename__ = "file_attachments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    filename = Column(String)
    original_filename = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    file_path = Column(String)
    google_drive_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    name: str
    google_id: str
    profile_picture: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    profile_picture: Optional[str] = None
    preferences: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserPreferences(BaseModel):
    theme: str = "light"
    language: str = "en"
    notifications: bool = True
    backup_frequency: str = "daily"

class NoteCreate(BaseModel):
    title: str
    content: str
    language: str = "en"
    theme: str = "light"
    attachments: Optional[List[str]] = []

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    language: str
    theme: str
    attachments: Optional[List[dict]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EventCreate(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    attachments: Optional[List[str]] = []

class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    google_event_id: Optional[str] = None
    attachments: Optional[List[dict]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BackupRequest(BaseModel):
    include_files: bool = True
    backup_name: Optional[str] = None

class RestoreRequest(BaseModel):
    backup_id: str
    restore_files: bool = True

# FastAPI app
app = FastAPI(title="Infosonik Notes & Calendar App")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(user_id: int = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Google OAuth functions
def get_google_oauth_flow():
    # Use more specific scope names for better compatibility
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    
    # Disable HTTPS requirement for local development
    # In production with HTTPS, this is automatically secure
    import os
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    return flow

def verify_infosonik_domain(email: str):
    return email.endswith(f"@{ALLOWED_DOMAIN}")

# Google Drive functions
def get_drive_service(credentials):
    return build('drive', 'v3', credentials=credentials)

def upload_to_drive(file_path: str, filename: str, credentials):
    service = get_drive_service(credentials)
    file_metadata = {'name': filename}
    media = MediaFileUpload(file_path)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

def download_from_drive(file_id: str, credentials):
    service = get_drive_service(credentials)
    request = service.files().get_media(fileId=file_id)
    file_io = io.BytesIO()
    downloader = MediaIoBaseDownload(file_io, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return file_io.getvalue()

# Voice recognition
def recognize_speech(audio_file, language='en-US'):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Could not request results"

# Google Calendar integration
def create_calendar_event(event_data, credentials):
    service = build('calendar', 'v3', credentials=credentials)
    
    event = {
        'summary': event_data.title,
        'description': event_data.description,
        'start': {
            'dateTime': event_data.start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': event_data.end_time.isoformat(),
            'timeZone': 'UTC',
        },
    }
    
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event['id']

# Authentication endpoints
@app.get("/auth/google")
async def google_auth():
    flow = get_google_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent')
    return {"auth_url": auth_url}

@app.get("/auth/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    flow = get_google_oauth_flow()
    try:
        flow.fetch_token(code=code)
    except Exception as e:
        # Handle OAuth scope warnings that are treated as exceptions
        if "Scope has changed" in str(e) or "Warning: Scope has changed" in str(e):
            print(f"OAuth scope warning handled: {e}")
            # Re-try the token fetch ignoring warnings
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                flow.fetch_token(code=code)
        else:
            print(f"OAuth error: {e}")
            raise HTTPException(status_code=400, detail=f"OAuth authentication failed: {str(e)}")
    
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
        user = User(
            email=email,
            name=user_info.get('name'),
            google_id=user_info.get('id'),
            profile_picture=user_info.get('picture'),
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
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "profile_picture": user.profile_picture,
            "preferences": json.loads(user.preferences) if user.preferences else {}
        }
    }

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    preferences = json.loads(current_user.preferences) if current_user.preferences else {}
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        profile_picture=current_user.profile_picture,
        preferences=preferences,
        created_at=current_user.created_at
    )

@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Remove user sessions
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Successfully logged out"}

# User preferences endpoints
@app.put("/user/preferences")
async def update_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.preferences = json.dumps(preferences.dict())
    db.commit()
    return {"message": "Preferences updated successfully"}

# File upload endpoints
@app.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_types = ['application/pdf', 'application/vnd.ms-excel', 
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'text/plain', 'image/jpeg', 'image/png']
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
    unique_filename = f"{file_id}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file locally
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # Upload to Google Drive if user has session
    google_drive_id = None
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if session and session.access_token:
        try:
            credentials = Credentials(token=session.access_token, refresh_token=session.refresh_token)
            google_drive_id = upload_to_drive(str(file_path), file.filename, credentials)
        except Exception as e:
            print(f"Failed to upload to Google Drive: {e}")
    
    # Save file info to database
    file_attachment = FileAttachment(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_type=file.content_type,
        file_size=len(content),
        file_path=str(file_path),
        google_drive_id=google_drive_id
    )
    db.add(file_attachment)
    db.commit()
    db.refresh(file_attachment)
    
    return {
        "id": file_attachment.id,
        "filename": file_attachment.original_filename,
        "file_type": file_attachment.file_type,
        "file_size": file_attachment.file_size,
        "google_drive_id": google_drive_id
    }

@app.get("/files/")
async def list_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    files = db.query(FileAttachment).filter(FileAttachment.user_id == current_user.id).all()
    return [{
        "id": file.id,
        "filename": file.original_filename,
        "file_type": file.file_type,
        "file_size": file.file_size,
        "google_drive_id": file.google_drive_id,
        "created_at": file.created_at
    } for file in files]

@app.get("/files/{file_id}/download")
async def download_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file_attachment = db.query(FileAttachment).filter(
        FileAttachment.id == file_id,
        FileAttachment.user_id == current_user.id
    ).first()
    
    if not file_attachment:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_attachment.file_path,
        filename=file_attachment.original_filename,
        media_type=file_attachment.file_type
    )

# Notes endpoints
@app.post("/notes/", response_model=NoteResponse)
async def create_note(
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_note = Note(
        user_id=current_user.id,
        title=note.title,
        content=note.content,
        language=note.language,
        theme=note.theme,
        attachments=json.dumps(note.attachments) if note.attachments else "[]"
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Process attachments
    attachments_data = []
    if note.attachments:
        for attachment_id in note.attachments:
            file_attachment = db.query(FileAttachment).filter(
                FileAttachment.id == int(attachment_id),
                FileAttachment.user_id == current_user.id
            ).first()
            if file_attachment:
                attachments_data.append({
                    "id": file_attachment.id,
                    "filename": file_attachment.original_filename,
                    "file_type": file_attachment.file_type
                })
    
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        language=db_note.language,
        theme=db_note.theme,
        attachments=attachments_data,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )

@app.get("/notes/", response_model=List[NoteResponse])
async def get_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notes = db.query(Note).filter(Note.user_id == current_user.id).all()
    result = []
    
    for note in notes:
        attachments_data = []
        if note.attachments:
            attachment_ids = json.loads(note.attachments)
            for attachment_id in attachment_ids:
                file_attachment = db.query(FileAttachment).filter(
                    FileAttachment.id == int(attachment_id),
                    FileAttachment.user_id == current_user.id
                ).first()
                if file_attachment:
                    attachments_data.append({
                        "id": file_attachment.id,
                        "filename": file_attachment.original_filename,
                        "file_type": file_attachment.file_type
                    })
        
        result.append(NoteResponse(
            id=note.id,
            title=note.title,
            content=note.content,
            language=note.language,
            theme=note.theme,
            attachments=attachments_data,
            created_at=note.created_at,
            updated_at=note.updated_at
        ))
    
    return result

@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db_note.title = note.title
    db_note.content = note.content
    db_note.language = note.language
    db_note.theme = note.theme
    db_note.attachments = json.dumps(note.attachments) if note.attachments else "[]"
    db_note.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_note)
    
    # Process attachments
    attachments_data = []
    if note.attachments:
        for attachment_id in note.attachments:
            file_attachment = db.query(FileAttachment).filter(
                FileAttachment.id == int(attachment_id),
                FileAttachment.user_id == current_user.id
            ).first()
            if file_attachment:
                attachments_data.append({
                    "id": file_attachment.id,
                    "filename": file_attachment.original_filename,
                    "file_type": file_attachment.file_type
                })
    
    return NoteResponse(
        id=db_note.id,
        title=db_note.title,
        content=db_note.content,
        language=db_note.language,
        theme=db_note.theme,
        attachments=attachments_data,
        created_at=db_note.created_at,
        updated_at=db_note.updated_at
    )

@app.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()
    
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted successfully"}

# Events endpoints
@app.post("/events/", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get user's Google credentials
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    google_event_id = None
    
    if session and session.access_token:
        try:
            credentials = Credentials(token=session.access_token, refresh_token=session.refresh_token)
            google_event_id = create_calendar_event(event, credentials)
        except Exception as e:
            print(f"Failed to create Google Calendar event: {e}")
    
    db_event = Event(
        user_id=current_user.id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        google_event_id=google_event_id,
        attachments=json.dumps(event.attachments) if event.attachments else "[]"
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Process attachments
    attachments_data = []
    if event.attachments:
        for attachment_id in event.attachments:
            file_attachment = db.query(FileAttachment).filter(
                FileAttachment.id == int(attachment_id),
                FileAttachment.user_id == current_user.id
            ).first()
            if file_attachment:
                attachments_data.append({
                    "id": file_attachment.id,
                    "filename": file_attachment.original_filename,
                    "file_type": file_attachment.file_type
                })
    
    return EventResponse(
        id=db_event.id,
        title=db_event.title,
        description=db_event.description,
        start_time=db_event.start_time,
        end_time=db_event.end_time,
        google_event_id=google_event_id,
        attachments=attachments_data,
        created_at=db_event.created_at,
        updated_at=db_event.updated_at
    )

@app.get("/events/", response_model=List[EventResponse])
async def get_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    events = db.query(Event).filter(Event.user_id == current_user.id).all()
    result = []
    
    for event in events:
        attachments_data = []
        if event.attachments:
            attachment_ids = json.loads(event.attachments)
            for attachment_id in attachment_ids:
                file_attachment = db.query(FileAttachment).filter(
                    FileAttachment.id == int(attachment_id),
                    FileAttachment.user_id == current_user.id
                ).first()
                if file_attachment:
                    attachments_data.append({
                        "id": file_attachment.id,
                        "filename": file_attachment.original_filename,
                        "file_type": file_attachment.file_type
                    })
        
        result.append(EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            start_time=event.start_time,
            end_time=event.end_time,
            google_event_id=event.google_event_id,
            attachments=attachments_data,
            created_at=event.created_at,
            updated_at=event.updated_at
        ))
    
    return result

# Backup and restore endpoints
@app.post("/backup/create")
async def create_backup(
    backup_request: BackupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Google Drive access required")
    
    # Create backup data
    notes = db.query(Note).filter(Note.user_id == current_user.id).all()
    events = db.query(Event).filter(Event.user_id == current_user.id).all()
    
    backup_data = {
        "backup_date": datetime.utcnow().isoformat(),
        "user_id": current_user.id,
        "notes": [{
            "title": note.title,
            "content": note.content,
            "language": note.language,
            "theme": note.theme,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        } for note in notes],
        "events": [{
            "title": event.title,
            "description": event.description,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "created_at": event.created_at.isoformat(),
            "updated_at": event.updated_at.isoformat()
        } for event in events]
    }
    
    # Save backup to temporary file
    backup_filename = f"infosonik_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    backup_path = UPLOAD_DIR / backup_filename
    
    async with aiofiles.open(backup_path, 'w') as f:
        await f.write(json.dumps(backup_data, indent=2))
    
    # Upload to Google Drive
    try:
        credentials = Credentials(token=session.access_token, refresh_token=session.refresh_token)
        backup_drive_id = upload_to_drive(str(backup_path), backup_filename, credentials)
        
        # Clean up local file
        os.remove(backup_path)
        
        return {
            "message": "Backup created successfully",
            "backup_id": backup_drive_id,
            "backup_name": backup_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@app.post("/backup/restore")
async def restore_backup(
    restore_request: RestoreRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Google Drive access required")
    
    try:
        credentials = Credentials(token=session.access_token, refresh_token=session.refresh_token)
        backup_data = download_from_drive(restore_request.backup_id, credentials)
        backup_json = json.loads(backup_data.decode('utf-8'))
        
        # Restore notes
        for note_data in backup_json.get('notes', []):
            db_note = Note(
                user_id=current_user.id,
                title=note_data['title'],
                content=note_data['content'],
                language=note_data['language'],
                theme=note_data.get('theme', 'light'),
                attachments="[]"
            )
            db.add(db_note)
        
        # Restore events
        for event_data in backup_json.get('events', []):
            db_event = Event(
                user_id=current_user.id,
                title=event_data['title'],
                description=event_data['description'],
                start_time=datetime.fromisoformat(event_data['start_time']),
                end_time=datetime.fromisoformat(event_data['end_time']),
                attachments="[]"
            )
            db.add(db_event)
        
        db.commit()
        
        return {"message": "Backup restored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")

@app.post("/voice-to-text/")
async def voice_to_text(language: str = "en-US"):
    # In a real app, you'd receive the audio file here
    # This is a placeholder implementation
    return {"text": "Recognized text will appear here"}

# Mount static files and serve React app
if os.path.exists("static"):
    # Mount the React build static files
    app.mount("/static", StaticFiles(directory="static/static"), name="static")
    
    @app.get("/")
    async def read_index():
        return FileResponse('static/index.html')
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # Serve React app for all routes not handled by API
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc"):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse('static/index.html')
