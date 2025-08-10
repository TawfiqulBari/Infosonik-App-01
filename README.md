# Infosonik Notes & Calendar App

A comprehensive enterprise web application built with React and FastAPI, featuring advanced productivity tools, leave management, file handling, and Google Workspace integration.

## 🌟 Key Features

### 📋 Core Functionality
- **Notes Management**: Create, edit, delete, and organize notes with rich text editing
- **Calendar Integration**: Google Calendar sync with event creation and management
- **File Management**: Upload, download, and organize files with Google Drive integration
- **User Authentication**: Google OAuth integration with secure session management

### 🏢 Enterprise Features

#### 🗓️ **Leave Management System** *(Bangladesh Labour Act Compliant)*
- **Leave Types**: Casual (10 days), Sick (14 days), Earned (22 days), Maternity (112 days), Paternity (5 days)
- **Real-time Balance Tracking**: Visual progress bars showing used/available leave days
- **Multi-level Approval Workflow**: Manager → HR → CEO approval chain based on leave type and duration
- **Half-day Leave Support**: Morning/Afternoon half-day options
- **Carry Forward Rules**: Automatic calculation of carried forward leaves
- **Medical Certificate Requirements**: Configurable requirements for sick leave
- **Comprehensive Reporting**: Team calendar, leave analytics, and audit trails
- **Legal Compliance**: Full adherence to Bangladesh Labour Act Sections 103-107

#### 💰 **Expense Management**
- Expense submission and approval workflow
- Receipt upload and management
- Expense categorization and reporting
- Manager and admin approval levels

#### 👥 **Administrative Controls**
- **User Management**: Create, edit, and manage user accounts
- **Role-Based Access Control (RBAC)**: Fine-grained permission management
- **Group Management**: Organize users into departments/teams
- **Audit Logging**: Complete activity tracking for compliance

#### 📊 **Reporting & Analytics**
- **User Activity Reports**: Comprehensive usage analytics
- **Leave Analytics**: Utilization patterns and trends
- **Expense Reports**: Financial tracking and budgeting
- **System Health Monitoring**: Performance and usage metrics

### 📧 **Communication Features**
- **Gmail Integration**: Read, compose, and send emails directly from the app
- **Contact Management**: Google Contacts integration with search functionality
- **Email Notifications**: Real-time notifications for important events
- **Contact Suggestions**: Smart contact suggestions while composing emails

### ☁️ **Cloud Integration**
- **Google Workspace**: Full integration with Gmail, Drive, Calendar, and Contacts
- **Google Drive**: File synchronization and sharing
- **Real-time Sync**: Automatic synchronization across all connected services

### 🎙️ **Advanced Features**
- **Voice-to-Text**: Speech recognition for quick note taking
- **Real-time Chat**: Built-in messaging system
- **File Attachments**: Support for various file formats
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

## 🚀 Recent Updates (August 2025)

### 🆕 **Leave Management System**
- ✅ **Complete Implementation**: Bangladesh Labour Act compliant leave management
- ✅ **Database Migration**: 7 new tables with comprehensive leave data structure
- ✅ **API Endpoints**: Full CRUD operations for leave management
- ✅ **Modern UI**: React-based interface with Material-UI components
- ✅ **Real-time Data**: Live balance updates and application tracking
- ✅ **Workflow Engine**: Multi-level approval system with notifications

### 🔧 **Technical Improvements**
- ✅ **API Route Optimization**: Fixed route ordering and middleware issues
- ✅ **Database Schema Updates**: Enhanced models for better performance
- ✅ **Frontend Build Process**: Optimized React build pipeline
- ✅ **Error Handling**: Improved error reporting and user feedback
- ✅ **Authentication Flow**: Enhanced security and session management

### 📧 **Email & Contact Features**
- ✅ **Gmail Integration**: Enhanced email reading and composition
- ✅ **Contact Suggestions**: Smart contact recommendations
- ✅ **Email Attachments**: Support for file attachments in emails
- ✅ **Notification System**: Real-time email and system notifications

## 🏗️ Technology Stack

### Frontend
- **React 18**: Modern React with hooks and functional components
- **Material-UI (MUI)**: Professional UI component library
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communications
- **React Toastify**: User notifications and feedback

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: ORM with PostgreSQL database
- **Pydantic**: Data validation and serialization
- **Google APIs**: Integration with Google Workspace services
- **JWT Authentication**: Secure token-based authentication
- **Alembic**: Database migration management

### Infrastructure
- **Docker**: Containerized deployment
- **PostgreSQL**: Primary database
- **Nginx**: Reverse proxy and static file serving
- **Docker Compose**: Multi-container orchestration
- **Environment Management**: Configurable deployment environments

## 📊 Database Schema

### Leave Management Tables
- `leave_policies`: Leave type definitions and entitlements
- `leave_balances`: User-specific leave balances per year
- `leave_applications`: Leave requests and applications
- `leave_approval_workflows`: Multi-level approval configurations
- `leave_calendar`: Team leave calendar for planning
- `leave_encashments`: Leave encashment records
- `leave_audit_logs`: Complete audit trail for compliance

