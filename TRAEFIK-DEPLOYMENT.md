# Traefik Deployment Guide

This guide explains how to deploy your application with Traefik as a reverse proxy.

## What's New

- **Traefik Reverse Proxy**: Handles SSL/TLS termination and routing
- **Automatic HTTPS**: Let's Encrypt SSL certificates
- **Google Chat Webhook Support**: Dedicated routing for `/webhook/chat`
- **Development Dashboard**: Traefik dashboard available at `http://localhost:8080`

## For Google Chat API Configuration

Use this webhook URL in your Google Chat API configuration:

### Development
```
http://localhost/webhook/chat
```

### Production
```
https://yourdomain.com/webhook/chat
```

## Deployment Options

### Development Deployment

```bash
# Start the development environment with Traefik
docker-compose up -d

# Access your application
# Main app: http://localhost
# Traefik dashboard: http://localhost:8080
```

### Production Deployment

```bash
# Start the production environment with Traefik
docker-compose -f docker-compose.prod.yml up -d

# Access your application
# Main app: https://yourdomain.com
# Google Chat webhook: https://yourdomain.com/webhook/chat
```

## Key Features

### Development Environment
- **HTTP only** (no SSL complexity)
- **Traefik dashboard** enabled at `:8080`
- **Local domain routing** (`localhost`, `127.0.0.1`)
- **Easy debugging** with dashboard

### Production Environment
- **Automatic HTTPS** with Let's Encrypt
- **HTTP to HTTPS redirect**
- **SSL certificate auto-renewal**
- **Production-ready security**
- **Dashboard disabled** for security

## Environment Variables

Make sure your `.env` file contains:

```env
# Database
DB_PASSWORD=your_secure_password

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Production Domain (for SSL)
DOMAIN_NAME=tawfiqulbari.work
ACME_EMAIL=baritechsys@gmail.com
```

## Traefik Routes

### Development Routes
- `http://localhost` → Your main application
- `http://localhost/webhook/chat` → Google Chat webhook
- `http://localhost:8080` → Traefik dashboard

### Production Routes
- `https://infsnk-app-01.tawfiqulbari.work` → Your main application
- `https://infsnk-app-01.tawfiqulbari.work/webhook/chat` → Google Chat webhook
- HTTP requests automatically redirect to HTTPS

## SSL Certificate Management

### Automatic Certificate Generation
- Certificates are automatically requested from Let's Encrypt
- Stored in the `letsencrypt` Docker volume
- Auto-renewed before expiration

### Certificate Storage
- Location: `/letsencrypt/acme.json` inside Traefik container
- Persisted in Docker volume `letsencrypt`

## Troubleshooting

### Check Traefik Logs
```bash
# Development
docker-compose logs traefik

# Production
docker-compose -f docker-compose.prod.yml logs traefik
```

### Check SSL Certificate Status
```bash
# Check certificate details
openssl s_client -connect tawfiqulbari.work:443 -servername tawfiqulbari.work
```

### Verify Webhook Endpoint
```bash
# Test webhook endpoint
curl -X POST https://infsnk-app-01.tawfiqulbari.work/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

## Network Architecture

```
Internet → Traefik (Port 80/443) → App Container (Port 8000)
                                 → Database (Internal Network)
```

## Security Notes

1. **Production**: Dashboard is disabled for security
2. **SSL**: All traffic uses HTTPS in production
3. **Internal Network**: Database is not exposed externally
4. **Docker Socket**: Traefik has read-only access to Docker socket

## Monitoring

### Available Endpoints
- **Health Check**: `https://infsnk-app-01.tawfiqulbari.work/health` (if implemented in your app)
- **Traefik API**: Available in development at `http://localhost:8080/api/rawdata`

### Logs
- Traefik logs: `docker-compose logs traefik`
- Application logs: `docker-compose logs app`
- Database logs: `docker-compose logs db`
