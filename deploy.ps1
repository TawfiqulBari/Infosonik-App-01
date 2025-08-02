# PowerShell Deployment Script for Notes & Calendar App
# Usage: .\deploy.ps1 -ServerIP 62.169.16.31 -Username root

param(
    [string]$ServerIP = "62.169.16.31",
    [string]$Username = "root",
    [string]$AppName = "webapp-01",
    [string]$RemotePath = "/opt/webapp-01"
)

Write-Host "🚀 Starting deployment to $ServerIP..." -ForegroundColor Green

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if required files exist
Write-Status "Checking required files..."
$requiredFiles = @("Dockerfile", "docker-compose.prod.yml", "main.py", "requirements.txt", "package.json")
foreach ($file in $requiredFiles) {
    if (!(Test-Path $file)) {
        Write-Error "Required file $file not found!"
        exit 1
    }
}

# Check if WSL is available for tar command
$tarAvailable = $false
try {
    $null = Get-Command tar -ErrorAction Stop
    $tarAvailable = $true
} catch {
    Write-Warning "tar command not found. Checking for WSL..."
    try {
        $null = wsl --version
        $tarAvailable = $true
        Write-Status "WSL found, will use WSL tar command"
    } catch {
        Write-Error "Neither tar nor WSL found. Please install WSL or use a different deployment method."
        exit 1
    }
}

# Create deployment package
Write-Status "Creating deployment package..."
$excludeItems = @(".git", "node_modules", "__pycache__", "*.pyc", ".env")
$tempFile = "${AppName}-deploy.tar.gz"

if ($tarAvailable) {
    if (Get-Command tar -ErrorAction SilentlyContinue) {
        tar -czf $tempFile --exclude=".git" --exclude="node_modules" --exclude="__pycache__" --exclude="*.pyc" --exclude=".env" .
    } else {
        wsl tar -czf $tempFile --exclude=".git" --exclude="node_modules" --exclude="__pycache__" --exclude="*.pyc" --exclude=".env" .
    }
} else {
    Write-Error "Cannot create tar.gz file. Please install WSL or 7-Zip."
    exit 1
}

Write-Status "Deployment package created: $tempFile"

# Check if SSH client is available
if (!(Get-Command ssh -ErrorAction SilentlyContinue)) {
    Write-Error "SSH client not found. Please install OpenSSH or use PuTTY."
    exit 1
}

# Copy files to server
Write-Status "Copying files to server $ServerIP..."
try {
    scp $tempFile "${Username}@${ServerIP}:/tmp/"
    if ($LASTEXITCODE -ne 0) {
        throw "SCP command failed"
    }
} catch {
    Write-Error "Failed to copy files to server. Please check your SSH connection and credentials."
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    exit 1
}

# Execute deployment on remote server
Write-Status "Executing deployment on remote server..."
$deploymentScript = @"
set -e

echo "🔧 Setting up application directory..."
sudo mkdir -p $RemotePath
cd $RemotePath

echo "📦 Extracting deployment package..."
sudo tar -xzf /tmp/${AppName}-deploy.tar.gz
sudo chown -R ${Username}:${Username} $RemotePath

echo "🐳 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $Username
    echo "Please log out and log back in for Docker group membership to take effect."
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-`$(uname -s)-`$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

echo "🔄 Stopping existing containers (if any)..."
sudo docker-compose -f docker-compose.prod.yml down --remove-orphans || true

echo "🏗️ Building and starting application..."
sudo docker-compose -f docker-compose.prod.yml up -d --build

echo "⏳ Waiting for services to start..."
sleep 15

echo "✅ Checking service status..."
sudo docker-compose -f docker-compose.prod.yml ps

echo "🔍 Checking if application is responding..."
sleep 5
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Application is responding successfully!"
else
    echo "⚠️ Application may still be starting up..."
fi

echo "🌐 Application should be accessible at:"
echo "   http://$ServerIP (Main App)"
echo "   http://$ServerIP/docs (API Documentation)"

echo "🧹 Cleaning up..."
rm -f /tmp/${AppName}-deploy.tar.gz

echo "🎉 Deployment completed successfully!"
"@

try {
    ssh "${Username}@${ServerIP}" $deploymentScript
    if ($LASTEXITCODE -ne 0) {
        throw "SSH deployment command failed"
    }
} catch {
    Write-Error "Failed to execute deployment on remote server."
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    exit 1
}

# Clean up local deployment package
Remove-Item $tempFile -ErrorAction SilentlyContinue

Write-Status "Deployment script completed!"
Write-Host ""
Write-Host "🎉 Your application should now be accessible at:" -ForegroundColor Green
Write-Host "  🌐 Main App: http://$ServerIP" -ForegroundColor Cyan
Write-Host "  📚 API Docs: http://$ServerIP/docs" -ForegroundColor Cyan
Write-Host "  🔄 Health Check: http://$ServerIP/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test the application in your browser"
Write-Host "  2. Update the .env.prod file with your actual Google OAuth credentials"
Write-Host "  3. Consider setting up SSL/TLS for production use"
Write-Host "  4. Set up monitoring and backup solutions"
