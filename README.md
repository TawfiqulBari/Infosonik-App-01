# 📧 Infosonik Notes & Calendar App

A comprehensive full-stack business application featuring **Notes Management**, **Calendar Events**, **Gmail Integration**, **File Management**, **Google Workspace Contacts**, and **Real-time Chat** functionality. Built with **React**, **FastAPI**, **PostgreSQL**, and **Google APIs**.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20App-blue)](https://infsnk-app-01.tawfiqulbari.work/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61dafb)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)](https://postgresql.org/)

---

## 🚀 **Key Features**

### **📧 Professional Email Management**
- **Gmail Integration** - Full inbox, sent items, drafts, and trash management
- **Email Composition** - Rich text editing with reply, forward, and compose features
- **Contact Suggestions** - Google Workspace contacts with intelligent autocomplete
- **File Attachments** - Upload and attach multiple files with progress tracking
- **Smart Search** - Advanced email search with filtering and sorting
- **Email Notifications** - Real-time unread email alerts for dashboard
- **Mobile Responsive** - Complete mobile email experience

### **📝 Advanced Notes System**
- **Rich Text Editor** - Full-featured note editing with formatting
- **Categorization** - Organize notes with tags and categories
- **Search & Filter** - Find notes quickly with advanced search
- **Version History** - Track changes and restore previous versions
- **Collaborative Features** - Share and collaborate on notes
- **Export Options** - Download notes in multiple formats

### **📅 Intelligent Calendar**
- **Google Calendar Sync** - Bidirectional calendar synchronization
- **Event Management** - Create, edit, and delete calendar events
- **Meeting Scheduling** - Smart meeting scheduling with availability
- **Reminders & Alerts** - Customizable event notifications
- **Calendar Views** - Month, week, day, and agenda views
- **Event Sharing** - Share events with team members

### **📁 File Management System**
- **Cloud Storage** - Secure file upload and storage
- **File Organization** - Folders, tags, and metadata management
- **Preview Support** - In-browser file previews for common formats
- **Version Control** - Track file versions and changes
- **Sharing & Permissions** - Control file access and sharing
- **Integration** - Seamless integration with email attachments

### **💬 Real-time Communication**
- **Chat Integration** - Google Chat integration for team communication
- **Real-time Messaging** - Instant messaging with WebSocket support
- **Notification System** - Push notifications for messages and updates
- **Presence Status** - Online/offline status tracking

### **🔐 Enterprise Security**
- **Google OAuth 2.0** - Secure authentication with Google Workspace
- **Role-Based Access Control (RBAC)** - Granular permissions system
- **Session Management** - Secure session handling and token refresh
- **Data Encryption** - End-to-end encryption for sensitive data
- **Audit Logging** - Comprehensive activity tracking

---

## 🏗️ **Technology Stack**

### **Frontend**
- **React 18** - Modern React with hooks and functional components
- **Material-UI (MUI)** - Professional UI component library
- **React Router** - Client-side routing and navigation
- **Axios** - HTTP client for API communication
- **Date-fns** - Modern date manipulation library
- **React-Toastify** - Elegant notification system

### **Backend**
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Advanced ORM with relationship mapping
- **PostgreSQL** - Robust relational database
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server for production deployment
- **Alembic** - Database migration management

### **Google APIs Integration**
- **Gmail API** - Full email management capabilities
- **Google Calendar API** - Calendar synchronization and management
- **Google People API** - Workspace contacts integration
- **Google Drive API** - File storage and management
- **Google Chat API** - Team communication features

### **Infrastructure**
- **Docker & Docker Compose** - Containerized deployment
- **Nginx** - Reverse proxy and static file serving
- **SSL/TLS** - HTTPS encryption with Let's Encrypt
- **GitHub Actions** - CI/CD pipeline automation
- **Proxmox VE** - Virtualized infrastructure

---

## 📱 **User Interface**

### **Email Interface**
- **Three-panel Layout** - Folder sidebar, email list, and email viewer
- **Responsive Design** - Optimized for desktop, tablet, and mobile
- **Contact Autocomplete** - Smart recipient suggestions while typing
- **Attachment Management** - Drag-and-drop file uploads with progress
- **Rich Text Compose** - Professional email composition interface
- **Advanced Filtering** - Filter by unread, starred, attachments, etc.

### **Dashboard**
- **Unified Overview** - All modules accessible from central dashboard
- **Real-time Notifications** - Live updates for emails, events, and messages
- **Quick Actions** - One-click access to common tasks
- **Activity Feed** - Recent activity across all modules
- **Customizable Widgets** - Personalized dashboard layout

### **Mobile Experience**
- **Progressive Web App (PWA)** - App-like experience on mobile
- **Touch-Optimized** - Native mobile gestures and interactions
- **Offline Support** - Limited functionality without internet
- **Push Notifications** - Native mobile notifications

---

## 🔧 **Installation & Setup**

### **Prerequisites**
```bash
# System Requirements
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Git
```

### **Google API Setup**
1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one
   - Enable required APIs:
     - Gmail API
     - Google Calendar API
     - Google People API (Contacts)
     - Google Drive API

2. **Configure OAuth 2.0**
   ```bash
   # Create OAuth 2.0 credentials
   - Application type: Web application
   - Authorized redirect URIs: https://your-domain.com/auth/callback
   - Download credentials JSON file
   ```

3. **Set Environment Variables**
   ```bash
   # Copy environment template
   cp .env.example .env.prod
   
   # Edit with your Google API credentials
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=https://your-domain.com/auth/callback
   ```

### **Quick Start**
```bash
# Clone the repository
git clone https://github.com/TawfiqulBari/Infosonik-App-01.git
cd Infosonik-App-01

# Configure environment
cp .env.example .env.prod
# Edit .env.prod with your configuration

# Deploy with Docker
./deploy.sh

# Access the application
https://your-domain.com
```

### **Development Setup**
```bash
# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
npm install

# Run database migrations
python apply_all_migrations.py

# Start development servers
# Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend
npm start
```

---

## 📧 **Email Features Deep Dive**

### **Gmail Integration**
- **Full API Access** - Complete Gmail functionality through Google APIs
- **Real-time Sync** - Live synchronization with Gmail servers
- **Folder Management** - Inbox, Sent, Drafts, Starred, Trash support
- **Label Support** - Custom Gmail labels and categories
- **Thread Management** - Email conversation threading

### **Contact Management**
- **Google Workspace Contacts** - Access to organization directory
- **Smart Autocomplete** - Contact suggestions with typing
- **Contact Search** - Search by name, email, or organization
- **Visual Contact Cards** - Profile pictures and organization info
- **Multiple Recipients** - Support for To, CC, BCC fields

### **File Attachments**
- **Multi-file Upload** - Attach multiple files simultaneously
- **File Type Support** - Documents, images, archives, presentations
- **Upload Progress** - Real-time upload progress tracking
- **File Management** - Preview, remove, and organize attachments
- **Size Limits** - Configurable file size restrictions
- **Virus Scanning** - Optional file scanning for security

### **Email Composition**
- **Rich Text Editor** - Full formatting capabilities
- **Template System** - Pre-defined email templates
- **Auto-save Drafts** - Automatic draft saving while composing
- **Signature Support** - Custom email signatures
- **Spell Check** - Built-in spell checking
- **Mobile Optimized** - Full mobile compose experience

---

## 🔐 **Security Features**

### **Authentication & Authorization**
- **Google OAuth 2.0** - Secure authentication with Google Workspace
- **JWT Tokens** - Secure API authentication
- **Refresh Tokens** - Automatic token renewal
- **Session Management** - Secure session handling
- **Multi-factor Authentication (MFA)** - Optional 2FA support

### **Data Protection**
- **Encryption at Rest** - Database encryption
- **Encryption in Transit** - HTTPS/TLS encryption
- **API Rate Limiting** - Protection against abuse
- **Input Validation** - Comprehensive data validation
- **SQL Injection Protection** - Parameterized queries
- **XSS Protection** - Cross-site scripting prevention

### **Access Control**
- **Role-Based Permissions** - Granular access control
- **Resource-Level Security** - Per-resource permissions
- **Audit Logging** - Comprehensive activity tracking
- **IP Whitelisting** - Optional IP-based restrictions
- **Session Timeout** - Automatic session expiration

---

## 🚀 **Deployment**

### **Production Deployment**
```bash
# Clone and configure
git clone https://github.com/TawfiqulBari/Infosonik-App-01.git
cd Infosonik-App-01

# Set up environment
cp .env.example .env.prod
# Edit .env.prod with production values

# Deploy with SSL
./deploy.sh

# Verify deployment
docker compose -f docker-compose.prod.yml ps
```

### **Infrastructure Requirements**
- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ recommended
- **Storage**: 50GB+ for files and database
- **Network**: HTTPS with valid SSL certificate
- **Backup**: Regular database and file backups

### **Monitoring & Maintenance**
- **Health Checks** - Automated container health monitoring
- **Log Aggregation** - Centralized logging with rotation
- **Performance Monitoring** - Resource usage tracking
- **Database Maintenance** - Regular vacuum and analyze
- **Security Updates** - Regular dependency updates

---

## 📊 **API Documentation**

### **Interactive API Docs**
- **Swagger UI**: `https://your-domain.com/docs`
- **ReDoc**: `https://your-domain.com/redoc`
- **OpenAPI Schema**: `https://your-domain.com/openapi.json`

### **Key API Endpoints**

#### **Authentication**
```http
GET  /auth/google          # Initiate Google OAuth
GET  /auth/callback        # OAuth callback handler
GET  /auth/me             # Get current user info
POST /auth/logout         # Logout user
```

#### **Email Management**
```http
GET    /gmail/messages          # Get email messages
POST   /gmail/send             # Send email with attachments
GET    /gmail/search           # Search emails
PUT    /gmail/messages/{id}/star # Toggle email star
POST   /gmail/messages/{id}/mark-read # Mark as read
DELETE /gmail/messages/{id}    # Delete email
```

#### **Contacts**
```http
GET /contacts              # Get Google Workspace contacts
GET /contacts/search       # Search contacts by query
```

#### **File Management**
```http
POST GET /files/upload     # Upload files
GET  /files/               # List files
GET  /files/{id}/download  # Download file
```

#### **Notes & Calendar**
```http
GET    /notes/             # Get notes
POST   /notes/             # Create note
PUT    /notes/{id}         # Update note
DELETE /notes/{id}         # Delete note

GET    /events/            # Get calendar events
POST   /events/            # Create event
PUT    /events/{id}        # Update event
DELETE /events/{id}        # Delete event
```

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Google API Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-domain.com/auth/callback

# Application Configuration
SECRET_KEY=your_secret_key_here
ENVIRONMENT=production
DEBUG=false

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# File Upload Configuration
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,doc,docx,txt,jpg,jpeg,png,gif,zip

# Security Configuration
SESSION_TIMEOUT=3600    # 1 hour
JWT_EXPIRATION=86400   # 24 hours
RATE_LIMIT=100         # requests per minute
```

### **Docker Configuration**
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/ssl/certs
```

---

## 🧪 **Testing**

### **Backend Testing**
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest tests/ -v --cov=main

# Run specific test categories
pytest tests/test_email.py -v
pytest tests/test_contacts.py -v
pytest tests/test_auth.py -v
```

### **Frontend Testing**
```bash
# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run end-to-end tests
npm run test:e2e
```

### **API Testing**
```bash
# Test email functionality
curl -X GET "https://your-domain.com/gmail/messages" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test contact search
curl -X GET "https://your-domain.com/contacts/search?query=john" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test file upload
curl -X POST "https://your-domain.com/files/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf"
```

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Contact Suggestions Not Working**
```bash
# Verify Google People API is enabled
# Check OAuth scopes include contacts.readonly
# Ensure user is authenticated with Google
# Check browser console for API errors
```

#### **File Upload Issues**
```bash
# Check file size limits
# Verify file type restrictions
# Ensure upload directory permissions
# Check disk space availability
```

#### **Email Integration Problems**
```bash
# Verify Gmail API is enabled
# Check OAuth scopes and permissions
# Test API credentials
# Review rate limiting settings
```

### **Debug Mode**
```bash
# Enable debug logging
DEBUG=true
LOG_LEVEL=debug

# View detailed logs
docker logs infosonik-app-01-app-1 -f

# Check database connections
docker exec -it infosonik-app-01-db-1 psql -U postgres -d infosonik
```

---

## 📈 **Performance Optimization**

### **Backend Optimization**
- **Database Indexing** - Optimized queries with proper indexes
- **Caching Strategy** - Redis caching for frequently accessed data
- **Connection Pooling** - Efficient database connection management
- **Background Tasks** - Celery for asynchronous processing
- **API Rate Limiting** - Prevent abuse and ensure stability

### **Frontend Optimization**
- **Code Splitting** - Lazy loading of React components
- **Bundle Optimization** - Webpack optimization for smaller bundles
- **Image Optimization** - Compressed and optimized images
- **CDN Integration** - Static asset delivery via CDN
- **Service Workers** - Caching for offline functionality

### **Infrastructure Optimization**
- **Load Balancing** - Multiple instance deployment
- **Container Optimization** - Optimized Docker images
- **Database Tuning** - PostgreSQL performance optimization
- **Monitoring** - Comprehensive performance monitoring
- **Auto-scaling** - Automatic resource scaling based on load

---

## 🤝 **Contributing**

### **Development Guidelines**
1. **Fork the repository** and create a feature branch
2. **Follow code standards** - ESLint for frontend, Black for backend
3. **Write tests** - Maintain test coverage above 80%
4. **Update documentation** - Update README and API docs
5. **Create pull request** - Detailed description of changes

### **Code Style**
- **Frontend**: ESLint + Prettier configuration
- **Backend**: Black + isort + flake8 configuration
- **Commits**: Conventional commit messages
- **Documentation**: Comprehensive inline comments

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 **Author**

**Tawfiqul Bari**
- GitHub: [@TawfiqulBari](https://github.com/TawfiqulBari)
- LinkedIn: [Tawfiqul Bari](https://linkedin.com/in/tawfiqulbari)
- Email: tawfiqul.bari@example.com

---

## 🌟 **Acknowledgments**

- **Google APIs** - Gmail, Calendar, Contacts, and Drive integration
- **Material-UI** - Excellent React component library
- **FastAPI** - Modern Python web framework
- **React Community** - Comprehensive ecosystem
- **Open Source Contributors** - Various libraries and tools

---

## 📞 **Support**

### **Getting Help**
- **Documentation**: Comprehensive setup and usage guides
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Community support via GitHub Discussions
- **Email**: Direct support for deployment assistance

### **Professional Services**
- **Custom Development** - Feature additions and customizations
- **Deployment Support** - Professional deployment assistance
- **Training & Consulting** - Team training and consulting services
- **Maintenance Contracts** - Ongoing maintenance and support

---

**⭐ Star this repository if you find it helpful!**

[![GitHub stars](https://img.shields.io/github/stars/TawfiqulBari/Infosonik-App-01.svg?style=social&label=Star)](https://github.com/TawfiqulBari/Infosonik-App-01)
[![GitHub forks](https://img.shields.io/github/forks/TawfiqulBari/Infosonik-App-01.svg?style=social&label=Fork)](https://github.com/TawfiqulBari/Infosonik-App-01/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/TawfiqulBari/Infosonik-App-01.svg?style=social&label=Watch)](https://github.com/TawfiqulBari/Infosonik-App-01)

---

*Last updated: $(date '+%B %d, %Y')*
