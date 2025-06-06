# 📋 Outfit Manager Deployment Guide

**Version:** 1.0  
**Last Updated:** June 2025  
**Framework:** FastAPI + HTMX + SQLite

---

## 📖 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Database Setup & Migration](#database-setup--migration)
4. [Configuration](#configuration)
5. [Production Deployment](#production-deployment)
6. [Docker Deployment](#docker-deployment)
7. [Cloud Deployment](#cloud-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)
10. [Security Considerations](#security-considerations)

---

## 🛠️ Prerequisites

### System Requirements
- **Python:** 3.8+ (3.11+ recommended)
- **RAM:** 512MB minimum, 1GB+ recommended
- **Storage:** 100MB+ for application, additional space for images
- **OS:** Linux, macOS, or Windows

### Required Software
```bash
# Python with pip
python3 --version  # Should be 3.8+
pip3 --version

# Git (for cloning)
git --version

# Optional: Virtual environment tools
python3 -m venv --help
```

---

## 🚀 Local Development Setup

### 1. Clone and Setup Project

```bash
# Clone the repository
git clone <your-repo-url>
cd outfit-manager

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Project Structure

```bash
# Run project validation
python utilities/debug.py

# Should show all ✅ checks passed
# If any ❌ failures, run:
python utilities/setup_directories.py
```

### 3. Initialize Database

```bash
# Create initial database and seed data
python -c "
from models.database import create_db_and_tables, engine
from services.seed_data import seed_initial_data
from sqlmodel import Session

create_db_and_tables()
with Session(engine) as session:
    seed_initial_data(session)
print('Database initialized successfully!')
"
```

### 4. Start Development Server

```bash
# Start the application
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Application will be available at:
# http://localhost:8000
```

### 5. Verify Installation

Visit `http://localhost:8000` and verify:
- ✅ Main page loads
- ✅ Components section works
- ✅ Outfits section works  
- ✅ Vendor management accessible via hamburger menu
- ✅ Piece type management works
- ✅ Image upload functions
- ✅ Score system works on outfits

---

## 🗄️ Database Setup & Migration

### Initial Setup

The application uses SQLite by default with the database file `outfit_manager.db`.

```bash
# Check current database schema
python utilities/check_schema.py

# Force recreate database (if needed)
python utilities/force_recreate_db.py
```

### Adding Score Field (Migration)

If upgrading from a version without score functionality:

```bash
# Add score field to existing outfits
python utilities/add_score_field.py

# Verify the migration
python utilities/check_schema.py score
```

### Database Backup and Restore

```bash
# Backup database
cp outfit_manager.db backup_$(date +%Y%m%d_%H%M%S).db

# Restore from backup
cp backup_20250606_143000.db outfit_manager.db
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file for production settings:

```bash
# .env file
DATABASE_URL=sqlite:///outfit_manager.db
DEBUG=False
SECRET_KEY=your-secret-key-here
MAX_IMAGE_SIZE=5242880  # 5MB in bytes
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### FastAPI Configuration

Update `main.py` for production:

```python
# main.py - Production configuration
import os
from fastapi import FastAPI

app = FastAPI(
    title="Outfit Manager",
    description="A modern fashion outfit management system",
    version="1.0.0",
    docs_url="/docs" if os.getenv("DEBUG") == "True" else None,
    redoc_url="/redoc" if os.getenv("DEBUG") == "True" else None,
)
```

### Image Storage Configuration

```python
# services/image_service.py - Configuration
class ImageService:
    MAX_FILE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "5242880"))  # 5MB default
    ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
    MAX_IMAGE_SIZE = (1200, 1200)
    THUMBNAIL_SIZE = (300, 300)
```

---

## 🌐 Production Deployment

### Option 1: systemd Service (Linux)

Create service file:

```bash
# /etc/systemd/system/outfit-manager.service
[Unit]
Description=Outfit Manager FastAPI App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/outfit-manager
Environment=PATH=/opt/outfit-manager/venv/bin
ExecStart=/opt/outfit-manager/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Deploy:

```bash
# Copy files to production directory
sudo cp -r outfit-manager /opt/
cd /opt/outfit-manager

# Set up virtual environment
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt

# Set permissions
sudo chown -R www-data:www-data /opt/outfit-manager

# Enable and start service
sudo systemctl enable outfit-manager
sudo systemctl start outfit-manager
sudo systemctl status outfit-manager
```

### Option 2: Gunicorn + Nginx

Install Gunicorn:

```bash
pip install gunicorn
```

Create Gunicorn configuration:

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
timeout = 30
```

Nginx configuration:

```nginx
# /etc/nginx/sites-available/outfit-manager
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;  # For image uploads

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/outfit-manager/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Start services:

```bash
# Start Gunicorn
gunicorn -c gunicorn.conf.py main:app

# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/outfit-manager /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create volume for database
VOLUME ["/app/data"]

# Expose port
EXPOSE 8000

# Set environment variables
ENV DATABASE_URL=sqlite:///data/outfit_manager.db
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  outfit-manager:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - outfit_data:/app/data
      - ./static:/app/static:ro
    environment:
      - DATABASE_URL=sqlite:///data/outfit_manager.db
      - DEBUG=False
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./static:/var/www/static:ro
    depends_on:
      - outfit-manager
    restart: unless-stopped

volumes:
  outfit_data:
```

Deploy with Docker:

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f outfit-manager

# Stop
docker-compose down
```

---

## ☁️ Cloud Deployment

### Heroku Deployment

Create Heroku configuration:

```bash
# Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

```bash
# runtime.txt
python-3.11.3
```

Deploy:

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-outfit-manager

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git push heroku main

# Open app
heroku open
```

### DigitalOcean App Platform

Create app specification:

```yaml
# .do/app.yaml
name: outfit-manager
services:
- name: web
  source_dir: /
  github:
    repo: your-username/outfit-manager
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    value: "your-secret-key"
```

### AWS Elastic Beanstalk

Create configuration:

```yaml
# .ebextensions/python.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
  aws:elasticbeanstalk:application:environment:
    DEBUG: "False"
    SECRET_KEY: "your-secret-key"
```

Deploy:

```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
eb init
eb create outfit-manager-prod
eb deploy
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Database Connection Errors

```bash
# Symptom: "database is locked" or "unable to open database file"
# Solution: Check file permissions and close other connections

# Fix permissions
sudo chown www-data:www-data outfit_manager.db
sudo chmod 644 outfit_manager.db

# Check for processes using the database
sudo lsof outfit_manager.db
```

#### 2. Image Upload Failures

```bash
# Symptom: Images not uploading or displaying
# Check: File size limits and permissions

# Check disk space
df -h

# Check upload directory permissions
ls -la static/images/

# Fix permissions
sudo chown -R www-data:www-data static/
```

#### 3. HTMX Not Working

```bash
# Symptom: Page interactions not working, full page reloads
# Check: Browser console for JavaScript errors

# Verify HTMX is loaded
curl -I http://localhost:8000/static/js/main.js

# Check base template includes HTMX
grep -n "htmx.org" templates/base.html
```

#### 4. Score Functionality Missing

```bash
# Symptom: Score buttons not appearing or working
# Solution: Run score field migration

python utilities/add_score_field.py
python utilities/check_schema.py score
```

#### 5. Template Not Found Errors

```bash
# Symptom: TemplateNotFound exceptions
# Check: Template file locations and naming

# Verify template structure
python utilities/debug.py

# Check template directory permissions
ls -la templates/
```

### Performance Issues

#### High Memory Usage

```bash
# Monitor memory usage
ps aux | grep uvicorn

# Optimize image processing
# Edit services/image_service.py to reduce MAX_IMAGE_SIZE
```

#### Slow Database Queries

```bash
# Enable SQL logging in development
# Edit models/database.py: engine = create_engine(..., echo=True)

# Check database size
ls -lah outfit_manager.db

# Optimize database
sqlite3 outfit_manager.db "VACUUM;"
```

### Log Analysis

```bash
# Application logs (systemd)
sudo journalctl -u outfit-manager -f

# Application logs (Docker)
docker-compose logs -f outfit-manager

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔄 Maintenance

### Regular Tasks

#### 1. Database Backup

```bash
#!/bin/bash
# backup_db.sh
DATE=$(date +%Y%m%d_%H%M%S)
cp outfit_manager.db "backups/backup_$DATE.db"
# Keep only last 30 backups
ls -t backups/backup_*.db | tail -n +31 | xargs rm -f
```

Set up cron job:

```bash
# Add to crontab (daily at 2 AM)
0 2 * * * /path/to/backup_db.sh
```

#### 2. Log Rotation

```bash
# /etc/logrotate.d/outfit-manager
/var/log/outfit-manager/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    postrotate
        systemctl reload outfit-manager
    endscript
}
```

#### 3. Health Checks

```bash
#!/bin/bash
# health_check.sh
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ $RESPONSE != "200" ]; then
    echo "Health check failed: HTTP $RESPONSE"
    systemctl restart outfit-manager
fi
```

#### 4. Updates and Security

```bash
# Update dependencies
pip list --outdated
pip install -r requirements.txt --upgrade

# Security audit
pip audit

# System updates
sudo apt update && sudo apt upgrade
```

### Monitoring

#### Application Metrics

```python
# Add to main.py for monitoring
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

#### Database Size Monitoring

```bash
#!/bin/bash
# monitor_db_size.sh
DB_SIZE=$(du -h outfit_manager.db | cut -f1)
echo "Database size: $DB_SIZE"

# Alert if over 1GB
if [ $(du -m outfit_manager.db | cut -f1) -gt 1024 ]; then
    echo "WARNING: Database size exceeds 1GB"
fi
```

---

## 🔒 Security Considerations

### 1. File Upload Security

```python
# services/image_service.py - Enhanced security
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
FORBIDDEN_EXTENSIONS = {'.php', '.exe', '.sh', '.py'}

def validate_file_extension(filename: str) -> bool:
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS and ext not in FORBIDDEN_EXTENSIONS
```

### 2. Input Validation

```python
# Enhanced form validation
from pydantic import BaseModel, validator

class ComponentCreate(BaseModel):
    name: str
    cost: float
    
    @validator('name')
    def name_must_be_clean(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('cost')
    def cost_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Cost must be positive')
        return v
```

### 3. Rate Limiting

```python
# Install: pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/components/")
@limiter.limit("10/minute")  # Limit uploads
async def create_component(request: Request, ...):
    ...
```

### 4. HTTPS Configuration

```nginx
# Nginx SSL configuration
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

### 5. Database Security

```bash
# Set proper database file permissions
chmod 600 outfit_manager.db
chown www-data:www-data outfit_manager.db

# Regular security audits
sqlite3 outfit_manager.db ".schema" | grep -i "password\|secret\|key"
```

---

## 📞 Support and Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HTMX Documentation](https://htmx.org/docs/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

### Getting Help
1. Check the troubleshooting section above
2. Run `python utilities/debug.py` for validation
3. Check application logs for specific errors
4. Review the GitHub issues for known problems

### Useful Commands

```bash
# Quick validation
python utilities/debug.py

# Database schema check
python utilities/check_schema.py

# View application status
systemctl status outfit-manager

# Monitor logs in real-time
journalctl -u outfit-manager -f

# Test application endpoint
curl -I http://localhost:8000/

# Check disk space
df -h

# Monitor system resources
top -p $(pgrep -f "uvicorn")
```

---

**🎉 Congratulations!** Your Outfit Manager application should now be successfully deployed and running. Remember to keep your system updated and monitor the application regularly for optimal performance.