# Horizontal Scaling Script for Crop Recommendation Platform
# This script scales the application horizontally

param(
    [int]$ApiReplicas = 3,
    [int]$FrontendReplicas = 2,
    [string]$Environment = "production"
)

Write-Host "🚀 Scaling Crop Recommendation Platform..." -ForegroundColor Green

$DOCKER_COMPOSE_FILE = "docker-compose.prod.yml"

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

# Check if Docker is running
function Test-Docker {
    try {
        docker --version | Out-Null
        docker-compose --version | Out-Null
        Write-Status "Docker and Docker Compose are available"
        return $true
    }
    catch {
        Write-Error "Docker is not installed or not running."
        return $false
    }
}

# Scale API services
function Scale-Api {
    Write-Status "Scaling API services to $ApiReplicas replicas..."
    
    try {
        docker-compose -f $DOCKER_COMPOSE_FILE up -d --scale api=$ApiReplicas
        Write-Status "API services scaled successfully"
    }
    catch {
        Write-Error "Failed to scale API services"
        return $false
    }
    return $true
}

# Scale frontend services
function Scale-Frontend {
    Write-Status "Scaling frontend services to $FrontendReplicas replicas..."
    
    try {
        docker-compose -f $DOCKER_COMPOSE_FILE up -d --scale frontend=$FrontendReplicas
        Write-Status "Frontend services scaled successfully"
    }
    catch {
        Write-Error "Failed to scale frontend services"
        return $false
    }
    return $true
}

# Update nginx configuration for load balancing
function Update-NginxConfig {
    Write-Status "Updating nginx configuration for load balancing..."
    
    $nginxConfig = @"
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api_1:5000;
        server api_2:5000;
        server api_3:5000;
    }

    upstream frontend {
        server frontend_1:3000;
        server frontend_2:3000;
    }

    # Load balancing configuration
    upstream api_backend {
        least_conn;
        server api_1:5000 weight=1 max_fails=3 fail_timeout=30s;
        server api_2:5000 weight=1 max_fails=3 fail_timeout=30s;
        server api_3:5000 weight=1 max_fails=3 fail_timeout=30s;
    }

    server {
        listen 80;
        server_name localhost;

        # API routes with load balancing
        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
            
            # Health check
            proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
            proxy_connect_timeout 5s;
            proxy_send_timeout 10s;
            proxy_read_timeout 10s;
        }

        # Frontend routes with load balancing
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }
    }
}
"@

    try {
        $nginxConfig | Out-File -FilePath "nginx-scaled.conf" -Encoding UTF8
        Write-Status "Nginx configuration updated for load balancing"
    }
    catch {
        Write-Error "Failed to update nginx configuration"
        return $false
    }
    return $true
}

# Check service health
function Test-ServiceHealth {
    Write-Status "Checking service health..."
    
    $maxRetries = 30
    $retryCount = 0
    
    do {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Status "All services are healthy"
                return $true
            }
        }
        catch {
            # Continue retrying
        }
        
        Start-Sleep -Seconds 2
        $retryCount++
    } while ($retryCount -lt $maxRetries)
    
    Write-Warning "Service health check timeout"
    return $false
}

# Show scaling status
function Show-ScalingStatus {
    Write-Status "Scaling completed successfully!"
    Write-Host ""
    Write-Host "📊 Scaling Summary:" -ForegroundColor Cyan
    Write-Host "   API Replicas: $ApiReplicas" -ForegroundColor White
    Write-Host "   Frontend Replicas: $FrontendReplicas" -ForegroundColor White
    Write-Host ""
    Write-Host "🔧 Management Commands:" -ForegroundColor Cyan
    Write-Host "   View running containers: docker-compose -f $DOCKER_COMPOSE_FILE ps" -ForegroundColor White
    Write-Host "   View logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f" -ForegroundColor White
    Write-Host "   Scale down: docker-compose -f $DOCKER_COMPOSE_FILE up -d --scale api=1" -ForegroundColor White
    Write-Host "   Scale up: docker-compose -f $DOCKER_COMPOSE_FILE up -d --scale api=5" -ForegroundColor White
}

# Main scaling function
function Main {
    Write-Status "Starting scaling process..."
    
    if (-not (Test-Docker)) {
        exit 1
    }
    
    if (Scale-Api) {
        if (Scale-Frontend) {
            Update-NginxConfig
            Test-ServiceHealth
            Show-ScalingStatus
            Write-Status "Scaling completed successfully! 🎉"
        }
    }
}

# Run main function
Main

