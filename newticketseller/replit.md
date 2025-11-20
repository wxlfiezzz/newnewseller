# Telegram Ticket Seller Bot

## Overview
This is a Telegram bot application for managing ticket/file distribution with subscription-based access. The bot allows users to subscribe via unique links and automatically distributes files to subscribers. Administrators can manage subscriptions, upload files, view statistics, and control the system through an admin panel.

## Current State
- **Status**: Running and operational
- **Language**: Python 3.11
- **Framework**: python-telegram-bot 20.7
- **Database**: SQLAlchemy 2.0.23 with SQLite
- **Last Updated**: November 20, 2025

## Recent Changes
- **November 20, 2025**: Initial Replit setup
  - Migrated from nested directory structure to root
  - Secured BOT_TOKEN to environment secrets
  - Configured workflow for bot execution
  - Commented out missing command handlers (`removeadmin`, `send_pending`) in main.py
  - Added Python .gitignore
  - Bot successfully running

## Project Architecture

### Directory Structure
```
/
├── database/           # Database models and session management
│   ├── models.py      # SQLAlchemy models (User, File, SubscriptionLink, etc.)
│   └── session.py     # Database session configuration
├── handlers/          # Telegram command and callback handlers
│   ├── admin.py       # Admin panel and commands
│   ├── callbacks.py   # Callback query handlers
│   ├── files.py       # File upload and processing
│   ├── start.py       # Start command and message handling
│   └── user.py        # User commands (subscription, tickets)
├── services/          # Business logic services
│   ├── auth.py        # Authentication and authorization
│   ├── file_manager.py # File management utilities
│   ├── logger.py      # Bot action logging
│   └── subscription.py # Subscription management
├── utils/             # Helper utilities
│   ├── excel_generator.py # Excel report generation
│   └── helpers.py     # General helper functions
├── main.py            # Main application entry point
├── config.py          # Configuration settings
└── requirements.txt   # Python dependencies
```

### Database Models
- **User**: Stores user information, access status, and file tracking
- **SubscriptionLink**: Manages unique subscription tokens
- **File**: Tracks uploaded files and distribution status
- **FileDelivery**: Records file delivery history and status
- **Admin**: Manages bot administrators

### Key Features
1. **Subscription Management**: Unique subscription links for user access
2. **File Distribution**: Automatic file distribution to subscribed users
3. **Admin Panel**: Comprehensive admin interface for management
4. **File Upload**: ZIP archive processing and file storage
5. **Statistics**: User and file statistics tracking
6. **Logging**: Comprehensive bot action logging
7. **Recovery**: File recovery system for failed deliveries

## Configuration

### Environment Variables
- `BOT_TOKEN`: Telegram bot token (required) - Set in Replit Secrets

### Admin Configuration
- Admin IDs are configured in `config.py`
- Default admin ID: 1049172316
- Use `/addadmin` command to add more admins

### File Storage Folders
- `pdf_files/`: Uploaded PDF files
- `zip_archives/`: ZIP archives
- `excel_reports/`: Generated Excel reports
- `ticket_archives/`: Archived tickets
- `backup_files/`: File backups
- `bot_logs/`: Bot action logs

## Running the Bot

The bot runs automatically via the configured workflow:
```bash
python main.py
```

## Available Commands

### User Commands
- `/start` - Start the bot and subscribe with link
- `/mysub` - View subscription status
- `/myticket` - View received ticket/file
- `/recover` - Recover lost ticket

### Admin Commands
- `/admin` - Open admin panel
- `/addadmin` - Add new administrator

### Admin Panel Features (via inline buttons)
- Create subscription links
- View statistics
- Upload ZIP archives
- Distribute files to users
- Send files to pending users
- Archive free tickets
- View subscriber list
- Manage administrators

## Known Issues
- Two command handlers are currently commented out in `main.py`:
  - `removeadmin` - Method not implemented in AdminHandler
  - `send_pending` - Method not implemented in AdminHandler
  - These features are available through the callback handlers in the admin panel

## User Preferences
None specified yet.

## Notes
- The bot uses polling mode for updates
- Database is SQLite-based for simplicity
- All sensitive tokens are stored in environment secrets
- File distribution is automatic when new users subscribe
