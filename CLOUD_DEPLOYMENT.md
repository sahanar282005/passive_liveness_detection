# Passive Liveness Detection - Cloud Deployment Guide

## Overview

This backend is production-ready for deployment on cloud platforms including **Render.com**, **AWS**, **Google Cloud**, and **Azure**. All code follows cloud-safe practices with relative paths, environment variables, and proper error handling.

---

## 📋 Deployment Checklist

✅ **Backend Structure**
- FastAPI application (`main.py`) with CORS enabled
- Deep learning model (`model.py`) using ResNet18 with PyTorch
- Image processing pipeline (`image_processing.py`)
- Environment variable support for configuration

✅ **Requirements**
- All dependencies in `requirements.txt` with version pinning
- Production-ready with gunicorn support
- No missing or conflicting packages

✅ **Error Handling**
- Graceful fallbacks for missing model or API failures
- Structured JSON responses in all cases
- Comprehensive logging for monitoring

✅ **Production Safety**
- No debug print statements (logging only)
- No hardcoded localhost URLs
- Relative paths work in any directory
- CORS allows frontend integration

---

## 🚀 Deploy to Render.com

### Step 1: Prepare Repository
```bash
# Ensure model.pth is in backend/ directory
# Commit all code to Git (GitHub, GitLab, etc.)
git add .
git commit -m "Production-ready cloud deployment"
git push
```

### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Fill in settings:

| Setting | Value |
|---------|-------|
| **Name** | `passive-liveness-api` |
| **Region** | Select closest region |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Python 3.11` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port 10000` |

### Step 3: Set Environment Variables
In Render Dashboard → Environment:

```
PORT=10000
GEMINI_API_KEY=your_api_key_here
```

### Step 4: Deploy
- Render will auto-deploy on git push
- Monitor logs in Render Dashboard
- Access API at: `https://your-service.onrender.com`

---

## 🔧 Deploy to AWS (Elastic Beanstalk)

### Step 1: Create `.ebextensions/python.config`
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: main:app
  aws:elasticbeanstalk:application:environment:
    PORT: 5000
```

### Step 2: Initialize EB
```bash
cd backend
eb init -p python-3.11 passive-liveness-api
```

### Step 3: Set Environment Variables
```bash
eb setenv GEMINI_API_KEY=your_api_key_here
```

### Step 4: Deploy
```bash
eb create passive-liveness-prod
eb open  # Opens in browser
```

---

## ☁️ Deploy to Google Cloud Run

### Step 1: Create `Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Step 2: Build and Deploy
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/passive-liveness-api
gcloud run deploy passive-liveness-api \
  --image gcr.io/PROJECT-ID/passive-liveness-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_api_key
```

---

## 🟦 Deploy to Azure

### Step 1: Create Resource Group
```bash
az group create --name passive-liveness-rg --location eastus
```

### Step 2: Create App Service Plan
```bash
az appservice plan create \
  --name passive-liveness-plan \
  --resource-group passive-liveness-rg \
  --sku B2
```

### Step 3: Create Web App
```bash
az webapp create \
  --resource-group passive-liveness-rg \
  --plan passive-liveness-plan \
  --name passive-liveness-api \
  --runtime "PYTHON|3.11"
```

### Step 4: Set Configuration
```bash
az webapp config appsettings set \
  --resource-group passive-liveness-rg \
  --name passive-liveness-api \
  --settings GEMINI_API_KEY=your_api_key PORT=8000
```

### Step 5: Deploy Code
```bash
az webapp deployment source config-zip \
  --resource-group passive-liveness-rg \
  --name passive-liveness-api \
  --src backend.zip
```

---

## 🧪 Testing Deployment

### Health Check
```bash
curl https://your-api-url/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "timestamp": "2026-04-28T..."
}
```

### Analyze Image
```bash
curl -X POST \
  -F "file=@image.jpg" \
  https://your-api-url/analyze
```

Expected response:
```json
{
  "prediction": "REAL",
  "spoof_score": 0.245,
  "confidence": 87.3,
  "risk_level": "LOW",
  "recommendation": "ALLOW",
  "explanations": [...],
  "inference_time_seconds": 1.234
}
```

### API Docs
Visit: `https://your-api-url/docs`

---

## 📊 Monitoring & Logging

### Cloud Platform Monitoring
- **Render**: Logs tab shows all output
- **AWS**: CloudWatch → Logs
- **GCP**: Cloud Logging
- **Azure**: Application Insights

### Key Metrics to Monitor
- Response time (should be < 5 seconds)
- Error rate (should be < 1%)
- Model initialization on startup
- Memory usage (torch models can be large)

### Check Logs
```bash
# Render
render logs

# AWS
eb logs

# GCP
gcloud run logs read passive-liveness-api

# Azure
az webapp log tail --resource-group passive-liveness-rg --name passive-liveness-api
```

---

## 🔐 Security Configuration

### Production CORS Settings
Update `main.py` to restrict origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### API Authentication (Optional)
Add API key validation in `main.py`:

```python
from fastapi import Header

@app.post("/analyze")
async def analyze_image(file: UploadFile, x_api_key: str = Header(None)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of code
```

---

## 📦 Model Deployment

### Option 1: Include in Repository (Recommended for < 500MB)
```bash
# Ensure model.pth is in backend/
ls -lh backend/model.pth
git add backend/model.pth
```

### Option 2: Download from S3/Cloud Storage
```python
import os
import boto3

if not os.path.exists("model.pth"):
    s3 = boto3.client('s3')
    s3.download_file(
        'your-bucket',
        'models/model.pth',
        'model.pth'
    )
    print("Model downloaded from S3")
```

### Option 3: Use Pre-built Models
```python
# Download from PyTorch Hub
model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
```

---

## 🛠️ Troubleshooting

### "Model not found" Error
```python
# Check in logs - model.pth must be in same directory as main.py
# Verify: ls -la backend/
# Should see: main.py, model.pth, model.py, etc.
```

### Port Already in Use
```bash
# Render: Automatic (uses PORT env var)
# Local: python main.py  # Uses port 10000
# Or: uvicorn main:app --port 5000
```

### Out of Memory
- Model uses ~500MB with torch
- Render free tier: 512MB (upgrade needed)
- AWS: Use at least t3.small
- GCP/Azure: Use at least 1GB RAM

### Slow Inference
- First request loads model (~2-3 seconds)
- Subsequent requests: < 1 second
- Normal behavior with PyTorch CPU inference

---

## 📞 Support

**API Documentation**: Visit `/docs` endpoint (Swagger UI)
**Health Check**: `GET /health`
**Test Image**: Use any JPG/PNG file < 10000x10000 pixels

---

## ✨ Next Steps

1. ✅ Update GEMINI_API_KEY in cloud dashboard
2. ✅ Test health endpoint
3. ✅ Upload test image for analysis
4. ✅ Monitor logs and performance
5. ✅ Integrate with frontend application

**Deployment status**: ✅ READY FOR PRODUCTION
