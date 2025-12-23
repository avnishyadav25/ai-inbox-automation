# Quick Setup Guide

## Step-by-Step Setup

### 1. Gmail API Setup (5 minutes)

#### Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select existing project
3. Name it "AI Inbox Automation"
4. Click "Create"

#### Enable Gmail API
1. In the search bar, type "Gmail API"
2. Click on "Gmail API"
3. Click "Enable"

#### Create OAuth Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: External
   - App name: AI Inbox Automation
   - User support email: your email
   - Developer contact: your email
   - Click "Save and Continue"
   - Scopes: Skip (click "Save and Continue")
   - Test users: Add your Gmail address
   - Click "Save and Continue"

4. Back to "Create OAuth client ID":
   - Application type: Desktop app
   - Name: AI Inbox Desktop
   - Click "Create"

5. Download the JSON file:
   - Click the download icon
   - Save as `credentials.json` in project root

### 2. Python Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys

#### Option A: Using Anthropic Claude (Recommended)

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up / Log in
3. Go to API Keys
4. Create a new API key
5. Copy the key

Edit `.env`:
```bash
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

#### Option B: Using OpenAI

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up / Log in
3. Go to API Keys
4. Create a new API key
5. Copy the key

Edit `.env`:
```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

### 4. Optional: Google Sheets Logging

1. Create a new Google Sheet
2. Copy the Sheet ID from URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
   ```
3. Add to `.env`:
   ```bash
   GOOGLE_SHEETS_ID=YOUR_SHEET_ID
   ```

### 5. Create Required Directories

```bash
mkdir -p data logs
```

### 6. First Run

```bash
python main.py
```

On first run:
1. Browser will open for Gmail authentication
2. Select your Gmail account
3. Click "Continue" (it's safe - you created this app)
4. Grant permissions
5. Close browser tab
6. Return to terminal

You should see:
```
AI INBOX AUTOMATION AGENT SUITE
================================================================================

Options:
  [1] Process emails once
  [2] Run continuous automation
  [3] Check follow-ups
  [4] Display statistics
  [5] Exit

Your choice (1-5):
```

Choose `1` to process emails once and test the system.

## Verification Checklist

- [ ] `credentials.json` exists in project root
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] `.env` file configured with API key
- [ ] `data/` and `logs/` directories created
- [ ] Gmail authentication successful
- [ ] System processes test email successfully

## Common Issues

### "credentials.json not found"
- Ensure the file is in the project root directory
- Check the filename is exactly `credentials.json`

### "Invalid API key"
- Verify the API key is correct in `.env`
- Check for extra spaces or quotes
- Ensure the key is active and has credits

### "No module named 'google'"
- Activate virtual environment: `source venv/bin/activate`
- Re-run: `pip install -r requirements.txt`

### "Permission denied" for Gmail
- Re-run the authentication flow
- Delete `token.json` and restart
- Check that test users include your email in OAuth consent screen

### Browser doesn't open for authentication
- Manually copy the URL from terminal
- Paste in browser
- Complete authentication
- Code will continue automatically

## Quick Test

Process a single email:
```bash
python main.py
# Choose option 1: Process emails once
```

Expected output:
```
🟡 📧 [GENERAL] [MEDIUM] Your email subject

================================================================================
EMAIL PREVIEW
================================================================================
...
```

## Next Steps

After successful setup:
1. Process a few test emails
2. Review draft replies
3. Approve/edit/skip as needed
4. Check Google Sheets for logs
5. Run continuous mode: Choose option 2

## Cost Estimates

### API Costs (approximate)

**Anthropic Claude:**
- $3 per million input tokens
- $15 per million output tokens
- ~$0.01-0.02 per email processed

**OpenAI GPT-4:**
- $10 per million input tokens
- $30 per million output tokens
- ~$0.02-0.04 per email processed

**Expected monthly cost:**
- 50 emails/day = $30-60/month
- 20 emails/day = $12-24/month
- 10 emails/day = $6-12/month

### Free Tiers

**Anthropic:**
- $5 free credit for new users

**OpenAI:**
- $5 free credit for new accounts

**Gmail API:**
- Free (with quota limits)

## Support

If you encounter issues:
1. Check `logs/` directory for detailed error logs
2. Verify all setup steps completed
3. Ensure API keys are valid and have credits
4. Check internet connection

For Gmail API quota issues:
- Default quota: 250 quota units per user per second
- 1 email read = 5 quota units
- 1 email send = 100 quota units
- Request quota increase if needed

---

You're all set! Start automating your inbox.
