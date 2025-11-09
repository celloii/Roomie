# Deployment Guide for Roomie

## Recommended: Render.com

### Why Render?
- ✅ Free tier available
- ✅ Persistent file storage (for uploads/ and JSON files)
- ✅ Native Flask support
- ✅ Easy environment variable setup
- ✅ Automatic HTTPS
- ✅ Simple deployment from GitHub

### Steps to Deploy:

1. **Push your code to GitHub** (if not already done)

2. **Go to Render.com** and sign up/login

3. **Create a New Web Service**:
   - Connect your GitHub repository
   - Select the repository
   - Choose "Python 3" environment
   - Build Command: `bash build.sh` (or `pip install --upgrade pip && pip install -r requirements.txt && pip install gunicorn`)
   - Start Command: `python -m gunicorn server:app --bind 0.0.0.0:$PORT`
   - Environment: `Python 3`

4. **Set Environment Variables** in Render dashboard:
   ```
   ANTHROPIC_API_KEY=your_key_here
   DEDALUS_API_KEY=your_key_here
   SECRET_KEY=generate_a_random_secret_key
   PORT=10000
   ENVIRONMENT=production
   ```

5. **Deploy!** Render will automatically build and deploy your app.

### Troubleshooting:

**If gunicorn is not found:**
- Make sure `gunicorn>=21.2.0` is in `requirements.txt`
- Use the build script: `bash build.sh`
- Or explicitly install in build command: `pip install -r requirements.txt && pip install gunicorn`
- Use `python -m gunicorn` instead of just `gunicorn` in start command

---

## Alternative: Railway.app

### Why Railway?
- ✅ Very easy setup
- ✅ Persistent storage
- ✅ Good for Flask apps
- ✅ Free tier with $5 credit

### Steps:
1. Go to railway.app
2. New Project → Deploy from GitHub
3. Select your repo
4. Railway auto-detects Python/Flask
5. Add environment variables
6. Set start command: `python -m gunicorn server:app --bind 0.0.0.0:$PORT`
7. Deploy!

---

## Alternative: Fly.io

### Why Fly.io?
- ✅ Persistent volumes for file storage
- ✅ Good free tier
- ✅ Global edge deployment

### Setup:
1. Install flyctl: `curl -L https://fly.io/install.sh | sh`
2. Run: `fly launch`
3. Follow prompts
4. Add environment variables: `fly secrets set ANTHROPIC_API_KEY=...`
5. Set start command in `fly.toml`: `python -m gunicorn server:app`

---

## Important Notes:

### File Storage
- **Render/Railway**: Files persist in the filesystem
- **Vercel**: ❌ Not recommended - serverless functions don't support persistent file storage
- **Fly.io**: Use volumes for persistent storage

### Environment Variables Needed:
- `ANTHROPIC_API_KEY` - Claude API key
- `DEDALUS_API_KEY` - Dedalus Labs API key (optional)
- `SECRET_KEY` - Flask session secret (generate random string)
- `PORT` - Usually set automatically by platform
- `ENVIRONMENT` - Set to `production` for HTTPS cookies

### Production Checklist:
- [x] `gunicorn` in requirements.txt
- [x] Build script ensures gunicorn is installed
- [x] Start command uses `python -m gunicorn`
- [ ] Set `ENVIRONMENT=production` for HTTPS cookies
- [ ] Use strong `SECRET_KEY`
- [ ] Configure CORS properly for your domain
- [ ] Set up proper error logging

### Dedalus Events API
The `dedalus_events.py` FastAPI server runs separately. For production:
- Option 1: Run it as a separate service on Render
- Option 2: Integrate it into the Flask app
- Option 3: Use the cloud Dedalus Labs API instead

---

## Quick Start with Render:

```bash
# 1. Ensure requirements.txt includes gunicorn
# 2. Push to GitHub
git add .
git commit -m "Prepare for deployment"
git push

# 3. Go to render.com and connect repo
# 4. Use build command: bash build.sh
# 5. Use start command: python -m gunicorn server:app --bind 0.0.0.0:$PORT
# 6. Deploy!
```

Your app will be live at: `https://your-app-name.onrender.com`
