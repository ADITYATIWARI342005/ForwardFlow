# CNCF Issue Tracker Bot

A Telegram bot that monitors CNCF and open source repositories for new issues and sends clean, formatted notifications.

## 🚀 Features

- **Real-time Monitoring**: Checks repositories every 1-4 minutes (configurable)
- **Clean Notifications**: Beautiful Telegram messages with issue details
- **Smart Tracking**: Prevents duplicate notifications using SQLite database
- **Rate Limit Protection**: Built-in GitHub API rate limiting protection
- **Batch Processing**: Efficiently processes multiple repositories
- **Error Handling**: Automatic retry and error notifications

## 📱 Notification Format

Each notification includes:
- 🆕 Issue title
- 👤 Author username
- 📦 Repository name
- 🔗 Direct GitHub link

## ⚙️ Configuration

### Environment Variables

Set these in your Railway dashboard (no hardcoded secrets in code):

```bash
GITHUB_TOKEN=<your_github_personal_access_token>   # Optional but recommended
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
TELEGRAM_CHAT_ID=<your_chat_id>
CHECK_INTERVAL=180                                  # 3 minutes (60-240 seconds)
# Optional tuning (defaults shown):
# LOG_LEVEL=INFO
# BATCH_SIZE=3
# BATCH_DELAY=2
# NOTIFICATION_DELAY=1
# API_TIMEOUT=10
# CHECK_BUFFER_MINUTES=2
# DB_PATH=/data/cncf_issues.db   # If you mount Railway persistent volume
```

### Repository List

Edit the repository list in `config.py` with your 10 repositories:

```python
REPOSITORIES = [
    "kubernetes/kubernetes",
    "prometheus/prometheus",
    # ...
]
```

## 🚀 Railway Deployment

### Option 1: Deploy from GitHub (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/cncf-issue-bot.git
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Visit [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "Deploy from GitHub repo"
   - Select your repository

### Option 2: Direct Deployment

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy**:
   ```bash
   railway login
   railway init
   railway up
   ```

## 🔧 Environment Variables Setup

In your Railway dashboard:

1. Go to your project → Variables
2. Add these environment variables:
   - `GITHUB_TOKEN`: Your GitHub personal access token
   - `TELEGRAM_BOT_TOKEN`: 8450859348:AAEprYshWYOz3MEFgXSaE65TooRI8b9Ygyg
   - `TELEGRAM_CHAT_ID`: 5757790216
   - `CHECK_INTERVAL`: 180 (or your preferred interval)

## 📊 Check Intervals

- `60` = 1 minute
- `120` = 2 minutes  
- `180` = 3 minutes (default)
- `240` = 4 minutes

## 🎯 Popular CNCF Projects

Here are some popular CNCF projects you might want to monitor:

- `kubernetes/kubernetes` - Kubernetes
- `prometheus/prometheus` - Prometheus
- `etcd-io/etcd` - etcd
- `containerd/containerd` - containerd
- `envoyproxy/envoy` - Envoy Proxy
- `helm/helm` - Helm
- `istio/istio` - Istio
- `jaegertracing/jaeger` - Jaeger
- `fluent/fluentd` - Fluentd
- `grpc/grpc` - gRPC
- `linkerd/linkerd2` - Linkerd
- `cilium/cilium` - Cilium

## 🔍 How It Works

1. **Startup**: Bot sends startup notification with repository list
2. **Monitoring**: Checks each repository every configured interval
3. **Issue Detection**: Fetches recent issues using GitHub API
4. **Deduplication**: Uses SQLite database to track seen issues
5. **Notification**: Sends formatted Telegram message for new issues
6. **Error Handling**: Automatic retry and error notifications

## 🛡️ Rate Limiting

- **Without GitHub Token**: 60 requests/hour per IP
- **With GitHub Token**: 5,000 requests/hour
- **Batch Processing**: Processes repositories in groups of 3
- **Smart Delays**: Built-in delays between API calls

## 📝 Local Testing

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export TELEGRAM_BOT_TOKEN="8450859348:AAEprYshWYOz3MEFgXSaE65TooRI8b9Ygyg"
   export TELEGRAM_CHAT_ID="5757790216"
   export CHECK_INTERVAL="180"
   ```

3. **Run the bot**:
   ```bash
   python cncf_issue_tracker.py
   ```

## 🚨 Troubleshooting

### Common Issues

1. **Telegram Bot Not Responding**:
   - Check bot token and chat ID
   - Ensure bot is added to your chat
   - Verify bot has permission to send messages

2. **GitHub API Errors**:
   - Check rate limits
   - Verify repository names are correct
   - Ensure repositories are public

3. **Bot Not Starting**:
   - Check environment variables
   - Verify Python version (3.7+)
   - Check Railway logs

### Logs

The bot provides detailed logging:
- Startup information
- Repository checking status
- New issue notifications
- Error messages
- Rate limit warnings

## 📈 Monitoring

- **Startup Notification**: Sent when bot starts
- **Issue Notifications**: Real-time for new issues
- **Error Notifications**: Automatic error reporting
- **Activity Logs**: Detailed logging in Railway dashboard

## 🎉 Success!

Once deployed, you'll receive:
1. **Startup notification** with repository list
2. **Real-time issue notifications** as they're created
3. **Error notifications** if something goes wrong
4. **24/7 monitoring** of your chosen repositories

The bot will run continuously and automatically restart on failures thanks to Railway's restart policy!
