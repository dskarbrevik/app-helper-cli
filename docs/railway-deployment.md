# Railway Deployment Guide

Detailed guide for deploying your FastAPI backend to Railway.

## Overview

Railway is a modern platform-as-a-service (PaaS) that automatically deploys and scales your applications. This guide covers:
- Creating a backend repository from the template
- Deploying to Railway from GitHub
- Configuring custom domains and environment variables
- Monitoring and debugging
- Cost management

## Prerequisites

- GitHub account with your backend repository
- Railway account (sign up at [railway.app](https://railway.app))
- Backend code based on `hello-world-be` template

## Create Backend Repository

### Use GitHub Template

1. Visit [hello-world-be repository](https://github.com/your-org/hello-world-be)
2. Click **Use this template** → **Create a new repository**
3. Configure:
   - **Owner:** Your GitHub username or organization
   - **Repository name:** `your-app-be` (or your chosen name)
   - **Visibility:** Private (recommended) or Public
4. Click **Create repository**

### Clone Locally (Optional)

If you want to test locally first:

```bash
git clone https://github.com/your-username/your-app-be.git
cd your-app-be

# Test locally
make setup
make validate
make dev

# Test endpoint
curl http://localhost:8000/
```

## Deploy to Railway

### Initial Deployment

1. **Sign in to Railway**
   - Visit [railway.app](https://railway.app)
   - Click **Login** → **Login with GitHub**
   - Authorize Railway to access your repositories

2. **Create New Project**
   - From Railway Dashboard, click **New Project**
   - Select **Deploy from GitHub repo**
   - Choose your `your-app-be` repository
   - Click **Deploy Now**

3. **Auto-Detection**
   Railway automatically detects:
   - Python runtime (from `main.py` and `pyproject.toml`)
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Wait for Build**
   - Initial build takes ~2-3 minutes
   - Watch build logs in real-time
   - Look for "Build successful" and "Deployment successful"

### Generate Public Domain

By default, Railway deployments are private. To make your API accessible:

1. Click on your deployment in Railway dashboard
2. Click **Settings** tab
3. Scroll to **Networking** section
4. Click **Generate Domain**
5. Railway creates a public URL: `your-app-be-production.up.railway.app`
6. Copy this URL (you'll need it for frontend configuration)

### Verify Deployment

Test your deployed API:

```bash
# Test root endpoint
curl https://your-app-be-production.up.railway.app/

# Expected response:
# {"message": "Hello World from FastAPI Backend!", "status": "success"}

# Test API endpoint
curl https://your-app-be-production.up.railway.app/api/hello

# Expected response:
# {"message": "Hello from the backend!", "timestamp": "2024-12-27T..."}
```

## Configuration

### Environment Variables

Add environment variables for production configuration:

1. Click on your service in Railway dashboard
2. Go to **Variables** tab
3. Click **+ New Variable**

**Common variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Server port | Auto-set by Railway |
| `DATABASE_URL` | Database connection | From Railway Postgres |
| `CORS_ORIGINS` | Allowed frontend origins | `https://your-app.vercel.app` |
| `LOG_LEVEL` | Logging level | `info` or `debug` |

**Add CORS origins:**
```
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### Custom Build/Start Commands

If you need custom commands:

1. Go to **Settings** tab
2. Scroll to **Build** section

**Build Command (optional):**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Railway uses the `PORT` environment variable automatically.

### Custom Domain (Optional)

Use your own domain instead of Railway's:

1. Go to **Settings** → **Networking**
2. Click **Custom Domain**
3. Enter your domain: `api.yourdomain.com`
4. Add CNAME record to your DNS:
   - **Name:** `api`
   - **Value:** `your-app-be-production.up.railway.app`
5. Wait for DNS propagation (~5 minutes to 48 hours)
6. Railway automatically provisions SSL certificate

## Monitoring & Debugging

### View Logs

Real-time logs help debug issues:

1. Click on your service
2. Go to **Deployments** tab
3. Click on latest deployment
4. View **Build Logs** and **Deploy Logs**

**Log commands:**
```bash
# Filter by level
# Look for ERROR, WARNING, INFO

# Common issues in logs:
# - Module not found: Missing dependency
# - Port binding errors: Check PORT variable
# - Connection refused: Database/service unavailable
```

### Metrics

Monitor your application performance:

1. Go to **Metrics** tab
2. View:
   - **CPU usage**
   - **Memory usage**
   - **Network traffic**
   - **Request count**

**Scaling triggers:**
- CPU consistently > 80%: Consider scaling
- Memory near limit: Increase memory or optimize code
- High request latency: Check database queries

### Deployment History

View past deployments:

1. Go to **Deployments** tab
2. See all deployments with:
   - Build time
   - Deploy time
   - Commit SHA
   - Status (success/failed)

**Rollback to previous version:**
1. Click on a previous successful deployment
2. Click **Redeploy**

## CI/CD & Auto-Deployment

### Automatic Deployments

Railway auto-deploys on every push to your repository:

**Workflow:**
1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Add new endpoint"
   git push origin main
   ```
3. Railway detects push and builds automatically
4. New version deployed in ~2-3 minutes

### Branch Deployments

Deploy multiple branches for testing:

1. Go to **Settings** → **Source**
2. Change **Branch** from `main` to your feature branch
3. Railway deploys that branch
4. Get a separate URL for testing

**Use case:** Deploy `staging` branch to test before merging to `main`.

### Disable Auto-Deploy

For manual control:

1. Go to **Settings** → **Source**
2. Toggle **Auto Deploy** off
3. Manually trigger deployments by clicking **Deploy**

## Database Integration

### Add PostgreSQL Database

If your app needs a database:

1. In your project, click **+ New**
2. Select **Database** → **PostgreSQL**
3. Railway provisions a database in ~30 seconds
4. Environment variable `DATABASE_URL` is automatically added

**Access in your FastAPI app:**
```python
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
```

### Database Backups

Railway automatically backs up databases daily (on paid plans).

**Manual backup:**
1. Install Railway CLI: `npm i -g @railway/cli`
2. Link project: `railway link`
3. Dump database:
   ```bash
   railway run pg_dump $DATABASE_URL > backup.sql
   ```

## Troubleshooting

### Build Fails

**Issue:** Build fails with "Module not found"

**Solution:**
1. Check `requirements.txt` includes all dependencies
2. Regenerate requirements:
   ```bash
   pip freeze > requirements.txt
   git add requirements.txt
   git commit -m "Update requirements"
   git push
   ```

### Deployment Fails

**Issue:** Build succeeds but deployment fails

**Solution:**
1. Check **Deploy Logs** for errors
2. Verify start command is correct
3. Ensure app binds to `0.0.0.0` and `$PORT`:
   ```python
   uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
   ```

### API Not Accessible

**Issue:** Domain generated but curl returns timeout

**Solution:**
1. Verify domain was generated in **Settings** → **Networking**
2. Check service is running (green status in dashboard)
3. View logs for startup errors
4. Test with Railway's internal URL first

### CORS Errors from Frontend

**Issue:** Frontend gets CORS errors when calling API

**Solution:**
1. Add `CORS_ORIGINS` environment variable
2. Update FastAPI CORS middleware:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   origins = os.getenv("CORS_ORIGINS", "").split(",")
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=origins,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
3. Redeploy

### High Memory Usage

**Issue:** App crashes with "Out of memory"

**Solution:**
1. Check for memory leaks in code
2. Optimize database queries
3. Increase memory limit in Railway (paid plans)
4. Use connection pooling for databases

## Cost Management

### Free Tier

Railway free tier includes:
- $5 credit per month
- ~500 hours of compute time
- Suitable for hobby projects and testing

**Usage monitoring:**
1. Go to **Settings** → **Usage**
2. View estimated monthly cost
3. Set up usage alerts

### Paid Plans

**When to upgrade:**
- Need more than $5/month resources
- Want custom domains
- Need database backups
- Require higher uptime SLA

**Pricing:** Pay-as-you-go based on:
- CPU time (per hour)
- Memory (per GB-hour)
- Network egress (per GB)

### Optimize Costs

**Tips to reduce usage:**
1. **Sleep unused services:** Pause services when not needed
2. **Right-size resources:** Don't over-provision memory/CPU
3. **Efficient code:** Optimize database queries, cache responses
4. **Use Railway Volumes:** Store files instead of memory
5. **Monitor metrics:** Identify spikes and optimize

## Advanced Configuration

### Health Checks

Add health check endpoint:

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

Railway can monitor this endpoint to restart unhealthy services.

### Multiple Environments

Deploy staging and production:

**Option 1: Separate Projects**
1. Create two Railway projects
2. One deploys from `main` branch
3. One deploys from `staging` branch

**Option 2: PR Environments**
1. Enable PR deployments in Settings
2. Each PR gets a temporary deployment
3. Test changes before merging

### Background Workers

Run background tasks alongside API:

1. Add separate service in same project
2. Click **+ New** → **Empty Service**
3. Set start command to worker script:
   ```bash
   python worker.py
   ```
4. Share environment variables between services

## Railway CLI

### Installation

```bash
npm i -g @railway/cli
```

### Useful Commands

```bash
# Link local project to Railway
railway link

# View logs
railway logs

# Run commands in Railway environment
railway run python manage.py migrate

# Deploy from CLI
railway up

# Open dashboard
railway open
```

## Next Steps

- Configure frontend to use your Railway API URL
- Set up monitoring and alerts
- Configure custom domain
- [Vercel Deployment](vercel-deployment.md) - Deploy your frontend
- [Main Deployment Guide](../DEPLOYMENT_GUIDE.md) - Complete workflow

## Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway Templates](https://railway.app/templates)
- [Railway Discord](https://discord.gg/railway) - Community support
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
