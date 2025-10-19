@echo off
echo 🚀 CNCF Issue Tracker Bot - Deployment Script
echo ==============================================

REM Check if git is initialized
if not exist ".git" (
    echo 📁 Initializing git repository...
    git init
    git add .
    git commit -m "Initial commit: CNCF Issue Tracker Bot"
    echo ✅ Git repository initialized
) else (
    echo ✅ Git repository already exists
)

REM Check if remote origin is set
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo.
    echo 🔗 Please set your GitHub repository URL:
    echo    git remote add origin https://github.com/yourusername/cncf-issue-bot.git
    echo.
    echo 📝 Then push to GitHub:
    echo    git branch -M main
    echo    git push -u origin main
) else (
    echo ✅ Remote origin already configured
    echo 📤 Pushing to GitHub...
    git add .
    git commit -m "Update: CNCF Issue Tracker Bot" 2>nul || echo No changes to commit
    git push
)

echo.
echo 🎯 Next Steps for Sevalla Deployment:
echo ======================================
echo 1. 📋 Edit the repository list in config.py
echo 2. 🌐 Go to sevalla.com and login to your dashboard
echo 3. 🚀 Deploy your application from GitHub
echo 4. ⚙️  Set environment variables in Sevalla dashboard:
echo    • TELEGRAM_BOT_TOKEN = your_telegram_bot_token
echo    • TELEGRAM_CHAT_ID = your_chat_id
echo    • GITHUB_TOKEN = your_github_token (optional but recommended)
echo    • CHECK_INTERVAL = 180 (or your preferred interval in seconds)
echo    • PORT = (Sevalla sets this automatically)
echo.
echo 🔒 SECURITY: Never commit credentials to Git!
echo    Always set them as environment variables in Sevalla dashboard.
echo.
echo 🎉 Your bot will be deployed and start monitoring repositories!
echo.
echo 📚 For detailed instructions, see README.md
pause
