### **Latest Updates (August 2025)**
- **Complete Role-Based Access Control**: Implemented comprehensive RBAC with Admin, HR, Accounts, Sales, and Technical roles
- **Sales Management Suite**: Full MEDDPICC analysis and Sales Funnel tracking system
- **HR & Expense Management**: Leave applications and convenience bill submission/approval workflows
- **Enhanced Google Integrations**: Gmail, Google Drive, and Calendar with advanced sharing capabilities
- **Database Schema Optimization**: Updated database structure with proper relationships and constraints
- **Production-Ready OAuth**: Fixed authentication flow with proper error handling and domain restrictions

# 🏢 Infosonik Systems Limited - Notes & Calendar Platform

![Infosonik Logo](public/infosonik-logo.svg)

**Professional workspace application for Infosonik team collaboration and productivity management.**

A modern, enterprise-grade web application built with React frontend and FastAPI backend, featuring professional branding, Google Workspace integration, secure authentication, and comprehensive productivity tools.

## 🌐 **Live Production Application**

**🚀 Access the live application:** [https://infsnk-app-01.tawfiqulbari.work](https://infsnk-app-01.tawfiqulbari.work)

- **Status:** ✅ Live and running in production
- **Environment:** Production-ready deployment
- **Security:** Restricted to @infosonik.com Google Workspace accounts
- **Server:** Ubuntu 20.04 LTS on dedicated infrastructure

## ✨ **Current Production Features** 

### 🏢 **Enterprise Branding & Design**
- **🎨 Professional Infosonik Systems Limited Branding**: Custom logo, blue gradient theme, and corporate identity
- **🖼️ Custom SVG Logo**: Integrated circuit-pattern logo with company branding
- **🎯 Service Showcase**: IT Solutions, Cloud Services, and Security service chips
- **🌟 Glass-morphism UI**: Modern backdrop blur effects and gradient backgrounds
- **📱 Fully Responsive**: Optimized for desktop, tablet, and mobile devices

### 🔐 **Security & Authentication**
- **🛡️ Domain-Restricted Access**: Limited to @infosonik.com Google Workspace accounts only
- **🔑 Google OAuth Integration**: ✅ **FULLY IMPLEMENTED** - Seamless single sign-on with Google Workspace
- **🔒 HTTPS Deployment**: Secure SSL/TLS encrypted connections via Traefik reverse proxy
- **🎯 Authentication Flow**: Complete OAuth 2.0 implementation with proper redirect handling
- **🌐 Production-Ready**: Live deployment with proper error handling and security

### ✅ **OAuth Implementation Status**
- **🔐 Google OAuth 2.0**: ✅ Successfully implemented and tested
- **🏢 Domain Restriction**: ✅ Limited to @infosonik.com Google Workspace accounts
- **🔄 Authentication Flow**: ✅ Complete redirect flow with token management
- **🎯 User Experience**: ✅ Seamless login experience with proper application landing
- **📱 State Management**: ✅ React context handles authentication state properly
- **🔒 Secure Token Storage**: ✅ JWT tokens stored securely with proper expiration
- **🌐 API Integration**: ✅ All API endpoints secured with authentication middleware

### 💻 **Technical Features**

#### **Core Functionality**
- **📝 Advanced Note Management**: Create, edit, and organize notes with multi-language support (English/Bengali)
- **📅 Calendar Integration**: Full Google Calendar sync with event creation, editing, and sharing
- **🎤 Voice-to-Text**: Speech recognition functionality for hands-free note taking
- **🌐 Multi-language Support**: Comprehensive English and Bengali language support
- **📁 File Management**: Complete Google Drive integration with upload, download, and sharing
- **🌙 Theme Support**: Professional light/dark mode with customizable themes
- **💾 Data Management**: Comprehensive backup, restore, and export functionality

#### **Enterprise Features**
- **👥 Role-Based Access Control (RBAC)**: Granular permission system with 5 distinct roles:
  - **🛡️ Admin**: Full system access, user management, and configuration
  - **👤 HR**: Leave management, employee records, and approval workflows
  - **💰 Accounts**: Expense management, bill approvals, and financial oversight
  - **💼 Sales**: MEDDPICC analysis, sales funnel tracking, and opportunity management
  - **🔧 Technical**: System maintenance, technical documentation, and infrastructure

#### **Sales Management Suite**
- **📊 MEDDPICC Analysis**: Complete sales methodology tracking with:
  - Metrics, Economic Buyer, Decision Criteria, Decision Process
  - Paper Process, Identify Pain, Champion, Competition analysis
- **🏆 Sales Funnel Management**: Opportunity pipeline with stages, probabilities, and forecasting
- **💡 Client Management**: Comprehensive client and opportunity tracking

#### **HR & Administrative Tools**
- **📋 Leave Management System**: 
  - Employee leave application submission
  - Multi-level approval workflows
  - Leave balance tracking and reporting
- **💳 Expense Management**: 
  - Convenience bill submission with receipt upload
  - Approval workflows with comments and tracking
  - Weekly expense reporting and analytics
- **📊 Admin Dashboard**: Real-time system statistics and user activity monitoring
- **👥 User Management**: Role assignment, permission management, and user lifecycle

#### **Google Workspace Integration**
- **📧 Gmail Integration**: 
  - Read, send, and reply to emails directly within the platform
  - Email threading and conversation management
  - Attachment handling and inline media support
- **💾 Google Drive**: 
  - File browser with folder navigation
  - Upload, download, and organize documents
  - Advanced sharing with domain-wide permissions
  - File preview and collaborative editing
- **📅 Google Calendar**: 
  - Event creation, editing, and deletion
  - Calendar sharing and public event management
  - Meeting invitation and RSVP handling

#### **Technical Infrastructure**
- **🐳 Containerization**: Full Docker deployment with multi-stage builds
- **🗄️ Database**: PostgreSQL 15 with optimized schema and relationships
- **🔐 Security**: JWT authentication, OAuth 2.0, and domain restrictions
- **⚡ Performance**: Optimized queries, caching, and connection pooling
- **🌐 Scalability**: Production-ready with horizontal scaling capabilities

## 📊 **Current Deployment Status**

### 🌐 **Production Environment Details**
- **🚀 Deployment Date**: August 3, 2025 (Latest Update)
- **⚡ Server Status**: ✅ Active and operational
- **🔄 Container Status**: 3/3 containers running (webapp + database + traefik)
- **🌐 HTTPS**: Fully configured with automatic SSL certificates
- **🗄️ Database**: PostgreSQL 15 with persistent volume storage
- **🔧 Restart Policy**: Configured for automatic container restart
- **🔐 OAuth Integration**: ✅ Fully functional Google Workspace authentication
- **🎯 OAuth Redirect**: `https://infsnk-app-01.tawfiqulbari.work/auth/callback`

### 🏗️ **Infrastructure Specifications**
- **🖥️ Server**: Ubuntu 20.04 LTS
- **🐳 Docker**: Multi-stage containerized deployment
- **🔗 Networking**: Isolated app network with service discovery
- **💾 Storage**: Persistent PostgreSQL data volumes
- **🛡️ Security**: HTTPS with Traefik reverse proxy, domain-restricted authentication
- **📈 Scalability**: Ready for horizontal scaling and load balancing
- **🌐 Domain**: `infsnk-app-01.tawfiqulbari.work` with automatic SSL certificate management

### 🎨 **UI/UX Enhancements**
- **✨ Professional Login Page**: Infosonik Systems Limited branded interface
- **🖼️ Custom Logo Integration**: SVG logo with circuit pattern design
- **🎨 Blue Gradient Theme**: Corporate blue color scheme throughout
- **🔧 Service Badges**: IT Solutions, Cloud Services, and Security indicators
- **📱 Responsive Design**: Optimized for all device sizes
- **🌟 Glass Morphism**: Modern backdrop blur and transparency effects

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern React with hooks
- **Axios** - HTTP client for API calls
- **JavaScript ES6+** - Modern JavaScript features

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Python SQL toolkit and ORM
- **PostgreSQL** - Robust relational database
- **Pydantic** - Data validation using Python type hints
- **Uvicorn** - ASGI server for FastAPI

### Integrations
- **Google Calendar API** - Calendar event management
- **Google Speech Recognition** - Voice-to-text conversion
- **Google OAuth 2.0** - Authentication and authorization

### DevOps
- **Docker** - Containerization platform
- **Docker Compose** - Multi-container orchestration
- **Multi-stage builds** - Optimized container images

## 📁 Project Structure

```
Infosonik-App-01/
├── src/                          # React frontend source
│   ├── App.js                    # Main React component
│   └── index.js                  # React entry point
├── public/                       # React public assets
│   └── index.html               # HTML template
├── migrations/                   # Database migrations
│   └── 001_initial.sql          # Initial database schema
├── main.py                      # FastAPI backend application
├── requirements.txt             # Python dependencies
├── package.json                 # Node.js dependencies
├── Dockerfile                   # Multi-stage container build
├── docker-compose.yml          # Development environment
├── docker-compose.prod.yml     # Production environment
├── .env.prod                   # Production environment variables
├── deploy.ps1                  # Windows deployment script
├── deploy.sh                   # Unix deployment script
├── DEPLOYMENT.md               # Detailed deployment guide
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **PostgreSQL** 15+ (for local development)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/TawfiqulBari/Infosonik-App-01.git
   cd Infosonik-App-01
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.prod .env
   # Edit .env with your configuration
   ```

5. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

6. **Access the application**
   - Main App: http://localhost:8080
   - API Docs: http://localhost:8080/docs

## 🐳 Docker Deployment

### Development Environment

```bash
docker-compose up -d
```

### Production Environment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Automated Deployment Scripts

#### Windows (PowerShell)
```powershell
.\deploy.ps1 -ServerIP your-server-ip -Username your-username
```

#### Unix/Linux
```bash
chmod +x deploy.sh
./deploy.sh your-server-ip your-username
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/notesapp
DB_PASSWORD=your_secure_password

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Optional Configuration
ENVIRONMENT=production
DEBUG=false
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API and Google OAuth2 API
4. Create OAuth 2.0 credentials
5. Add your domain to authorized origins
6. Update `.env` with your credentials

## 📚 API Documentation

Once the application is running, visit:
- **Swagger UI**: `http://your-domain/docs`
- **ReDoc**: `http://your-domain/redoc`

### Main Endpoints

#### **Core Functionality**
- `POST /notes/` - Create a new note
- `GET /notes/` - List all notes
- `POST /events/` - Create calendar event
- `POST /voice-to-text/` - Convert speech to text

#### **Sales Management** (Role-based access)
- `POST /sales/meddpicc` - Create MEDDPICC analysis
- `GET /sales/meddpicc` - List MEDDPICC records
- `POST /sales/funnel` - Create sales funnel entry
- `GET /sales/funnel` - List sales funnel records

#### **Admin Management** (Admin only)
- `GET /admin/users` - List all users
- `GET /admin/stats` - Get system statistics
- `POST /admin/roles` - Create new role
- `GET /admin/roles` - List all roles
- `PUT /admin/users/{user_id}/role` - Assign role to user

#### **Leave Management**
- `POST /leave/apply` - Submit leave application
- `GET /leave/my-applications` - Get user's leave applications
- `GET /leave/pending` - Get pending leave applications (Admin/HR)
- `POST /leave/{application_id}/approve` - Approve/reject leave (Admin/HR)

#### **Expense Management**
- `POST /bills/submit` - Submit convenience bill
- `GET /bills/my-bills` - Get user's submitted bills
- `GET /bills/pending` - Get pending bills (Admin/Accounts)
- `POST /bills/{bill_id}/approve` - Approve/reject bill (Admin/Accounts)

#### **Google Integrations**
- `GET /gmail/messages` - Get Gmail messages
- `POST /gmail/send` - Send email
- `GET /drive/files` - List Google Drive files
- `POST /drive/files/{file_id}/share` - Share Drive file

## 🗄️ Database Schema

The application uses a comprehensive PostgreSQL database schema with the following key tables:

### **Core Tables**

#### **Users & Authentication**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    profile_picture VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    role_id INTEGER REFERENCES roles (id),
    preferences TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Content Management**
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    title VARCHAR(255),
    content TEXT,
    language VARCHAR(10),
    theme VARCHAR(255) DEFAULT 'light',
    attachments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    title VARCHAR(255),
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    google_event_id VARCHAR(255),
    attachments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Enterprise Features**

#### **Sales Management**
```sql
CREATE TABLE meddpicc (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    client_name VARCHAR(255),
    opportunity_name VARCHAR(255),
    metrics TEXT,
    economic_buyer TEXT,
    decision_criteria TEXT,
    decision_process TEXT,
    paper_process TEXT,
    identify_pain TEXT,
    champion TEXT,
    competition TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales_funnel (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    opportunity_name VARCHAR(255),
    client_name VARCHAR(255),
    stage VARCHAR(255),
    probability INTEGER,
    amount INTEGER,
    closing_date TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **HR & Administrative**
```sql
CREATE TABLE leave_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    leave_type VARCHAR(255),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    days_requested INTEGER,
    reason TEXT,
    status VARCHAR(255) DEFAULT 'pending',
    approved_by INTEGER,
    approval_date TIMESTAMP,
    approval_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE convenience_bills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    week_start_date TIMESTAMP,
    week_end_date TIMESTAMP,
    total_amount INTEGER,
    description TEXT,
    receipt_file_id INTEGER,
    status VARCHAR(255) DEFAULT 'pending',
    approved_by INTEGER,
    approval_date TIMESTAMP,
    approval_comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Supporting Tables**

- **file_attachments**: File management and Google Drive integration
- **user_sessions**: OAuth token management and session handling
- **user_groups**: Team and department organization
- **group_memberships**: User-to-group relationship management

For the complete schema, see `migrations/001_initial.sql`.

## 🚀 Production Deployment

### Server Requirements

- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 20GB minimum
- **Network**: Port 80/443 open for web traffic

### Deployment Steps

1. **Clone repository on server**
   ```bash
   git clone https://github.com/TawfiqulBari/Infosonik-App-01.git
   cd Infosonik-App-01
   ```

2. **Configure production environment**
   ```bash
   cp .env.prod .env
   # Edit .env with production values
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

4. **Verify deployment**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   curl http://localhost
   ```

### SSL/TLS Setup (Recommended)

For production, set up SSL/TLS certificates:

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Configure reverse proxy** (Nginx recommended)
3. **Obtain SSL certificate**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## 🔧 Development

### Adding New Features

1. **Backend (FastAPI)**
   - Add new endpoints in `main.py`
   - Create new database models
   - Update Pydantic schemas

2. **Frontend (React)**
   - Add new components in `src/`
   - Update `App.js` for routing
   - Install new dependencies with npm

3. **Database**
   - Create migration files in `migrations/`
   - Update SQLAlchemy models

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🐛 Troubleshooting

### Common Issues

1. **White screen on frontend**
   - Check if static files are being served correctly
   - Verify React build was successful
   - Check browser console for JavaScript errors

2. **Database connection errors**
   - Verify PostgreSQL is running
   - Check environment variables
   - Ensure network connectivity between containers

3. **Port conflicts**
   - Change port mappings in docker-compose files
   - Check which services are using ports 80/8080

4. **Build failures**
   - Clear Docker cache: `docker system prune -a`
   - Check Dockerfile syntax
   - Verify all dependencies are available

### Logs and Debugging

```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f db

# Access container shell
docker exec -it infosonik-app-01-app-1 /bin/bash
```

## 📈 Performance Optimization

### Production Optimizations

1. **Enable gzip compression**
2. **Use CDN for static assets**
3. **Implement database connection pooling**
4. **Add Redis for caching**
5. **Set up load balancing**

### Monitoring

1. **Application monitoring** with tools like Prometheus
2. **Log aggregation** with ELK stack
3. **Database monitoring** with pgAdmin
4. **Container monitoring** with cAdvisor

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ features and consistent formatting
- **Documentation**: Update README and code comments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Tawfiqul Bari** - *Initial work* - [@TawfiqulBari](https://github.com/TawfiqulBari)

## 🙏 Acknowledgments

- **FastAPI** team for the excellent web framework
- **React** team for the powerful frontend library
- **Docker** for containerization technology
- **Google** for Calendar and Speech APIs
- **PostgreSQL** community for the robust database

## 📞 Support

For support and questions:

- Create an issue on GitHub
- Check the [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions
- Review the API documentation at `/docs` endpoint

## 🗺️ Roadmap

### Upcoming Features

- [ ] **Real-time Collaboration** - WebSocket integration for live editing
- [ ] **Mobile App** - React Native version for iOS/Android
- [ ] **Advanced Search** - Full-text search with Elasticsearch
- [ ] **Notification System** - Real-time push notifications and email alerts
- [ ] **Advanced Analytics** - Business intelligence dashboards and reporting
- [ ] **Chat Integration** - Google Chat API integration for team communication
- [ ] **Document Templates** - Pre-built templates for common business documents
- [ ] **Workflow Automation** - Custom business process automation
- [ ] **Multi-tenant Support** - Support for multiple organizations
- [ ] **API Gateway** - Rate limiting and API management

### Technical Improvements

- [ ] **Test Coverage** - Comprehensive test suite
- [ ] **CI/CD Pipeline** - Automated testing and deployment
- [ ] **Kubernetes** - Container orchestration
- [ ] **Microservices** - Service decomposition
- [ ] **GraphQL** - Alternative API interface
- [ ] **WebAssembly** - Performance optimization

---

**Happy Coding! 🚀**
## Recent Changes\n\n- Integrated enhanced calendar functionality with month view and hourly day view side by side.\n- Clickable event cards displaying full details in modals.\n- Support for joining events, sharing, and inviting participants.\n- Environment files (.env, .env.prod) added to .gitignore for security purposes.

## 🎉 Latest Calendar Enhancements (August 2025)

### Enhanced Calendar Interface
- **Dual View Layout**: Month view and detailed day view side by side with optimal spacing
- **Interactive Event Cards**: Clickable cards with professional styling and hover effects
- **Day View Features**: 24-hour breakdown with hourly time slots showing scheduled events
- **View Toggle**: Switch between month-focused and day-focused layout modes

### Event Management Features
- **Click for Details**: Event cards open comprehensive modal dialogs with full information
- **Join Events**: Automatic detection and launching of meeting links (Google Meet, Zoom, Teams)
- **Share Events**: Built-in sharing functionality for app-created events
- **Invite Participants**: Send invitations to team members for events
- **Copy Event Links**: Generate and copy shareable URLs for events

### Google Calendar Integration
- **Real-time Sync**: Pulls events from Google Calendar with proper authentication
- **Visual Distinction**: Google Calendar events marked with special badges and styling
- **Meeting Link Detection**: Automatically extracts and provides access to meeting links
- **Dual Event Support**: Seamlessly handles both local and Google Calendar events

### UI/UX Improvements
- **Professional Styling**: Material-UI design with consistent theme and colors
- **Fixed Calendar Colors**: Resolved visibility issues with proper contrast and theme support
- **Responsive Design**: Optimized for all screen sizes and devices
- **Enhanced Navigation**: Intuitive date selection and event browsing
- **Loading States**: Professional loading indicators and error handling

### Technical Enhancements
- **OAuth Fixed**: Resolved authentication issues with proper environment variable handling
- **Backend Endpoints**: Added `/events/{id}/invite` and improved sharing functionality
- **Error Handling**: Comprehensive error management with user-friendly messages
- **Performance**: Optimized event filtering and rendering for better performance

### Security Updates
- **Environment Protection**: Added .env and .env.prod to .gitignore for security
- **Secure Deployment**: Production environment variables properly configured
- **OAuth Security**: Proper token handling and refresh mechanisms

