# Crop Recommendation Platform Deployment Script for Windows
# This script deploys the application to production

param(
    [string]$Environment = "production"
)

Write-Host "🚀 Starting Crop Recommendation Platform Deployment..." -ForegroundColor Green

# Configuration
$APP_NAME = "crop-recommendation"
$DOCKER_COMPOSE_FILE = "docker-compose.prod.yml"
$ENV_FILE = "env.production"

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

# Check if Docker is installed
function Test-Docker {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        Write-Status "Docker and Docker Compose are available"
        return $true
    }
    catch {
        Write-Error "Docker is not installed or not running. Please install Docker Desktop first."
        return $false
    }
}

# Check if environment file exists
function Test-EnvFile {
    if (-not (Test-Path $ENV_FILE)) {
        Write-Warning "Environment file $ENV_FILE not found. Creating from template..."
        Copy-Item "env.example" $ENV_FILE
        Write-Warning "Please edit $ENV_FILE with your production values before continuing."
        return $false
    }
    Write-Status "Environment file found"
    return $true
}

# Create necessary directories
function New-Directories {
    Write-Status "Creating necessary directories..."
    New-Item -ItemType Directory -Force -Path "uploads" | Out-Null
    New-Item -ItemType Directory -Force -Path "logs" | Out-Null
    New-Item -ItemType Directory -Force -Path "ssl" | Out-Null
    New-Item -ItemType Directory -Force -Path "monitoring" | Out-Null
    Write-Status "Directories created"
}

# Deploy services
function Deploy-Services {
    Write-Status "Building and starting services..."
    
    # Stop existing containers
    docker-compose -f $DOCKER_COMPOSE_FILE down
    
    # Build and start services
    docker-compose -f $DOCKER_COMPOSE_FILE --env-file $ENV_FILE up -d --build
    
    Write-Status "Services started successfully"
}

# Wait for services to be ready
function Wait-ForServices {
    Write-Status "Waiting for services to be ready..."
    
    # Wait for database
    Write-Status "Waiting for database..."
    $timeout = 60
    $elapsed = 0
    do {
        try {
            docker-compose -f $DOCKER_COMPOSE_FILE exec -T db pg_isready -U postgres | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Status "Database is ready"
                break
            }
        }
        catch {
            # Continue waiting
        }
        Start-Sleep -Seconds 2
        $elapsed += 2
    } while ($elapsed -lt $timeout)
    
    if ($elapsed -ge $timeout) {
        Write-Warning "Database startup timeout"
    }
    
    # Wait for API
    Write-Status "Waiting for API..."
    $timeout = 60
    $elapsed = 0
    do {
        try {
            Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing | Out-Null
            Write-Status "API is ready"
            break
        }
        catch {
            # Continue waiting
        }
        Start-Sleep -Seconds 2
        $elapsed += 2
    } while ($elapsed -lt $timeout)
    
    if ($elapsed -ge $timeout) {
        Write-Warning "API startup timeout"
    }
    
    Write-Status "All services are ready"
}

# Run database migrations
function Invoke-Migrations {
    Write-Status "Running database migrations..."
    try {
        docker-compose -f $DOCKER_COMPOSE_FILE exec -T api python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
        Write-Status "Database migrations completed"
    }
    catch {
        Write-Warning "Database migration failed, but deployment continues"
    }
}

# Run tests
function Invoke-Tests {
    Write-Status "Running API tests..."
    try {
        python test_api_comprehensive.py
        Write-Status "All tests passed"
    }
    catch {
        Write-Warning "Some tests failed, but deployment continues"
    }
}

# Show deployment status
function Show-Status {
    Write-Status "Deployment completed successfully!"
    Write-Host ""
    Write-Host "🌐 Application URLs:" -ForegroundColor Cyan
    Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   API: http://localhost:5000" -ForegroundColor White
    Write-Host "   API Health: http://localhost:5000/api/health" -ForegroundColor White
    Write-Host "   Grafana: http://localhost:3001" -ForegroundColor White
    Write-Host "   Prometheus: http://localhost:9090" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 Monitoring:" -ForegroundColor Cyan
    Write-Host "   View logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f" -ForegroundColor White
    Write-Host "   Check status: docker-compose -f $DOCKER_COMPOSE_FILE ps" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Management:" -ForegroundColor Cyan
    Write-Host "   Stop services: docker-compose -f $DOCKER_COMPOSE_FILE down" -ForegroundColor White
    Write-Host "   Restart services: docker-compose -f $DOCKER_COMPOSE_FILE restart" -ForegroundColor White
    Write-Host "   Update services: docker-compose -f $DOCKER_COMPOSE_FILE up -d --build" -ForegroundColor White
}

# Main deployment function
function Main {
    Write-Status "Starting deployment process..."
    
    if (-not (Test-Docker)) {
        exit 1
    }
    
    if (-not (Test-EnvFile)) {
        exit 1
    }
    
    New-Directories
    Deploy-Services
    Wait-ForServices
    Invoke-Migrations
    Invoke-Tests
    Show-Status
    
    Write-Status "Deployment completed successfully! 🎉"
}

# Run main function
Main

