# Employee Feedback Agent — Deployment Guide

## Option 1: Docker Compose (Recommended for Demo)

```bash
# 1. Copy environment file and add your Groq API key
cp .env.example .env
# Edit .env and set GROQ_API_KEY=gsk_...

# 2. Start all services
docker-compose up --build -d

# 3. Seed sample data (optional)
docker-compose exec app python scripts/seed_data.py

# 4. Open dashboard
# http://localhost:8000
```

## Option 2: Railway (Free Cloud Deployment)

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add a **MongoDB** plugin (Railway MongoDB or MongoDB Atlas free tier)
4. Set environment variables:
   - `GROQ_API_KEY` = your Groq API key
   - `MONGODB_URI` = your MongoDB connection string
   - `MONGODB_DB` = employee_feedback
5. Railway auto-detects the Dockerfile
6. Your live URL will be: `https://your-app.up.railway.app`

## Option 3: Render.com

1. Push to GitHub
2. Create a **Web Service** on [render.com](https://render.com)
3. Connect repo, set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add MongoDB Atlas (free M0 cluster) and set `MONGODB_URI`
5. Set `GROQ_API_KEY`

## Option 4: AWS EC2 + Docker

```bash
# On EC2 Ubuntu instance
sudo apt update && sudo apt install -y docker.io docker-compose
git clone <your-repo-url>
cd Employee_FeedBack_Agent
cp .env.example .env  # add keys
sudo docker-compose up --build -d
# Open port 8000 in Security Group
```

## Get Groq API Key (Free)

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up / log in
3. Create API key
4. Add to `.env` as `GROQ_API_KEY`

## Health Check

- App: `GET /health`
- API Status: `GET /api/status`
