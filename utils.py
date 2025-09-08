import uuid
import json
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from pathlib import Path
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
from jose import JWTError, jwt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import speech_recognition as sr

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, UPLOAD_DIR
from models import User, UserSession, ExpenseCategory, IntelligentExpense

# Create upload directory
UPLOAD_DIR_PATH = Path(UPLOAD_DIR)
UPLOAD_DIR_PATH.mkdir(exist_ok=True)

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

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user_from_token(token: str, db: Session):
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Google OAuth functions
def get_google_oauth_flow():
    from google_auth_oauthlib.flow import Flow
    from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

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
    from config import ALLOWED_DOMAIN
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
    from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

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

# Expense utility functions
def generate_expense_number():
    """Generate unique expense number"""
    timestamp = datetime.now().strftime("%Y%m")
    random_part = str(uuid.uuid4())[:8].upper()
    return f"EXP-{timestamp}-{random_part}"

def auto_categorize_expense(title: str, description: str, amount: int, db: Session):
    """Auto-categorize expense using simple keyword matching"""
    categories = db.query(ExpenseCategory).filter(ExpenseCategory.is_active == True).all()

    text = f"{title} {description or ''}".lower()

    # Simple keyword matching
    category_keywords = {
        'Transportation': ['transport', 'taxi', 'uber', 'bus', 'train', 'fuel', 'parking', 'car', 'bike'],
        'Meals & Entertainment': ['meal', 'lunch', 'dinner', 'restaurant', 'food', 'coffee', 'breakfast'],
        'Office Supplies': ['office', 'supplies', 'stationery', 'paper', 'pen', 'notebook'],
        'Travel & Accommodation': ['hotel', 'accommodation', 'flight', 'travel', 'booking', 'airfare'],
        'Communication': ['phone', 'internet', 'mobile', 'communication', 'telecom'],
        'Training & Development': ['training', 'course', 'seminar', 'workshop', 'education'],
        'Equipment & Technology': ['computer', 'laptop', 'software', 'equipment', 'hardware', 'tech']
    }

    best_match = None
    confidence = 0.0

    for category in categories:
        if category.name in category_keywords:
            keywords = category_keywords[category.name]
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                category_confidence = matches / len(keywords)

                if category_confidence > confidence:
                    confidence = category_confidence
                    best_match = category

    return best_match, min(confidence * 100, 95.0) if best_match else (None, 0.0)

# File handling utilities
def save_upload_file(upload_file, destination: Path) -> None:
    """Save an uploaded file to the specified destination"""
    with destination.open("wb") as buffer:
        import shutil
        shutil.copyfileobj(upload_file.file, buffer)

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1] if '.' in filename else ''

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename"""
    file_id = str(uuid.uuid4())
    extension = get_file_extension(original_filename)
    return f"{file_id}.{extension}" if extension else file_id

# Validation utilities
def validate_file_type(content_type: str) -> bool:
    """Validate if file type is allowed"""
    from config import ALLOWED_FILE_TYPES
    return content_type in ALLOWED_FILE_TYPES

def validate_file_size(file_size: int) -> bool:
    """Validate if file size is within limits"""
    from config import MAX_FILE_SIZE
    return file_size <= MAX_FILE_SIZE

# Date and time utilities
def calculate_working_days(start_date: date, end_date: date) -> int:
    """Calculate working days between two dates (excluding Fridays in Bangladesh)"""
    working_days = 0
    current_date = start_date

    while current_date <= end_date:
        # In Bangladesh, Friday is weekend, Saturday is half-day
        if current_date.weekday() != 4:  # Not Friday
            working_days += 1
        current_date += timedelta(days=1)

    return working_days

# Permission utilities
def user_has_permission(user: User, permission: str, db: Session) -> bool:
    """Check if user has a specific permission through their role"""
    from models import Role
    role = None
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
    if role and role.permissions:
        permissions = json.loads(role.permissions)
        return permission in permissions
    return False

def require_permission(permission: str):
    """Dependency factory to require specific permission"""
    def permission_dependency(user: User = None, db: Session = None):
        from config import SECRET_KEY, ALGORITHM
        # This will be implemented in the auth module
        return user
    return permission_dependency

# Audit logging utilities
def create_audit_log(action: str, user_id: int, details: Dict[str, Any], db: Session):
    """Create an audit log entry"""
    # For now, just log to console - implement proper audit table later
    print(f"AUDIT: User {user_id}, Action: {action}, Details: {details}")

# Health check utilities
def perform_health_check(db: Session) -> Dict[str, Any]:
    """Perform comprehensive health check"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }