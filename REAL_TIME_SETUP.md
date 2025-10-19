# 🚀 CNCF Issue Tracker - Real-Time Webhook Setup Guide

## 🎯 **Why Your Bot Wasn't Working**

Your original bot had these issues:
1. **Duplicate code files** causing import errors
2. **Polling-based** (3-minute delays) instead of real-time
3. **Missing webhook configuration** for GitHub
4. **Incorrect Sevalla configuration**

## ⚡ **New Real-Time Solution**

The new `cncf_issue_tracker_webhook.py` provides:
- **TRUE real-time notifications** (instant when issues are created)
- **GitHub webhook integration** (no polling delays)
- **Proper Sevalla configuration**
- **Fixed import issues**

## 🔧 **Setup Instructions**

### Step 1: Deploy to Sevalla

1. **Push your updated code to GitHub**:
   ```bash
   git add .
   git commit -m "Add real-time webhook support"
   git push
   ```

2. **Deploy on Sevalla**:
   - Go to [sevalla.com](https://sevalla.com)
   - Connect your GitHub repository
   - Deploy the application

### Step 2: Configure Environment Variables

In your Sevalla dashboard, set these environment variables:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GITHUB_WEBHOOK_SECRET=your_random_secret_string

# Optional (but recommended)
GITHUB_TOKEN=your_github_personal_access_token
LOG_LEVEL=INFO
DB_PATH=/data/cncf_issues.db
```

### Step 3: Set Up GitHub Webhooks

For **EACH repository** you want to monitor:

1. **Go to repository Settings** → **Webhooks** → **Add webhook**
2. **Payload URL**: `https://your-sevalla-app-url.com/webhook`
3. **Content type**: `application/json`
4. **Secret**: Use the same value as `GITHUB_WEBHOOK_SECRET`
5. **Events**: Select "Issues" (uncheck others)
6. **Active**: ✅ Checked
7. **Click "Add webhook"**

### Step 4: Test the Setup

1. **Check Sevalla logs** for startup message
2. **Create a test issue** in one of your monitored repositories
3. **Verify instant notification** in Telegram

## 📋 **Repository List**

Edit `config.py` to customize which repositories to monitor:

```python
REPOSITORIES = [
    "prometheus/prometheus",
    "envoyproxy/envoy",
    "jaegertracing/jaeger",
    "cilium/cilium",
    # Add your repositories here
]
```

## 🔒 **Security Notes**

- **Never commit secrets** to Git
- **Use strong webhook secrets** (random strings)
- **Verify webhook signatures** (built-in)
- **Monitor webhook deliveries** in GitHub

## 🚨 **Troubleshooting**

### Bot Not Starting
- Check Sevalla logs for errors
- Verify all environment variables are set
- Ensure `cncf_issue_tracker_webhook.py` is the main file

### No Notifications
- Verify webhook URLs are correct
- Check webhook secret matches environment variable
- Ensure repositories are in your monitoring list
- Test webhook delivery in GitHub settings

### Database Issues
- Check if persistent storage is available
- Verify database path permissions
- Monitor Sevalla logs for database errors

## 🎉 **Expected Results**

With this setup, you'll get:
- **Instant notifications** when issues are created
- **No polling delays** (true real-time)
- **Reliable webhook delivery**
- **Proper error handling**
- **Sevalla platform compatibility**

## 📊 **Monitoring**

- **Startup notification**: Confirms bot is running
- **Real-time issue notifications**: Instant delivery
- **Error notifications**: Automatic error reporting
- **Health check endpoint**: `/health` for monitoring

Your bot will now provide **true real-time notifications** instead of the previous 3-minute polling delays!
