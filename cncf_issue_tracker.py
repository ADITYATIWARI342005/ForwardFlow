#!/usr/bin/env python3
"""
CNCF Projects Issue Tracker Bot
Monitors public CNCF repositories for new issues and sends clean Telegram notifications.
Optimized for Railway/Render deployment.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
import aiohttp
import sqlite3
from dataclasses import dataclass

# Configuration
try:
    from config import REPOSITORIES, DEFAULT_CHECK_INTERVAL, DATABASE_PATH
except ImportError:
    # Fallback configuration if config.py doesn't exist
    REPOSITORIES = [
        "kubernetes/kubernetes",           # Kubernetes
        "prometheus/prometheus",          # Prometheus  
        "etcd-io/etcd",                  # etcd
        "containerd/containerd",         # containerd
        "envoyproxy/envoy",              # Envoy Proxy
        "helm/helm",                     # Helm
        "istio/istio",                   # Istio
        "jaegertracing/jaeger",          # Jaeger
        "fluent/fluentd",                # Fluentd
        "grpc/grpc",                     # gRPC
    ]
    DEFAULT_CHECK_INTERVAL = 180
    DATABASE_PATH = "cncf_issues.db"

@dataclass
class Config:
    github_token: str = os.getenv('GITHUB_TOKEN', '')
    telegram_bot_token: str = os.getenv('TELEGRAM_BOT_TOKEN', '8450859348:AAEprYshWYOz3MEFgXSaE65TooRI8b9Ygyg')
    telegram_chat_id: str = os.getenv('TELEGRAM_CHAT_ID', '5757790216')
    check_interval: int = int(os.getenv('CHECK_INTERVAL', str(DEFAULT_CHECK_INTERVAL)))
    db_path: str = os.getenv('DB_PATH', DATABASE_PATH)
    repositories: List[str] = REPOSITORIES

@dataclass
class Issue:
    id: int
    number: int
    title: str
    url: str
    created_at: str
    repository: str
    author: str

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracked_issues (
                issue_id INTEGER,
                repository TEXT,
                created_at TEXT,
                tracked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (issue_id, repository)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_issue_tracked(self, issue_id: int, repository: str) -> bool:
        """Check if an issue is already tracked."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT 1 FROM tracked_issues WHERE issue_id = ? AND repository = ?',
            (issue_id, repository)
        )
        
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def add_issue(self, issue: Issue):
        """Add a new issue to tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO tracked_issues (issue_id, repository, created_at)
                VALUES (?, ?, ?)
            ''', (issue.id, issue.repository, issue.created_at))
            conn.commit()
        except Exception as e:
            logging.error(f"Database error: {e}")
        finally:
            conn.close()

class GitHubAPI:
    def __init__(self, token: str = ""):
        self.token = token
        self.base_url = "https://api.github.com"
        # GitHub allows higher rate limits for public repos even without token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CNCF-Issue-Tracker-Bot/1.0'
        }
        
        # Add token if provided (recommended for higher rate limits)
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'
    
    async def get_recent_issues(self, repository: str, since_minutes: int = 10) -> List[Issue]:
        """Fetch recent issues from a public repository."""
        since_time = (datetime.utcnow() - timedelta(minutes=since_minutes)).isoformat() + 'Z'
        
        url = f"{self.base_url}/repos/{repository}/issues"
        params = {
            'state': 'open',
            'since': since_time,
            'sort': 'created',
            'direction': 'desc',
            'per_page': 20  # Reduced for efficiency
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        issues_data = await response.json()
                        # Filter out pull requests and parse issues
                        issues = []
                        for issue_data in issues_data:
                            if not issue_data.get('pull_request'):  # Exclude PRs
                                issues.append(self._parse_issue(issue_data, repository))
                        return issues
                    elif response.status == 403:
                        logging.warning(f"Rate limit hit for {repository}")
                        return []
                    elif response.status == 404:
                        logging.error(f"Repository {repository} not found or private")
                        return []
                    else:
                        logging.warning(f"HTTP {response.status} for {repository}")
                        return []
        except asyncio.TimeoutError:
            logging.warning(f"Timeout fetching issues for {repository}")
            return []
        except Exception as e:
            logging.error(f"Error fetching issues for {repository}: {str(e)}")
            return []
    
    def _parse_issue(self, issue_data: dict, repository: str) -> Issue:
        """Parse GitHub API issue data."""
        return Issue(
            id=issue_data['id'],
            number=issue_data['number'],
            title=issue_data['title'],
            url=issue_data['html_url'],
            created_at=issue_data['created_at'],
            repository=repository,
            author=issue_data['user']['login']
        )

class TelegramBot:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(self, message: str):
        """Send a message to Telegram chat."""
        url = f"{self.base_url}/sendMessage"
        
        data = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False,
            'disable_notification': False
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return True
                    else:
                        logging.error(f"Telegram API error: {response.status}")
                        return False
        except Exception as e:
            logging.error(f"Error sending Telegram message: {str(e)}")
            return False
    
    def format_issue_notification(self, issue: Issue) -> str:
        """Format issue into clean chat-style notification."""
        # Clean title for HTML
        title = issue.title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Truncate very long titles
        if len(title) > 80:
            title = title[:77] + "..."
        
        message = f"""🆕 <b>New Issue</b>

