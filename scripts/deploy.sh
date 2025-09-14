#!/bin/bash

# Crop Recommendation Platform Deployment Script
# This script deploys the application to production

set -e

echo "🚀 Starting Crop Recommendation Platform Deployment..."

# Configuration
APP_NAME="crop-recommendation"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are available"
}

# Check if environment file exists
check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "Environment file $ENV_FILE not found. Creating from template..."
        cp env.example "$ENV_FILE"
        print_warning "Please edit $ENV_FILE with your production values before continuing."
        exit 1
    fi
    print_status "Environment file found"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p uploads
    mkdir -p logs
    mkdir -p ssl
    mkdir -p monitoring
    print_status "Directories created"
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Stop existing containers
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Build and start services
    docker-compose -f "$DOCKER_COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build
    
    print_status "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    timeout 60 bash -c 'until docker-compose -f "$DOCKER_COMPOSE_FILE" exec db pg_isready -U postgres; do sleep 2; done'
    
    # Wait for API
    print_status "Waiting for API..."
    timeout 60 bash -c 'until curl -f http://localhost:5000/api/health; do sleep 2; done'
    
    # Wait for frontend
    print_status "Waiting for frontend..."
    timeout 60 bash -c 'until curl -f http://localhost:3000; do sleep 2; done'
    
    print_status "All services are ready"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec api python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
    print_status "Database migrations completed"
}

# Run tests
run_tests() {
    print_status "Running API tests..."
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec api python test_api_comprehensive.py; then
        print_status "All tests passed"
    else
        print_warning "Some tests failed, but deployment continues"
    fi
}

# Show deployment status
show_status() {
    print_status "Deployment completed successfully!"
    echo ""
    echo "🌐 Application URLs:"
    echo "   Frontend: http://localhost:3000"
    echo "   API: http://localhost:5000"
    echo "   API Health: http://localhost:5000/api/health"
    echo "   Grafana: http://localhost:3001"
    echo "   Prometheus: http://localhost:9090"
    echo ""
    echo "📊 Monitoring:"
    echo "   View logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    echo "   Check status: docker-compose -f $DOCKER_COMPOSE_FILE ps"
    echo ""
    echo "🔧 Management:"
    echo "   Stop services: docker-compose -f $DOCKER_COMPOSE_FILE down"
    echo "   Restart services: docker-compose -f $DOCKER_COMPOSE_FILE restart"
    echo "   Update services: docker-compose -f $DOCKER_COMPOSE_FILE up -d --build"
}

# Main deployment function
main() {
    print_status "Starting deployment process..."
    
    check_docker
    check_env_file
    create_directories
    deploy_services
    wait_for_services
    run_migrations
    run_tests
    show_status
    
    print_status "Deployment completed successfully! 🎉"
}

# Run main function
main "$@"
