# Production Management Script for Crop Recommendation Platform
# This script provides various management operations

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "backup", "restore", "update", "health")]
    [string]$Action,
    [string]$Service = "all"
)

Write-Host "🔧 Crop Recommendation Platform Management" -ForegroundColor Green

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

# Start services
function Start-Services {
    Write-Status "Starting services..."
    try {
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
        Write-Status "Services started successfully"
    }
    catch {
        Write-Error "Failed to start services"
    }
}

# Stop services
function Stop-Services {
    Write-Status "Stopping services..."
    try {
        docker-compose -f $DOCKER_COMPOSE_FILE down
        Write-Status "Services stopped successfully"
    }
    catch {
        Write-Error "Failed to stop services"
    }
}

# Restart services
function Restart-Services {
    Write-Status "Restarting services..."
    try {
        docker-compose -f $DOCKER_COMPOSE_FILE restart
        Write-Status "Services restarted successfully"
    }
    catch {
        Write-Error "Failed to restart services"
    }
}

# Show service status
function Show-Status {
    Write-Status "Service Status:"
    Write-Host ""
    try {
        docker-compose -f $DOCKER_COMPOSE_FILE ps
    }
    catch {
        Write-Error "Failed to get service status"
    }
    
    Write-Host ""
    Write-Status "Health Check:"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ API is healthy" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "❌ API is not responding" -ForegroundColor Red
    }
}

# Show logs
function Show-Logs {
    Write-Status "Showing logs for $Service..."
    try {
        if ($Service -eq "all") {
            docker-compose -f $DOCKER_COMPOSE_FILE logs -f
        } else {
            docker-compose -f $DOCKER_COMPOSE_FILE logs -f $Service
        }
    }
    catch {
        Write-Error "Failed to show logs"
    }
}

# Backup database
function Backup-Database {
    Write-Status "Creating database backup..."
    try {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupFile = "backup_$timestamp.sql"
        
        docker-compose -f $DOCKER_COMPOSE_FILE exec -T db pg_dump -U postgres crop_recommendation_prod > $backupFile
        
        Write-Status "Database backup created: $backupFile"
    }
    catch {
        Write-Error "Failed to create database backup"
    }
}

# Restore database
function Restore-Database {
    param([string]$BackupFile)
    
    if (-not $BackupFile) {
        Write-Error "Backup file not specified"
        return
    }
    
    if (-not (Test-Path $BackupFile)) {
        Write-Error "Backup file not found: $BackupFile"
        return
    }
    
    Write-Status "Restoring database from $BackupFile..."
    try {
        Get-Content $BackupFile | docker-compose -f $DOCKER_COMPOSE_FILE exec -T db psql -U postgres crop_recommendation_prod
        Write-Status "Database restored successfully"
    }
    catch {
        Write-Error "Failed to restore database"
    }
}

# Update services
function Update-Services {
    Write-Status "Updating services..."
    try {
        # Pull latest images
        docker-compose -f $DOCKER_COMPOSE_FILE pull
        
        # Rebuild and restart
        docker-compose -f $DOCKER_COMPOSE_FILE up -d --build
        
        Write-Status "Services updated successfully"
    }
    catch {
        Write-Error "Failed to update services"
    }
}

# Health check
function Test-Health {
    Write-Status "Performing comprehensive health check..."
    
    $checks = @(
        @{Name="API Health"; Url="http://localhost:5000/api/health"},
        @{Name="Frontend"; Url="http://localhost:3000"},
        @{Name="Grafana"; Url="http://localhost:3001"},
        @{Name="Prometheus"; Url="http://localhost:9090"}
    )
    
    foreach ($check in $checks) {
        try {
            $response = Invoke-WebRequest -Uri $check.Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $($check.Name): Healthy" -ForegroundColor Green
            } else {
                Write-Host "⚠️ $($check.Name): Status $($response.StatusCode)" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "❌ $($check.Name): Not responding" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Status "Container Status:"
    docker-compose -f $DOCKER_COMPOSE_FILE ps
}

# Main function
function Main {
    switch ($Action) {
        "start" { Start-Services }
        "stop" { Stop-Services }
        "restart" { Restart-Services }
        "status" { Show-Status }
        "logs" { Show-Logs }
        "backup" { Backup-Database }
        "restore" { Restore-Database -BackupFile $args[0] }
        "update" { Update-Services }
        "health" { Test-Health }
        default { Write-Error "Invalid action: $Action" }
    }
}

# Run main function
Main

