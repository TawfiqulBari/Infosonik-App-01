# Infosonik App 01 - Notes & Calendar Application

A full-stack web application built with React frontend and FastAPI backend, featuring note-taking, calendar management, and voice-to-text capabilities.

## 🚀 Features

- **📝 Note Management**: Create, store, and manage notes with multi-language support (English/Bengali)
- **📅 Calendar Integration**: Google Calendar event creation and management
- **🎤 Voice-to-Text**: Speech recognition functionality (infrastructure ready)
- **🌐 Multi-language Support**: English and Bengali language support
- **🔐 OAuth Integration**: Google OAuth authentication ready
- **📱 Responsive Design**: Mobile-friendly React interface
- **🐳 Docker Ready**: Containerized deployment with Docker Compose

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
   - Main App: http://localhost:8000
   - API Docs: http://localhost:8000/docs

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

- `POST /notes/` - Create a new note
- `GET /notes/` - List all notes
- `POST /events/` - Create calendar event
- `POST /voice-to-text/` - Convert speech to text

## 🗄️ Database Schema

### Notes Table
```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    content TEXT,
    language VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Events Table
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    google_event_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

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

- [ ] **User Authentication** - Multi-user support
- [ ] **Real-time Collaboration** - WebSocket integration
- [ ] **Mobile App** - React Native version
- [ ] **Advanced Search** - Full-text search capabilities
- [ ] **File Attachments** - Document and image uploads
- [ ] **Export/Import** - Data backup and restore
- [ ] **Notifications** - Email and push notifications
- [ ] **Themes** - Dark mode and customization options

### Technical Improvements

- [ ] **Test Coverage** - Comprehensive test suite
- [ ] **CI/CD Pipeline** - Automated testing and deployment
- [ ] **Kubernetes** - Container orchestration
- [ ] **Microservices** - Service decomposition
- [ ] **GraphQL** - Alternative API interface
- [ ] **WebAssembly** - Performance optimization

---

**Happy Coding! 🚀**