📋 <b>Title:</b> {title}
👤 <b>Author:</b> @{issue.author}
📦 <b>Repository:</b> <code>{issue.repository}</code>
🔗 <b>Link:</b> <a href="{issue.url}">#{issue.number}</a>"""
        
        return message

class CNCFIssueTracker:
    def __init__(self, config: Config):
        self.config = config
        self.github = GitHubAPI(config.github_token)
        self.telegram = TelegramBot(config.telegram_bot_token, config.telegram_chat_id)
        self.db = Database(config.db_path)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)
    
    async def check_all_repositories(self):
        """Check all repositories for new issues."""
        self.logger.info(f"🔍 Checking {len(self.config.repositories)} repositories...")
        
        new_issues_count = 0
        check_minutes = max(5, int(self.config.check_interval / 60) + 2)  # Buffer time
        
        # Process repositories in batches to avoid overwhelming APIs
        batch_size = 3
        for i in range(0, len(self.config.repositories), batch_size):
            batch = self.config.repositories[i:i+batch_size]
            
            tasks = []
            for repo in batch:
                tasks.append(self.check_repository(repo, check_minutes))
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, int):
                    new_issues_count += result
                elif isinstance(result, Exception):
                    self.logger.error(f"Batch error: {result}")
            
            # Small delay between batches
            if i + batch_size < len(self.config.repositories):
                await asyncio.sleep(2)
        
        if new_issues_count > 0:
            self.logger.info(f"✅ Found {new_issues_count} new issues")
        else:
            self.logger.info("📭 No new issues found")
        
        return new_issues_count
    
    async def check_repository(self, repository: str, since_minutes: int) -> int:
        """Check a single repository for new issues."""
        try:
            recent_issues = await self.github.get_recent_issues(repository, since_minutes)
            new_count = 0
            
            for issue in recent_issues:
                if not self.db.is_issue_tracked(issue.id, issue.repository):
                    # New issue found!
                    success = await self.notify_new_issue(issue)
                    if success:
                        self.db.add_issue(issue)
                        new_count += 1
                        self.logger.info(f"📢 Notified: {repository}#{issue.number}")
                    
                    # Rate limiting delay
                    await asyncio.sleep(1)
            
            return new_count
            
        except Exception as e:
            self.logger.error(f"❌ Error checking {repository}: {str(e)}")
            return 0
    
    async def notify_new_issue(self, issue: Issue) -> bool:
        """Send notification for a new issue."""
        message = self.telegram.format_issue_notification(issue)
        return await self.telegram.send_message(message)
    
    async def send_startup_notification(self):
        """Send startup notification."""
        repo_list = "\n".join([f"• <code>{repo}</code>" for repo in self.config.repositories[:5]])
        if len(self.config.repositories) > 5:
            repo_list += f"\n• ... and {len(self.config.repositories) - 5} more"
        
        message = f"""🚀 <b>CNCF Issue Tracker Started!</b>

⏰ <b>Check Interval:</b> {self.config.check_interval // 60} minutes
📦 <b>Monitoring {len(self.config.repositories)} repositories:</b>

{repo_list}

Bot is now monitoring for new issues! 🎯"""
        
        return await self.telegram.send_message(message)
    
    async def run(self):
        """Main monitoring loop."""
        self.logger.info("🤖 Starting CNCF Issue Tracker Bot...")
        
        # Send startup notification
        startup_success = await self.send_startup_notification()
        if not startup_success:
            self.logger.error("❌ Failed to send startup notification. Check Telegram credentials.")
            return
        
        self.logger.info(f"✅ Bot started - checking every {self.config.check_interval} seconds")
        
        # Main monitoring loop
        while True:
            try:
                await self.check_all_repositories()
                
                # Wait for next check
                self.logger.info(f"⏳ Next check in {self.config.check_interval // 60} minutes...")
                await asyncio.sleep(self.config.check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Bot stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Unexpected error: {str(e)}")
                # Send error notification
                error_msg = f"⚠️ <b>Bot Error</b>\n\nError: <code>{str(e)}</code>\n\nRetrying in 2 minutes..."
                await self.telegram.send_message(error_msg)
                await asyncio.sleep(120)  # Wait 2 minutes before retrying

def main():
    """Entry point."""
    config = Config()
    
    # Validate configuration
    if not config.telegram_bot_token or not config.telegram_chat_id:
        print("❌ Error: Telegram credentials not configured")
        return
    
    if not config.repositories:
        print("❌ Error: No repositories configured")
        return
    
    # Log configuration
    print(f"🔧 Configuration:")
    print(f"   • Check interval: {config.check_interval // 60} minutes")
    print(f"   • Repositories: {len(config.repositories)}")
    print(f"   • GitHub token: {'✅ Configured' if config.github_token else '❌ Not set (using public API)'}")
    print(f"   • Telegram: ✅ Configured")
    
    # Start the tracker
    tracker = CNCFIssueTracker(config)
    asyncio.run(tracker.run())

if __name__ == "__main__":
    main()
