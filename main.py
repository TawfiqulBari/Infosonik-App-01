from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, LargeBinary, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
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
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Admin, HR, Accounts, Sales, Technical
    description = Column(Text)
    permissions = Column(Text)  # JSON string for permissions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    google_id = Column(String, unique=True)
    profile_picture = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role_id = Column(Integer, nullable=True)  # Foreign key to Role
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

class LeaveApplication(Base):
    __tablename__ = "leave_applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    leave_type = Column(String)  # annual, sick, emergency, etc.
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    days_requested = Column(Integer)
    reason = Column(Text)
    status = Column(String, default="pending")  # pending, approved, rejected
    approved_by = Column(Integer, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConvenienceBill(Base):
    __tablename__ = "convenience_bills"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    bill_date = Column(DateTime, nullable=False)
    
    # Detailed expense breakdown in BDT paisa (1 BDT = 100 paisa)
    transport_amount = Column(Integer, default=0)  # Transportation costs
    transport_description = Column(Text)
    
    food_amount = Column(Integer, default=0)  # Food costs
    food_description = Column(Text)
    
    other_amount = Column(Integer, default=0)  # Other costs
    other_description = Column(Text)
    
    # Enhanced transportation details
    transport_to = Column(String(255))
    transport_from = Column(String(255))
    means_of_transportation = Column(String(255))
    
    # Additional cost breakdown in BDT paisa
    fuel_cost = Column(Integer, default=0)
    rental_cost = Column(Integer, default=0)
    
    # Client information fields
    client_id = Column(Integer, nullable=True)
    client_company_name = Column(String(255))
    client_contact_number = Column(String(50))
    expense_purpose = Column(Text)
    project_reference = Column(String(255))
    is_billable = Column(Boolean, default=False)
    
    # General description and metadata
    general_description = Column(Text)
    receipt_file_id = Column(Integer, nullable=True)
    status = Column(String, default="pending")
    approved_by = Column(Integer, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def total_amount(self):
        return ((self.transport_amount or 0) + (self.food_amount or 0) +
                (self.other_amount or 0) + (self.fuel_cost or 0) + (self.rental_cost or 0))

class UserGroup(Base):
    __tablename__ = "user_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    created_by = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GroupMembership(Base):
    __tablename__ = "group_memberships"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    group_id = Column(Integer, index=True)
    role = Column(String, default="member")  # member, admin
    added_by = Column(Integer, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)

# Models for MEDDPICC and Sales Funnel
class MEDDPICC(Base):
    __tablename__ = "meddpicc"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    client_name = Column(String)
    opportunity_name = Column(String)
    metrics = Column(Text)
    economic_buyer = Column(Text)
    decision_criteria = Column(Text)
    decision_process = Column(Text)
    paper_process = Column(Text)
    identify_pain = Column(Text)
    champion = Column(Text)
    competition = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# RBAC Models
class UserPermission(Base):
    __tablename__ = "user_permissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    module = Column(String)
    permission = Column(String)
    granted_by = Column(Integer, index=True)
    granted_at = Column(DateTime, default=datetime.utcnow)

class GroupPermission(Base):
    __tablename__ = "group_permissions"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, index=True)
    module = Column(String)
    permission = Column(String)
    granted_by = Column(Integer, index=True)
    granted_at = Column(DateTime, default=datetime.utcnow)

class ExpenseModification(Base):
    __tablename__ = "expense_modifications"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, index=True)
    modified_by = Column(Integer, index=True)
    modification_type = Column(String)
    old_values = Column(Text)  # JSON string
    new_values = Column(Text)  # JSON string
    modification_reason = Column(Text)
    modified_at = Column(DateTime, default=datetime.utcnow)

class GeneratedReport(Base):
    __tablename__ = "generated_reports"
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String)
    report_period = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    user_id = Column(Integer, nullable=True, index=True)
    group_id = Column(Integer, nullable=True, index=True)
    generated_by = Column(Integer, index=True)
    file_path = Column(String)
    file_format = Column(String)
    share_link = Column(String, nullable=True)
    drive_file_id = Column(String, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class ReceiptAttachment(Base):
    __tablename__ = "receipt_attachments"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, index=True)
    file_attachment_id = Column(Integer, index=True)
    receipt_type = Column(String)
    uploaded_by = Column(Integer, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# Client Management Model
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False, index=True)
    contact_person = Column(String)
    contact_number = Column(String)
    email = Column(String)
    address = Column(Text)
    created_by = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class SalesFunnel(Base):
    __tablename__ = "sales_funnel"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    opportunity_name = Column(String)
    client_name = Column(String)
    stage = Column(String)  # Lead, Qualified, Proposal, Negotiation, Closed Won, Closed Lost
    probability = Column(Integer)  # 0-100
    amount = Column(Integer)  # Amount in cents
    closing_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic models for MEDDPICC and Sales Funnel
class MEDDPICCCreate(BaseModel):
    client_name: str
    opportunity_name: str
    metrics: str
    economic_buyer: str
    decision_criteria: str
    decision_process: str
    paper_process: str
    identify_pain: str
    champion: str
    competition: str

class MEDDPICCResponse(BaseModel):
    id: int
    user_id: int
    client_name: str
    opportunity_name: str
    metrics: str
    economic_buyer: str
    decision_criteria: str
    decision_process: str
    paper_process: str
    identify_pain: str
    champion: str
    competition: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SalesFunnelCreate(BaseModel):
    opportunity_name: str
    client_name: str
    stage: str
    probability: int
    amount: int
    closing_date: datetime
    notes: Optional[str] = ""

class SalesFunnelResponse(BaseModel):
    id: int
    user_id: int
    opportunity_name: str
    client_name: str
    stage: str
    probability: int
    amount: int
    closing_date: datetime
    notes: Optional[str] = ""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
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

class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    reply_to_id: Optional[str] = None

class EmailResponse(BaseModel):
    id: str
    subject: str
    sender: str
    recipient: str
    body: str
    timestamp: datetime
    is_read: bool
    has_attachments: bool
    thread_id: str

class LeaveApplicationCreate(BaseModel):
    leave_type: str
    start_date: datetime
    end_date: datetime
    days_requested: int
    reason: str

class LeaveApplicationResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    leave_type: str
    start_date: datetime
    end_date: datetime
    days_requested: int
    reason: str
    status: str
    approved_by: Optional[int] = None
    approver_name: Optional[str] = None
    approval_date: Optional[datetime] = None
    approval_comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class LeaveApprovalRequest(BaseModel):
    status: str  # approved or rejected
    comments: Optional[str] = None

class ConvenienceBillCreate(BaseModel):
    bill_date: datetime
    transport_amount: int = 0  # Amount in BDT paisa
    transport_description: Optional[str] = ""
    food_amount: int = 0  # Amount in BDT paisa
    food_description: Optional[str] = ""
    other_amount: int = 0  # Amount in BDT paisa
    other_description: Optional[str] = ""
    transport_to: Optional[str] = ""
    transport_from: Optional[str] = ""
    means_of_transportation: Optional[str] = ""
    fuel_cost: int = 0  # Amount in BDT paisa
    rental_cost: int = 0  # Amount in BDT paisa
    client_id: Optional[int] = None
    client_company_name: Optional[str] = ""
    client_contact_number: Optional[str] = ""
    expense_purpose: Optional[str] = ""
    project_reference: Optional[str] = ""
    is_billable: bool = False
    general_description: str
    receipt_file_id: Optional[int] = None

class ConvenienceBillResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    bill_date: datetime
    transport_amount: int
    transport_description: Optional[str] = ""
    food_amount: int
    food_description: Optional[str] = ""
    other_amount: int
    other_description: Optional[str] = ""
    transport_to: Optional[str] = ""
    transport_from: Optional[str] = ""
    means_of_transportation: Optional[str] = ""
    fuel_cost: int
    rental_cost: int
    client_id: Optional[int] = None
    client_company_name: Optional[str] = ""
    client_contact_number: Optional[str] = ""
    expense_purpose: Optional[str] = ""
    project_reference: Optional[str] = ""
    is_billable: bool
    total_amount: int
    general_description: Optional[str] = ""
    receipt_file_id: Optional[int] = None
    receipt_filename: Optional[str] = None
    status: str
    approved_by: Optional[int] = None
    approver_name: Optional[str] = None
    approval_date: Optional[datetime] = None
    approval_comments: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BillApprovalRequest(BaseModel):
    status: str  # approved or rejected
    comments: Optional[str] = None

# Client Pydantic Models
class ClientCreate(BaseModel):
    company_name: str
    contact_person: Optional[str] = ""
    contact_number: Optional[str] = ""
    email: Optional[str] = ""
    address: Optional[str] = ""

class ClientResponse(BaseModel):
    id: int
    company_name: str
    contact_person: Optional[str] = ""
    contact_number: Optional[str] = ""
    email: Optional[str] = ""
    address: Optional[str] = ""
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Group Management Models
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = ""
    created_by: int
    creator_name: str
    member_count: int
    created_at: datetime
    updated_at: datetime

class GroupMemberAdd(BaseModel):
    user_ids: List[int]
    role: str = "member"

class GroupMemberResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: str
    group_id: int
    role: str
    added_by: int
    added_by_name: str
    added_at: datetime

class RoleCreate(BaseModel):
    name: str
    description: str
    permissions: Optional[List[str]] = []

class RoleResponse(BaseModel):
    id: int
    name: str
    description: str
    permissions: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role_id: Optional[int] = None

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
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/contacts.readonly"
        ]
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI
    
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

# Gmail functions
def get_credentials_from_session(session):
    """Create proper Google credentials from user session"""
    if not session or not session.access_token:
        return None
    
    credentials = Credentials(
        token=session.access_token,
        refresh_token=session.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET
    )
    
    # Set expiry if available
    if session.expires_at:
        credentials.expiry = session.expires_at
    
    return credentials

def get_gmail_service(credentials):
    return build('gmail', 'v1', credentials=credentials)

def parse_email_message(message, service):
    """Parse Gmail message and extract relevant information"""
    headers = message['payload'].get('headers', [])
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
    recipient = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown Recipient')
    date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
    
    # Parse body
    body = ''
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html':
                if 'data' in part['body'] and not body:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    else:
        if message['payload']['body'].get('data'):
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
    
    # Convert timestamp
    timestamp = datetime.fromtimestamp(int(message['internalDate']) / 1000)
    
    return {
        'id': message['id'],
        'subject': subject,
        'sender': sender,
        'recipient': recipient,
        'body': body[:1000] + ('...' if len(body) > 1000 else ''),  # Truncate for list view
        'timestamp': timestamp,
        'is_read': 'UNREAD' not in message.get('labelIds', []),
        'has_attachments': any('filename' in part for part in message['payload'].get('parts', [])),
        'thread_id': message['threadId']
    }

def create_email_message(to, subject, body, cc=None, bcc=None):
    """Create email message for sending"""
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    if cc:
        message['cc'] = cc
    if bcc:
        message['bcc'] = bcc
    
    message.attach(MIMEText(body, 'plain'))
    
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

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

def fetch_google_calendar_events(credentials, time_min=None, time_max=None):
    """Fetch events from Google Calendar"""
    # Refresh token if needed
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    
    service = build('calendar', 'v3', credentials=credentials)
    
    # Default to fetching events from 30 days ago to 30 days from now
    if not time_min:
        time_min = (datetime.utcnow() - timedelta(days=30)).isoformat() + 'Z'
    if not time_max:
        time_max = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        maxResults=100,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    return events

# Authentication endpoints
@app.get("/auth/google")
async def google_auth():
    flow = get_google_oauth_flow()
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
    return {"auth_url": auth_url}

@app.get("/auth/callback")
async def google_callback(code: str, state: str = None, db: Session = Depends(get_db)):
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
            credentials = get_credentials_from_session(session)
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
            credentials = get_credentials_from_session(session)
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
    # Get local events from database
    local_events = db.query(Event).filter(Event.user_id == current_user.id).all()
    result = []
    
    # Process local events
    for event in local_events:
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
    
    # Try to fetch Google Calendar events
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if session and session.access_token:
        try:
            credentials = get_credentials_from_session(session)
            google_events = fetch_google_calendar_events(credentials)
            
            # Add Google Calendar events that aren't already in our database
            for g_event in google_events:
                # Check if this Google event is already in our local database
                existing_event = db.query(Event).filter(
                    Event.user_id == current_user.id,
                    Event.google_event_id == g_event.get('id')
                ).first()
                
                if not existing_event:
                    # Parse start and end times
                    start_time = None
                    end_time = None
                    
                    if 'dateTime' in g_event.get('start', {}):
                        start_time = datetime.fromisoformat(g_event['start']['dateTime'].replace('Z', '+00:00'))
                    elif 'date' in g_event.get('start', {}):
                        start_time = datetime.fromisoformat(g_event['start']['date'] + 'T00:00:00+00:00')
                    
                    if 'dateTime' in g_event.get('end', {}):
                        end_time = datetime.fromisoformat(g_event['end']['dateTime'].replace('Z', '+00:00'))
                    elif 'date' in g_event.get('end', {}):
                        end_time = datetime.fromisoformat(g_event['end']['date'] + 'T23:59:59+00:00')
                    
                    if start_time and end_time:
                        # Add Google Calendar event to results
                        result.append(EventResponse(
                            id=-abs(hash(g_event.get('id', 'unknown')) % 1000000),  # Negative hash-based ID for Google events
                            title=g_event.get('summary', 'No Title'),
                            description=g_event.get('description', ''),
                            start_time=start_time,
                            end_time=end_time,
                            google_event_id=g_event.get('id'),
                            attachments=[],
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        ))
        
        except Exception as e:
            print(f"Failed to fetch Google Calendar events: {e}")
            # Continue with just local events if Google Calendar fails
    
    # Sort events by start time
    # Sort events by start time with timezone handling
    try:
        result.sort(key=lambda x: x.start_time.replace(tzinfo=None) if x.start_time.tzinfo else x.start_time)
    except (AttributeError, TypeError):
        # Fallback sorting if datetime comparison fails
        result.sort(key=lambda x: str(x.start_time))
    
    return result

