# Deployment Guide

This guide provides step-by-step instructions for deploying the Expenses AI Agent application:

| Service | Platform | URL Pattern |
|---------|----------|-------------|
| FastAPI Backend | Fly.io | `https://expenses-ai-agent-api.fly.dev` |
| Telegram Bot | Fly.io | N/A (long-running process) |
| Streamlit Dashboard | Streamlit Cloud | `https://expenses-ai-agent.streamlit.app` |

---

## Prerequisites

### 1. Required Accounts

- **Fly.io**: Sign up at https://fly.io (credit card required, free tier available)
- **Streamlit Cloud**: Sign up at https://streamlit.io/cloud (free tier, GitHub SSO)
- **GitHub**: Repository must be public or you need Streamlit Cloud Pro for private repos

### 2. Required API Keys

Before deploying, ensure you have these API keys ready:

| Key | Required For | Get From |
|-----|--------------|----------|
| `OPENAI_API_KEY` | All services | https://platform.openai.com/api-keys |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot | [@BotFather](https://t.me/BotFather) on Telegram |
| `EXCHANGE_RATE_API_KEY` | Currency conversion | https://www.exchangerate-api.com/ |

### 3. Install Fly.io CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Verify installation:

```bash
fly version
```

---

## Part 1: Deploy FastAPI Backend (Fly.io)

The FastAPI backend provides the REST API for expense classification and storage.

### Step 1.1: Authenticate with Fly.io

```bash
fly auth login
```

This opens a browser for authentication. Complete the login process.

### Step 1.2: Create the Fly.io App

From the project root directory:

```bash
fly apps create expenses-ai-agent-api
```

> **Note**: If the name is taken, choose a different name and update `fly.toml` accordingly.

### Step 1.3: Create Persistent Volume

The SQLite database needs persistent storage.

> **Important**: The volume region MUST match `primary_region` in `fly.toml` (default: `cdg` Paris). If you want a different region, update `fly.toml` first.

```bash
fly volumes create expenses_data --region cdg --size 1 --app expenses-ai-agent-api
```

- `--region cdg`: Must match `primary_region` in `fly.toml`
- `--size 1`: 1GB storage (sufficient for SQLite)

List available regions:

```bash
fly platform regions
```

### Step 1.4: Set Environment Secrets

```bash
fly secrets set \
  OPENAI_API_KEY="your-openai-api-key" \
  EXCHANGE_RATE_API_KEY="your-exchange-rate-api-key" \
  CORS_ORIGINS="https://expenses-ai-agent.streamlit.app" \
  --app expenses-ai-agent-api
```

> **Important**: Replace `https://expenses-ai-agent.streamlit.app` with your actual Streamlit Cloud URL after deploying Streamlit.

### Step 1.5: Deploy

```bash
fly deploy
```

This will:
1. Build the Docker image
2. Push to Fly.io registry
3. Deploy to the region specified in `fly.toml`
4. Run health checks

### Step 1.6: Verify Deployment

Check the health endpoint:

```bash
curl https://expenses-ai-agent-api.fly.dev/health
```

Expected response:

```json
{"status": "healthy"}
```

Check logs if there are issues:

```bash
fly logs --app expenses-ai-agent-api
```

### Step 1.7: Get Your API URL

Your API is now live at:

```
https://expenses-ai-agent-api.fly.dev/api/v1
```

Test the categories endpoint:

```bash
curl https://expenses-ai-agent-api.fly.dev/api/v1/categories
```

---

## Part 2: Deploy Telegram Bot (Fly.io)

The Telegram bot runs as a separate long-running process.

### Step 2.1: Create the Bot App

```bash
fly apps create expenses-ai-agent-bot
```

### Step 2.2: Create Persistent Volume

The bot needs its own database volume. Create a volume in the same region as `fly.bot.toml`:

```bash
fly volumes create expenses_data --region cdg --size 1 --app expenses-ai-agent-bot
```

> **Note**: If you want the bot and API to share data, you'll need to use a shared database solution (PostgreSQL, Turso, etc.) instead of SQLite. For separate user bases, SQLite volumes work fine.

### Step 2.3: Set Environment Secrets

