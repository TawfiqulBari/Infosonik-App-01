from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
import json

from database import get_db
from models import Note, FileAttachment
from auth import get_current_user
from utils import save_upload_file, generate_unique_filename, validate_file_type, validate_file_size
from config import UPLOAD_DIR

router = APIRouter()

# Pydantic models
class NoteCreate(BaseModel):
    title: str
    content: str
    language: str = "en"
    theme: str = "light"
    attachments: List[str] = []

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    language: str
    theme: str
    attachments: List[dict] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/notes/", response_model=NoteResponse)
async def create_note(
    note: NoteCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new note"""
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

@router.get("/notes/", response_model=List[NoteResponse])
async def get_notes(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notes for the current user"""
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

@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    note: NoteCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing note"""
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

@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a note"""
    db_note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == current_user.id
    ).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted successfully"}