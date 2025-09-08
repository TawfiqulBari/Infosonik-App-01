from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from pathlib import Path
import os
import aiofiles
import shutil
from datetime import datetime

# Import from our segregated modules
from database import get_db, wait_for_database, create_tables
from models import User, FileAttachment, ConvenienceBill, IntelligentExpense, ExpenseCategory
from config import UPLOAD_DIR, API_V1_PREFIX
from auth import router as auth_router, get_current_user, require_admin
from routes.notes import router as notes_router
from routes.events import router as events_router
from utils import (
    save_upload_file, generate_unique_filename, validate_file_type, validate_file_size,
    upload_to_drive, get_credentials_from_session, perform_health_check
)

# Create upload directory
UPLOAD_DIR_PATH = Path(UPLOAD_DIR)
UPLOAD_DIR_PATH.mkdir(exist_ok=True)

# Create FastAPI app
app = FastAPI(title="Infosonik Notes & Calendar App")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and create tables on startup"""
    try:
        print("Waiting for database connection...")
        wait_for_database()
        print("Creating database tables...")
        create_tables()
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        # Don't raise exception here to allow app to start even if DB fails

# Include routers
app.include_router(auth_router, prefix=API_V1_PREFIX, tags=["authentication"])
app.include_router(notes_router, prefix=API_V1_PREFIX, tags=["notes"])
app.include_router(events_router, prefix=API_V1_PREFIX, tags=["events"])

# File upload endpoints
@app.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file"""
    # Validate file type
    if not validate_file_type(file.content_type):
        raise HTTPException(status_code=400, detail="File type not allowed")

    # Read file content
    content = await file.read()

    # Validate file size
    if not validate_file_size(len(content)):
        raise HTTPException(status_code=400, detail="File size too large")

    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR_PATH / unique_filename

    # Save file locally
    async with aiofiles.open(file_path, 'wb') as f:
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
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's files"""
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
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a file"""
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

# Expense endpoints (simplified)
@app.get("/expenses/categories")
async def get_expense_categories(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all active expense categories"""
    categories = db.query(ExpenseCategory).filter(ExpenseCategory.is_active == True).all()
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "icon": cat.icon,
            "color": cat.color,
            "requires_receipt": cat.requires_receipt,
            "receipt_threshold": cat.receipt_threshold
        }
        for cat in categories
    ]

# Bills endpoints (simplified)
@app.get("/bills/my-bills")
async def get_my_convenience_bills(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's convenience bills"""
    bills = db.query(ConvenienceBill).filter(
        ConvenienceBill.user_id == current_user.id
    ).order_by(ConvenienceBill.created_at.desc()).all()

    result = []
    for bill in bills:
        result.append({
            "id": bill.id,
            "bill_date": bill.bill_date,
            "transport_amount": bill.transport_amount or 0,
            "food_amount": bill.food_amount or 0,
            "other_amount": bill.other_amount or 0,
            "total_amount": bill.total_amount,
            "general_description": bill.general_description,
            "status": bill.status,
            "created_at": bill.created_at
        })

    return result

# Admin endpoints
@app.get("/admin/users")
async def get_all_users(
    admin_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
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
    admin_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin statistics"""
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

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    return perform_health_check(db)

# Mount static files and serve React app
if os.path.exists("static"):
    # Mount the React build static files
    app.mount("/static", StaticFiles(directory="static/static"), name="static")

    @app.get("/")
    async def read_index():
        return FileResponse('static/index.html')

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for all routes not handled by API"""
    # Skip API routes
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
        full_path.startswith("webhook/") or
        full_path.startswith("contacts") or
        full_path.startswith("email-notifications") or
        full_path.startswith("test/")
    ):
        raise HTTPException(status_code=404, detail="Not found")

    if os.path.exists("static/index.html"):
        return FileResponse('static/index.html')

    raise HTTPException(status_code=404, detail="Not found")

# Import additional models that might be needed
from models import (
    UserSession, Note, Event, LeaveApplication, Client,
    MEDDPICC, SalesFunnel, UserGroup, GroupMembership
)