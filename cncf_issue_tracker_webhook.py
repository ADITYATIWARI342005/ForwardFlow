#!/usr/bin/env python3
"""
CNCF Projects Issue Tracker Bot - Webhook Version
Provides TRUE real-time notifications using GitHub webhooks.
Optimized for Sevalla deployment.
"""

import os
import asyncio
import logging
import json
import hmac
import hashlib
from datetime import datetime
from typing import List, Dict, Any
import aiohttp
from aiohttp import web
import sqlite3
from dataclasses import dataclass, field

# Import configuration
try:
    from config import (
        REPOSITORIES,
        DEFAULT_CHECK_INTERVAL,
        DATABASE_PATH,
        LOG_LEVEL,
        BATCH_SIZE,
        BATCH_DELAY,
        NOTIFICATION_DELAY,
        API_TIMEOUT,
        CHECK_BUFFER_MINUTES,
    )
except ImportError:
    # Fallback configuration
    REPOSITORIES = [
        "prometheus/prometheus",
        "prometheus/client_golang",
        "open-telemetry/opentelemetry-collector-contrib",
        "prometheus/docs",
        "envoyproxy/gateway",
        "envoyproxy/envoy",
        "jaegertracing/jaeger",
        "jaegertracing/jaeger-operator",
        "jaegertracing/helm-charts",
        "jaegertracing/documentation",
        "jaegertracing/jaeger-ui",
        "cilium/cilium.io",
        "cilium/cilium",
        "cilium/hubble-ui"
    ]
    DEFAULT_CHECK_INTERVAL = 60
    DATABASE_PATH = "cncf_issues.db"
    LOG_LEVEL = "INFO"
    BATCH_SIZE = 3
    BATCH_DELAY = 2
    NOTIFICATION_DELAY = 1
    API_TIMEOUT = 10
    CHECK_BUFFER_MINUTES = 2

def resolve_default_db_path(default_path: str) -> str:
    """Select a safe database path for Sevalla."""
    try:
        for path in ["/var/lib/data", "/data", "/app/data"]:
            if os.path.isdir(path):
                db_path = os.path.join(path, "cncf_issues.db")
                try:
                    test_file = os.path.join(path, ".write_test")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    logging.info(f"Using persistent storage: {db_path}")
                    return db_path
                except Exception:
                    continue
        
        if os.path.isdir("/tmp"):
            logging.warning("Using ephemeral storage /tmp - data will be lost on restart!")
            return "/tmp/cncf_issues.db"
    except Exception as e:
        logging.warning(f"Error resolving DB path: {e}")
    
    logging.warning(f"Using local path: {default_path}")
    return default_path

@dataclass
class Config:
    github_token: str = os.getenv('GITHUB_TOKEN', '')
    telegram_bot_token: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    telegram_chat_id: str = os.getenv('TELEGRAM_CHAT_ID', '')
    github_webhook_secret: str = os.getenv('GITHUB_WEBHOOK_SECRET', '')
    port: int = int(os.getenv('PORT', '8080'))
    db_path: str = os.getenv('DB_PATH', resolve_default_db_path(DATABASE_PATH))
    repositories: List[str] = field(default_factory=list)
    log_level: str = os.getenv('LOG_LEVEL', LOG_LEVEL)

    def __post_init__(self):
        if not self.repositories:
            self.repositories = list(REPOSITORIES)

@dataclass
class Issue:
    id: int
    number: int
    title: str
    url: str
    created_at: str
    repository: str
    author: str
    labels: List[str]

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database."""
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
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
            logging.info(f"✅ Database initialized: {self.db_path}")
        except Exception as e:
            logging.error(f"❌ Database initialization error: {e}")
            raise
    
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
        title = issue.title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        if len(title) > 80:
            title = title[:77] + "..."
        
        labels_line = ""
        if issue.labels:
            safe_labels = []
            for name in issue.labels[:6]:
                safe = name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                if len(safe) > 20:
                    safe = safe[:17] + "..."
                safe_labels.append(f"<code>{safe}</code>")
            labels_line = "\n🏷️ <b>Labels:</b> " + ", ".join(safe_labels)
        
        message = f"""🆕 <b>New Issue</b>

📋 <b>Title:</b> {title}
👤 <b>Author:</b> @{issue.author}
📦 <b>Repository:</b> <code>{issue.repository}</code>
🔗 <b>Link:</b> <a href="{issue.url}">#{issue.number}</a>{labels_line}"""
        
        return message

