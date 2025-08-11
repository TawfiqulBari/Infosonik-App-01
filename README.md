# Infosonik Enterprise Management Platform

A comprehensive enterprise web application built with React and FastAPI, featuring advanced productivity tools, intelligent expense management, leave management, file handling, and Google Workspace integration.

## 🌟 Key Features

### 📋 Core Functionality
- **Smart Notes Management**: Create, edit, delete, and organize notes with rich text editing
- **Calendar Integration**: Google Calendar sync with event creation and management
- **File Management**: Upload, download, and organize files with Google Drive integration
- **User Authentication**: Google OAuth integration with secure session management

### 🏢 Enterprise Features

#### 🤖 **Smart Expense Management System** *(NEW - August 2025)*
- **Intelligent Categorization**: AI-powered automatic expense categorization with confidence scoring
- **Multi-Transport Support**: 12+ transport modes (Bus, CNG, Rickshaw, Uber/Pathao, Train, Flight, etc.)
- **Google Maps Integration**: Real-time route visualization and distance calculation
- **Receipt Processing**: OCR receipt scanning with duplicate detection
- **Batch Operations**: Create multiple expenses simultaneously
- **Policy Compliance**: Automated policy checking and threshold alerts
- **Real-time Budgeting**: Live budget tracking with overspend notifications
- **Advanced Reporting**: Comprehensive expense analytics and insights
- **Multi-level Approval**: Configurable approval workflows (Standard, High Value, Travel, Auto)
- **10 Predefined Categories**: Transportation, Meals, Office Supplies, Travel, Communication, etc.

#### 🗓️ **Leave Management System** *(Bangladesh Labour Act Compliant)*
- **Leave Types**: Casual (10 days), Sick (14 days), Earned (22 days), Maternity (112 days), Paternity (5 days)
- **Real-time Balance Tracking**: Visual progress bars showing used/available leave days
- **Multi-level Approval Workflow**: Manager → HR → CEO approval chain based on leave type and duration
- **Half-day Leave Support**: Morning/Afternoon half-day options
- **Carry Forward Rules**: Automatic calculation of carried forward leaves
- **Medical Certificate Requirements**: Configurable requirements for sick leave
- **Comprehensive Reporting**: Team calendar, leave analytics, and audit trails
- **Legal Compliance**: Full adherence to Bangladesh Labour Act Sections 103-107

#### 👥 **Administrative Controls**
- **User Management**: Create, edit, and manage user accounts
- **Role-Based Access Control (RBAC)**: Fine-grained permission management
- **Group Management**: Organize users into departments/teams
- **Audit Logging**: Complete activity tracking for compliance

#### 📊 **Reporting & Analytics**
- **User Activity Reports**: Comprehensive usage analytics
- **Leave Analytics**: Utilization patterns and trends
- **Expense Reports**: Financial tracking and budgeting with category breakdowns
- **System Health Monitoring**: Performance and usage metrics

### 📧 **Communication Features**
- **Gmail Integration**: Read, compose, and send emails directly from the app
- **Contact Management**: Google Contacts integration with search functionality
- **Email Notifications**: Real-time notifications for important events
- **Contact Suggestions**: Smart contact suggestions while composing emails

### ☁️ **Cloud Integration**
- **Google Workspace**: Full integration with Gmail, Drive, Calendar, and Contacts
- **Google Drive**: File synchronization and sharing
- **Google Maps API**: Route visualization and distance calculation
- **Real-time Sync**: Automatic synchronization across all connected services

### 🎙️ **Advanced Features**
- **Voice-to-Text**: Speech recognition for quick note taking
- **Real-time Chat**: Built-in messaging system
- **File Attachments**: Support for various file formats
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **PWA Support**: Installable as a mobile app

## 🚀 Recent Updates (August 2025)

