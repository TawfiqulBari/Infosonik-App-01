from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import speech_recognition as sr
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    language = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    google_event_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Pydantic models
class NoteCreate(BaseModel):
    title: str
    content: str
    language: str

class NoteResponse(NoteCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class EventCreate(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime

class EventResponse(EventCreate):
    id: int
    google_event_id: str
    created_at: datetime

    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI(title="Notes & Calendar App")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    creds = Credentials(token=credentials['token'])
    service = build('calendar', 'v3', credentials=creds)
    
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

# Endpoints
@app.post("/notes/", response_model=NoteResponse)
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    db_note = Note(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.post("/events/", response_model=EventResponse)
def create_event(event: EventCreate, credentials: dict, db: Session = Depends(get_db)):
    google_event_id = create_calendar_event(event, credentials)
    db_event = Event(
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        google_event_id=google_event_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.post("/voice-to-text/")
def voice_to_text(language: str = "en-US"):
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
