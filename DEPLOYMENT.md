# Deployment Guide for Notes & Calendar App

## Overview
This guide explains how to deploy the Notes & Calendar application to a remote Docker environment at `62.169.16.31`.

## Prerequisites

### On Your Local Machine (Windows)
- PowerShell 5.1 or later
- SSH client (OpenSSH or PuTTY)
- WSL (Windows Subsystem for Linux) for tar command

### On Remote Server (62.169.16.31)
- Ubuntu/Debian Linux
- SSH access with sudo privileges
- Internet connection for downloading Docker

## Quick Deployment

### Option 1: Using PowerShell Script (Recommended for Windows)

1. **Open PowerShell as Administrator** in the project directory
2. **Run the deployment script:**
   ```powershell
   .\deploy.ps1 -ServerIP 62.169.16.31 -Username root
   ```

### Option 2: Using Bash Script (If you have WSL or Git Bash)

1. **Make the script executable:**
   ```bash
   chmod +x deploy.sh
   ```

2. **Run the deployment:**
   ```bash
   ./deploy.sh 62.169.16.31 root
   ```

## Manual Deployment Steps

If the automated scripts don't work, follow these manual steps:

### 1. Create Deployment Package
```powershell
# Create tar.gz file (using WSL)
wsl tar -czf webapp-01-deploy.tar.gz --exclude=".git" --exclude="node_modules" --exclude="__pycache__" --exclude="*.pyc" --exclude=".env" .
```

### 2. Copy to Server
```powershell
scp webapp-01-deploy.tar.gz root@62.169.16.31:/tmp/
```

### 3. Deploy on Server
```bash
# SSH into the server
ssh root@62.169.16.31

# Create application directory
sudo mkdir -p /opt/webapp-01
cd /opt/webapp-01

# Extract files
sudo tar -xzf /tmp/webapp-01-deploy.tar.gz
sudo chown -R root:root /opt/webapp-01

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Deploy the application
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

## Configuration

### Environment Variables
Edit `.env.prod` file with your production settings:

```bash
# Production Environment Variables
DB_PASSWORD=your_secure_database_password
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### Production Features
- **Automatic restart**: Containers restart unless stopped manually
- **Port 80**: Application accessible on standard HTTP port
- **Persistent data**: Database data is stored in Docker volumes
- **Security**: Uses secure database password

## Access Points

After successful deployment:

- **Main Application**: http://62.169.16.31
- **API Documentation**: http://62.169.16.31/docs
- **Interactive API**: http://62.169.16.31/redoc

## Monitoring and Maintenance

### Check Status
```bash
ssh root@62.169.16.31
cd /opt/webapp-01
sudo docker-compose -f docker-compose.prod.yml ps
```

### View Logs
```bash
sudo docker-compose -f docker-compose.prod.yml logs -f
```

### Update Application
1. Re-run the deployment script
2. Or manually update and rebuild:
   ```bash
   sudo docker-compose -f docker-compose.prod.yml down
   sudo docker-compose -f docker-compose.prod.yml up -d --build
   ```

### Backup Database
```bash
sudo docker-compose -f docker-compose.prod.yml exec db pg_dump -U user notesapp > backup.sql
```

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   - Verify server IP and credentials
   - Check if SSH service is running on the server

2. **Docker Installation Failed**
   - Ensure server has internet connectivity
   - Check if user has sudo privileges

3. **Application Not Accessible**
   - Check if containers are running: `sudo docker-compose ps`
   - Verify firewall settings (port 80 should be open)
   - Check container logs: `sudo docker-compose logs`

4. **Database Connection Issues**
   - Ensure database container is healthy
   - Check environment variables
   - Verify network connectivity between containers

### Port Configuration
If port 80 is already in use, modify `docker-compose.prod.yml`:
```yaml
ports:
  - "8080:8000"  # Change to available port
```

## Security Recommendations

1. **Use HTTPS**: Set up SSL/TLS certificates
2. **Firewall**: Configure firewall rules
3. **Updates**: Keep Docker and system updated
4. **Backup**: Regular database backups
5. **Monitoring**: Set up application monitoring
6. **Secrets**: Use Docker secrets for sensitive data

## Support

If you encounter issues during deployment:
1. Check the deployment logs
2. Verify all prerequisites are met
3. Test SSH connectivity manually
4. Check server resources (disk space, memory)

## Files Included in Deployment

- `Dockerfile` - Container build configuration
- `docker-compose.prod.yml` - Production orchestration
- `.env.prod` - Production environment variables
- `main.py` - FastAPI backend application
- `requirements.txt` - Python dependencies
- `package.json` - Node.js dependencies
- `src/` - React frontend source
- `public/` - React public assets
- `migrations/` - Database migrations
