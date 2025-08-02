#!/bin/bash

# Deployment script for Notes & Calendar App
# Usage: ./deploy.sh [server_ip] [username]

SERVER_IP=${1:-62.169.16.31}
USERNAME=${2:-root}
APP_NAME="webapp-01"
REMOTE_PATH="/opt/$APP_NAME"

echo "🚀 Starting deployment to $SERVER_IP..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required files exist
print_status "Checking required files..."
required_files=("Dockerfile" "docker-compose.prod.yml" "main.py" "requirements.txt" "package.json")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file $file not found!"
        exit 1
    fi
done

# Create deployment package
print_status "Creating deployment package..."
tar -czf ${APP_NAME}-deploy.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    .

print_status "Deployment package created: ${APP_NAME}-deploy.tar.gz"

# Copy files to server
print_status "Copying files to server $SERVER_IP..."
scp ${APP_NAME}-deploy.tar.gz $USERNAME@$SERVER_IP:/tmp/

# Execute deployment on remote server
print_status "Executing deployment on remote server..."
ssh $USERNAME@$SERVER_IP << EOF
    set -e
    
    echo "🔧 Setting up application directory..."
    sudo mkdir -p $REMOTE_PATH
    cd $REMOTE_PATH
    
    echo "📦 Extracting deployment package..."
    sudo tar -xzf /tmp/${APP_NAME}-deploy.tar.gz
    sudo chown -R $USERNAME:$USERNAME $REMOTE_PATH
    
    echo "🐳 Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USERNAME
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "Installing Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
    
    echo "🔄 Stopping existing containers (if any)..."
    sudo docker-compose -f docker-compose.prod.yml down --remove-orphans || true
    
    echo "🏗️ Building and starting application..."
    sudo docker-compose -f docker-compose.prod.yml up -d --build
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    echo "✅ Checking service status..."
    sudo docker-compose -f docker-compose.prod.yml ps
    
    echo "🌐 Application should be accessible at:"
    echo "   http://$SERVER_IP (Main App)"
    echo "   http://$SERVER_IP/docs (API Documentation)"
    
    echo "🧹 Cleaning up..."
    rm -f /tmp/${APP_NAME}-deploy.tar.gz
    
    echo "🎉 Deployment completed successfully!"
EOF

# Clean up local deployment package
rm -f ${APP_NAME}-deploy.tar.gz

print_status "Deployment script completed!"
print_status "Your application should be accessible at:"
print_status "  🌐 Main App: http://$SERVER_IP"
print_status "  📚 API Docs: http://$SERVER_IP/docs"
