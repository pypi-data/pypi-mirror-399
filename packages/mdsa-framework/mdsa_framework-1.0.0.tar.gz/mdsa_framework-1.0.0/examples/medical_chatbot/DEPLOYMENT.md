# Medical Chatbot - Production Deployment Guide

This guide covers deploying the medical chatbot to production environments.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Security Hardening](#security-hardening)
5. [Monitoring & Logging](#monitoring--logging)
6. [Backup & Recovery](#backup--recovery)

---

## Pre-Deployment Checklist

Before deploying to production:

- [ ] **Security audit completed** (no API keys in code)
- [ ] **HTTPS configured** (SSL certificate installed)
- [ ] **Rate limiting enabled** (prevent abuse)
- [ ] **Authentication implemented** (if required)
- [ ] **Logging configured** (centralized logging)
- [ ] **Monitoring setup** (health checks, alerts)
- [ ] **Backup strategy** (knowledge base, configs)
- [ ] **Resource limits set** (memory, CPU)
- [ ] **Error handling tested** (graceful degradation)
- [ ] **Documentation updated** (deployment procedures)

---

## Docker Deployment

### Option 1: Basic Docker

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY app/ ./app/
COPY knowledge_base/ ./knowledge_base/
COPY requirements.txt .env ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install MDSA framework
RUN pip install --no-cache-dir mdsa-framework

# Expose chatbot port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD curl -f http://localhost:7860/ || exit 1

# Run chatbot
CMD ["python", "app/enhanced_medical_chatbot_fixed.py", "--host", "0.0.0.0"]
```

**Build and run:**
```bash
# Build image
docker build -t medical-chatbot:1.0 .

# Run container
docker run -d \
  --name medical-chatbot \
  -p 7860:7860 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --restart unless-stopped \
  medical-chatbot:1.0

# View logs
docker logs -f medical-chatbot

# Stop container
docker stop medical-chatbot
```

### Option 2: Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  chatbot:
    build: .
    container_name: medical-chatbot
    ports:
      - "7860:7860"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - DASHBOARD_URL=http://dashboard:9000
    volumes:
      - ./knowledge_base:/app/knowledge_base
      - ./logs:/app/logs
    depends_on:
      - ollama
      - dashboard
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

  dashboard:
    build: ../../mdsa/ui/dashboard
    container_name: mdsa-dashboard
    ports:
      - "9000:9000"
    restart: unless-stopped

volumes:
  ollama_data:
```

**Deploy:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

## Cloud Deployment

### AWS EC2

**1. Launch EC2 Instance:**
```bash
# Instance type: t3.xlarge (4 vCPU, 16GB RAM)
# OS: Ubuntu 22.04 LTS
# Storage: 50GB EBS
# Security group: Open ports 22, 7860, 9000
```

**2. Install Dependencies:**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3-pip python3-venv -y

# Install Docker (optional)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu
```

**3. Deploy Application:**
```bash
# Clone repository
git clone https://github.com/your-org/mdsa-framework.git
cd mdsa-framework/examples/medical_chatbot

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
cd ../.. && pip install -e . && cd examples/medical_chatbot

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull deepseek-v3.1

# Run chatbot (with nohup for background)
nohup python app/enhanced_medical_chatbot_fixed.py > chatbot.log 2>&1 &
```

**4. Configure Nginx Reverse Proxy:**
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/medical-chatbot
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support for Gradio
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Enable and start:**
```bash
sudo ln -s /etc/nginx/sites-available/medical-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**5. Enable HTTPS (Let's Encrypt):**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

### Azure VM

Similar to AWS, but using Azure CLI:
```bash
# Create resource group
az group create --name mdsa-rg --location eastus

# Create VM
az vm create \
  --resource-group mdsa-rg \
  --name mdsa-chatbot-vm \
  --image Ubuntu2204 \
  --size Standard_D4s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys

# Open ports
az vm open-port --port 80 --resource-group mdsa-rg --name mdsa-chatbot-vm
az vm open-port --port 443 --resource-group mdsa-rg --name mdsa-chatbot-vm
```

### Google Cloud Platform (GCP)

```bash
# Create instance
gcloud compute instances create mdsa-chatbot \
  --machine-type=n1-standard-4 \
  --zone=us-central1-a \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --tags=http-server,https-server
```

---

## Security Hardening

### 1. Authentication

**Basic Auth (Nginx):**
```nginx
server {
    ...
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    ...
}
```

**Create password file:**
```bash
sudo apt install apache2-utils -y
sudo htpasswd -c /etc/nginx/.htpasswd admin
```

### 2. Rate Limiting

**Nginx rate limiting:**
```nginx
http {
    limit_req_zone $binary_remote_addr zone=chatbot:10m rate=10r/m;

    server {
        ...
        location / {
            limit_req zone=chatbot burst=5;
            proxy_pass http://localhost:7860;
        }
    }
}
```

### 3. Input Sanitization

**In application code:**
```python
import re

def sanitize_input(user_input: str) -> str:
    """Remove potentially harmful content."""
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]+>', '', user_input)
    # Limit length
    cleaned = cleaned[:2000]
    # Remove control characters
    cleaned = ''.join(char for char in cleaned if char.isprintable() or char.isspace())
    return cleaned.strip()
```

### 4. Environment Variables

**Never commit sensitive data:**
```bash
# Use .env file (add to .gitignore)
OPENAI_API_KEY=sk-...
DATABASE_PASSWORD=...

# Or use AWS Secrets Manager / Azure Key Vault
```

### 5. Firewall Rules

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## Monitoring & Logging

### 1. Application Logging

**Configure logging:**
```python
import logging
from logging.handlers import RotatingFileHandler

# Setup rotating file handler
handler = RotatingFileHandler(
    'logs/chatbot.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)
```

### 2. Health Monitoring

**Health check endpoint:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

**Uptime monitoring** (use services like):
- UptimeRobot
- Pingdom
- StatusCake

### 3. Performance Monitoring

**Monitor with MDSA Dashboard:**
- Real-time request tracking
- Domain distribution
- Latency metrics
- Error rates

**External APM tools:**
- New Relic
- DataDog
- Prometheus + Grafana

---

## Backup & Recovery

### 1. Knowledge Base Backup

**Daily backup script:**
```bash
#!/bin/bash
# backup_kb.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/knowledge_base"
KB_PATH="/app/knowledge_base"

# Create backup
tar -czf "$BACKUP_DIR/kb_backup_$DATE.tar.gz" "$KB_PATH"

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "kb_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: kb_backup_$DATE.tar.gz"
```

**Schedule with cron:**
```bash
# Run daily at 2 AM
crontab -e
0 2 * * * /path/to/backup_kb.sh
```

### 2. Configuration Backup

```bash
# Backup configs
tar -czf configs_backup.tar.gz .env app/config.yaml

# Store in S3 (AWS)
aws s3 cp configs_backup.tar.gz s3://your-bucket/backups/

# Or Azure Blob Storage
az storage blob upload \
  --account-name youraccount \
  --container-name backups \
  --name configs_backup.tar.gz \
  --file configs_backup.tar.gz
```

### 3. Disaster Recovery

**Restore procedure:**
```bash
# 1. Restore knowledge base
tar -xzf kb_backup_YYYYMMDD.tar.gz -C /

# 2. Restore configurations
tar -xzf configs_backup.tar.gz

# 3. Restart services
docker-compose restart
# OR
systemctl restart medical-chatbot
```

---

## Production Checklist

### Pre-Launch

- [ ] Load testing completed (100+ concurrent users)
- [ ] Security penetration testing done
- [ ] SSL certificate installed and verified
- [ ] Backup and restore tested
- [ ] Monitoring alerts configured
- [ ] Error handling tested
- [ ] Documentation complete
- [ ] Rollback plan documented

### Post-Launch

- [ ] Monitor error rates (target: <1%)
- [ ] Check response times (target: <2s)
- [ ] Verify backup jobs running
- [ ] Review security logs daily
- [ ] Update knowledge base weekly
- [ ] Patch security vulnerabilities
- [ ] Scale resources as needed

---

## Support

For deployment issues:
- Documentation: [README.md](README.md)
- GitHub Issues: [Report deployment issues](https://github.com/your-org/mdsa-framework/issues)
- Email: devops@your-org.com

---

**Deployment Guide Version:** 1.0.0
**Last Updated:** December 25, 2025
**Production Status:** Ready
