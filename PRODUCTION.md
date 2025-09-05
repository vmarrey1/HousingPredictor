# Berkeley Four Year Plan Generator - Production Deployment Guide

## 🚀 Production Features

- **Docker Containerization**: Multi-stage build for optimized production images
- **Nginx Reverse Proxy**: Load balancing, SSL termination, and static file serving
- **Health Checks**: Automated monitoring and restart capabilities
- **Rate Limiting**: API protection against abuse
- **Security Headers**: XSS protection, content type validation, and more
- **Environment Configuration**: Secure configuration management
- **Logging**: Comprehensive application logging
- **Error Handling**: Graceful error responses and fallbacks

## 📋 Prerequisites

- Docker and Docker Compose
- Git
- SSL certificates (for HTTPS)
- Google Gemini API key

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/vmarrey1/HousingPredictor.git
cd HousingPredictor
```

### 2. Configure Environment

```bash
cp env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
FLASK_ENV=production
```

### 3. Deploy

```bash
# Make scripts executable
chmod +x build.sh deploy.sh

# Build and deploy
./build.sh
./deploy.sh
```

## 🐳 Docker Configuration

### Services

- **berkeley-planner**: Flask backend with AI integration
- **nginx**: Reverse proxy and static file server

### Ports

- `80`: HTTP (redirects to HTTPS)
- `443`: HTTPS
- `5000`: Backend API (internal)

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `SECRET_KEY` | Flask secret key | Required |
| `FLASK_ENV` | Flask environment | `production` |
| `PORT` | Backend port | `5000` |
| `HOST` | Backend host | `0.0.0.0` |
| `LOG_LEVEL` | Logging level | `INFO` |

### SSL Configuration

Place your SSL certificates in the `ssl/` directory:
- `ssl/cert.pem`: SSL certificate
- `ssl/key.pem`: SSL private key

## 📊 Monitoring

### Health Checks

- **Backend**: `GET /health`
- **Docker**: Built-in health checks
- **Nginx**: Upstream health monitoring

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f berkeley-planner
docker-compose logs -f nginx
```

### Metrics

The application provides health status at `/health` endpoint:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "ok",
    "ai_model": "ok",
    "course_data": "ok"
  }
}
```

## 🔒 Security Features

### Rate Limiting

- **API endpoints**: 10 requests/minute
- **General endpoints**: 30 requests/minute
- **Search endpoints**: 60 requests/minute

### Security Headers

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`

### CORS Configuration

- Configured for production domains
- Secure cross-origin requests

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
./deploy.sh
```

### Option 2: Manual Docker

```bash
# Build image
docker build -t berkeley-planner:latest .

# Run container
docker run -d \
  --name berkeley-planner \
  -p 5000:5000 \
  -e GEMINI_API_KEY=your_key \
  berkeley-planner:latest
```

### Option 3: Cloud Deployment

#### AWS ECS/Fargate

1. Push image to ECR
2. Create ECS task definition
3. Configure load balancer
4. Set up auto-scaling

#### Google Cloud Run

1. Build and push to GCR
2. Deploy with Cloud Run
3. Configure custom domain

#### Azure Container Instances

1. Push to Azure Container Registry
2. Deploy with Azure CLI
3. Configure public IP

## 📈 Performance Optimization

### Frontend

- **Static Generation**: Pre-built pages for better performance
- **Code Splitting**: Automatic code splitting for smaller bundles
- **Image Optimization**: Next.js automatic image optimization
- **Caching**: Aggressive caching for static assets

### Backend

- **Connection Pooling**: Efficient database connections
- **Caching**: In-memory caching for frequently accessed data
- **Rate Limiting**: Protection against abuse
- **Error Handling**: Graceful degradation

### Nginx

- **Gzip Compression**: Reduced bandwidth usage
- **Static File Serving**: Direct serving of static assets
- **Load Balancing**: Multiple backend instances
- **SSL Termination**: Efficient SSL handling

## 🔧 Maintenance

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
./deploy.sh
```

### Backup

```bash
# Backup course data
cp courses-report.2025-09-04\ \(7\).csv backup/

# Backup configuration
cp .env backup/
```

### Scaling

```bash
# Scale backend service
docker-compose up -d --scale berkeley-planner=3
```

## 🐛 Troubleshooting

### Common Issues

1. **API Key Issues**
   ```bash
   # Check environment variables
   docker-compose exec berkeley-planner env | grep GEMINI
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :5000
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate validity
   openssl x509 -in ssl/cert.pem -text -noout
   ```

### Debug Mode

```bash
# Run in debug mode
FLASK_DEBUG=True docker-compose up
```

## 📞 Support

For production support and issues:

1. Check application logs
2. Verify health endpoints
3. Review configuration
4. Check external dependencies

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ./deploy.sh
```

## 📊 Monitoring and Alerting

### Recommended Tools

- **Prometheus + Grafana**: Metrics and dashboards
- **ELK Stack**: Log aggregation and analysis
- **Uptime Robot**: External monitoring
- **Sentry**: Error tracking and alerting

### Key Metrics to Monitor

- Response times
- Error rates
- Memory usage
- CPU utilization
- API rate limits
- Health check status
