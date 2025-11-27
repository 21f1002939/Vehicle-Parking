# MailHog Setup for Email Testing

## What is MailHog?
MailHog is a local email testing tool that catches all emails sent from your application. It provides a web interface to view and inspect emails without actually sending them to real recipients.

## Installation

### Windows (Using Go)
```powershell
# Download MailHog executable from GitHub
# Visit: https://github.com/mailhog/MailHog/releases
# Download: MailHog_windows_amd64.exe

# Or using Chocolatey
choco install mailhog
```

### Windows (Using Docker)
```powershell
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

### Linux/Mac
```bash
# Using Homebrew (Mac)
brew install mailhog

# Using Go
go install github.com/mailhog/MailHog@latest

# Using Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

## Running MailHog

### Standalone
```powershell
# Windows
MailHog.exe

# Linux/Mac
mailhog
```

### Using Docker
```powershell
docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

## Access MailHog

- **SMTP Server:** `localhost:1025` (for sending emails)
- **Web UI:** `http://localhost:8025` (to view received emails)

## Configuration in Your App

The email configuration has been updated in `tasks.py`:

```python
SMTP_SERVER = 'localhost'
SMTP_PORT = 1025
SENDER_EMAIL = 'parking-system@localhost'
```

No authentication is required for MailHog.

## Testing Email Functionality

### 1. Start MailHog
```powershell
mailhog
# or
docker start mailhog
```

### 2. Start Your Application
```powershell
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Celery Worker
cd backend
python run_worker.py

# Terminal 3 - Celery Beat
cd backend
python run_beat.py
```

### 3. Trigger Email Actions

**Daily Reminders (6 PM scheduled):**
- Or manually trigger via Python shell:
```python
from tasks import send_daily_reminder
send_daily_reminder.delay()
```

**Monthly Reports (1st of month, 9 AM):**
```python
from tasks import generate_monthly_report
generate_monthly_report.delay()
```

**CSV Export:**
```python
from tasks import export_user_parking_history
export_user_parking_history.delay(user_id=2)
```

### 4. View Emails
Open your browser and go to: `http://localhost:8025`

You'll see all emails sent by your application with:
- Full HTML rendering
- Email headers
- Plain text version
- Attachments (CSV files)

## Benefits of MailHog

✅ **No Real Email Setup:** No need for Gmail app passwords or SMTP credentials
✅ **Local Testing:** Test email functionality without internet
✅ **Safe Development:** No risk of accidentally sending test emails to real users
✅ **Email Inspection:** View HTML, headers, and attachments
✅ **Multiple Recipients:** Test bulk emails without spam concerns
✅ **No Configuration:** Works out of the box

## Production Migration

When deploying to production, update the SMTP settings in `tasks.py`:

```python
# For Gmail
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'your-email@gmail.com'
SENDER_PASSWORD = 'your-app-password'

# For SendGrid
SMTP_SERVER = 'smtp.sendgrid.net'
SMTP_PORT = 587
SENDER_EMAIL = 'apikey'
SENDER_PASSWORD = 'your-sendgrid-api-key'

# For AWS SES
SMTP_SERVER = 'email-smtp.us-east-1.amazonaws.com'
SMTP_PORT = 587
SENDER_EMAIL = 'your-verified-email@domain.com'
SENDER_PASSWORD = 'your-ses-smtp-password'
```

## Docker Compose Setup (Optional)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI
    restart: unless-stopped
```

Run with: `docker-compose up -d mailhog`

## Troubleshooting

**MailHog not receiving emails?**
- Check if MailHog is running: `netstat -an | findstr 1025`
- Verify SMTP settings in `tasks.py`
- Check Celery worker logs for connection errors

**Port 1025 already in use?**
- Change MailHog port: `mailhog -smtp-bind-addr :2525`
- Update `SMTP_PORT` in `tasks.py`

**Docker container not starting?**
- Check if ports are available
- View logs: `docker logs mailhog`

## Quick Start Command

```powershell
# Start everything with one script
# Terminal 1
mailhog

# Terminal 2
cd backend; python app.py

# Terminal 3
cd backend; python run_worker.py

# Terminal 4
cd backend; python run_beat.py

# Open browser
start http://localhost:8025
```
