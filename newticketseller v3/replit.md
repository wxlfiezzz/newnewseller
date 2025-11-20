# Telegram Ticket Seller Bot

## Overview
This is a Telegram bot application for managing ticket/file distribution with subscription-based access. The bot allows users to subscribe via unique links and automatically distributes files to subscribers. Administrators can manage subscriptions, upload files, view statistics, broadcast messages, and control user access through an admin panel.

## Current State
- **Status**: Running and operational
- **Language**: Python 3.11
- **Framework**: python-telegram-bot 20.7
- **Database**: SQLAlchemy 2.0.23 with SQLite
- **Last Updated**: November 20, 2025

## Recent Changes
- **November 20, 2025**: Major feature updates (completed and verified)
  - ✅ Added automatic file cleanup (files older than 6 months are deleted daily at 03:00 UTC)
  - ✅ Added broadcast system with `/sent` command (supports text, photos, videos, locations, documents)
  - ✅ Added **global anti-spam protection** - limits ALL user actions to 5 per 60 seconds using middleware
  - ✅ Added user blocking system with `/block` and `/unblock` commands
  - ✅ Added user activity tracking with automatic cleanup (daily at 04:00 UTC)
  - ✅ Updated database models with new fields (upload_date, is_blocked, UserActivity table)
  - ✅ Implemented TypeHandler middleware at group=-1 for global spam/block enforcement
  - ✅ ApplicationHandlerStop exception used to prevent handler execution for blocked/spam users

- **November 20, 2025**: Initial Replit setup
  - Migrated from nested directory structure to root
  - Secured BOT_TOKEN to environment secrets
  - Configured workflow for bot execution
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
│   ├── broadcast.py   # Broadcast and user blocking commands
│   ├── callbacks.py   # Callback query handlers
│   ├── files.py       # File upload and processing
│   ├── start.py       # Start command and message handling
│   └── user.py        # User commands (subscription, tickets)
├── services/          # Business logic services
│   ├── antispam.py    # Anti-spam service
│   ├── auth.py        # Authentication and authorization
│   ├── file_cleanup.py # Automatic file cleanup service
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
- **User**: Stores user information, access status, file tracking, and blocking status
- **SubscriptionLink**: Manages unique subscription tokens
- **File**: Tracks uploaded files, distribution status, and upload dates
- **FileDelivery**: Records file delivery history and status
- **Admin**: Manages bot administrators
- **UserActivity**: Tracks user actions for anti-spam detection

### Key Features
1. **Subscription Management**: Unique subscription links for user access
2. **File Distribution**: Automatic file distribution to subscribed users
3. **Admin Panel**: Comprehensive admin interface for management
4. **File Upload**: ZIP archive processing and file storage
5. **Statistics**: User and file statistics tracking
6. **Logging**: Comprehensive bot action logging
7. **Recovery**: File recovery system for failed deliveries
8. **Broadcast System**: Send messages to all active users (text, photos, videos, locations)
9. **User Blocking**: Block/unblock users from accessing the bot
10. **Anti-Spam Protection**: Prevents users from flooding the bot
11. **Auto-Cleanup**: Automatically deletes files older than 6 months

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

### Automated Tasks
- **File Cleanup**: Daily at 03:00 UTC - deletes files older than 6 months
- **Activity Cleanup**: Daily at 04:00 UTC - removes old user activity records

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
- `/sent` - Send broadcast message to all active users
  - Usage: `/sent Your message here`
  - Or reply to a message (photo/video/location) with `/sent` to forward it
- `/block USER_ID` - Block a user from accessing the bot
  - Example: `/block 123456789`
- `/unblock USER_ID` - Unblock a previously blocked user
  - Example: `/unblock 123456789`

### Admin Panel Features (via inline buttons)
- Create subscription links
- View statistics
- Upload ZIP archives
- Distribute files to users
- Send files to pending users
- Archive free tickets
- View subscriber list
- Manage administrators

## Anti-Spam System
- **Global Protection**: ALL user actions are rate-limited via TypeHandler middleware at group=-1
- **Rate Limit**: Maximum 5 actions per 60 seconds (commands, messages, callbacks)
- **Handler Blocking**: ApplicationHandlerStop exception prevents downstream handlers for spam/blocked users
- **Admin Exemption**: Admins bypass the global limit but have separate broadcast rate-limiting
- **User Feedback**: Blocked users receive notifications for both messages and callback queries
- **Auto-Cleanup**: Old activity records are automatically cleaned up daily at 04:00 UTC

## User Blocking System
- Blocked users cannot use the bot
- Their access is automatically revoked
- Admins can block/unblock users with commands
- Blocked users receive notification when blocked/unblocked

## File Management
- **Automatic Cleanup**: Files older than 6 months are automatically deleted
- **Daily Schedule**: Cleanup runs at 03:00 UTC every day
- **Safe Deletion**: Both main files and backups are removed
- **Database Cleanup**: File records are also removed from database

## Broadcast System
Admins can send broadcasts in two ways:

1. **Text Broadcast**:
   ```
   /sent Hello everyone! Important announcement.
   ```

2. **Media Broadcast** (reply to message):
   - Send a photo/video/location in the chat
   - Reply to it with `/sent` command
   - The bot will forward it to all active users

Supported media types:
- 📝 Text messages
- 📷 Photos (with captions)
- 🎥 Videos (with captions)
- 📍 Locations
- 📎 Documents (with captions)

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
- Daily automated cleanup tasks ensure optimal performance
- Anti-spam protection prevents abuse
