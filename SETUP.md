# Infosonik Notes & Calendar App - Setup Guide

## 🎉 Deployment Status: SUCCESSFUL ✅

Your advanced notes and calendar application has been successfully deployed and is running at:
**http://62.169.16.31:8080**

---

## 📋 Implemented Features

### ✅ **1. Google Workspace Authentication**
- **Domain Restriction**: Only `@infosonik.com` users can access the application
- **OAuth Integration**: Secure Google Workspace SSO
- **JWT Authentication**: Session management with secure tokens
- **User Profiles**: Automatic profile creation with Google data

### ✅ **2. File Attachment System**
- **Local Storage**: Files stored securely on the server
- **Google Drive Sync**: Automatic backup to user's Google Drive
- **Supported Formats**: PDF, Excel (.xls/.xlsx), Word (.doc/.docx), Images (JPG/PNG), Text files
- **Drag & Drop Upload**: Modern file upload interface
- **File Management**: Download, view, and organize attachments

### ✅ **3. Dark/Light Theme Support**
- **User Preferences**: Personal theme settings
- **Real-time Switching**: Instant theme changes
- **Persistent Settings**: Themes saved to user profile
- **Material-UI Integration**: Professional design system

### ✅ **4. Data Backup & Restore**
- **Google Drive Integration**: Secure cloud backup
- **Complete Data Export**: Notes, events, and files
- **One-Click Restore**: Easy data recovery
- **Scheduled Backups**: Configurable backup frequency

### ✅ **5. Enhanced User Interface**
- **Material-UI Components**: Modern, responsive design
- **Mobile-Friendly**: Works on all devices
- **Multi-language Support**: English and Bangla
- **Rich Dashboard**: Overview of notes, events, and files
- **Search & Filter**: Find content quickly

### ✅ **6. Advanced Features**
- **Calendar Integration**: Google Calendar synchronization
- **File Attachments**: Attach files to notes and events
- **Voice Recognition**: Speech-to-text capabilities (framework ready)
- **RESTful API**: Complete backend API
- **Database Management**: PostgreSQL with migrations

---

## 🔧 Google OAuth Setup (Required)

To enable authentication, you need to configure Google OAuth credentials:

### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google+ API
   - Google Drive API
   - Google Calendar API

### Step 2: Configure OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **Internal** (for workspace users only)
3. Fill in application details:
   - App name: `Infosonik Notes & Calendar`
   - User support email: Your admin email
   - Developer contact: Your admin email
4. Add scopes:
   - `userinfo.email`
   - `userinfo.profile`
   - `https://www.googleapis.com/auth/drive`
   - `https://www.googleapis.com/auth/calendar`

### Step 3: Create OAuth Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client IDs**
3. Choose **Web application**
4. Add authorized redirect URIs:
   - `http://62.169.16.31:8080/auth/callback`
   - `http://localhost:8080/auth/callback` (for development)
5. Save and copy the **Client ID** and **Client Secret**

### Step 4: Update Server Configuration
SSH into your server and update the environment variables:

```bash
ssh root@62.169.16.31
cd /opt/webapp-01
nano .env.prod
```

Update these values in `.env.prod`:
```bash
GOOGLE_CLIENT_ID=your_actual_client_id_here
GOOGLE_CLIENT_SECRET=your_actual_client_secret_here
SECRET_KEY=your_very_long_secure_secret_key_for_jwt_tokens
```

### Step 5: Restart Application
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🚀 Application Structure

### Backend (FastAPI)
- **Authentication**: JWT + Google OAuth
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Storage**: Local + Google Drive integration
- **API Endpoints**: RESTful design with OpenAPI docs

### Frontend (React)
- **Framework**: React 18 with hooks
- **UI Library**: Material-UI v5
- **Routing**: React Router v6
- **State Management**: Context API
- **Styling**: Material-UI + Custom CSS

### Database Schema
- **Users**: Profile and preferences
- **Notes**: Content with attachments and themes
- **Events**: Calendar integration
- **Files**: Attachment metadata
- **Sessions**: User authentication state

---

## 📱 Usage Guide

### Initial Setup
1. **Admin Setup**: Configure Google OAuth credentials (above)
2. **User Access**: Only `@infosonik.com` accounts can sign in
3. **First Login**: Users will be prompted to authorize Google permissions

### Creating Notes
1. Navigate to **Notes** section
2. Click **New Note**
3. Add title, content, select language and theme
4. Drag & drop files to attach them
5. Save note (automatically synced to Google Drive)

### Managing Calendar Events
1. Go to **Calendar** section
2. Click **New Event**
3. Fill in event details with date/time
4. Attach relevant files
5. Events sync with Google Calendar

### File Management
1. Visit **Files** section
2. Drag & drop files to upload
3. Files are stored locally and backed up to Google Drive
4. Download or view files anytime

### Backup & Restore
1. Go to **Backup** section
2. Click **Create Backup** for complete data export
3. Use backup ID to restore data later
4. All backups stored in Google Drive

---

## 🔒 Security Features

- **Domain Restriction**: Only infosonik.com accounts
- **Secure Authentication**: JWT tokens with expiration
- **HTTPS Ready**: SSL certificate support
- **Data Encryption**: Secure password hashing
- **CORS Protection**: Configured for security
- **Input Validation**: Comprehensive data validation

---

## 🛠 Technical Specifications

### System Requirements
- **Server**: Ubuntu/Debian Linux
- **Docker**: Version 20.10+
- **Memory**: Minimum 2GB RAM
- **Storage**: 10GB+ available space
- **Network**: Internet access for Google APIs

### Dependencies
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: Node.js 18, React 18, Material-UI
- **Database**: PostgreSQL 15
- **Storage**: Local filesystem + Google Drive API

---

## 📊 API Documentation

Once the application is running, visit:
- **API Docs**: http://62.169.16.31:8080/docs
- **Alternative Docs**: http://62.169.16.31:8080/redoc

---

## 🆔 Support & Maintenance

### Logs & Monitoring
```bash
# View application logs
ssh root@62.169.16.31
cd /opt/webapp-01
docker-compose -f docker-compose.prod.yml logs app

# Check container status
docker ps

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### Database Management
```bash
# Access database
docker exec -it webapp-01-db-1 psql -U user -d webapp_db

# Backup database
docker exec webapp-01-db-1 pg_dump -U user webapp_db > backup.sql
```

### Updates & Deployment
```bash
# Pull latest changes
cd /opt/webapp-01
git pull origin main

# Rebuild and deploy
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🎯 Next Steps

1. **Configure Google OAuth** (Priority 1)
2. **Test with infosonik.com accounts**
3. **Set up SSL certificate** for HTTPS
4. **Configure automated backups**
5. **Train users** on new features
6. **Monitor application performance**

---

## 📞 Contact

For technical support or questions:
- **Repository**: https://github.com/TawfiqulBari/Infosonik-App-01
- **Deployment**: http://62.169.16.31:8080
- **Status**: ✅ Successfully Deployed and Running

---

**Congratulations! Your advanced Infosonik Notes & Calendar application is now live and ready for your team to use! 🎉**