### 🆕 **Smart Expense Management System**
- ✅ **Complete Implementation**: AI-powered intelligent expense management
- ✅ **Database Migration**: 8 new tables with comprehensive expense data structure
- ✅ **Google Maps Integration**: Route visualization with distance and cost estimation
- ✅ **OCR Processing**: Receipt scanning and data extraction
- ✅ **Multi-level Approvals**: Configurable workflow engine
- ✅ **Real-time Analytics**: Live expense tracking and budget monitoring
- ✅ **Mobile Optimized**: Full responsive design for mobile expense entry
- ✅ **Batch Operations**: Create multiple expenses in a single transaction

### 🔧 **Critical Bug Fixes**
- ✅ **Database Schema**: Fixed missing `transport_mode` column in intelligent_expenses table
- ✅ **API Dependencies**: Resolved missing database session dependencies
- ✅ **Syntax Errors**: Fixed function definition formatting issues
- ✅ **Authentication**: Corrected user object access patterns
- ✅ **Error Handling**: Improved error reporting and user feedback

### 🆕 **Leave Management System**
- ✅ **Complete Implementation**: Bangladesh Labour Act compliant leave management
- ✅ **Database Migration**: 7 new tables with comprehensive leave data structure
- ✅ **API Endpoints**: Full CRUD operations for leave management
- ✅ **Modern UI**: React-based interface with Material-UI components
- ✅ **Real-time Data**: Live balance updates and application tracking
- ✅ **Workflow Engine**: Multi-level approval system with notifications

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
- **Google Maps JavaScript API**: Interactive mapping and route visualization

### Backend
- **FastAPI**: High-performance Python web framework
- **SQLAlchemy**: ORM with PostgreSQL database
- **Pydantic**: Data validation and serialization
- **Google APIs**: Integration with Google Workspace services
- **JWT Authentication**: Secure token-based authentication
- **Alembic**: Database migration management
- **psycopg2**: PostgreSQL adapter

### Infrastructure
- **Docker**: Containerized deployment
- **PostgreSQL**: Primary database with JSONB support
- **Nginx**: Reverse proxy and static file serving
- **Docker Compose**: Multi-container orchestration
- **Let's Encrypt**: Automatic SSL certificate management
- **Traefik**: Load balancer and reverse proxy

## 📊 Database Schema

### Smart Expense Management Tables
- `expense_categories`: Expense category definitions with color coding
- `intelligent_expenses`: Core expense records with AI categorization
- `expense_approval_workflows`: Multi-level approval configurations
- `expense_approvals`: Approval tracking and history
- `expense_reports`: Generated reports and analytics
- `expense_budgets`: Budget tracking and threshold management
- `expense_analytics`: Performance metrics and insights
- `expense_notifications`: Real-time notification system

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
- `user_sessions`: Authentication and session management

## 🚀 Deployment

### Production Environment
- **URL**: https://infsnk-app-01.tawfiqulbari.work/
- **SSL**: Automatic HTTPS with Let's Encrypt
- **CDN**: Optimized static asset delivery
- **Monitoring**: Health checks and performance monitoring
- **Database**: PostgreSQL with automated backups

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

# Run database migrations
docker exec webapp python3 intelligent_expense_migration.py
docker exec webapp python3 leave_management_migration.py

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

# Database migrations
python apply_migration.py
python leave_management_migration.py
python intelligent_expense_migration.py
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

# Google Maps API
REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key

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
2. Enable required APIs:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google People API (Contacts)
   - Google Maps JavaScript API
   - Places API
3. Configure OAuth consent screen
4. Create OAuth 2.0 credentials
5. Set up authorized redirect URIs

## 📚 API Documentation

### Smart Expense Management Endpoints
- `GET /expenses/categories` - Get all expense categories
- `GET /expenses/my-expenses` - Get user's expenses
- `POST /expenses/create` - Create single expense
- `POST /expenses/create_batch` - Create multiple expenses
- `PUT /expenses/{id}/update` - Update draft expense
- `POST /expenses/{id}/submit` - Submit expense for approval
- `GET /expenses/drafts` - Get draft expenses
- `POST /expenses/generate-report` - Generate expense report

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
- **Rate Limiting**: API request throttling
- **Data Encryption**: Sensitive data encryption

## 🧪 Testing

