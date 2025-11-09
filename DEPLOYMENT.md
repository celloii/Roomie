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
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn server:app`
   - Environment: `Python 3`

4. **Set Environment Variables** in Render dashboard:
   ```
   ANTHROPIC_API_KEY=your_key_here
   DEDALUS_API_KEY=your_key_here
   SECRET_KEY=generate_a_random_secret_key
   PORT=10000
   ```

5. **Deploy!** Render will automatically build and deploy your app.

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
6. Deploy!

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

### Production Checklist:
- [ ] Set `FLASK_DEBUG=False` or remove debug mode
- [ ] Use strong `SECRET_KEY`
- [ ] Set `SESSION_COOKIE_SECURE=True` for HTTPS
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
# 4. Deploy!
```

Your app will be live at: `https://your-app-name.onrender.com`

