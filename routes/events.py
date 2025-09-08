from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import json

from database import get_db
from models import Event, FileAttachment, UserSession
from auth import get_current_user
from utils import (
    create_calendar_event, fetch_google_calendar_events,
    get_credentials_from_session
)

router = APIRouter()

# Pydantic models
class EventCreate(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    attachments: List[str] = []

class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    google_event_id: str = None
    attachments: List[dict] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/events/", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new event"""
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

@router.get("/events/", response_model=List[EventResponse])
async def get_events(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all events for the current user"""
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
    try:
        result.sort(key=lambda x: x.start_time.replace(tzinfo=None) if x.start_time.tzinfo else x.start_time)
    except (AttributeError, TypeError):
        # Fallback sorting if datetime comparison fails
        result.sort(key=lambda x: str(x.start_time))

    return result

@router.post("/events/{event_id}/share")
async def share_event(
    event_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Share an event"""
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
        from googleapiclient.discovery import build
        credentials = get_credentials_from_session(session)
        service = build('calendar', 'v3', credentials=credentials)

        if event.google_event_id:
            # Share existing Google Calendar event
            event_body = service.events().get(calendarId='primary', eventId=event.google_event_id).execute()

            # Add domain-wide sharing
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