#!/bin/bash

echo "🚀 CNCF Issue Tracker Bot - Deployment Script"
echo "=============================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: CNCF Issue Tracker Bot"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Check if remote origin is set
if ! git remote get-url origin > /dev/null 2>&1; then
    echo ""
    echo "🔗 Please set your GitHub repository URL:"
    echo "   git remote add origin https://github.com/yourusername/cncf-issue-bot.git"
    echo ""
    echo "📝 Then push to GitHub:"
    echo "   git branch -M main"
    echo "   git push -u origin main"
else
    echo "✅ Remote origin already configured"
    echo "📤 Pushing to GitHub..."
    git add .
    git commit -m "Update: CNCF Issue Tracker Bot" 2>/dev/null || echo "No changes to commit"
    git push
fi

echo ""
echo "🎯 Next Steps:"
echo "==============="
echo "1. 📋 Edit the repository list in config.py"
echo "2. 🌐 Go to railway.app and sign up/login with GitHub"
echo "3. 🚀 Click 'Deploy from GitHub repo' and select this repository"
echo "4. ⚙️  Set environment variables in Railway dashboard:"
echo "   • TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>"
echo "   • TELEGRAM_CHAT_ID=<your_chat_id>"
echo "   • CHECK_INTERVAL=180 (or your preferred interval)"
echo "   • GITHUB_TOKEN=<your_github_personal_access_token> (optional but recommended)"
echo "   • Optional: LOG_LEVEL=INFO, BATCH_SIZE=3, BATCH_DELAY=2, NOTIFICATION_DELAY=1"
echo "   • If you attach a persistent volume: DB_PATH=/data/cncf_issues.db"
echo ""
echo "🎉 Your bot will be deployed and start monitoring repositories!"
echo ""
echo "📚 For detailed instructions, see README.md"
