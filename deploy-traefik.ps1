# PowerShell deployment script for webapp with Traefik

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("dev", "prod")]
    [string]$Environment = "dev"
)

Write-Host "🚀 Deploying webapp with Traefik..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Please copy .env.example to .env and configure it." -ForegroundColor Yellow
    exit 1
}

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
if ($Environment -eq "prod") {
    docker-compose -f docker-compose.prod.yml down
} else {
    docker-compose down
}

# Build and start containers
Write-Host "🔨 Building and starting containers..." -ForegroundColor Blue
if ($Environment -eq "prod") {
    docker-compose -f docker-compose.prod.yml up -d --build
    Write-Host "✅ Production deployment complete!" -ForegroundColor Green
    Write-Host "🌐 Application: https://yourdomain.com" -ForegroundColor Cyan
    Write-Host "🪝 Google Chat Webhook: https://yourdomain.com/webhook/chat" -ForegroundColor Cyan
} else {
    docker-compose up -d --build
    Write-Host "✅ Development deployment complete!" -ForegroundColor Green
    Write-Host "🌐 Application: http://localhost" -ForegroundColor Cyan
    Write-Host "📊 Traefik Dashboard: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "🪝 Google Chat Webhook: http://localhost/webhook/chat" -ForegroundColor Cyan
}

# Show container status
Write-Host "`n📋 Container Status:" -ForegroundColor Magenta
docker-compose ps

Write-Host "`n🔍 To view logs, run:" -ForegroundColor Gray
Write-Host "docker-compose logs -f" -ForegroundColor Gray
