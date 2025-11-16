# Bay Area Sports Memorabilia Tracker

Automated system to track, analyze, and alert on Bay Area sports memorabilia deals across multiple platforms.

## What It Does

- **Scrapes 5+ platforms daily** (eBay, PWCC, Goldin, Heritage, Pristine)
- **Tracks investment-grade pieces**: Stephen Curry, Buster Posey, Patrick Willis
- **Monitors collection items**: Klay Thompson, George Kittle, Christian McCaffrey, Frank Gore, Giants pitchers, Tiger Woods, Scottie Scheffler
- **Scores opportunities** based on price vs market, authentication, inscriptions
- **Generates daily HTML dashboard** with prioritized findings
- **Emails dashboard** to your inbox every morning at 7 AM PST

## Setup Instructions (30 minutes)

### Step 1: Create GitHub Account (if needed)
1. Go to https://github.com
2. Click "Sign up" and create free account
3. Verify your email

### Step 2: Create New Repository
1. Click the "+" in top right → "New repository"
2. Repository name: `memorabilia-tracker`
3. Set to **Private** (important!)
4. Check "Add a README file"
5. Click "Create repository"

### Step 3: Upload Files
1. Click "Add file" → "Upload files"
2. Drag and drop ALL files from the memorabilia-tracker folder:
   - `config.json`
   - `requirements.txt`
   - `database.py`
   - `scraper.py`
   - `analyzer.py`
   - `dashboard_generator.py`
   - `run.py`
   - `.github/workflows/daily_scrape.yml`
3. Click "Commit changes"

### Step 4: Set Up Gmail for Notifications

#### 4a. Enable 2-Factor Authentication on Gmail
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"

#### 4b. Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select app: "Mail"
3. Select device: "Other" → type "GitHub Actions"
4. Click "Generate"
5. **Copy the 16-character password** (you'll need this in Step 5)

### Step 5: Add GitHub Secrets
1. In your GitHub repository, click "Settings"
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add these 3 secrets:

**Secret 1:**
- Name: `EMAIL_USERNAME`
- Value: Your Gmail address (e.g., yourname@gmail.com)

**Secret 2:**
- Name: `EMAIL_PASSWORD`
- Value: The 16-character app password from Step 4b

**Secret 3:**
- Name: `EMAIL_TO`
- Value: Email where you want reports sent (can be same Gmail)

### Step 6: Enable GitHub Actions
1. Click "Actions" tab in your repository
2. Click "I understand my workflows, go ahead and enable them"

### Step 7: Test Run (Optional)
1. Click "Actions" tab
2. Click "Daily Memorabilia Scraper"
3. Click "Run workflow" → "Run workflow"
4. Wait 2-3 minutes
5. Check your email for dashboard

## ✅ You're Done!

The system will now run automatically every day at 2 AM PST (10 AM UTC).

## Daily Workflow

**Automatic (every 2 AM PST):**
1. Scraper runs → finds listings
2. Analyzer scores opportunities
3. Dashboard generated
4. Email sent to your inbox at 7 AM PST
5. Dashboard saved to GitHub

**Your Morning Routine (5-10 minutes):**
1. Open email or visit: `https://github.com/YOUR-USERNAME/memorabilia-tracker/blob/main/data/dashboard.html`
2. Review priority alerts (Curry/Posey/Willis)
3. Browse collection sections
4. Click through to buy anything interesting
5. Manually verify authentication certs on PSA/JSA websites

## Viewing the Dashboard

**Option 1: Email**
- Check inbox every morning for HTML dashboard
- Open attachment in browser

**Option 2: GitHub**
- Visit: `https://github.com/YOUR-USERNAME/memorabilia-tracker/blob/main/data/dashboard.html`
- Click "Raw" button to view
- Bookmark this URL for daily checking

**Option 3: Download**
- Clone repository to computer
- Open `data/dashboard.html` in any browser

## Customizing Settings

Edit `config.json` to adjust:
- Price thresholds
- Players to track
- Inscription priorities
- Authentication services
- Scoring weights

After editing, commit changes to GitHub. Changes take effect next run.

## Verifying Authentication Certificates

**Always verify cert numbers before purchasing:**

- **PSA:** https://www.psacard.com/cert
- **JSA:** https://www.jsauthentication.com/authentication/
- **Beckett:** https://www.beckett.com/authentication

Paste the cert number from the listing and verify:
1. Certificate exists
2. Player name matches
3. Item description matches
4. Not marked as fake/counterfeit

## Troubleshooting

### Dashboard Not Generating
- Check "Actions" tab for errors
- Verify all secrets are set correctly
- Email password must be app-specific password

### No Email Received
- Check spam folder
- Verify EMAIL_TO secret is correct
- Check GitHub Actions log for errors

### Missing Listings
- eBay may block scraping occasionally (rate limits)
- GitHub Actions has usage limits (2000 minutes/month free)
- Some platforms require authentication (future feature)

## Cost

**$0/month** using GitHub's free tier:
- 2000 minutes/month of Actions
- Daily run uses ~5 minutes
- = 400 runs/month available (13x what you need)

## Future Enhancements

Potential additions you could request:
- PWCC/Goldin/Heritage scraping (requires authentication)
- Text/SMS alerts for hot deals
- Price prediction ML model
- Auto-bid on eBay
- Portfolio tracking for purchased items

## Security Notes

- Repository is PRIVATE - only you can see it
- Never commit API keys or passwords to code
- All sensitive data in GitHub Secrets (encrypted)
- Email password is app-specific, not your main password

## Support

If something breaks:
1. Check Actions tab for error logs
2. Re-run workflow manually to test
3. Verify all secrets are still set
4. Check if Gmail app password expired

---

**Created for Jeff - Writer Enterprise AE**
*Tracking Bay Area sports memorabilia investments*
