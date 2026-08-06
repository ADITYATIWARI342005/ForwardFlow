#!/usr/bin/env python3
"""
Test script for CNCF Issue Tracker Bot
Tests configuration and Telegram connection locally.
"""

import os
import asyncio
import sys
from cncf_issue_tracker import Config, TelegramBot, CNCFIssueTracker

async def test_telegram_connection():
    """Test Telegram bot connection."""
    print("🔍 Testing Telegram connection...")
    
    config = Config()
    
    if not config.telegram_bot_token or not config.telegram_chat_id:
        print("❌ Error: Telegram credentials not configured")
        return False
    
    bot = TelegramBot(config.telegram_bot_token, config.telegram_chat_id)
    
    # Test message
    test_message = """🧪 <b>Test Message</b>

This is a test message from your CNCF Issue Tracker Bot.

✅ If you receive this, your bot is working correctly!
🎯 Ready to monitor repositories for new issues."""
    
    try:
        success = await bot.send_message(test_message)
        if success:
            print("✅ Telegram connection successful! Check your Telegram chat.")
            return True
        else:
            print("❌ Failed to send Telegram message")
            return False
    except Exception as e:
        print(f"❌ Error testing Telegram: {str(e)}")
        return False

async def test_configuration():
    """Test bot configuration."""
    print("🔧 Testing configuration...")
    
    config = Config()
    
    print(f"   • Check interval: {config.check_interval} seconds ({config.check_interval // 60} minutes)")
    print(f"   • Repositories: {len(config.repositories)}")
    print(f"   • GitHub token: {'✅ Configured' if config.github_token else '❌ Not set (using public API)'}")
    print(f"   • Telegram token: {'✅ Configured' if config.telegram_bot_token else '❌ Not set'}")
    print(f"   • Telegram chat ID: {'✅ Configured' if config.telegram_chat_id else '❌ Not set'}")
    print(f"   • Database path: {config.db_path}")
    
    print("\n📦 Repositories to monitor:")
    for i, repo in enumerate(config.repositories, 1):
        print(f"   {i:2d}. {repo}")
    
    return True

async def test_github_api():
    """Test GitHub API connection."""
    print("\n🔍 Testing GitHub API connection...")
    
    config = Config()
    
    if not config.repositories:
        print("❌ No repositories configured")
        return False
    
    # Test with first repository
    test_repo = config.repositories[0]
    print(f"   • Testing with: {test_repo}")
    
    try:
        from cncf_issue_tracker import GitHubAPI
        github = GitHubAPI(config.github_token)
        
        # Test API call
        issues = await github.get_recent_issues(test_repo, since_minutes=60)
        print(f"   • API call successful: {len(issues)} recent issues found")
        return True
        
    except Exception as e:
        print(f"   • API call failed: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("🧪 CNCF Issue Tracker Bot - Test Suite")
    print("=" * 50)
    
    # Test configuration
    config_ok = await test_configuration()
    if not config_ok:
        print("❌ Configuration test failed")
        return
    
    # Test GitHub API
    github_ok = await test_github_api()
    if not github_ok:
        print("⚠️  GitHub API test failed (this might be expected without token)")
    
    # Test Telegram
    telegram_ok = await test_telegram_connection()
    if not telegram_ok:
        print("❌ Telegram test failed")
        return
    
    print("\n🎉 All tests completed!")
    print("✅ Your bot is ready for deployment to Railway!")
    
    print("\n📋 Next steps:")
    print("   1. Push this code to GitHub")
    print("   2. Deploy to Railway")
    print("   3. Set environment variables in Railway dashboard")
    print("   4. Your bot will start monitoring repositories!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        sys.exit(1)