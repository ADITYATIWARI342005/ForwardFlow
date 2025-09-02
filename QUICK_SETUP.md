# 🚀 Quick Setup Guide - CNCF Issue Tracker Bot

## ⚡ 5-Minute Setup

### 1. 📝 Customize Repositories (1 minute)
Edit `config.py` and replace the repository list with your 10 CNCF projects:

```python
REPOSITORIES = [
    "your-project/repo1",
    "your-project/repo2",
    # ... add your 10 repositories
]
```

### 2. 🚀 Deploy to Railway (2 minutes)

**Option A: GitHub + Railway (Recommended)**
```bash
# Push to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# Deploy on Railway
# 1. Go to railway.app
# 2. Sign up with GitHub
# 3. Click "Deploy from GitHub repo"
# 4. Select your repository
```

**Option B: Direct Railway CLI**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### 3. ⚙️ Set Environment Variables (1 minute)
In Railway dashboard → Variables:
```
TELEGRAM_BOT_TOKEN = 8450859348:AAEprYshWYOz3MEFgXSaE65TooRI8b9Ygyg
TELEGRAM_CHAT_ID = 5757790216
CHECK_INTERVAL = 180
GITHUB_TOKEN = your_token_here (optional)
```

### 4. 🎯 Test Your Bot (1 minute)
- Check Railway logs
- You should receive a startup message on Telegram
- Bot will start monitoring repositories

## ✅ What You Get

- 🤖 **24/7 Monitoring** of your 10 repositories
- 📱 **Real-time Notifications** for new issues
- 🎨 **Clean Chat Format** with issue details
- ⚡ **1-4 Minute Checks** (configurable)
- 🛡️ **Rate Limit Protection**
- 🔄 **Auto-restart** on failures

## 🎉 Success!

Your bot will:
1. Send startup notification with repository list
2. Monitor repositories every 3 minutes (or your chosen interval)
3. Send beautiful notifications for new issues
4. Run continuously on Railway's free tier

## 🆘 Need Help?

- 📚 Full documentation: `README.md`
- 🧪 Test locally: `python test_bot.py`
- 🚀 Deploy script: `deploy.bat` (Windows) or `deploy.sh` (Linux/Mac)
- 📧 Check Railway logs for any errors

**Your bot is ready to track CNCF issues! 🎯**
