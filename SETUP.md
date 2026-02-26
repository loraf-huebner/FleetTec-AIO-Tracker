# fleetTEC AI Visibility Tracker — Setup Guide

This automation queries ChatGPT, Claude, and Gemini every Monday at 10am with 25 prompts mapped to fleetTEC's buyers and verticals. It measures how often fleetTEC appears in AI-generated responses and sends a formatted report to Slack.

---

## What You'll Need (15 minutes total)

- A free GitHub account
- API keys for OpenAI, Anthropic, and Gemini
- A Slack webhook URL (5 minutes to create)

---

## Step 1: Create a GitHub Repository (3 minutes)

1. Go to [github.com](https://github.com) and sign in (or create a free account)
2. Click the **+** in the top right → **New repository**
3. Name it: `fleettec-ai-visibility`
4. Set it to **Private**
5. Click **Create repository**

---

## Step 2: Upload the Files (2 minutes)

**For the three main files** — drag and drop into GitHub:
- `tracker.py`
- `requirements.txt`
- `SETUP.md`

Click **Add file → Upload files**, drag them in, then **Commit changes**.

**For the workflow file** — create it manually to get the folder path right:
1. Click **Add file → Create new file**
2. In the filename box, type: `.github/workflows/weekly-ai-visibility.yml`
   (GitHub turns the `/` characters into folder breadcrumbs automatically)
3. Open `weekly-ai-visibility.yml`, copy all the text, paste it into the editor
4. Click **Commit changes → Commit directly to main**

Your repo should look like this when done:
```
fleettec-ai-visibility/
├── .github/
│   └── workflows/
│       └── weekly-ai-visibility.yml
├── tracker.py
├── requirements.txt
└── SETUP.md
```

---

## Step 3: Create Your Slack Webhook (5 minutes)

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Name it: `fleetTEC Visibility Bot` | Select your workspace
4. Click **Incoming Webhooks** in the left sidebar
5. Toggle **Activate Incoming Webhooks** to ON
6. Click **Add New Webhook to Workspace**
7. In the "Post to" dropdown, choose the channel or person who should receive the report
8. Click **Allow**
9. **Copy the webhook URL** — it starts with `https://hooks.slack.com/services/...`

---

## Step 4: Add Secrets to GitHub (3 minutes)

1. In your repo, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret** for each of the following:

| Secret Name | Value |
|---|---|
| `OPENAI_API_KEY` | Your OpenAI key |
| `ANTHROPIC_API_KEY` | Your Anthropic key |
| `GEMINI_API_KEY` | Your Gemini key |
| `SLACK_WEBHOOK_URL` | The webhook URL from Step 3 |

---

## Step 5: Run a Test

1. Go to the **Actions** tab in your repo
2. Click **Weekly AI Visibility Report** in the left sidebar
3. Click **Run workflow** → **Run workflow**
4. Wait 3–4 minutes for all 75 queries to complete
5. Check Slack for the report

---

## What the Report Looks Like

```
🚛 fleetTEC AI Visibility Report — Week of 2026-03-02
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall: 0/75 prompts (0%) — baseline week — tracking starts now

By Platform:
  • ChatGPT: 0/25 (0%)  `░░░░░░░░░░`
  • Claude:  0/25 (0%)  `░░░░░░░░░░`
  • Gemini:  0/25 (0%)  `░░░░░░░░░░`

✅ Prompts Where fleetTEC Appeared: None this week — keep publishing!

❌ Visibility Gaps — 25 prompts with no mention:
  • Who are the best vehicle upfitters for police departments? (Public Safety)
  • Who are authorized Panasonic Toughbook installers for fleet vehicles? (Partner Channel)
  ...
```

---

## Prompt Categories

The 25 prompts are organized across five audience segments:

- **Public Safety** — Fleet managers, IT directors, command staff at police/fire/EMS agencies
- **Energy/Utility** — Fleet managers at utility companies (Georgia Power, Southern Gas, etc.)
- **Mobile/Transit** — Public transportation fleets, mobile installation opportunities
- **Partner Channel** — Panasonic sales reps and their customers, certified installer searches
- **Competitive** — General upfitter comparisons and hardware vendor searches

---

## Schedule

Runs every **Monday at 10:00 AM CDT** (9:00 AM CST in winter). GitHub Actions uses UTC, so the cron is set to `0 15 * * 1`.

To change the time, edit `.github/workflows/weekly-ai-visibility.yml` and update the cron line.

---

## Updating the Prompts

All 25 prompts live in `tracker.py` in the `PROMPTS` list near the top. Each entry has a category label and a question. Edit and commit anytime to add new prompts as fleetTEC's business evolves (new verticals, new partnerships, new services).