class CNCFIssueTracker:
    def __init__(self, config: Config):
        self.config = config
        self.telegram = TelegramBot(config.telegram_bot_token, config.telegram_chat_id)
        self.db = Database(config.db_path)
        
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper(), logging.INFO),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        if not self.config.github_webhook_secret:
            self.logger.warning("No webhook secret configured - skipping signature verification")
            return True
        
        expected_signature = 'sha256=' + hmac.new(
            self.config.github_webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def parse_issue_from_webhook(self, payload: Dict[str, Any]) -> Issue:
        """Parse issue data from GitHub webhook payload."""
        issue_data = payload['issue']
        repository = payload['repository']['full_name']
        
        labels = []
        try:
            labels = [label['name'] for label in issue_data.get('labels', [])]
        except Exception:
            labels = []
        
        return Issue(
            id=issue_data['id'],
            number=issue_data['number'],
            title=issue_data['title'],
            url=issue_data['html_url'],
            created_at=issue_data['created_at'],
            repository=repository,
            author=issue_data['user']['login'],
            labels=labels,
        )
    
    async def handle_webhook(self, request):
        """Handle GitHub webhook requests."""
        try:
            # Get headers
            signature = request.headers.get('X-Hub-Signature-256', '')
            event_type = request.headers.get('X-GitHub-Event', '')
            
            # Read payload
            payload_bytes = await request.read()
            
            # Verify signature
            if not self.verify_webhook_signature(payload_bytes, signature):
                self.logger.warning("Invalid webhook signature")
                return web.Response(text="Unauthorized", status=401)
            
            # Parse JSON
            try:
                payload = json.loads(payload_bytes.decode('utf-8'))
            except json.JSONDecodeError:
                self.logger.error("Invalid JSON payload")
                return web.Response(text="Invalid JSON", status=400)
            
            # Handle different event types
            if event_type == 'issues' and payload.get('action') == 'opened':
                await self.handle_new_issue(payload)
            elif event_type == 'ping':
                self.logger.info("Received webhook ping from GitHub")
                return web.Response(text="Pong", status=200)
            else:
                self.logger.info(f"Ignoring event: {event_type}")
            
            return web.Response(text="OK", status=200)
            
        except Exception as e:
            self.logger.error(f"Error handling webhook: {str(e)}")
            return web.Response(text="Internal Server Error", status=500)
    
    async def handle_new_issue(self, payload: Dict[str, Any]):
        """Handle new issue webhook."""
        try:
            issue = self.parse_issue_from_webhook(payload)
            
            # Check if repository is in our monitoring list
            if issue.repository not in self.config.repositories:
                self.logger.info(f"Ignoring issue from unmonitored repository: {issue.repository}")
                return
            
            # Check if we've already tracked this issue
            if self.db.is_issue_tracked(issue.id, issue.repository):
                self.logger.info(f"Issue already tracked: {issue.repository}#{issue.number}")
                return
            
            # Send notification
            message = self.telegram.format_issue_notification(issue)
            success = await self.telegram.send_message(message)
            
            if success:
                self.db.add_issue(issue)
                self.logger.info(f"📢 Real-time notification sent: {issue.repository}#{issue.number}")
            else:
                self.logger.error(f"Failed to send notification for {issue.repository}#{issue.number}")
                
        except Exception as e:
            self.logger.error(f"Error handling new issue: {str(e)}")
    
    async def send_startup_notification(self):
        """Send startup notification."""
        repo_list = "\n".join([f"• <code>{repo}</code>" for repo in self.config.repositories[:5]])
        if len(self.config.repositories) > 5:
            repo_list += f"\n• ... and {len(self.config.repositories) - 5} more"
        
        message = f"""🚀 <b>CNCF Issue Tracker Started!</b>

⚡ <b>Mode:</b> Real-time Webhooks
📦 <b>Monitoring {len(self.config.repositories)} repositories:</b>

{repo_list}

🏥 <b>Platform:</b> Sevalla
💾 <b>Database:</b> {self.config.db_path}

Bot is now monitoring for new issues in REAL-TIME! 🎯"""
        
        return await self.telegram.send_message(message)

async def health_check(request):
    """Health check endpoint."""
    return web.Response(text="OK - CNCF Issue Tracker Running (Webhook Mode)", status=200)

async def start_server(config: Config, tracker: CNCFIssueTracker):
    """Start the webhook server."""
    app = web.Application()
    
    # Add routes
    app.router.add_post('/webhook', tracker.handle_webhook)
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', config.port)
    await site.start()
    
    logging.info(f"🚀 Webhook server running on port {config.port}")
    logging.info(f"📡 Webhook URL: https://your-domain.com/webhook")
    
    return runner

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
    print(f"   • Platform port: {config.port}")
    print(f"   • Repositories: {len(config.repositories)}")
    print(f"   • GitHub token: {'✅ Configured' if config.github_token else '❌ Not set'}")
    print(f"   • Webhook secret: {'✅ Configured' if config.github_webhook_secret else '❌ Not set'}")
    print(f"   • Telegram: ✅ Configured")
    print(f"   • Database path: {config.db_path}")
    print(f"   • Log level: {config.log_level}")
    
    # Start the tracker
    tracker = CNCFIssueTracker(config)
    
    async def run():
        # Send startup notification
        await tracker.send_startup_notification()
        
        # Start webhook server
        runner = await start_server(config, tracker)
        
        try:
            # Keep server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logging.info("🛑 Bot stopped by user")
        finally:
            await runner.cleanup()
    
    asyncio.run(run())

if __name__ == "__main__":
    main()
