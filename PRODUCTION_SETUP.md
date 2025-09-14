# 🚀 Production Setup Guide - Crop Recommendation Platform

## 📋 Prerequisites

### 1. Install Docker Desktop
1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Install and start Docker Desktop
3. Verify installation: `docker --version`

### 2. Install Node.js (for frontend development)
1. Download Node.js from [nodejs.org](https://nodejs.org/)
2. Install Node.js (LTS version recommended)
3. Verify installation: `node --version`

## 🚀 Quick Deployment

### Option 1: Docker Compose (Recommended)
```powershell
# 1. Navigate to project directory
cd "D:\deep ai farm"

# 2. Deploy with Docker Compose
powershell -ExecutionPolicy Bypass -File scripts\deploy.ps1

# 3. Check status
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 -Action status
```

### Option 2: Manual Setup
```powershell
# 1. Start services
docker-compose -f docker-compose.prod.yml up -d

# 2. Check logs
docker-compose -f docker-compose.prod.yml logs -f

# 3. Run tests
python test_api_comprehensive.py
```

## 🔧 Configuration

### 1. Environment Variables
Edit `env.production` file with your settings:

```env
# Database
POSTGRES_PASSWORD=YourSecurePassword123!

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-production-key
JWT_SECRET_KEY=your-jwt-secret-production-key

# External APIs (Optional)
OPENWEATHER_API_KEY=your_openweather_key
GOOGLE_TRANSLATE_API_KEY=your_google_translate_key
```

### 2. External API Keys
Follow the guide in `API_KEYS_SETUP.md` to configure:
- Weather data (OpenWeatherMap)
- Translation (Google Translate)
- Market data (Agricultural APIs)
- Disease detection (Plant APIs)

## 📊 Monitoring Setup

### 1. Access Monitoring Dashboards
- **Grafana**: http://localhost:3001 (admin/admin123!)
- **Prometheus**: http://localhost:9090
- **API Health**: http://localhost:5000/api/health

### 2. Import Grafana Dashboard
1. Open Grafana at http://localhost:3001
2. Login with admin/admin123!
3. Import dashboard from `monitoring/grafana-dashboard.json`

## 🔄 Management Commands

### Service Management
```powershell
# Start services
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 -Action start

# Stop services
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 -Action stop

# Restart services
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 -Action restart

# Check status
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 -Action status

# View logs
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 -Action logs

# Health check
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 -Action health
```

### Scaling
```powershell
# Scale to 3 API instances
powershell -ExecutionPolicy Bypass -File scripts\scale.ps1 -ApiReplicas 3

# Scale to 2 frontend instances
powershell -ExecutionPolicy Bypass -File scripts\scale.ps1 -FrontendReplicas 2
```

### Database Management
```powershell
# Backup database
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 -Action backup

# Restore database
powershell -ExecutionPolicy Bypass -File scripts\manage.ps1 -Action restore -BackupFile backup_20241213_120000.sql
```

## 🌐 Application URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React application |
| API | http://localhost:5000 | Flask REST API |
| API Health | http://localhost:5000/api/health | Health check |
| Grafana | http://localhost:3001 | Monitoring dashboard |
| Prometheus | http://localhost:9090 | Metrics collection |

## 🧪 Testing

### 1. API Testing
```powershell
# Run comprehensive tests
python test_api_comprehensive.py

# Run production tests
python scripts\test_production.py

# Test specific endpoint
curl http://localhost:5000/api/health
```

### 2. Frontend Testing
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## 🔒 Security Configuration

### 1. SSL/HTTPS Setup
1. Place SSL certificates in `ssl/` directory
2. Update `nginx.conf` to enable HTTPS
3. Restart nginx service

### 2. Firewall Configuration
```powershell
# Allow required ports
netsh advfirewall firewall add rule name="Crop API" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="Crop Frontend" dir=in action=allow protocol=TCP localport=3000
```

### 3. Database Security
- Change default passwords
- Enable SSL connections
- Restrict network access
- Regular backups

## 📈 Performance Optimization

### 1. Database Optimization
- Enable connection pooling
- Add database indexes
- Regular VACUUM and ANALYZE
- Monitor query performance

### 2. Caching
- Redis caching for API responses
- Frontend asset caching
- Database query caching

### 3. Load Balancing
- Use nginx for load balancing
- Scale API instances horizontally
- Implement health checks

## 🚨 Troubleshooting

### Common Issues

1. **Docker not starting**
   - Check Docker Desktop is running
   - Restart Docker Desktop
   - Check system resources

2. **Port conflicts**
   - Check if ports 3000, 5000, 5432 are available
   - Stop conflicting services
   - Change ports in docker-compose.yml

3. **Database connection failed**
   - Check PostgreSQL container status
   - Verify connection string
   - Check firewall settings

4. **API not responding**
   - Check API container logs
   - Verify environment variables
   - Check database connectivity

### Debug Commands
```powershell
# Check container status
docker-compose -f docker-compose.prod.yml ps

# View container logs
docker-compose -f docker-compose.prod.yml logs api

# Access container shell
docker-compose -f docker-compose.prod.yml exec api bash

# Check resource usage
docker stats
```

## 📞 Support

### Logs Location
- Application logs: `logs/app.log`
- Docker logs: `docker-compose logs`
- System logs: Windows Event Viewer

### Monitoring
- Use Grafana dashboards for system monitoring
- Set up alerts for critical metrics
- Monitor API response times and error rates

## 🎉 Success!

Your AI-based crop recommendation platform is now running in production!

### Quick Verification
1. Open http://localhost:3000 - Frontend should load
2. Open http://localhost:5000/api/health - Should return healthy status
3. Run `python test_api_comprehensive.py` - All tests should pass

**Your platform is ready for farmers to use! 🌾🚀**

