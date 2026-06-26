# ForwardFlow

A GitHub issue tracker bot that monitors public repositories and delivers formatted Telegram notifications for new issues.

---

## How It Works

The bot polls configured repositories on a fixed interval using the GitHub Issues API. For each repository, it fetches issues created within a rolling lookback window, checks each one against a local SQLite database, and sends a Telegram notification for any issue it has not seen before. Repositories are processed in batches to stay within GitHub API rate limits.

---

## Architecture

- **Polling loop** -- aiohttp-based async loop, configurable interval (60-240 seconds)
- **Batch processing** -- repositories processed in groups of 3 with inter-batch delays
- **Deduplication** -- SQLite database with `(issue_id, repository)` composite primary key prevents duplicate notifications
- **Database path resolution** -- prefers `/data` (Railway persistent disk) over `/tmp` over local path
- **Restart policy** -- Railway restarts the process on failure, up to 10 retries

---

## Notification Format

Each Telegram message includes:

- Issue title (truncated at 80 characters)
- Author username
- Repository name
- Direct link to the issue
- Labels (up to 6, each truncated at 20 characters)

Messages are sent as HTML via the Telegram Bot API.

---

## Configuration

All settings are controlled via environment variables. The defaults are defined in `config.py` and can be overridden at runtime.

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | required | Telegram bot token from BotFather |
| `TELEGRAM_CHAT_ID` | required | Target chat or channel ID |
| `GITHUB_TOKEN` | optional | Personal access token for higher rate limits |
| `CHECK_INTERVAL` | `180` | Poll interval in seconds (60-240) |
| `DB_PATH` | auto-resolved | Path to SQLite database file |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `BATCH_SIZE` | `3` | Repositories processed per batch |
| `BATCH_DELAY` | `2` | Seconds between batches |
| `NOTIFICATION_DELAY` | `1` | Seconds between Telegram notifications |
| `API_TIMEOUT` | `10` | GitHub API request timeout in seconds |
| `CHECK_BUFFER_MINUTES` | `2` | Extra buffer added to the lookback window |

**GitHub API rate limits:**
- Without token: 60 requests/hour
- With token: 5,000 requests/hour

---

## Repository List

Edit `config.py` to set the repositories to monitor (up to any number, formatted as `owner/repo`):

```python
REPOSITORIES = [
    "litmuschaos/litmus",
    "knative/docs",
    "antrea-io/antrea",
    # add more here
]
```

---

## Deployment (Railway)

The project includes a `railway.json` configured for Nixpacks with automatic restart on failure.

1. Push the repository to GitHub.

2. Create a new project on [railway.app](https://railway.app) and connect the repository.

3. Add the following environment variables in the Railway dashboard:

```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
GITHUB_TOKEN=your_github_token   # recommended
CHECK_INTERVAL=180
```

4. Railway will build and deploy automatically. The bot sends a startup notification to your Telegram chat when it comes online.

For persistent issue tracking across restarts, mount a Railway volume at `/data`. Without it, the bot uses `/tmp` which is ephemeral.

---

## Local Setup

**Requirements:** Python 3.7+

```bash
pip install -r requirements.txt
```

Set environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export GITHUB_TOKEN="your_github_token"
```

Run the bot:

```bash
python cncf_issue_tracker.py
```

To verify your configuration and test the Telegram connection before running:

```bash
python test_bot.py
```

---

## Error Handling

- API timeouts and HTTP errors are caught per-repository and logged; the bot continues checking remaining repositories
- On unexpected errors in the main loop, the bot sends an error notification to Telegram and retries after 2 minutes
- Railway's restart policy handles process-level failures