@app.post("/events/{event_id}/share")
async def share_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find the event
    event = db.query(Event).filter(
        Event.id == event_id,
        Event.user_id == current_user.id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        return {"message": "Event shared locally (Google Calendar sharing requires authentication)"}
    
    try:
        credentials = get_credentials_from_session(session)
        service = build('calendar', 'v3', credentials=credentials)
        
        if event.google_event_id:
            # Share existing Google Calendar event
            # Add attendees from the organization domain
            event_body = service.events().get(calendarId='primary', eventId=event.google_event_id).execute()
            
            # Add domain-wide sharing (this would require admin setup in real implementation)
            event_body['visibility'] = 'public'
            
            updated_event = service.events().update(
                calendarId='primary',
                eventId=event.google_event_id,
                body=event_body
            ).execute()
            
            return {"message": "Event shared successfully on Google Calendar"}
        else:
            # Create and share new Google Calendar event
            google_event = {
                'summary': event.title,
                'description': event.description,
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'visibility': 'public'
            }
            
            created_event = service.events().insert(calendarId='primary', body=google_event).execute()
            
            # Update local event with Google event ID
            event.google_event_id = created_event['id']
            db.commit()
            
            return {"message": "Event created and shared on Google Calendar"}
            
    except Exception as e:
        print(f"Failed to share event on Google Calendar: {e}")
        return {"message": "Event shared locally (Google Calendar sharing failed)"}

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
        credentials = get_credentials_from_session(session)
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
        credentials = get_credentials_from_session(session)
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

# Google Drive endpoints
@app.get("/drive/files")
async def get_drive_files(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Google Drive access required")
    
    try:
        credentials = get_credentials_from_session(session)
        # Refresh token if needed
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        
        service = get_drive_service(credentials)
        
        # List files from Google Drive
        results = service.files().list(
            pageSize=100,
            fields="nextPageToken, files(id, name, size, mimeType, modifiedTime, parents)"
        ).execute()
        
        items = results.get('files', [])
        return items
    except Exception as e:
        print(f"Failed to fetch Google Drive files: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Google Drive files")

@app.get("/drive/files/{file_id}/download")
async def download_drive_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Google Drive access required")
    
    try:
        credentials = get_credentials_from_session(session)
        file_data = download_from_drive(file_id, credentials)
        
        # Get file metadata for filename
        service = get_drive_service(credentials)
        file_metadata = service.files().get(fileId=file_id).execute()
        
        return FileResponse(
            io.BytesIO(file_data),
            media_type='application/octet-stream',
            filename=file_metadata.get('name', 'download')
        )
    except Exception as e:
        print(f"Failed to download file from Google Drive: {e}")
        raise HTTPException(status_code=500, detail="Failed to download file")

@app.post("/drive/files/{file_id}/share")
async def share_drive_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Google Drive access required")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_drive_service(credentials)
        
        # Share file with domain
        batch = service.new_batch_http_request()
        file_permission = {
            'type': 'domain',
            'role': 'reader',
            'domain': ALLOWED_DOMAIN,
            'allowFileDiscovery': True
        }
        batch.add(service.permissions().create(
            fileId=file_id,
            body=file_permission,
            fields='id'
        ))
        batch.execute()
        return {"message": "File shared successfully"}
    except Exception as e:
        print(f"Failed to share file on Google Drive: {e}")
        raise HTTPException(status_code=500, detail="Failed to share file")

# Gmail endpoints
@app.get("/gmail/messages")
async def get_gmail_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    max_results: int = 20
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        # Refresh token if needed
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        
        service = get_gmail_service(credentials)
        
        # Get list of messages
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q='in:inbox'
        ).execute()
        
        messages = results.get('messages', [])
        
        # Get detailed message info
        email_list = []
        for msg in messages:
            try:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                parsed_email = parse_email_message(message, service)
                email_list.append(parsed_email)
            except Exception as e:
                print(f"Failed to parse message {msg['id']}: {e}")
                continue
        
        return email_list
    except Exception as e:
        print(f"Failed to fetch Gmail messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Gmail messages")

@app.get("/gmail/messages/{message_id}")
async def get_gmail_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        parsed_email = parse_email_message(message, service)
        # Don't truncate body for individual message view
        headers = message['payload'].get('headers', [])
        
        # Parse full body
        body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body'] and not body:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            if message['payload']['body'].get('data'):
                body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        parsed_email['body'] = body  # Full body for detailed view
        return parsed_email
    except Exception as e:
        print(f"Failed to fetch Gmail message {message_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Gmail message")

@app.post("/gmail/messages/{message_id}/mark-read")
async def mark_message_read(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        # Remove UNREAD label
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        
        return {"message": "Message marked as read"}
    except Exception as e:
        print(f"Failed to mark message as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark message as read")

@app.post("/gmail/send")
async def send_email(
    email_request: EmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        # Create email message
        message = create_email_message(
            to=email_request.to,
            subject=email_request.subject,
            body=email_request.body,
            cc=email_request.cc,
            bcc=email_request.bcc
        )
        
        # Send email
        sent_message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        return {
            "message": "Email sent successfully",
            "message_id": sent_message['id']
        }
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@app.post("/gmail/reply/{message_id}")
async def reply_to_email(
    message_id: str,
    email_request: EmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        # Get original message for thread info
        original_message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Create reply message
        message = create_email_message(
            to=email_request.to,
            subject=f"Re: {email_request.subject}",
            body=email_request.body,
            cc=email_request.cc,
            bcc=email_request.bcc
        )
        
        # Add threading information
        message['threadId'] = original_message['threadId']
        
        # Send reply
        sent_message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        return {
            "message": "Reply sent successfully",
            "message_id": sent_message['id']
        }
    except Exception as e:
        print(f"Failed to send reply: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reply")

@app.get("/gmail/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        return {"count": 0}
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        # Get count of unread messages
        results = service.users().messages().list(
            userId='me',
            q='in:inbox is:unread'
        ).execute()
        
        messages = results.get('messages', [])
        return {"count": len(messages)}
    except Exception as e:
        print(f"Failed to get unread count: {e}")
        return {"count": 0}

# Google Chat endpoints (placeholder - Google Chat API requires workspace domain setup)
@app.get("/chat/messages")
async def get_chat_messages(current_user: User = Depends(get_current_user)):
    # Placeholder implementation - Google Chat API integration would require 
    # Google Workspace domain setup and additional OAuth scopes
    return [
        {
            "id": "1",
            "content": "Welcome to Infosonik Chat integration!",
            "sender": {
                "name": "System",
                "avatar": "/static/system-avatar.png"
            },
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "id": "2",
            "content": "This is a placeholder for Google Chat integration. Full implementation requires Google Workspace admin setup.",
            "sender": {
                "name": "Infosonik Bot",
                "avatar": "/static/bot-avatar.png"
            },
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        }
    ]

@app.post("/chat/messages")
async def send_chat_message(
    message: dict,
    current_user: User = Depends(get_current_user)
):
    # Placeholder implementation
    return {
        "id": str(uuid.uuid4()),
        "content": message.get("content", ""),
        "sender": {
            "name": current_user.name,
            "avatar": current_user.profile_picture
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Admin helper function
def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin and current_user.email != 'tawfiqul.bari@infosonik.com':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Helper functions for role-based access
def get_user_role(user: User, db: Session) -> Optional[Role]:
    """Get the role assigned to a user"""
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

# Leave Application endpoints
@app.post("/leave/apply", response_model=LeaveApplicationResponse)
async def apply_for_leave(
    leave_request: LeaveApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    leave_application = LeaveApplication(
        user_id=current_user.id,
        leave_type=leave_request.leave_type,
        start_date=leave_request.start_date,
        end_date=leave_request.end_date,
        days_requested=leave_request.days_requested,
        reason=leave_request.reason
    )
    db.add(leave_application)
    db.commit()
    db.refresh(leave_application)
    
    return LeaveApplicationResponse(
        id=leave_application.id,
        user_id=leave_application.user_id,
        user_name=current_user.name,
        leave_type=leave_application.leave_type,
        start_date=leave_application.start_date,
        end_date=leave_application.end_date,
        days_requested=leave_application.days_requested,
        reason=leave_application.reason,
        status=leave_application.status,
        approved_by=leave_application.approved_by,
        approver_name=None,
        approval_date=leave_application.approval_date,
        approval_comments=leave_application.approval_comments,
        created_at=leave_application.created_at,
        updated_at=leave_application.updated_at
    )

@app.get("/leave/my-applications", response_model=List[LeaveApplicationResponse])
async def get_my_leave_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    applications = db.query(LeaveApplication).filter(
        LeaveApplication.user_id == current_user.id
    ).order_by(LeaveApplication.created_at.desc()).all()
    
    result = []
    for app in applications:
        approver_name = None
        if app.approved_by:
            approver = db.query(User).filter(User.id == app.approved_by).first()
            approver_name = approver.name if approver else None
        
        result.append(LeaveApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            user_name=current_user.name,
            leave_type=app.leave_type,
            start_date=app.start_date,
            end_date=app.end_date,
            days_requested=app.days_requested,
            reason=app.reason,
            status=app.status,
            approved_by=app.approved_by,
            approver_name=approver_name,
            approval_date=app.approval_date,
            approval_comments=app.approval_comments,
            created_at=app.created_at,
            updated_at=app.updated_at
        ))
    
    return result

@app.get("/leave/pending", response_model=List[LeaveApplicationResponse])
async def get_pending_leave_applications(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    applications = db.query(LeaveApplication).filter(
        LeaveApplication.status == "pending"
    ).order_by(LeaveApplication.created_at.desc()).all()
    
    result = []
    for app in applications:
        user = db.query(User).filter(User.id == app.user_id).first()
        
        result.append(LeaveApplicationResponse(
            id=app.id,
            user_id=app.user_id,
            user_name=user.name if user else "Unknown User",
            leave_type=app.leave_type,
            start_date=app.start_date,
            end_date=app.end_date,
            days_requested=app.days_requested,
            reason=app.reason,
            status=app.status,
            approved_by=app.approved_by,
            approver_name=None,
            approval_date=app.approval_date,
            approval_comments=app.approval_comments,
            created_at=app.created_at,
            updated_at=app.updated_at
        ))
    
    return result

@app.post("/leave/{application_id}/approve")
async def approve_leave_application(
    application_id: int,
    approval_request: LeaveApprovalRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    application = db.query(LeaveApplication).filter(
        LeaveApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Leave application not found")
    
    if application.status != "pending":
        raise HTTPException(status_code=400, detail="Application has already been processed")
    
    application.status = approval_request.status
    application.approved_by = admin_user.id
    application.approval_date = datetime.utcnow()
    application.approval_comments = approval_request.comments
    application.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Leave application {approval_request.status} successfully"}

# Convenience Bills endpoints
@app.post("/bills/submit", response_model=ConvenienceBillResponse)
async def submit_convenience_bill(
    bill_request: ConvenienceBillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit convenience bill with client information"""
    convenience_bill = ConvenienceBill(
        user_id=current_user.id,
        bill_date=bill_request.bill_date,
        transport_amount=bill_request.transport_amount,
        transport_description=bill_request.transport_description,
        food_amount=bill_request.food_amount,
        food_description=bill_request.food_description,
        other_amount=bill_request.other_amount,
        other_description=bill_request.other_description,
        transport_to=bill_request.transport_to,
        transport_from=bill_request.transport_from,
        means_of_transportation=bill_request.means_of_transportation,
        fuel_cost=bill_request.fuel_cost,
        rental_cost=bill_request.rental_cost,
        general_description=bill_request.general_description,
        receipt_file_id=bill_request.receipt_file_id,
        # Client information fields
        client_id=bill_request.client_id,
        client_company_name=bill_request.client_company_name,
        client_contact_number=bill_request.client_contact_number,
        expense_purpose=bill_request.expense_purpose,
        project_reference=bill_request.project_reference,
        is_billable=bill_request.is_billable
    )
    db.add(convenience_bill)
    db.commit()
    db.refresh(convenience_bill)
    
    receipt_filename = None
    if bill_request.receipt_file_id:
        receipt_file = db.query(FileAttachment).filter(
            FileAttachment.id == bill_request.receipt_file_id,
            FileAttachment.user_id == current_user.id
        ).first()
        receipt_filename = receipt_file.original_filename if receipt_file else None
    
    return ConvenienceBillResponse(
        id=convenience_bill.id,
        user_id=convenience_bill.user_id,
        user_name=current_user.name,
        bill_date=convenience_bill.bill_date,
        transport_amount=convenience_bill.transport_amount,
        transport_description=convenience_bill.transport_description,
        food_amount=convenience_bill.food_amount,
        food_description=convenience_bill.food_description,
        other_amount=convenience_bill.other_amount,
        other_description=convenience_bill.other_description,
        transport_to=convenience_bill.transport_to,
        transport_from=convenience_bill.transport_from,
        means_of_transportation=convenience_bill.means_of_transportation,
        fuel_cost=convenience_bill.fuel_cost,
        rental_cost=convenience_bill.rental_cost,
        total_amount=convenience_bill.total_amount,
        general_description=convenience_bill.general_description,
        receipt_file_id=convenience_bill.receipt_file_id,
        receipt_filename=receipt_filename,
        client_id=convenience_bill.client_id,
        client_company_name=convenience_bill.client_company_name,
        client_contact_number=convenience_bill.client_contact_number,
        expense_purpose=convenience_bill.expense_purpose,
        project_reference=convenience_bill.project_reference,
        is_billable=convenience_bill.is_billable,
        status=convenience_bill.status,
        approved_by=convenience_bill.approved_by,
        approver_name=None,
        approval_date=convenience_bill.approval_date,
        approval_comments=convenience_bill.approval_comments,
        created_at=convenience_bill.created_at,
        updated_at=convenience_bill.updated_at
    )

@app.get("/bills/my-bills", response_model=List[ConvenienceBillResponse])
async def get_my_convenience_bills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bills = db.query(ConvenienceBill).filter(
        ConvenienceBill.user_id == current_user.id
    ).order_by(ConvenienceBill.created_at.desc()).all()
    
    result = []
    for bill in bills:
        approver_name = None
        if bill.approved_by:
            approver = db.query(User).filter(User.id == bill.approved_by).first()
            approver_name = approver.name if approver else None
        
        receipt_filename = None
        if bill.receipt_file_id:
            receipt_file = db.query(FileAttachment).filter(
                FileAttachment.id == bill.receipt_file_id
            ).first()
            receipt_filename = receipt_file.original_filename if receipt_file else None
        
        result.append(ConvenienceBillResponse(
            id=bill.id,
            user_id=bill.user_id,
            user_name=current_user.name,
            bill_date=bill.bill_date,
            transport_amount=bill.transport_amount,
            transport_description=bill.transport_description,
            food_amount=bill.food_amount,
            food_description=bill.food_description,
            other_amount=bill.other_amount,
            other_description=bill.other_description,
            transport_to=bill.transport_to,
            transport_from=bill.transport_from,
            means_of_transportation=bill.means_of_transportation,
            fuel_cost=bill.fuel_cost,
            rental_cost=bill.rental_cost,
            total_amount=bill.total_amount,
            general_description=bill.general_description,
            receipt_file_id=bill.receipt_file_id,
            receipt_filename=receipt_filename,
            status=bill.status,
            approved_by=bill.approved_by,
            approver_name=approver_name,
            approval_date=bill.approval_date,
            approval_comments=bill.approval_comments,
            created_at=bill.created_at,
            updated_at=bill.updated_at
        ))
    
    return result

@app.get("/bills/pending", response_model=List[ConvenienceBillResponse])
async def get_pending_convenience_bills(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    bills = db.query(ConvenienceBill).filter(
        ConvenienceBill.status == "pending"
    ).order_by(ConvenienceBill.created_at.desc()).all()
    
    result = []
    for bill in bills:
        user = db.query(User).filter(User.id == bill.user_id).first()
        
        receipt_filename = None
        if bill.receipt_file_id:
            receipt_file = db.query(FileAttachment).filter(
                FileAttachment.id == bill.receipt_file_id
            ).first()
            receipt_filename = receipt_file.original_filename if receipt_file else None
        
        result.append(ConvenienceBillResponse(
            id=bill.id,
            user_id=bill.user_id,
            user_name=user.name if user else "Unknown User",
            bill_date=bill.bill_date,
            transport_amount=bill.transport_amount,
            transport_description=bill.transport_description,
            food_amount=bill.food_amount,
            food_description=bill.food_description,
            other_amount=bill.other_amount,
            other_description=bill.other_description,
            transport_to=bill.transport_to,
            transport_from=bill.transport_from,
            means_of_transportation=bill.means_of_transportation,
            fuel_cost=bill.fuel_cost,
            rental_cost=bill.rental_cost,
            total_amount=bill.total_amount,
            general_description=bill.general_description,
            receipt_file_id=bill.receipt_file_id,
            receipt_filename=receipt_filename,
            status=bill.status,
            approved_by=bill.approved_by,
            approver_name=None,
            approval_date=bill.approval_date,
            approval_comments=bill.approval_comments,
            created_at=bill.created_at,
            updated_at=bill.updated_at
        ))
    
    return result

@app.post("/bills/{bill_id}/approve")
async def approve_convenience_bill(
    bill_id: int,
    approval_request: BillApprovalRequest,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    bill = db.query(ConvenienceBill).filter(
        ConvenienceBill.id == bill_id
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="Convenience bill not found")
    
    if bill.status != "pending":
        raise HTTPException(status_code=400, detail="Bill has already been processed")
    
    bill.status = approval_request.status
    bill.approved_by = admin_user.id
    bill.approval_date = datetime.utcnow()
    bill.approval_comments = approval_request.comments
    bill.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Convenience bill {approval_request.status} successfully"}

# Admin endpoints
@app.get("/admin/users")
async def get_all_users(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return [{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat()
    } for user in users]

@app.get("/admin/stats")
async def get_admin_stats(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_notes = db.query(Note).count()
    total_events = db.query(Event).count()
    total_files = db.query(FileAttachment).count()
    
    return {
        "total_users": total_users,
        "total_notes": total_notes,
        "total_events": total_events,
        "total_files": total_files
    }

@app.put("/admin/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_data: dict,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = status_data.get("is_active", user.is_active)
    db.commit()
    
    return {"message": "User status updated successfully"}

@app.put("/admin/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: dict,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.name = user_data.get("name", user.name)
    user.email = user_data.get("email", user.email)
    user.is_active = user_data.get("is_active", user.is_active)
    db.commit()
    
    return {"message": "User updated successfully"}

# MEDDPICC Endpoints
@app.post("/sales/meddpicc", response_model=MEDDPICCResponse)
async def create_meddpicc(
    meddpicc_data: MEDDPICCCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_meddpicc = MEDDPICC(
        user_id=current_user.id,
        client_name=meddpicc_data.client_name,
        opportunity_name=meddpicc_data.opportunity_name,
        metrics=meddpicc_data.metrics,
        economic_buyer=meddpicc_data.economic_buyer,
        decision_criteria=meddpicc_data.decision_criteria,
        decision_process=meddpicc_data.decision_process,
        paper_process=meddpicc_data.paper_process,
        identify_pain=meddpicc_data.identify_pain,
        champion=meddpicc_data.champion,
        competition=meddpicc_data.competition
    )
    db.add(new_meddpicc)
    db.commit()
    db.refresh(new_meddpicc)

    return new_meddpicc

@app.get("/sales/meddpicc", response_model=List[MEDDPICCResponse])
async def list_meddpicc(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meddpiccs = db.query(MEDDPICC).filter(MEDDPICC.user_id == current_user.id).all()
    return meddpiccs

# Sales Funnel Endpoints
@app.post("/sales/funnel", response_model=SalesFunnelResponse)
async def create_sales_funnel(
    funnel_data: SalesFunnelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_funnel = SalesFunnel(
        user_id=current_user.id,
        opportunity_name=funnel_data.opportunity_name,
        client_name=funnel_data.client_name,
        stage=funnel_data.stage,
        probability=funnel_data.probability,
        amount=funnel_data.amount,
        closing_date=funnel_data.closing_date,
        notes=funnel_data.notes
    )
    db.add(new_funnel)
    db.commit()
    db.refresh(new_funnel)

    return new_funnel

@app.get("/sales/funnel", response_model=List[SalesFunnelResponse])
async def list_sales_funnel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    funnels = db.query(SalesFunnel).filter(SalesFunnel.user_id == current_user.id).all()
    return funnels
@app.post("/admin/roles", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # Check if role already exists
    existing_role = db.query(Role).filter(Role.name == role.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    db_role = Role(
        name=role.name,
        description=role.description,
        permissions=json.dumps(role.permissions)
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    
    return RoleResponse(
        id=db_role.id,
        name=db_role.name,
        description=db_role.description,
        permissions=json.loads(db_role.permissions) if db_role.permissions else [],
        created_at=db_role.created_at,
        updated_at=db_role.updated_at
    )

@app.get("/admin/roles", response_model=List[RoleResponse])
async def get_all_roles(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    roles = db.query(Role).all()
    return [
        RoleResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            permissions=json.loads(role.permissions) if role.permissions else [],
            created_at=role.created_at,
            updated_at=role.updated_at
        )
        for role in roles
    ]

@app.put("/admin/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_update: RoleCreate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if the new name already exists (if changed)
    if role_update.name != db_role.name:
        existing_role = db.query(Role).filter(Role.name == role_update.name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role name already exists")
    
    db_role.name = role_update.name
    db_role.description = role_update.description
    db_role.permissions = json.dumps(role_update.permissions)
    db_role.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_role)
    
    return RoleResponse(
        id=db_role.id,
        name=db_role.name,
        description=db_role.description,
        permissions=json.loads(db_role.permissions) if db_role.permissions else [],
        created_at=db_role.created_at,
        updated_at=db_role.updated_at
    )

@app.delete("/admin/roles/{role_id}")
async def delete_role(
    role_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if any users have this role
    users_with_role = db.query(User).filter(User.role_id == role_id).count()
    if users_with_role > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete role. {users_with_role} users are assigned to this role."
        )
    
    db.delete(db_role)
    db.commit()
    
    return {"message": "Role deleted successfully"}

@app.put("/admin/users/{user_id}/role")
async def assign_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if role_update.role_id is not None:
        # Verify the role exists
        role = db.query(Role).filter(Role.id == role_update.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        user.role_id = role_update.role_id
        role_name = role.name
    else:
        user.role_id = None
        role_name = "None"
    
    db.commit()
    
    return {
        "message": f"User role updated to {role_name} successfully",
        "user_id": user.id,
        "role_id": user.role_id
    }

@app.get("/admin/users/{user_id}/role")
async def get_user_role(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        if role:
            return {
                "user_id": user.id,
                "user_name": user.name,
                "role": {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "permissions": json.loads(role.permissions) if role.permissions else []
                }
            }
    
    return {
        "user_id": user.id,
        "user_name": user.name,
        "role": None
    }


# Initialize default roles
@app.on_event("startup")
async def create_default_roles():
    """Create default roles if they don't exist"""
    db = SessionLocal()
    try:
        # Check if roles already exist
        existing_roles = db.query(Role).count()
        if existing_roles == 0:
            default_roles = [
                {
                    "name": "Admin",
                    "description": "Full system administrator with all permissions",
                    "permissions": ["all"]
                },
                {
                    "name": "HR",
                    "description": "Human Resources - manage leave applications and user data",
                    "permissions": ["manage_leave", "view_users", "manage_bills"]
                },
                {
                    "name": "Accounts",
                    "description": "Accounts department - manage convenience bills and financial data",
                    "permissions": ["manage_bills", "view_financial_reports"]
                },
                {
                    "name": "Sales",
                    "description": "Sales team members",
                    "permissions": ["view_sales_data", "manage_sales_data", "manage_client_notes"]
                },
                {
                    "name": "Technical",
                    "description": "Technical team members",
                    "permissions": ["view_technical_docs", "manage_project_notes"]
                }
            ]
            
            for role_data in default_roles:
                db_role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=json.dumps(role_data["permissions"])
                )
                db.add(db_role)
            
            db.commit()
            print("Default roles created successfully")
    except Exception as e:
        print(f"Error creating default roles: {e}")  
    finally:
        db.close()

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
        if (
            full_path.startswith("api/") or 
            full_path.startswith("docs") or 
            full_path.startswith("redoc") or
            full_path.startswith("auth/") or
            full_path.startswith("notes/") or
            full_path.startswith("events/") or
            full_path.startswith("files/") or
            full_path.startswith("admin/") or
            full_path.startswith("leave/") or
            full_path.startswith("bills/") or
            full_path.startswith("sales/") or
            full_path.startswith("user/") or
            full_path.startswith("backup/") or
            full_path.startswith("voice-to-text/") or
            full_path.startswith("drive/") or
            full_path.startswith("gmail/") or
            full_path.startswith("chat/") or
            full_path.startswith("webhook/")
        ):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse('static/index.html')

# Test endpoint to debug authentication
@app.get("/test/auth")
async def test_auth(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.name}, your ID is {current_user.id}"}
# Update sharing and invitation endpoints

@app.post("/events/{event_id}/invite")
async def invite_to_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Example invitation logic
    try:
        event = db.query(Event).filter(Event.id == event_id, Event.user_id == current_user.id).first()
        if not event:
            return {"message": "Event not found or not owned by the user."}

        # Add invitation logic here (e.g., send email or notification)
        # This is a placeholder implementation
        return {"message": "Invitation sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to invite: {e}")

# Group Management Endpoints

@app.post("/admin/groups", response_model=GroupResponse)
async def create_group(
    group: GroupCreate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new user group"""
    # Check if group already exists
    existing_group = db.query(UserGroup).filter(UserGroup.name == group.name).first()
    if existing_group:
        raise HTTPException(status_code=400, detail="Group already exists")
    
    db_group = UserGroup(
        name=group.name,
        description=group.description,
        created_by=admin_user.id
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    return GroupResponse(
        id=db_group.id,
        name=db_group.name,
        description=db_group.description or "",
        created_by=db_group.created_by,
        creator_name=admin_user.name,
        member_count=0,
        created_at=db_group.created_at,
        updated_at=db_group.updated_at
    )

@app.get("/admin/groups", response_model=List[GroupResponse])
async def get_all_groups(
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all user groups"""
    groups = db.query(UserGroup).all()
    result = []
    
    for group in groups:
        creator = db.query(User).filter(User.id == group.created_by).first()
        member_count = db.query(GroupMembership).filter(GroupMembership.group_id == group.id).count()
        
        result.append(GroupResponse(
            id=group.id,
            name=group.name,
            description=group.description or "",
            created_by=group.created_by,
            creator_name=creator.name if creator else "Unknown",
            member_count=member_count,
            created_at=group.created_at,
            updated_at=group.updated_at
        ))
    
    return result

@app.put("/admin/groups/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_update: GroupCreate,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a user group"""
    db_group = db.query(UserGroup).filter(UserGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if the new name already exists (if changed)
    if group_update.name != db_group.name:
        existing_group = db.query(UserGroup).filter(UserGroup.name == group_update.name).first()
        if existing_group:
            raise HTTPException(status_code=400, detail="Group name already exists")
    
    db_group.name = group_update.name
    db_group.description = group_update.description
    db_group.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_group)
    
    creator = db.query(User).filter(User.id == db_group.created_by).first()
    member_count = db.query(GroupMembership).filter(GroupMembership.group_id == group_id).count()
    
    return GroupResponse(
        id=db_group.id,
        name=db_group.name,
        description=db_group.description or "",
        created_by=db_group.created_by,
        creator_name=creator.name if creator else "Unknown",
        member_count=member_count,
        created_at=db_group.created_at,
        updated_at=db_group.updated_at
    )

@app.delete("/admin/groups/{group_id}")
async def delete_group(
    group_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user group"""
    db_group = db.query(UserGroup).filter(UserGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Remove all group memberships first
    db.query(GroupMembership).filter(GroupMembership.group_id == group_id).delete()
    
    # Delete the group
    db.delete(db_group)
    db.commit()
    
    return {"message": "Group deleted successfully"}

@app.post("/admin/groups/{group_id}/members")
async def add_group_members(
    group_id: int,
    member_add: GroupMemberAdd,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Add users to a group"""
    db_group = db.query(UserGroup).filter(UserGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    added_users = []
    for user_id in member_add.user_ids:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        
        # Check if user is already in the group
        existing_membership = db.query(GroupMembership).filter(
            GroupMembership.user_id == user_id,
            GroupMembership.group_id == group_id
        ).first()
        
        if not existing_membership:
            membership = GroupMembership(
                user_id=user_id,
                group_id=group_id,
                role=member_add.role,
                added_by=admin_user.id
            )
            db.add(membership)
            added_users.append(user.name)
    
    db.commit()
    
    return {
        "message": f"Added {len(added_users)} users to group",
        "added_users": added_users
    }

@app.get("/admin/groups/{group_id}/members", response_model=List[GroupMemberResponse])
async def get_group_members(
    group_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all members of a group"""
    db_group = db.query(UserGroup).filter(UserGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    memberships = db.query(GroupMembership).filter(GroupMembership.group_id == group_id).all()
    result = []
    
    for membership in memberships:
        user = db.query(User).filter(User.id == membership.user_id).first()
        added_by_user = db.query(User).filter(User.id == membership.added_by).first()
        
        if user:
            result.append(GroupMemberResponse(
                id=membership.id,
                user_id=membership.user_id,
                user_name=user.name,
                user_email=user.email,
                group_id=membership.group_id,
                role=membership.role,
                added_by=membership.added_by,
                added_by_name=added_by_user.name if added_by_user else "Unknown",
                added_at=membership.added_at
            ))
    
    return result

@app.delete("/admin/groups/{group_id}/members/{user_id}")
async def remove_group_member(
    group_id: int,
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Remove a user from a group"""
    membership = db.query(GroupMembership).filter(
        GroupMembership.group_id == group_id,
        GroupMembership.user_id == user_id
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Group membership not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(membership)
    db.commit()
    
    return {
        "message": f"Removed {user.name if user else 'user'} from group successfully"
    }


# Additional Imports
import json

# Role-Based Access Control (RBAC) Functionality
class RBACManager:
    def __init__(self, db_session):
        self.db = db_session

    def user_has_permission(self, user_id, module, permission):
        # Check individual permissions
        user_permissions = self.db.query(UserPermission).filter_by(user_id=user_id, module=module).all()
        if any(p.permission == permission for p in user_permissions):
            return True
        # Check group permissions
        user_groups = self.db.query(GroupMembership.group_id).filter_by(user_id=user_id).all()
        group_permissions = self.db.query(GroupPermission).filter(GroupPermission.group_id.in_(user_groups)).filter_by(module=module, permission=permission).all()
        return group_permissions.exists()

# Expense Report Generator
class ExpenseReportGenerator:
    def __init__(self, db_session):
        self.db = db_session

    def generate_report(self, report_type, start_date, end_date, user_id=None, group_id=None, file_format='pdf'):
        # Logic to generate reports based on user or group within specified date range
        # Use libraries like Pandas, XlsxWriter, and PDF generation tools
        report_data = self._fetch_expense_data(report_type, start_date, end_date, user_id, group_id)
        if file_format == 'pdf':
            return self._generate_pdf(report_data)
        elif file_format == 'excel':
            return self._generate_excel(report_data)
        elif file_format == 'csv':
            return self._generate_csv(report_data)

    def _fetch_expense_data(self, report_type, start_date, end_date, user_id, group_id):
        
        # Logic to fetch and compile expense data
        
        return {}

    def _generate_pdf(self, data):
        
        # Logic for PDF generation
        
        return 'path_to_pdf_file'

    def _generate_excel(self, data):
        
        # Logic for Excel generation
        
        return 'path_to_excel_file'

    def _generate_csv(self, data):

        # Logic for CSV generation

        return 'path_to_csv_file'

# Expense Modification Logging
class ExpenseModificationLogger:
    def __init__(self, db_session):
        self.db = db_session

    def log_modification(self, expense_id, modified_by, modification_type, old_values, new_values, modification_reason):
        modification_log = ExpenseModification(
            expense_id=expense_id,
            modified_by=modified_by,
            modification_type=modification_type,
            old_values=json.dumps(old_values),
            new_values=json.dumps(new_values),
            modification_reason=modification_reason
        )
        self.db.add(modification_log)
        self.db.commit()

# Enhanced API Endpoints for RBAC and Reporting

# Admin Expense Management Endpoints
@app.get("/admin/expenses")
async def get_admin_expenses(
    group: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all expenses for admin review, optionally filtered by group"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(ConvenienceBill).join(User, ConvenienceBill.user_id == User.id)
    
    if group:
        query = query.join(GroupMembership, User.id == GroupMembership.user_id).filter(GroupMembership.group_id == group)
    
    expenses = query.all()
    
    result = []
    for expense in expenses:
        user = db.query(User).filter(User.id == expense.user_id).first()
        group_membership = db.query(GroupMembership).filter(GroupMembership.user_id == expense.user_id).first()
        group_name = None
        if group_membership:
            group_obj = db.query(UserGroup).filter(UserGroup.id == group_membership.group_id).first()
            group_name = group_obj.name if group_obj else None
        
        result.append({
            "id": expense.id,
            "user_name": user.name,
            "group_name": group_name,
            "bill_date": expense.bill_date,
            "total_amount": expense.total_amount,
            "general_description": expense.general_description,
            "status": expense.status
        })
    
    return result

@app.post("/admin/expenses/{expense_id}/approve")
async def approve_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve an expense"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    expense = db.query(ConvenienceBill).filter(ConvenienceBill.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    expense.status = "approved"
    expense.approved_by = current_user.id
    expense.approval_date = datetime.utcnow()
    
    db.commit()
    return {"message": "Expense approved successfully"}

@app.post("/admin/expenses/{expense_id}/reject")
async def reject_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject an expense"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    expense = db.query(ConvenienceBill).filter(ConvenienceBill.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    expense.status = "rejected"
    expense.approved_by = current_user.id
    expense.approval_date = datetime.utcnow()
    
    db.commit()
    return {"message": "Expense rejected successfully"}

# Report Generation Endpoints
@app.post("/admin/reports/generate")
async def generate_admin_report(
    report_request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate expense report for admin"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Generate report logic here
    report = GeneratedReport(
        report_type="admin_summary",
        report_period=report_request.get("period", "monthly"),
        start_date=datetime.strptime(report_request["start_date"], "%Y-%m-%d").date(),
        end_date=datetime.strptime(report_request["end_date"], "%Y-%m-%d").date(),
        generated_by=current_user.id,
        file_format=report_request.get("format", "pdf"),
        file_path=f"/reports/admin_report_{datetime.now().timestamp()}.pdf"
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {"id": report.id, "message": "Report generated successfully"}

# User Monthly Report Endpoints
@app.get("/bills/monthly-report")
async def get_user_monthly_report(
    start_date: str,
    end_date: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's monthly expense report"""
    expenses = db.query(ConvenienceBill).filter(
        ConvenienceBill.user_id == current_user.id,
        ConvenienceBill.bill_date >= datetime.strptime(start_date, "%Y-%m-%d"),
        ConvenienceBill.bill_date <= datetime.strptime(end_date, "%Y-%m-%d")
    ).all()
    
    total_amount = sum(expense.total_amount for expense in expenses)
    transport_total = sum(expense.transport_amount or 0 for expense in expenses)
    food_total = sum(expense.food_amount or 0 for expense in expenses)
    fuel_total = sum(expense.fuel_cost or 0 for expense in expenses)
    rental_total = sum(expense.rental_cost or 0 for expense in expenses)
    other_total = sum(expense.other_amount or 0 for expense in expenses)
    
    return {
        "expenses": [
            {
                "id": expense.id,
                "bill_date": expense.bill_date,
                "transport_amount": expense.transport_amount or 0,
                "food_amount": expense.food_amount or 0,
                "fuel_cost": expense.fuel_cost or 0,
                "rental_cost": expense.rental_cost or 0,
                "other_amount": expense.other_amount or 0,
                "total_amount": expense.total_amount,
                "general_description": expense.general_description,
                "status": expense.status
            }
            for expense in expenses
        ],
        "summary": {
            "total_amount": total_amount,
            "transport_total": transport_total,
            "food_total": food_total,
            "fuel_total": fuel_total,
            "rental_total": rental_total,
            "other_total": other_total
        }
    }

# Enhanced Bill Update Endpoint
@app.post("/bills/{bill_id}/update")
async def update_convenience_bill(
    bill_id: int,
    bill_request: ConvenienceBillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing convenience bill"""
    bill = db.query(ConvenienceBill).filter(
        ConvenienceBill.id == bill_id,
        ConvenienceBill.user_id == current_user.id
    ).first()
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    if bill.status == "approved":
        raise HTTPException(status_code=400, detail="Cannot modify approved bills")
    
    # Store old values for audit trail
    old_values = {
        "transport_amount": bill.transport_amount,
        "food_amount": bill.food_amount,
        "other_amount": bill.other_amount,
        "fuel_cost": bill.fuel_cost,
        "rental_cost": bill.rental_cost,
        "general_description": bill.general_description
    }
    
    # Update bill fields
    bill.bill_date = bill_request.bill_date
    bill.transport_amount = bill_request.transport_amount
    bill.transport_description = bill_request.transport_description
    bill.food_amount = bill_request.food_amount
    bill.food_description = bill_request.food_description
    bill.other_amount = bill_request.other_amount
    bill.other_description = bill_request.other_description
    bill.fuel_cost = bill_request.fuel_cost
    bill.rental_cost = bill_request.rental_cost
    bill.transport_to = bill_request.transport_to
    bill.transport_from = bill_request.transport_from
    bill.means_of_transportation = bill_request.means_of_transportation
    bill.general_description = bill_request.general_description
    bill.last_modified_by = current_user.id
    bill.last_modified_at = datetime.utcnow()
    bill.status = "pending"  # Reset to pending after modification
    
    db.commit()
    
    # Log modification
    modification = ExpenseModification(
        expense_id=bill.id,
        modified_by=current_user.id,
        modification_type="updated",
        old_values=json.dumps(old_values),
        new_values=json.dumps({
            "transport_amount": bill.transport_amount,
            "food_amount": bill.food_amount,
            "other_amount": bill.other_amount,
            "fuel_cost": bill.fuel_cost,
            "rental_cost": bill.rental_cost,
            "general_description": bill.general_description
        }),
        modification_reason="User update"
    )
    db.add(modification)
    db.commit()
    
    return {"message": "Bill updated successfully"}


@app.get("/admin/reports")
async def get_admin_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all generated reports"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    reports = db.query(GeneratedReport).order_by(GeneratedReport.generated_at.desc()).all()
    return [
        {
            "id": report.id,
            "report_type": report.report_type,
            "report_period": report.report_period,
            "start_date": report.start_date,
            "end_date": report.end_date,
            "generated_at": report.generated_at,
            "file_format": report.file_format
        }
        for report in reports
    ]

# Client Management API Endpoints

@app.get("/clients", response_model=List[ClientResponse])
async def get_clients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active clients"""
    clients = db.query(Client).filter(Client.is_active == True).all()
    return clients

@app.post("/clients", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new client"""
    client = Client(
        company_name=client_data.company_name,
        contact_person=client_data.contact_person,
        contact_number=client_data.contact_number,
        email=client_data.email,
        address=client_data.address,
        created_by=current_user.id
    )
    
    db.add(client)
    db.commit()
    db.refresh(client)
    
    return client

@app.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing client"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client.company_name = client_data.company_name
    client.contact_person = client_data.contact_person
    client.contact_number = client_data.contact_number
    client.email = client_data.email
    client.address = client_data.address
    client.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(client)
    
    return client

@app.delete("/clients/{client_id}")
async def delete_client(
    client_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a client (mark as inactive)"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client.is_active = False
    client.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Client deleted successfully"}


# Enhanced Gmail API endpoints for Outlook-like functionality

@app.get("/gmail/folders")
async def get_gmail_folders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Gmail folders/labels"""
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        # Get standard labels
        labels_result = service.users().labels().list(userId='me').execute()
        labels = labels_result.get('labels', [])
        
        # Format for frontend
        folders = []
        standard_labels = {
            'INBOX': {'name': 'Inbox', 'icon': 'inbox', 'color': '#1976d2'},
            'SENT': {'name': 'Sent Items', 'icon': 'send', 'color': '#388e3c'},
            'DRAFT': {'name': 'Drafts', 'icon': 'drafts', 'color': '#f57c00'},
            'STARRED': {'name': 'Starred', 'icon': 'star', 'color': '#fbc02d'},
            'TRASH': {'name': 'Deleted Items', 'icon': 'delete', 'color': '#d32f2f'},
        }
        
        for label in labels:
            if label['id'] in standard_labels:
                folder_info = standard_labels[label['id']]
                folders.append({
                    'id': label['id'].lower(),
                    'name': folder_info['name'],
                    'icon': folder_info['icon'],
                    'color': folder_info['color'],
                    'count': label.get('messagesUnread', 0)
                })
        
        return folders
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch folders: {str(e)}")

@app.put("/gmail/messages/{message_id}/star")
async def toggle_star_gmail_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle star status of a Gmail message"""
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        # Get current message to check if it's starred
        message = service.users().messages().get(
            userId='me', 
            id=message_id,
            format='metadata'
        ).execute()
        
        labels = message.get('labelIds', [])
        is_starred = 'STARRED' in labels
        
        # Toggle star
        if is_starred:
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['STARRED']}
            ).execute()
            return {"starred": False, "message": "Star removed"}
        else:
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['STARRED']}
            ).execute()
            return {"starred": True, "message": "Star added"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle star: {str(e)}")

@app.put("/gmail/messages/{message_id}/archive")
async def archive_gmail_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive a Gmail message"""
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': ['INBOX']}
        ).execute()
        
        return {"message": "Email archived successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to archive email: {str(e)}")

@app.delete("/gmail/messages/{message_id}")
async def delete_gmail_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move Gmail message to trash"""
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        service.users().messages().trash(
            userId='me',
            id=message_id
        ).execute()
        
        return {"message": "Email moved to trash"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete email: {str(e)}")

@app.get("/gmail/search")
async def search_gmail_messages(
    query: str,
    max_results: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search Gmail messages"""
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        formatted_messages = []
        
        for msg in messages:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata'
            ).execute()
            
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
            
            formatted_messages.append({
                'id': message['id'],
                'threadId': message['threadId'],
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'labels': message.get('labelIds', []),
                'snippet': message.get('snippet', '')
            })
        
        return formatted_messages
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search emails: {str(e)}")


# Google Contacts API integration
@app.get("/contacts")
async def get_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Google Workspace contacts"""
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Google Workspace access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = build('people', 'v1', credentials=credentials)
        
        # Get connections (contacts)
        results = service.people().connections().list(
            resourceName='people/me',
            personFields='names,emailAddresses,organizations,photos,phoneNumbers',
            pageSize=1000
        ).execute()
        
        connections = results.get('connections', [])
        formatted_contacts = []
        
        for person in connections:
            # Extract name
            names = person.get('names', [])
            name = names[0].get('displayName', '') if names else ''
            
            # Extract email addresses
            emails = person.get('emailAddresses', [])
            email_list = []
            for email in emails:
                email_list.append({
                    'email': email.get('value', ''),
                    'type': email.get('type', 'other')
                })
            
            # Extract organization
            orgs = person.get('organizations', [])
            organization = orgs[0].get('name', '') if orgs else ''
            
            # Extract photo
            photos = person.get('photos', [])
            photo_url = photos[0].get('url', '') if photos else ''
            
            # Extract phone numbers
            phones = person.get('phoneNumbers', [])
            phone_list = []
            for phone in phones:
                phone_list.append({
                    'number': phone.get('value', ''),
                    'type': phone.get('type', 'other')
                })
            
            if email_list:  # Only include contacts with email addresses
                formatted_contacts.append({
                    'id': person.get('resourceName', ''),
                    'name': name,
                    'emails': email_list,
                    'organization': organization,
                    'photo': photo_url,
                    'phones': phone_list,
                    'primary_email': email_list[0]['email'] if email_list else ''
                })
        
        # Sort by name
        formatted_contacts.sort(key=lambda x: x['name'].lower() if x['name'] else 'zzz')
        
        return formatted_contacts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch contacts: {str(e)}")

@app.get("/contacts/search")
async def search_contacts(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search Google Workspace contacts"""
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Google Workspace access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = build('people', 'v1', credentials=credentials)
        
        # Search for contacts
        results = service.people().searchContacts(
            query=query,
            pageSize=50,
            readMask='names,emailAddresses,organizations,photos'
        ).execute()
        
        search_results = results.get('results', [])
        formatted_contacts = []
        
        for result in search_results:
            person = result.get('person', {})
            
            # Extract name
            names = person.get('names', [])
            name = names[0].get('displayName', '') if names else ''
            
            # Extract email addresses
            emails = person.get('emailAddresses', [])
            email_list = []
            for email in emails:
                email_list.append({
                    'email': email.get('value', ''),
                    'type': email.get('type', 'other')
                })
            
            # Extract organization
            orgs = person.get('organizations', [])
            organization = orgs[0].get('name', '') if orgs else ''
            
            # Extract photo
            photos = person.get('photos', [])
            photo_url = photos[0].get('url', '') if photos else ''
            
            if email_list:  # Only include contacts with email addresses
                formatted_contacts.append({
                    'id': person.get('resourceName', ''),
                    'name': name,
                    'emails': email_list,
                    'organization': organization,
                    'photo': photo_url,
                    'primary_email': email_list[0]['email'] if email_list else ''
                })
        
        return formatted_contacts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search contacts: {str(e)}")

@app.get("/gmail/unread-notifications")
async def get_unread_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unread email notifications for dashboard"""
    session = db.query(UserSession).filter(UserSession.user_id == current_user.id).first()
    if not session or not session.access_token:
        raise HTTPException(status_code=400, detail="Gmail access requires authentication")
    
    try:
        credentials = get_credentials_from_session(session)
        service = get_gmail_service(credentials)
        
        # Get unread messages
        results = service.users().messages().list(
            userId='me',
            maxResults=10,
            q='in:inbox is:unread'
        ).execute()
        
        messages = results.get('messages', [])
        notifications = []
        
        for msg in messages[:5]:  # Get only first 5 for dashboard
            try:
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata'
                ).execute()
                
                headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
                
                # Get snippet
                snippet = message.get('snippet', '')[:100] + '...' if len(message.get('snippet', '')) > 100 else message.get('snippet', '')
                
                notifications.append({
                    'id': message['id'],
                    'subject': headers.get('Subject', 'No Subject'),
                    'from': headers.get('From', 'Unknown Sender'),
                    'snippet': snippet,
                    'timestamp': message.get('internalDate', ''),
                    'thread_id': message['threadId']
                })
            except Exception as e:
                continue
        
        return {
            'total_unread': len(messages),
            'recent_emails': notifications
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch email notifications: {str(e)}")

