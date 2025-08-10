# Production Setup Guide

## Environment Variables Security

### Important: `.env.prod` Protection

The `.env.prod` file contains sensitive production credentials and must never be committed to GitHub.

**✅ Current Protection Status:**
- ✅ `.env.prod` is properly ignored by Git
- ✅ File is excluded from repository tracking
- ✅ Backup files are also ignored
- ✅ Template available as `.env.example`

### Environment Variables Checklist

When deploying to production, ensure these variables are properly set in `.env.prod`:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@db:5432/webapp_db
DB_PASSWORD=your_secure_database_password

# Google OAuth Configuration (REQUIRED)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=https://yourdomain.com/auth/callback

# Security
SECRET_KEY=your-very-long-and-secure-jwt-secret-key-here
ENVIRONMENT=production
DEBUG=false

# Domain Configuration
DOMAIN_NAME=yourdomain.com
ACME_EMAIL=your-email@yourdomain.com
```

### Deployment Process

1. **Initial Setup:**
   ```bash
   # Copy template
   cp .env.example .env.prod
   
   # Edit with actual values
   nano .env.prod
   ```

2. **Verify Protection:**
   ```bash
   # Should show .env.prod as ignored
   git status --ignored | grep env
   
   # Should NOT show .env.prod
   git ls-files | grep env
   ```

3. **Deploy:**
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

### Security Best Practices

- ✅ Never commit `.env.prod` to version control
- ✅ Use strong, unique passwords for all services
- ✅ Regularly rotate secrets and API keys
- ✅ Keep backups of environment files in secure location
- ✅ Use environment-specific secrets for different deployments
- ✅ Monitor for accidental exposure in logs

### Backup Strategy

Production environment backups are automatically created with timestamps:
```bash
.env.prod.backup.YYYYMMDD_HHMMSS
```

These backups are also ignored by Git for security.

### Troubleshooting

**If `.env.prod` is accidentally tracked:**
```bash
# Remove from Git tracking but keep local file
git rm --cached .env.prod

# Commit the removal
git commit -m "Remove .env.prod from tracking"

# Verify it's now ignored
git status --ignored | grep env
```

**If environment variables aren't loading:**
1. Check file exists: `ls -la .env.prod`
2. Check Docker Compose configuration
3. Restart containers: `docker compose -f docker-compose.prod.yml restart`
4. Check container logs: `docker logs container_name`

### Environment File Priority

The application loads environment variables in this order:
1. System environment variables (highest priority)
2. `.env.prod` file (production)
3. `.env` file (development)
4. Default values in code (lowest priority)