### API Testing
```bash
# Test expense management endpoints
curl -X GET "https://infsnk-app-01.tawfiqulbari.work/expenses/categories"
curl -X GET "https://infsnk-app-01.tawfiqulbari.work/expenses/my-expenses" -H "Authorization: Bearer YOUR_TOKEN"

# Test leave management endpoints
curl -X GET "https://infsnk-app-01.tawfiqulbari.work/leave/policies"
curl -X GET "https://infsnk-app-01.tawfiqulbari.work/leave/balances" -H "Authorization: Bearer YOUR_TOKEN"

# Test core functionality
curl -X GET "https://infsnk-app-01.tawfiqulbari.work/notes/" -H "Authorization: Bearer YOUR_TOKEN"
```

### Frontend Testing
- Navigate to https://infsnk-app-01.tawfiqulbari.work/
- Test smart expense creation with Google Maps integration
- Verify expense categorization and approval workflows
- Test leave application submission
- Verify leave balance display
- Check email composition and contact suggestions

## 📱 Mobile Responsiveness

The application is fully responsive and optimized for:
- **Desktop**: Full feature set with optimal layout
- **Tablet**: Adapted interface for touch interaction
- **Mobile**: Streamlined mobile-first design with:
  - Speed dial for quick actions
  - Optimized expense entry forms
  - Touch-friendly map interactions
  - Responsive data tables
- **PWA Support**: Installable as a mobile app

## 🔄 Data Migration

### Smart Expense Management Migration
```bash
# Run the intelligent expense migration
python intelligent_expense_migration.py
```

This migration adds:
- 10 predefined expense categories with smart thresholds
- AI categorization system with confidence scoring
- Multi-level approval workflow configurations
- Comprehensive expense analytics and reporting infrastructure
- OCR and receipt processing capabilities

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
- **Backend Architecture**: FastAPI + PostgreSQL + Google APIs
- **Frontend Development**: React + Material-UI + Google Maps
- **DevOps**: Docker + Nginx + Traefik
- **AI Integration**: Intelligent categorization and analytics

## 📞 Support

For support and questions:
- **Email**: baritechsys@gmail.com
- **GitHub Issues**: Create an issue in this repository
- **Documentation**: Check the `/docs` endpoint for API documentation
- **Live Demo**: https://infsnk-app-01.tawfiqulbari.work/

## 🎯 Roadmap

### Upcoming Features
- [ ] Mobile App (React Native)
- [ ] Advanced AI Analytics Dashboard
- [ ] Expense Fraud Detection
- [ ] Integration with Accounting Systems (QuickBooks, Xero)
- [ ] Multi-language Support (Bengali, English)
- [ ] Blockchain-based Audit Trail
- [ ] Advanced OCR with ML Validation
- [ ] Real-time Collaborative Features

### Performance Improvements
- [ ] Redis Caching for Frequent Queries
- [ ] Database Query Optimization
- [ ] CDN Integration for Global Performance
- [ ] Progressive Web App (PWA) Enhancements
- [ ] Offline Functionality
- [ ] GraphQL API Implementation

### AI & Machine Learning
- [ ] Expense Pattern Recognition
- [ ] Fraud Detection Algorithm
- [ ] Predictive Budget Analytics
- [ ] Smart Receipt Categorization
- [ ] Natural Language Expense Entry

---

## 📊 Current System Status

### ✅ Fully Operational Components
- **Smart Expense Management**: Complete with AI categorization
- **Leave Management**: Bangladesh Labour Act compliant
- **Google Workspace Integration**: Gmail, Drive, Calendar, Contacts, Maps
- **User Authentication**: OAuth 2.0 with JWT tokens
- **File Management**: Upload, download, and organization
- **Notes & Calendar**: Full CRUD operations
- **Responsive UI**: Mobile-first design

### 🔧 Recent Bug Fixes (August 2025)
- Fixed database schema issues in intelligent_expenses table
- Resolved API endpoint authentication dependencies
- Corrected syntax errors in function definitions
- Enhanced error handling and user feedback
- Optimized database queries for better performance

**Built with ❤️ by the Infosonik Team**

*Last Updated: August 11, 2025*
