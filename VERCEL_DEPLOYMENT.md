# Vercel Deployment Guide

This directory is configured for deployment on Vercel.

## Quick Deploy to Vercel (Frontend)

### 1. Connect Repository
1. Visit [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Select the repository

### 2. Configure Project
- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm install && npm run build`
- **Output Directory**: `dist`

### 3. Set Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

```
VITE_API_URL=https://your-backend-service.onrender.com
```

Replace `your-backend-service.onrender.com` with your actual Render backend service URL.

### 4. Deploy
- Click "Deploy"
- Vercel automatically deploys on every git push
- Your frontend will be live at: `https://your-project.vercel.app`

## Environment Variables

### Required
- **VITE_API_URL**: Full URL to your backend API (e.g., https://api.onrender.com)
  - For local development: `http://localhost:10000`
  - For production: Your Render service URL

### Optional
- None at this time

## Vercel Logs

- Dashboard → Deployments tab
- View build logs and runtime logs
- Search for errors or warnings

## Testing

After deployment:

```bash
# Test that frontend loads
curl https://your-project.vercel.app

# Test that API calls work (check browser console)
# Open the site in a browser and upload an image
```

## Troubleshooting

### Build fails
- Error: `npm not found`
  - Solution: Ensure Node.js is available (Vercel provides it)
  
- Error: `VITE_API_URL not set`
  - Solution: Add environment variable in Vercel dashboard
  
- Error: `Module not found`
  - Solution: Verify all dependencies in frontend/package.json are installed

### Frontend works but API calls fail
- Error: `CORS error` or `Cannot reach backend`
  - Solution: Check that VITE_API_URL is correct and backend is running
  - Verify backend CORS is configured for frontend domain

### Static files not loading
- Error: `404 on styles or scripts`
  - Solution: Ensure output directory is set to `dist` in vercel.json
