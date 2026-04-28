# 🚀 QUICK START: DEPLOYMENT IN 30 MINUTES

## PRE-DEPLOYMENT CHECKLIST (5 min)

### 1. Rotate API Key (CRITICAL)
- [ ] Visit: https://makersuite.google.com/app/apikey
- [ ] Delete old key: `AIzaSyAi0eUXQsRhNhrlVcnhRsvvScj2iAsTh-E`
- [ ] Create new key
- [ ] Save new key for Step 4 below

### 2. Get Your Vercel Domain (After Frontend Deploy)
- [ ] Will be auto-generated: `https://your-project.vercel.app`
- [ ] (Don't have this yet? Continue, you'll get it during frontend deployment)

### 3. Test Locally (Optional but Recommended)
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 10000

# Terminal 2: Frontend (in new terminal)
cd frontend
npm install
npm run dev

# Terminal 3: Test
curl -X POST -F "file=@backend/test_real_face.jpg" \
  http://localhost:10000/analyze
```
- [ ] Backend responds at http://localhost:10000/health
- [ ] Frontend loads at http://localhost:5173
- [ ] Image upload works

### 4. Push to GitHub
```bash
git add .
git commit -m "Production-ready deployment"
git push origin main
```
- [ ] Code pushed successfully

---

## BACKEND DEPLOYMENT (Render) - 5 MINUTES

1. [ ] Visit **https://render.com** and sign in with GitHub

2. [ ] Click **"New +" → "Web Service"**

3. [ ] Select your repository and click **"Connect"**

4. [ ] Configure settings:
   - **Name**: `passive-liveness-api`
   - **Environment**: Python
   - **Region**: Choose closest
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
   - **Plan**: Standard (production)

5. [ ] Click **"Advanced"** and add environment variables:
   ```
   PYTHON_VERSION = 3.11
   PORT = 10000
   GEMINI_API_KEY = <paste-your-new-key-from-step-1>
   CORS_ALLOWED_ORIGINS = https://YOUR_VERCEL_DOMAIN.vercel.app
   ```
   (You can update CORS_ALLOWED_ORIGINS after getting Vercel domain)

6. [ ] Click **"Create Web Service"** and wait 2-3 minutes

7. [ ] Copy your backend URL: **`https://your-api-name.onrender.com`**

8. [ ] Test health check:
   ```bash
   curl https://your-api-name.onrender.com/health
   ```
   - [ ] Returns JSON with `"status": "healthy"`

---

## FRONTEND DEPLOYMENT (Vercel) - 5 MINUTES

1. [ ] Visit **https://vercel.com** and sign in with GitHub

2. [ ] Click **"Add New Project"**

3. [ ] Select your repository and click **"Import"**

4. [ ] Configure settings:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: Leave default (auto-detected)
   - **Output Directory**: `dist`

5. [ ] Click **"Environment Variables"** and add:
   ```
   VITE_API_URL = https://your-api-name.onrender.com
   ```
   (Use your Render backend URL from previous step)

6. [ ] Click **"Deploy"** and wait 1-2 minutes

7. [ ] Copy your frontend URL: **`https://your-project.vercel.app`**

8. [ ] (OPTIONAL) Update Render CORS:
   - Go back to Render dashboard
   - Your service → Settings → Environment
   - Edit `CORS_ALLOWED_ORIGINS`
   - Set to: `https://your-project.vercel.app`

---

## VERIFICATION (5 MINUTES)

### Test Backend Health
```bash
curl https://your-api-name.onrender.com/health
```
✅ Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### Test Frontend + Full Flow
1. [ ] Open **`https://your-project.vercel.app`**
2. [ ] Upload a test image (JPG or PNG)
3. [ ] Click "Analyze"
4. [ ] Verify results appear
5. [ ] Check prediction, confidence, risk level

### Check Logs
- **Render**: Dashboard → Logs tab
- **Vercel**: Dashboard → Deployments → View logs

✅ No errors = **DEPLOYMENT SUCCESSFUL**

---

## SUMMARY OF CHANGES

| Issue | Before | After | Status |
|-------|--------|-------|--------|
| Frontend API URL | Hardcoded localhost | Environment variable | ✅ Fixed |
| Backend Port | 8000 (wrong) | 10000 (consistent) | ✅ Fixed |
| API Key | Hardcoded in .env | Environment only | ✅ Fixed |
| CORS | Allow all | Restricted to domain | ✅ Fixed |
| Vercel Config | Missing | Added vercel.json | ✅ Fixed |
| Env Variables | Missing | .env files created | ✅ Fixed |

---

## DOCUMENTS TO READ

- **[DEPLOYMENT_READY.md](DEPLOYMENT_READY.md)** - Full deployment guide (15 min read)
- **[AUDIT_REPORT.md](AUDIT_REPORT.md)** - Detailed audit findings (10 min read)
- **[VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)** - Vercel-specific guide
- **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)** - Render-specific guide

---

## SUPPORT & TROUBLESHOOTING

### Build Fails on Render
- Check: Build logs in Render dashboard
- Ensure: `backend/requirements.txt` is valid
- Ensure: `backend/model.pth` exists

### Build Fails on Vercel
- Check: Build logs in Vercel dashboard
- Ensure: `frontend/package.json` is valid
- Ensure: `VITE_API_URL` is set in environment

### Frontend Can't Reach Backend
- Check: `VITE_API_URL` is correct in Vercel environment
- Check: Render backend URL is accessible
- Check: `CORS_ALLOWED_ORIGINS` includes your Vercel domain

### Status Still Shows Loading
- Check: Browser console for errors (F12)
- Check: Render logs for API errors
- Verify: API URL is correct

---

## TIMELINE

| Step | Time | Status |
|------|------|--------|
| Pre-deployment checks | 5 min | ⏳ Now |
| Backend deployment | 5 min | Next |
| Frontend deployment | 5 min | After backend |
| Verification | 5 min | After frontend |
| **Total** | **20 min** | **Ready!** |

---

## IMPORTANT LINKS

- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **Gemini API Keys**: https://makersuite.google.com/app/apikey
- **GitHub**: Your repository

---

✅ **STATUS**: **READY FOR PRODUCTION**

You have all the tools and configuration needed. Follow the steps above and you'll be live in 30 minutes!

Need help? See [AUDIT_REPORT.md](AUDIT_REPORT.md) for detailed troubleshooting.