```bash
fly secrets set \
  TELEGRAM_BOT_TOKEN="your-telegram-bot-token" \
  OPENAI_API_KEY="your-openai-api-key" \
  EXCHANGE_RATE_API_KEY="your-exchange-rate-api-key" \
  DATABASE_URL="sqlite:///./data/expenses.db" \
  --app expenses-ai-agent-bot
```

### Step 2.4: Deploy the Bot

```bash
fly deploy -c fly.bot.toml
```

This uses the bot-specific configuration which:
- Runs `expenses-telegram-bot` command instead of uvicorn
- Disables HTTP service (bot doesn't serve HTTP)
- Uses `immediate` deployment strategy (no rolling deploys)

### Step 2.5: Verify Bot is Running

Check the logs:

```bash
fly logs --app expenses-ai-agent-bot
```

You should see:

```
INFO - Starting Expenses AI Agent Telegram Bot...
INFO - Bot is running. Press Ctrl+C to stop.
```

### Step 2.6: Test the Bot

1. Open Telegram and search for your bot (the username you created with @BotFather)
2. Send `/start` - should receive welcome message
3. Send an expense like `Coffee at Starbucks $5.50`
4. Confirm or change the category

### Bot Commands Reference

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and instructions |
| `/help` | Show usage instructions |
| `/currency` | Set preferred display currency |
| `/cancel` | Cancel current operation |

---

## Part 3: Deploy Streamlit Dashboard (Streamlit Cloud)

The Streamlit dashboard provides a web interface for viewing and adding expenses.

### Step 3.1: Push Code to GitHub

Ensure your latest code is pushed to GitHub:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 3.2: Connect to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click **"New app"**
3. Connect your GitHub account if not already connected
4. Select your repository: `your-username/expenses_ai_agent`
5. Select branch: `main`
6. Set Main file path: `src/expenses_ai_agent/streamlit/app.py`

### Step 3.3: Configure Secrets

Before clicking Deploy, configure secrets:

1. Click **"Advanced settings"**
2. Click **"Secrets"**
3. Add the following in TOML format:

```toml
API_BASE_URL = "https://expenses-ai-agent-api.fly.dev/api/v1"
DEFAULT_USER_ID = "12345"
```

> **Important**: Replace the API_BASE_URL with your actual Fly.io API URL from Part 1.

### Step 3.4: Deploy

Click **"Deploy!"**

Streamlit Cloud will:
1. Clone your repository
2. Install dependencies from `pyproject.toml`
3. Run the Streamlit app
4. Provide a public URL

### Step 3.5: Verify Deployment

Your app should be live at:

```
https://your-app-name.streamlit.app
```

Check that:
- The sidebar shows "API Connected"
- Dashboard loads with charts
- You can add new expenses

### Step 3.6: Update CORS Origins

Now that you have the Streamlit URL, update the FastAPI CORS settings:

```bash
fly secrets set \
  CORS_ORIGINS="https://your-app-name.streamlit.app" \
  --app expenses-ai-agent-api
```

---

## Post-Deployment Verification

### Checklist

- [ ] **FastAPI**: `curl https://your-api.fly.dev/health` returns `{"status": "healthy"}`
- [ ] **FastAPI**: `curl https://your-api.fly.dev/api/v1/categories` returns category list
- [ ] **Telegram Bot**: `/start` command works
- [ ] **Telegram Bot**: Expense classification works
- [ ] **Streamlit**: Dashboard loads without API errors
- [ ] **Streamlit**: Can add new expenses
- [ ] **Integration**: Expenses added via Telegram appear in Streamlit (if sharing DB)

### Monitoring Commands

```bash
# View FastAPI logs
fly logs --app expenses-ai-agent-api

# View Bot logs
fly logs --app expenses-ai-agent-bot

# Check app status
fly status --app expenses-ai-agent-api
fly status --app expenses-ai-agent-bot

# SSH into container (for debugging)
fly ssh console --app expenses-ai-agent-api

# Check secrets (names only, not values)
fly secrets list --app expenses-ai-agent-api
```

---

## Troubleshooting

### FastAPI Won't Start

**Symptom**: Health check fails, app crashes

**Solutions**:
1. Check logs: `fly logs --app expenses-ai-agent-api`
2. Verify secrets are set: `fly secrets list --app expenses-ai-agent-api`
3. Ensure volume is mounted: `fly volumes list --app expenses-ai-agent-api`

### Telegram Bot Not Responding

**Symptom**: Bot doesn't reply to messages

**Solutions**:
1. Check logs: `fly logs --app expenses-ai-agent-bot`
2. Verify `TELEGRAM_BOT_TOKEN` is correct
3. Ensure bot is running: `fly status --app expenses-ai-agent-bot`
4. Check if another instance is running (only one bot per token)

### Streamlit Can't Connect to API

**Symptom**: "API is not available" error

**Solutions**:
1. Verify `API_BASE_URL` in Streamlit secrets
2. Check CORS_ORIGINS includes your Streamlit URL
3. Test API directly: `curl https://your-api.fly.dev/health`

### Database Issues

**Symptom**: Data not persisting between deploys

**Solutions**:
1. Verify volume is created: `fly volumes list --app your-app`
2. Check volume is mounted at `/app/data`
3. Ensure `DATABASE_URL` points to `/app/data/expenses.db`

---

## Cost Estimates

### Fly.io (as of 2024)

| Resource | Free Tier | Paid |
|----------|-----------|------|
| Shared CPU VMs | 3 VMs | $1.94/mo per 256MB |
| Persistent Storage | 3GB total | $0.15/GB/mo |
| Outbound Transfer | 100GB/mo | $0.02/GB |

**Estimated monthly cost**: $0 (within free tier for light usage)

### Streamlit Cloud

| Plan | Cost | Limits |
|------|------|--------|
| Free | $0 | Public repos, 1GB memory |
| Teams | $250/mo | Private repos, more resources |

---

## Updating Deployments

### Update FastAPI or Bot

```bash
# Make changes, then:
git add .
git commit -m "Update feature"
git push origin main

# Deploy FastAPI
fly deploy --app expenses-ai-agent-api

# Deploy Bot
fly deploy -c fly.bot.toml
```

### Update Streamlit

Streamlit Cloud automatically redeploys when you push to the connected branch.

---

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐
│   Telegram      │     │   Streamlit     │
│   Mobile App    │     │   Dashboard     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Telegram Bot   │     │   FastAPI       │
│  (Fly.io)       │     │   (Fly.io)      │
│                 │     │                 │
│  SQLite Volume  │     │  SQLite Volume  │
└─────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│              OpenAI API                 │
│         (Expense Classification)        │
└─────────────────────────────────────────┘
```

> **Note**: Bot and API use separate SQLite databases by default. See "Part 4: Shared Database" below to share data between services.

---

## Part 4: Shared Database with PostgreSQL (Fly.io)

By default, the Telegram Bot and FastAPI use separate SQLite databases. To share expenses between both services, migrate to Fly Postgres.

There are several options for a shared PostgreSQL database:

| Option | Cost | Pros | Cons |
|--------|------|------|------|
| Fly Postgres (Unmanaged) | Free tier | Same network, low latency | Self-managed, no support |
| Fly Managed Postgres | ~$15/mo+ | Fully managed, supported | Higher cost |
| Neon | Free tier (0.5GB) | Serverless, auto-scaling | External latency |
| Supabase | Free tier (500MB) | Dashboard, auth features | External latency |

### Option A: Fly Postgres (Unmanaged) - Recommended for Learning

```bash
fly postgres create --name expenses-db --region cdg
```

> **Note**: You'll see a warning about "Unmanaged Fly Postgres". Type `y` to continue - it still works, just means Fly won't help debug database issues.

Choose the **Development** plan (free tier):
- 1 shared CPU
- 256MB RAM
- 1GB storage

Save the connection string output - you'll need it!

### Step 4.2: Get Database Connection String

```bash
fly postgres connect -a expenses-db
```

Or get the connection string:

```bash
fly postgres attach expenses-db --app expenses-ai-agent-api
```

This automatically sets `DATABASE_URL` as a secret. The format is:

```
postgres://postgres:<password>@expenses-db.flycast:5432/expenses_db?sslmode=disable
```

### Step 4.3: Install PostgreSQL Driver

Add `psycopg2-binary` to your dependencies in `pyproject.toml`:

```toml
dependencies = [
    # ... existing deps ...
    "psycopg2-binary>=2.9.9",
]
```

Then update the lock file and redeploy:

```bash
uv lock
git add pyproject.toml uv.lock
git commit -m "Add psycopg2 for PostgreSQL support"
git push
```

### Step 4.4: Attach Database to Both Apps

```bash
# Attach to API (if not already done)
fly postgres attach expenses-db --app expenses-ai-agent-api

# Attach to Bot
fly postgres attach expenses-db --app expenses-ai-agent-bot
```

This sets `DATABASE_URL` secret on both apps automatically.

### Step 4.5: Remove SQLite Volume Mounts (Optional)

Since we're using PostgreSQL, the SQLite volumes are no longer needed. Edit `fly.toml` and `fly.bot.toml` to remove:

```toml
# Remove this section from both files:
[mounts]
  source = "expenses_data"
  destination = "/app/data"
```

### Step 4.6: Redeploy Both Apps

```bash
# Redeploy API
fly deploy --app expenses-ai-agent-api

# Redeploy Bot
fly deploy -c fly.bot.toml
```

### Step 4.7: Verify Shared Database

1. Add an expense via Telegram Bot
2. Check the Streamlit Dashboard - the expense should appear
3. Add an expense via Dashboard
4. The data is now shared!

### PostgreSQL Management Commands

```bash
# Connect to database shell
fly postgres connect -a expenses-db

# View database size
fly postgres db list -a expenses-db

# Create a backup
fly postgres backup create -a expenses-db

# View backups
fly postgres backup list -a expenses-db
```

### Troubleshooting PostgreSQL

**"App already contains a secret named DATABASE_URL"**:
- The app has an existing DATABASE_URL (from SQLite setup)
- Unset it first, then attach:
  ```bash
  fly secrets unset DATABASE_URL --app expenses-ai-agent-bot
  fly postgres attach expenses-db --app expenses-ai-agent-bot
  ```

**Connection refused**:
- Ensure both apps are attached: `fly postgres attach expenses-db --app <app-name>`
- Check the app can reach the database: `fly ssh console --app expenses-ai-agent-api` then `ping expenses-db.flycast`

**Tables not created**:
- SQLModel creates tables on first connection
- Check logs: `fly logs --app expenses-ai-agent-api`

**Permission denied**:
- The attached user should have full permissions
- Check connection string is correct in secrets

**"DATABASE_URL may be a potentially sensitive environment variable"**:
- This warning appears if DATABASE_URL is in `[env]` section of fly.toml
- Remove it from `[env]` - it should only be set as a secret via `fly postgres attach` or `fly secrets set`
- The config files have been updated to use secrets instead

---

## Alternative Database Options

### Option B: Fly Managed Postgres

For production workloads with support:

```bash
fly mpg create --name expenses-db --region cdg
```

See pricing and features: https://fly.io/docs/mpg/overview/

After creation, set the connection string manually:

```bash
fly secrets set DATABASE_URL="<connection-string-from-mpg>" --app expenses-ai-agent-api
fly secrets set DATABASE_URL="<connection-string-from-mpg>" --app expenses-ai-agent-bot
```

### Option C: Neon (External - Free Tier)

Neon offers serverless Postgres with a generous free tier.

1. Sign up at https://neon.tech
2. Create a new project
3. Copy the connection string (looks like `postgres://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require`)
4. Set on both apps:

```bash
fly secrets set DATABASE_URL="postgres://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require" --app expenses-ai-agent-api
fly secrets set DATABASE_URL="postgres://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require" --app expenses-ai-agent-bot
```

**Free tier limits**: 0.5GB storage, 3GB data transfer/month

### Option D: Supabase (External - Free Tier)

Supabase provides Postgres with additional features (auth, storage, realtime).

1. Sign up at https://supabase.com
2. Create a new project
3. Go to Settings → Database → Connection string
4. Copy the URI and set on both apps:

```bash
fly secrets set DATABASE_URL="postgres://postgres:pass@db.xxx.supabase.co:5432/postgres" --app expenses-ai-agent-api
fly secrets set DATABASE_URL="postgres://postgres:pass@db.xxx.supabase.co:5432/postgres" --app expenses-ai-agent-bot
```

**Free tier limits**: 500MB storage, 2 projects

---

## Next Steps

1. **Custom Domain**: Configure custom domains in Fly.io dashboard
2. **Monitoring**: Set up Fly.io Metrics or external monitoring
3. **Backups**: Schedule regular PostgreSQL backups with `fly postgres backup create`
