# Render.com Deployment Configuration

This directory is configured for one-click deployment on Render.com.

## Quick Deploy to Render

### Step 1: Connect Repository
1. Push your code to GitHub: `git push origin main`
2. Visit [render.com](https://render.com)
3. Sign in with GitHub account
4. Click "New +" → "Web Service"
5. Select your repository

### Step 2: Configure Service
Use these exact settings:

```
Name:                    passive-liveness-api
Runtime:                 Python 3.11
Root Directory:          backend
Build Command:           pip install -r requirements.txt
Start Command:           uvicorn main:app --host 0.0.0.0 --port 10000
Instance Type:           Standard (at least for production)
```

### Step 3: Set Environment Variables
In Render Dashboard → Environment:

```
PORT=10000
GEMINI_API_KEY=your_gemini_api_key_here
```

### Step 4: Deploy
- Click "Create Web Service"
- Render automatically deploys on every git push
- Monitor logs in Render Dashboard

---

## Environment Variables

### Required
- **PORT** (optional): Default 10000, override if needed

### Optional
- **GEMINI_API_KEY**: Google Gemini API key for AI explanations
  - Get from: https://makersuite.google.com/app/apikey
  - Leave empty to disable AI explanations

---

## Monitoring

### Health Check
```bash
curl https://your-service-url.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### View Logs
- Dashboard → Logs tab
- Real-time log streaming
- Filter by timestamp, level, service

### Common Metrics
- **Response time**: Should be < 5 seconds
- **Success rate**: Should be > 99%
- **Error rate**: Should be < 1%

---

## Troubleshooting

### Service Won't Start
- Check build logs for errors
- Ensure requirements.txt has all packages
- Verify model.pth is in backend/ directory

### Build Fails
- Error: `pip install failed`
  - Solution: Check requirements.txt syntax
  - Ensure all package names are correct
  
- Error: `Python not found`
  - Solution: Render requires Python 3.11+
  - Update runtime to latest Python

### Out of Memory
- Error: `OOMKilled` in logs
- Solution: Upgrade to Standard or Pro instance
  - Free tier: 512MB (insufficient for torch)
  - Standard: 1GB (recommended minimum)
  - Pro: 2GB+ (for production)

### Slow Deployment
- First deploy: 5-10 minutes (normal)
- Build: ~2-3 minutes
- Model load: ~2-3 seconds
- Subsequent deploys: Faster (cached dependencies)

---

## Costs

### Render Free Tier
- ✅ 1 web service included
- ✅ 1GB RAM (insufficient for this app)
- ⚠️ Auto-sleeps after 15 min of inactivity
- ❌ Poor performance for ML workloads

### Render Starter ($7/month)
- ✅ 1GB RAM (minimum recommended)
- ✅ 0.5 CPU core
- ✅ No auto-sleep
- ✅ Good for testing

### Render Standard ($12/month)
- ✅ 1GB RAM
- ✅ 1 CPU core
- ✅ Recommended for production
- ✅ Fast deployments

### Render Pro ($27/month+)
- ✅ 2GB+ RAM
- ✅ Multiple CPU cores
- ✅ Best for high-traffic

---

## Auto-Deploy on Git Push

Render automatically redeploys when you push to your repository:

```bash
# Make changes locally
git add .
git commit -m "Update model or fix bugs"
git push origin main

# Render automatically redeploys (5-10 minutes)
# Check Dashboard → Logs to monitor deployment
```

---

## Custom Domain

### Add Custom Domain
1. Render Dashboard → Settings
2. Custom Domains → Add Custom Domain
3. Enter your domain (e.g., api.example.com)
4. Update DNS records as shown
5. Render provides free SSL/HTTPS certificate

---

## Performance Tips

### Optimize Load Time
1. ✅ Model loads once at startup
2. ✅ First request: ~3-5 seconds
3. ✅ Subsequent requests: ~1 second
4. ✅ Keep-alive connections reduce overhead

### Monitor Performance
```bash
# Test response time
time curl https://your-service.onrender.com/health

# Load test with Apache Bench
ab -n 100 -c 10 https://your-service.onrender.com/health
```

---

## Security

### CORS Configuration
Currently allows all origins. For production:

Update `main.py`:
```python
allow_origins=["https://your-frontend-domain.com"]
```

### API Key Protection (Optional)
Add in `main.py`:
```python
api_key = request.headers.get("X-API-Key")
if api_key != os.getenv("API_KEY"):
    raise HTTPException(status_code=401, detail="Unauthorized")
```

### HTTPS
- ✅ Automatic
- ✅ Free SSL certificate
- ✅ Auto-renewal
- All connections use HTTPS

---

## Backup & Restore

### Export Data
- Render doesn't provide database backups for this API
- Model (model.pth) is in Git repository
- No persistent state (stateless API)

### Rollback
```bash
# If deployment fails, rollback to previous version
git revert HEAD
git push origin main
# Render automatically redeploys
```

---

## Support

### Render Support
- Documentation: https://render.com/docs
- Support Portal: https://support.render.com
- Community: https://discord.gg/rendercom

### API Issues
- Check `/docs` endpoint for API details
- View server logs in Render Dashboard
- Enable debug logging if needed

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Connect Render to GitHub
3. ✅ Set environment variables
4. ✅ Deploy service
5. ✅ Test health endpoint
6. ✅ Monitor logs
7. ✅ Integrate with frontend
8. ✅ Add custom domain

**Estimated setup time**: 10-15 minutes

**Status**: Ready for deployment ✅