### Core Tables
- `users`: User accounts and profiles
- `notes`: Note storage with metadata
- `events`: Calendar events and scheduling
- `files`: File metadata and storage
- `expenses`: Expense management
- `user_sessions`: Authentication and session management

## 🚀 Deployment

### Production Environment
- **URL**: https://infsnk-app-01.tawfiqulbari.work/
- **SSL**: Automatic HTTPS with Let's Encrypt
- **CDN**: Optimized static asset delivery
- **Monitoring**: Health checks and performance monitoring

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/infosonik-app.git
cd infosonik-app

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run with Docker Compose
docker-compose up -d

# Access the application
open http://localhost
```

### Manual Deployment
```bash
# Backend setup
pip install -r requirements.txt
python main.py

# Frontend setup
npm install
npm run build

# Database migration
python apply_migration.py
python leave_management_migration.py
```

## 🔧 Configuration

### Environment Variables
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/infosonik
DB_PASSWORD=your_secure_password

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback

# Security
SECRET_KEY=your_jwt_secret_key
ENVIRONMENT=production
DEBUG=false

# Domain Configuration
DOMAIN_NAME=yourdomain.com
ACME_EMAIL=admin@yourdomain.com
```

### Google Workspace Setup
1. Create a Google Cloud Project
2. Enable required APIs (Gmail, Drive, Calendar, People)
3. Configure OAuth consent screen
4. Create OAuth 2.0 credentials
5. Set up authorized redirect URIs

## 📚 API Documentation

### Leave Management Endpoints
- `GET /leave/policies` - Get all leave policies
- `GET /leave/balances` - Get user's leave balances
- `GET /leave/my-applications` - Get user's leave applications
- `POST /leave/applications` - Submit new leave application
- `GET /leave/team-calendar` - Get team leave calendar
- `GET /leave/pending-approvals` - Get pending approvals (managers/HR)

### Core API Endpoints
- `GET /notes/` - Get all notes
- `POST /notes/` - Create new note
- `GET /events/` - Get calendar events
- `POST /files/upload` - Upload files
- `GET /gmail/messages` - Get email messages
- `POST /gmail/send` - Send email

### Authentication
- `GET /auth/google` - Initiate Google OAuth
- `GET /auth/callback` - OAuth callback
- `GET /auth/me` - Get current user
- `POST /auth/logout` - Logout user

## 🛡️ Security Features

- **OAuth 2.0**: Secure Google authentication
- **JWT Tokens**: Stateless authentication
- **CORS Protection**: Cross-origin request filtering
- **Input Validation**: Pydantic data validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **HTTPS Enforcement**: SSL/TLS encryption
- **Session Management**: Secure session handling

## 🧪 Testing

### API Testing
```bash
# Test leave management endpoints
curl -X GET "https://infsnk-app-01.tawfiqulbari.work/leave/policies"
curl -X GET "https://infsnk-app-01.tawfiqulbari.work/leave/balances" -H "Authorization: Bearer YOUR_TOKEN"

# Test core functionality
curl -X GET "https://infsnk-app-01.tawfiqulbari.work/notes/" -H "Authorization: Bearer YOUR_TOKEN"
```

### Frontend Testing
- Navigate to https://infsnk-app-01.tawfiqulbari.work/
- Test leave application submission
- Verify leave balance display
- Check email composition and contact suggestions

## 📱 Mobile Responsiveness

The application is fully responsive and optimized for:
- **Desktop**: Full feature set with optimal layout
- **Tablet**: Adapted interface for touch interaction
- **Mobile**: Streamlined mobile-first design
- **PWA Support**: Installable as a mobile app

## 🔄 Data Migration

### Leave Management Migration
```bash
# Run the leave management migration
python leave_management_migration.py
```

This migration adds:
- Bangladesh Labour Act compliant leave policies
- User leave balances with pro-rata calculations
- Multi-level approval workflow configurations
- Comprehensive audit logging system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Lead Developer**: Tawfiqul Bari
- **Backend Architecture**: FastAPI + PostgreSQL
- **Frontend Development**: React + Material-UI
- **DevOps**: Docker + Nginx

## 📞 Support

For support and questions:
- **Email**: baritechsys@gmail.com
- **GitHub Issues**: Create an issue in this repository
- **Documentation**: Check the `/docs` endpoint for API documentation

## 🎯 Roadmap

### Upcoming Features
- [ ] Mobile App (React Native)
- [ ] Advanced Reporting Dashboard
- [ ] AI-powered Leave Predictions
- [ ] Integration with HR Systems
- [ ] Multi-language Support
- [ ] Advanced File Preview
- [ ] Real-time Collaborative Editing

### Performance Improvements
- [ ] Redis Caching
- [ ] Database Query Optimization
- [ ] CDN Integration
- [ ] Progressive Web App (PWA)
- [ ] Offline Functionality

---

**Built with ❤️ by the Infosonik Team**

*Last Updated: August 2025*
