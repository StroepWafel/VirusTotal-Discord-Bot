# VirusTotal Discord Bot

A Discord bot that automatically scans file attachments using VirusTotal's API to help keep your server safe from malicious files.

## Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Prerequisites](#prerequisites)
- [Creating a Discord Bot](#creating-a-discord-bot)
  - [Step 1: Create a Discord Application](#step-1-create-a-discord-application)
  - [Step 2: Create a Bot](#step-2-create-a-bot)
  - [Step 3: Set Bot Permissions](#step-3-set-bot-permissions)
  - [Step 4: Invite Bot to Your Server](#step-4-invite-bot-to-your-server)
- [Getting a VirusTotal API Key](#getting-a-virustotal-api-key)
- [Hosting on Ubuntu Server](#hosting-on-ubuntu-server)
  - [Step 1: Update System Packages](#step-1-update-system-packages)
  - [Step 2: Install Python and pip](#step-2-install-python-and-pip)
  - [Step 3: Clone or Upload the Bot Files](#step-3-clone-or-upload-the-bot-files)
  - [Step 4: Create a Virtual Environment](#step-4-create-a-virtual-environment)
  - [Step 5: Install Dependencies](#step-5-install-dependencies)
  - [Step 6: Configure the Bot](#step-6-configure-the-bot)
  - [Step 7: Test the Bot](#step-7-test-the-bot)
  - [Step 8: Create a Systemd Service (Recommended)](#step-8-create-a-systemd-service-recommended)
  - [Step 9: Firewall Configuration (if applicable)](#step-9-firewall-configuration-if-applicable)
- [Usage](#usage)
- [Configuration Options](#configuration-options)
  - [Required Configuration](#required-configuration)
  - [Bot Behavior Settings](#bot-behavior-settings)
  - [Message Templates](#message-templates)
  - [Configuration File Details](#configuration-file-details)
- [Updating the Bot](#updating-the-bot)
  - [Manual Update](#manual-update)
  - [Automatic Updates (Optional)](#automatic-updates-optional)
  - [Alternative: Cron Job for Auto-Updates](#alternative-cron-job-for-auto-updates)
  - [Important Notes](#important-notes)
- [Uninstalling the Bot](#uninstalling-the-bot)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)
- [License](#license)

## Features

- Automatically scans file attachments posted in Discord channels
- Supports multiple file attachments in a single message
- Provides real-time scan results with links to detailed VirusTotal reports
- Handles large files and timeouts gracefully

## Demo:
[Visit the Discord Server!](https://discord.gg/BPRdkATNB6)


## Prerequisites

Before you begin, you'll need:

- A Discord application and bot token
- A VirusTotal API key (sign up at https://www.virustotal.com/gui/join-us)
- An Ubuntu server (or any Linux system with Python 3.7+)
- Basic knowledge of Linux command line

## Creating a Discord Bot

### Step 1: Create a Discord Application

1. Go to https://discord.com/developers/applications
2. Click "New Application" in the top right corner
3. Give your application a name and click "Create"

### Step 2: Create a Bot

1. In your application, go to the "Bot" section in the left sidebar
2. Click "Add Bot" and confirm
3. Under "Privileged Gateway Intents", enable "Message Content Intent"
   - This is required for the bot to read message content and attachments
4. Copy the bot token (you'll need this later)
   - Keep this token secret! Never share it publicly

### Step 3: Set Bot Permissions

1. Go to the "OAuth2" section in the left sidebar
2. Click on "URL Generator" submenu
3. Under "Scopes", check:
   - `bot`
4. Under "Bot Permissions", check the following:
- Change nickname
- View Channels
- Send Messages
- Send Messages in Threads
- Embed links
- Read Message History
- Add reactions
5. Copy the generated URL at the bottom of the page

### Step 4: Invite Bot to Your Server

1. Use the URL you copied in Step 3 to invite the bot to your Discord server
2. Select the server where you want to add the bot
3. Authorize the bot with the permissions you selected
4. The bot should now appear in your server (though it won't be online until you run it)

## Getting a VirusTotal API Key

1. Go to https://www.virustotal.com/gui/join-us
2. Sign up for a free account
3. Once logged in, go to your API key settings
4. Copy your API key (you'll need this later)

## Hosting on Ubuntu Server

### Step 1: Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Python and pip

```bash
sudo apt install python3 python3-pip python3-venv -y
```

### Step 3: Clone or Upload the Bot Files

If you're using Git:

```bash
git clone https://github.com/StroepWafel/VirusTotal-Discord-Bot
cd VirusTotal-Discord-Bot
```

Alternatively, you can upload the files using SCP, SFTP, or any file transfer method:

```bash
# Example using SCP from your local machine
scp -r VirusTotal-Discord-Bot user@your-server-ip:/path/to/destination
```

### Step 4: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Configure the Bot

The bot uses an external configuration file (`config.json`) to store your settings. This file is not tracked by git and will not be overwritten during updates, keeping your configuration safe.

**Important:** The bot will automatically create `config.json` on first run. You must run the bot at least once (even if it fails to start) to generate this file before you can edit it.

1. First, run the bot to generate the configuration file:

```bash
python3 main.py
```

The bot will fail to start (since tokens aren't set yet), but it will create `config.json` with default values. You should see a message like: "Created config.json - please edit it with your bot token and VirusTotal API key"

Press Ctrl+C to stop the bot.

2. Now edit the configuration file:

```bash
nano config.json
```

The file will already exist with default values in JSON format. You just need to add your credentials. Find the `"bot_token"` and `"virustotal_api_key"` fields and replace the empty strings with your actual tokens:

```json
{
    "bot_token": "YOUR_DISCORD_BOT_TOKEN_HERE",
    "virustotal_api_key": "YOUR_VIRUSTOTAL_API_KEY_HERE"
}
```

The full configuration file structure looks like this:

```json
{
    "bot_token": "",
    "virustotal_api_key": "",
    "mention_reply_author": false,
    "timeout_seconds": 300,
    "max_attempts": 2,
    "file_recieved_message": "Attachment `{filename}` received. Submitting for scanning...",
    "file_too_large_warning": "Attachment `{filename}` is too large ({file_size} bytes). Maximum allowed size is 1 GB. Proceed with caution",
    "download_error_warning": "Attachment `{filename}` could not be downloaded. Please proceed with caution.",
    "file_submitted_for_scanning_message": "Attachment `{filename}` has been submitted for scanning. Analysis ID: {analysis_id}",
    "file_scanning_error_message": "Error scanning `{filename}`: {e}",
    "results_recieved_message": "Scan completed for `{filename}`. \n {malicious_count}/{total_engines} vendors marked this file as malicious. \n More details can be found here: {results_url}",
    "scan_timeout_message": "Scan for `{filename}` timed out after waiting for {timeout} seconds. \n You might still be able to check the results here: {results_url}",
    "ignored_filetypes": [
        ".txt",
        ".md",
        ".json",
        ".xml",
        ".csv",
        ".log",
        ".ini",
        ".cfg",
        ".conf",
        ".yaml",
        ".yml",
        ".png",
        ".webp",
        ".jpeg",
        ".jpg"
    ]
}
```

3. Replace `YOUR_DISCORD_BOT_TOKEN_HERE` and `YOUR_VIRUSTOTAL_API_KEY_HERE` with your actual tokens. You can customize any of the other settings as needed.

4. Save the file (Ctrl+X, then Y, then Enter if using nano).

**Important:** The `config.json` file is excluded from git (via `.gitignore`), so your tokens and configuration will never be overwritten by updates. The bot automatically creates this file on first run, making setup easier. Simply run the bot once, then edit the generated file with your credentials.

### Step 7: Test the Bot

Run the bot manually to ensure everything works:

```bash
python3 main.py
```

You should see "Logged in as [Bot Name]!" if everything is configured correctly. 

Upload a file to the server the bot is in to check everything is working, you should eventually see a message similar to:
```bash
Scan completed for <filename>. 
X/Y vendors marked this file as malicious. 
More details can be found here: https://www.virustotal.com/gui/file/<SHA256>/detection 
```

Press Ctrl+C to stop the bot.

### Step 8: Create a Systemd Service (Recommended)

To keep the bot running in the background and automatically restart it if it crashes, create a systemd service:

1. Create the service file:

```bash
sudo nano /etc/systemd/system/virustotal-bot.service
```

2. Add the following content (adjust paths as needed):

```ini
[Unit]
Description=VirusTotal Discord Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/VirusTotal-Discord-Bot
Environment="PATH=/path/to/VirusTotal-Discord-Bot/venv/bin"
ExecStart=/path/to/VirusTotal-Discord-Bot/venv/bin/python3 /path/to/VirusTotal-Discord-Bot/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace:
- `your-username` with your Ubuntu username
- `/path/to/VirusTotal-Discord-Bot` with the actual path to your bot directory (for me this was `/root/VirusTotal-Discord-Bot`)

Save the file (Ctrl+X, then Y, then Enter if using nano).

3. Reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable virustotal-bot.service
sudo systemctl start virustotal-bot.service
```

4. Check the status:

```bash
sudo systemctl status virustotal-bot.service
```

5. View logs if needed:

```bash
sudo journalctl -u virustotal-bot.service -f
```

### Step 9: Firewall Configuration (if applicable)

If you have a firewall enabled, make sure it's not blocking outbound connections (the bot needs to connect to Discord and VirusTotal APIs):

```bash
# Check firewall status
sudo ufw status

# If firewall is active, ensure outbound connections are allowed (usually enabled by default)
```

## Usage

Once the bot is running, it will automatically:

1. Monitor all channels where it has access
2. Detect file attachments in messages
3. Download and scan files using VirusTotal
4. Reply to the message with scan results

The bot will reply with:
- A confirmation when a file is received
- Scan progress updates
- Final results showing how many antivirus engines detected the file as malicious
- A link to the full VirusTotal report

## Configuration Options

You can customize the bot behavior by editing the variables in your `config.json` file. The bot will automatically create this file with default values on first run if it doesn't exist.

**Important:** You must run the bot at least once (even if it fails to start due to missing tokens) to generate the `config.json` file. After it's created, you can edit it with your credentials and restart the bot.

### Required Configuration

**`bot_token`** (string, required)
- Your Discord bot token obtained from the Discord Developer Portal
- Get your token at: https://discord.com/developers/applications
- This is required for the bot to connect to Discord
- Example in `config.json`: `"bot_token": "YOUR_DISCORD_BOT_TOKEN_HERE"`

**`virustotal_api_key`** (string, required)
- Your VirusTotal API key for scanning files
- Sign up and get your API key at: https://www.virustotal.com/gui/join-us
- This is required for the bot to scan files
- Example in `config.json`: `"virustotal_api_key": "YOUR_VIRUSTOTAL_API_KEY_HERE"`

### Bot Behavior Settings

**`mention_reply_author`** (boolean, default: `false`)
- Whether to mention (ping) the original message author when replying with scan results
- Set to `true` to ping the user who uploaded the file
- Set to `false` to reply without mentioning (recommended for busy servers)
- Example in `config.json`: `"mention_reply_author": true`

**`timeout_seconds`** (integer, default: `300`)
- How long to wait (in seconds) for VirusTotal scan results before timing out
- Default is 300 seconds (5 minutes)
- Increase this value if you want to wait longer for scan results (e.g., for large files)
- Decrease this value if you want faster responses (may result in more timeouts)
- Example in `config.json`: `"timeout_seconds": 600`

**`max_attempts`** (integer, default: `2`)
- Maximum number of retry attempts when checking for scan results if an error occurs
- If VirusTotal API returns an error, the bot will retry this many times before giving up
- Increase for better reliability (e.g., `3` or `4`)
- Decrease for faster failure notifications
- Example in `config.json`: `"max_attempts": 3`

**`ignored_filetypes`** (array, default: `[".txt", ".md", ".json", ".xml", ".csv", ".log", ".ini", ".cfg", ".conf", ".yaml", ".yml", ".png", ".webp", ".jpeg", ".jpg"]`)
- Array of file extensions (with leading dot) that the bot should ignore and not scan
- Files with these extensions will be silently ignored to reduce unnecessary scans
- Add or remove file extensions as needed for your server
- Example in `config.json`: `"ignored_filetypes": [".txt", ".md", ".png", ".jpg", ".gif", ".webp"]`
- To scan all files, use an empty array: `"ignored_filetypes": []`

### Message Templates

You can customize all the messages the bot sends. Use placeholders like `{filename}`, `{file_size}`, `{analysis_id}`, `{malicious_count}`, `{total_engines}`, `{results_url}`, `{timeout}`, and `{e}` as placeholders that will be replaced with actual values.

**`file_recieved_message`** (string)
- Message sent when a file attachment is first received
- Available placeholders: `{filename}`
- Example in `config.json`: `"file_recieved_message": "Attachment `{filename}` received. Submitting for scanning..."`

**`file_too_large_warning`** (string)
- Message sent when a file is too large to scan (over 1 GB)
- Available placeholders: `{filename}`, `{file_size}`
- Example in `config.json`: `"file_too_large_warning": "Attachment `{filename}` is too large ({file_size} bytes). Maximum allowed size is 1 GB. Proceed with caution"`

**`download_error_warning`** (string)
- Message sent when the bot cannot download the file attachment from Discord
- Available placeholders: `{filename}`
- Example in `config.json`: `"download_error_warning": "Attachment `{filename}` could not be downloaded. Please proceed with caution."`

**`file_submitted_for_scanning_message`** (string)
- Message sent when a file has been successfully submitted to VirusTotal for scanning
- Available placeholders: `{filename}`, `{analysis_id}`
- Example in `config.json`: `"file_submitted_for_scanning_message": "Attachment `{filename}` has been submitted for scanning. Analysis ID: {analysis_id}"`

**`file_scanning_error_message`** (string)
- Message sent when an error occurs during the scanning process
- Available placeholders: `{filename}`, `{e}` (error message)
- Example in `config.json`: `"file_scanning_error_message": "Error scanning `{filename}`: {e}"`

**`results_recieved_message`** (string)
- Message sent when scan results are received from VirusTotal
- Available placeholders: `{filename}`, `{malicious_count}`, `{total_engines}`, `{results_url}`
- Use `\n` for new lines in the message
- Example in `config.json`: `"results_recieved_message": "Scan completed for `{filename}`. \n {malicious_count}/{total_engines} vendors marked this file as malicious. \n More details can be found here: {results_url}"`

**`scan_timeout_message`** (string)
- Message sent when the scan times out before completion
- Available placeholders: `{filename}`, `{timeout}`, `{results_url}`
- Use `\n` for new lines in the message
- Example in `config.json`: `"scan_timeout_message": "Scan for `{filename}` timed out after waiting for {timeout} seconds. \n You might still be able to check the results here: {results_url}"`

### Configuration File Details

The configuration file `config.json`:
- Is automatically created on first run if it doesn't exist (you must run the bot once to generate it)
- Is excluded from git (via `.gitignore`) so it won't be overwritten by updates
- Is located in the same directory as `main.py`
- Can be edited at any time - changes take effect after restarting the bot
- Contains all your sensitive tokens and custom settings in one place

**First-time setup:** Run the bot once with `python3 main.py` (it will fail to start without tokens, but this creates the `config.json` file). Then edit the file with your tokens and restart the bot.

## Updating the Bot

### Manual Update

To update the bot to the latest version:

1. Stop the bot service:

```bash
sudo systemctl stop virustotal-bot.service
```

2. Navigate to the bot directory:

```bash
cd /path/to/VirusTotal-Discord-Bot
```

Replace `/path/to/VirusTotal-Discord-Bot` with the actual path where you installed the bot.

3. Pull the latest changes from the repository:

```bash
git pull origin main
```

4. Update dependencies (if requirements.txt has changed):

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

5. Restart the bot service:

```bash
sudo systemctl start virustotal-bot.service
```

6. Verify the bot is running:

```bash
sudo systemctl status virustotal-bot.service
```

### Automatic Updates (Optional)

You can set up automatic updates using a systemd timer. This will check for updates daily and restart the bot if changes are found.

**Important:** Your configuration in `config.json` will never be overwritten by updates because it's excluded from git. The bot will continue to use your custom settings even after automatic updates.

1. Create an update script:

```bash
nano /path/to/VirusTotal-Discord-Bot/update.sh
```

2. Add the following content:

```bash
#!/bin/bash

BOT_DIR="/path/to/VirusTotal-Discord-Bot"
SERVICE_NAME="virustotal-bot.service"

cd "$BOT_DIR"

# Fetch latest changes
git fetch origin main

# Check if there are any updates
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
    echo "Update available. Updating bot..."
    
    # Stop the service
    systemctl stop "$SERVICE_NAME"
    
    # Pull latest changes
    git pull origin main
    
    # Update dependencies
    source venv/bin/activate
    pip install --upgrade -r requirements.txt
    deactivate
    
    # Start the service
    systemctl start "$SERVICE_NAME"
    
    echo "Bot updated and restarted successfully."
else
    echo "Bot is up to date."
fi
```

Replace `/path/to/VirusTotal-Discord-Bot` with the actual path where you installed the bot.

3. Make the script executable:

```bash
chmod +x /path/to/VirusTotal-Discord-Bot/update.sh
```

4. Create a systemd timer file:

```bash
sudo nano /etc/systemd/system/virustotal-bot-update.timer
```

5. Add the following content:

```ini
[Unit]
Description=Daily update check for VirusTotal Discord Bot
After=network.target

[Timer]
OnCalendar=daily
RandomizedDelaySec=3600
Persistent=true

[Install]
WantedBy=timers.target
```

6. Create a systemd service file for the update:

```bash
sudo nano /etc/systemd/system/virustotal-bot-update.service
```

7. Add the following content:

```ini
[Unit]
Description=Update VirusTotal Discord Bot
After=network.target

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/path/to/VirusTotal-Discord-Bot
ExecStart=/path/to/VirusTotal-Discord-Bot/update.sh

[Install]
WantedBy=multi-user.target
```

Replace:
- `your-username` with your Ubuntu username
- `/path/to/VirusTotal-Discord-Bot` with the actual path to your bot directory

8. Enable and start the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable virustotal-bot-update.timer
sudo systemctl start virustotal-bot-update.timer
```

9. Check the timer status:

```bash
sudo systemctl status virustotal-bot-update.timer
```

10. View when the next update check will run:

```bash
sudo systemctl list-timers virustotal-bot-update.timer
```

The timer will check for updates daily at a random time (within a 1-hour window) to avoid server load spikes. You can manually trigger an update check by running:

```bash
sudo systemctl start virustotal-bot-update.service
```

### Alternative: Cron Job for Auto-Updates

If you prefer using cron instead of systemd timers, you can add a cron job:

1. Edit the crontab:

```bash
crontab -e
```

2. Add the following line (runs daily at 2 AM):

```bash
0 2 * * * /path/to/VirusTotal-Discord-Bot/update.sh >> /var/log/virustotal-bot-update.log 2>&1
```

Replace `/path/to/VirusTotal-Discord-Bot` with the actual path where you installed the bot.

### Important Notes

- Your configuration in `config.json` is automatically protected from being overwritten by updates. This file is excluded from git via `.gitignore`, so your tokens and settings will always be preserved.
- Auto-updates will restart the bot automatically, which may cause brief downtime during the update process.
- If you make custom modifications to `main.py` (beyond configuration), those changes will be overwritten by updates. Consider using git branches or forks if you need to maintain custom code changes.
- The update script only updates code files, not your `config.json` file, so your configuration is always safe.

## Uninstalling the Bot

If you need to remove the bot from your server, follow these steps:

### Step 1: Stop and Disable the Systemd Service

If you created a systemd service, stop and disable it:

```bash
sudo systemctl stop virustotal-bot.service
sudo systemctl disable virustotal-bot.service
```

### Step 2: Remove the Systemd Service File

```bash
sudo rm /etc/systemd/system/virustotal-bot.service
sudo systemctl daemon-reload
```

### Step 3: Remove the Bot Files

Navigate to the bot directory and remove it:

```bash
cd /path/to/VirusTotal-Discord-Bot
cd ..
rm -rf VirusTotal-Discord-Bot
```

Replace `/path/to/VirusTotal-Discord-Bot` with the actual path where you installed the bot.

### Step 4: Remove Bot from Discord Server (Optional)

If you want to remove the bot from your Discord server:

1. Go to your Discord server
2. Right-click on the bot in the member list
3. Select "Kick" or "Ban" to remove it from the server

Alternatively, you can revoke the bot's access in the server settings under "Integrations" or "Members".

### Note

This will remove the bot files and service, but will not uninstall Python or pip packages that may be used by other applications on your system. If you want to remove the Python packages installed for this bot specifically, you can deactivate and remove the virtual environment before deleting the bot directory:

```bash
cd /path/to/VirusTotal-Discord-Bot
source venv/bin/activate
deactivate
cd ..
rm -rf VirusTotal-Discord-Bot
```

## Troubleshooting

### Bot doesn't respond to file attachments

- Verify the bot is online in your Discord server
- Check that the Message Content Intent is enabled in Discord Developer Portal
- Ensure the bot has "View Channels" and "Read Message History" permissions
- Check bot logs for errors: `sudo journalctl -u virustotal-bot.service -f`

### Bot crashes or stops running

- Check systemd logs: `sudo journalctl -u virustotal-bot.service -n 50`
- Verify your API keys are correct
- Ensure your server has internet connectivity
- Check if the bot token is valid and hasn't been regenerated

### Permission errors

- Make sure the bot has all required permissions in the Discord server
- Verify the bot's role in the server has the necessary channel permissions

## Security Notes

- Never commit your bot token or API keys to version control
- Keep your bot token and API keys secure
- Regularly regenerate tokens if they're accidentally exposed
- Consider using environment variables or a configuration file excluded from Git for sensitive data

## License

See LICENSE file for details.

## ToDo

- Add list of filetypes to ignore when scanning
