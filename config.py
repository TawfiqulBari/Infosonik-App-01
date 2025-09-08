import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://infsnk-app-01.tawfiqulbari.work/auth/callback")

# Domain and security settings
ALLOWED_DOMAIN = "infosonik.com"

# Application settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DOMAIN_NAME = os.getenv("DOMAIN_NAME", "localhost")

# Email settings (for future use)
ACME_EMAIL = os.getenv("ACME_EMAIL", "admin@example.com")

# Database URL is handled in database.py
DATABASE_URL = os.getenv("DATABASE_URL")

# Upload settings
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [
    'application/pdf',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'image/jpeg',
    'image/png'
]

# API Settings
API_V1_PREFIX = "/api/v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Health check settings
HEALTH_CHECK_TIMEOUT = 30

# Rate limiting (for future implementation)
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds

# Cache settings (for future implementation)
CACHE_TTL = 300  # 5 minutes
REDIS_URL = os.getenv("REDIS_URL")

# External service URLs
EXTERNAL_TRAEFIK_URL = os.getenv("EXTERNAL_TRAEFIK_URL", "http://traefik:8080")

# Feature flags
ENABLE_GOOGLE_INTEGRATION = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
ENABLE_FILE_UPLOAD = True
ENABLE_BACKUP_RESTORE = True
ENABLE_REPORTING = True
ENABLE_NOTIFICATIONS = True