# Discord Link Cleaner Bot

A Discord bot that automatically removes tracking parameters from URLs in messages to help protect user privacy. The bot detects URLs with tracking parameters (like `utm_source`, `fbclid`, `gclid`, etc.) and reposts the message with cleaned URLs.

## Table of Contents

- [Discord Link Cleaner Bot](#discord-link-cleaner-bot)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Creating a Discord Bot](#creating-a-discord-bot)
    - [Step 1: Create a Discord Application](#step-1-create-a-discord-application)
    - [Step 2: Create a Bot](#step-2-create-a-bot)
    - [Step 3: Set Bot Permissions](#step-3-set-bot-permissions)
    - [Step 4: Invite Bot to Your Server](#step-4-invite-bot-to-your-server)
  - [Hosting on Ubuntu Server](#hosting-on-ubuntu-server)
    - [Step 1: Update System Packages](#step-1-update-system-packages)
    - [Step 2: Install Python and pip](#step-2-install-python-and-pip)
    - [Step 3: Clone or Upload the Bot Files](#step-3-clone-or-upload-the-bot-files)
    - [Step 4: Create a Virtual Environment](#step-4-create-a-virtual-environment)
    - [Step 5: Install Dependencies](#step-5-install-dependencies)
    - [Step 6: Configure the Bot](#step-6-configure-the-bot)
    - [Step 7: Test the Bot](#step-7-test-the-bot)
    - [Step 8: Create a Systemd Service (Recommended)](#step-8-create-a-systemd-service-recommended)
  - [Usage](#usage)
  - [Configuration Options](#configuration-options)
    - [Required Configuration](#required-configuration)
    - [Bot Behavior Settings](#bot-behavior-settings)
    - [Tracker Configuration](#tracker-configuration)
  - [Updating the Bot](#updating-the-bot)
    - [Manual Update](#manual-update)
  - [Uninstalling the Bot](#uninstalling-the-bot)
  - [Troubleshooting](#troubleshooting)
  - [Security Notes](#security-notes)
  - [License](#license)

## Features

- Automatically detects URLs in Discord messages
- Removes tracking parameters from URLs (Google Analytics, Facebook, TikTok, Twitter, Reddit, and many more)
- Deletes the original message and reposts it with cleaned URLs
- Configurable tracker list via `trackers.json`
- Supports custom regex patterns for URL detection
- Optional requirement for messages to contain links before processing

## Prerequisites

Before you begin, you'll need:

- A Discord application and bot token
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
   - This is required for the bot to read message content and detect URLs
4. Copy the bot token (you'll need this later)
   - Keep this token secret! Never share it publicly

### Step 3: Set Bot Permissions

1. Go to the "OAuth2" section in the left sidebar
2. Click on "URL Generator" submenu
3. Under "Scopes", check:
   - `bot`
4. Under "Bot Permissions", check the following:
   - View Channels
   - Send Messages
   - Send Messages in Threads
   - Manage Messages
   - Read Message History
5. Copy the generated URL at the bottom of the page

### Step 4: Invite Bot to Your Server

1. Use the URL you copied in Step 3 to invite the bot to your Discord server
2. Select the server where you want to add the bot
3. Authorize the bot with the permissions you selected
4. The bot should now appear in your server (though it won't be online until you run it)

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
git clone https://github.com/your-username/Discord-Link-Cleaner
cd Discord-Link-Cleaner
```

Alternatively, you can upload the files using SCP, SFTP, or any file transfer method:

```bash
# Example using SCP from your local machine
scp -r Discord-Link-Cleaner user@your-server-ip:/path/to/destination
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

**Note:** The bot only requires `discord.py`. You can simplify `requirements.txt` to just contain `discord.py` if desired.

### Step 6: Configure the Bot

The bot uses an external configuration file (`config.json`) to store your settings. This file is not tracked by git and will not be overwritten during updates, keeping your configuration safe.

**Important:** The bot will automatically create `config.json` on first run. You must run the bot at least once (even if it fails to start) to generate this file before you can edit it.

1. First, run the bot to generate the configuration file:

```bash
python3 main.py
```

The bot will fail to start (since tokens aren't set yet), but it will create `config.json` with default values. You should see a message like: "Created missing file: config.json"

Press Ctrl+C to stop the bot.

2. Now edit the configuration file:

```bash
nano config.json
```

The file will already exist with default values in JSON format. You just need to add your bot token. Find the `"bot_token"` field and replace the empty string with your actual token:

```json
{
    "bot_token": "YOUR_DISCORD_BOT_TOKEN_HERE",
    "mention_reply_author": true,
    "require_links": true,
    "regex_keys": "(?i)\\b((?:https?://|www\\.)[^\\s<>\"']+|(?:[a-z0-9-]+\\.)+[a-z]{2,}(?:/[^\\s<>\"']*)?)\\b"
}
```

3. Replace `YOUR_DISCORD_BOT_TOKEN_HERE` with your actual bot token. You can customize any of the other settings as needed (see [Configuration Options](#configuration-options) below).

4. Save the file (Ctrl+X, then Y, then Enter if using nano).

**Important:** The `config.json` file is excluded from git (via `.gitignore`), so your tokens and configuration will never be overwritten by updates. The bot automatically creates this file on first run, making setup easier.

### Step 7: Test the Bot

Run the bot manually to ensure everything works:

```bash
python3 main.py
```

You should see "Logged in as [Bot Name]!" if everything is configured correctly.

Post a message with a URL containing tracking parameters (e.g., `https://example.com/page?utm_source=test&fbclid=123`) to check everything is working. The bot should delete your message and repost it with the tracking parameters removed.

Press Ctrl+C to stop the bot.

### Step 8: Create a Systemd Service (Recommended)

To keep the bot running in the background and automatically restart it if it crashes, create a systemd service:

1. Create the service file:

```bash
sudo nano /etc/systemd/system/discord-link-cleaner.service
```

2. Add the following content (adjust paths as needed):

```ini
[Unit]
Description=Discord Link Cleaner Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/Discord-Link-Cleaner
Environment="PATH=/path/to/Discord-Link-Cleaner/venv/bin"
ExecStart=/path/to/Discord-Link-Cleaner/venv/bin/python3 /path/to/Discord-Link-Cleaner/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Replace:
- `your-username` with your Ubuntu username
- `/path/to/Discord-Link-Cleaner` with the actual path to your bot directory

Save the file (Ctrl+X, then Y, then Enter if using nano).

3. Reload systemd and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-link-cleaner.service
sudo systemctl start discord-link-cleaner.service
```

4. Check the status:

```bash
sudo systemctl status discord-link-cleaner.service
```

5. View logs if needed:

```bash
sudo journalctl -u discord-link-cleaner.service -f
```

## Usage

Once the bot is running, it will automatically:

1. Monitor all channels where it has access
2. Detect URLs in messages
3. Check if URLs contain tracking parameters
4. If trackers are found, delete the original message and repost it with cleaned URLs
5. Include a notice indicating which companies' trackers were removed

The bot will only process messages that contain URLs (if `require_links` is set to `true` in the config).

**Example:**
- Original message: `Check this out: https://example.com/page?utm_source=test&fbclid=123`
- Bot reposts: `@user Your message has been reposted without trackers from Google, and Meta: Check this out: https://example.com/page`

## Configuration Options

You can customize the bot behavior by editing the variables in your `config.json` file. The bot will automatically create this file with default values on first run if it doesn't exist.

**Important:** You must run the bot at least once (even if it fails to start due to missing tokens) to generate the `config.json` file. After it's created, you can edit it with your credentials and restart the bot.

### Required Configuration

**`bot_token`** (string, required)
- Your Discord bot token obtained from the Discord Developer Portal
- Get your token at: https://discord.com/developers/applications
- This is required for the bot to connect to Discord
- Example in `config.json`: `"bot_token": "YOUR_DISCORD_BOT_TOKEN_HERE"`

### Bot Behavior Settings

**`mention_reply_author`** (boolean, default: `true`)
- Whether to mention (ping) the original message author when reposting with cleaned URLs
- Set to `true` to ping the user who posted the message
- Set to `false` to repost without mentioning (recommended for busy servers)
- Example in `config.json`: `"mention_reply_author": false`

**`require_links`** (boolean, default: `true`)
- Whether the bot should only process messages that contain URLs
- Set to `true` to only process messages with links (recommended)
- Set to `false` to process all messages (not recommended, as the bot will check every message)
- Example in `config.json`: `"require_links": true`

**`regex_keys`** (string, default: `"(?i)\\b((?:https?://|www\\.)[^\\s<>\"']+|(?:[a-z0-9-]+\\.)+[a-z]{2,}(?:/[^\\s<>\"']*)?)\\b"`)
- Regular expression pattern used to detect URLs in messages
- The default pattern matches HTTP/HTTPS URLs and domain names
- Only modify if you understand regex patterns and need custom URL detection
- Example in `config.json`: `"regex_keys": "(?i)\\b((?:https?://|www\\.)[^\\s<>\"']+|(?:[a-z0-9-]+\\.)+[a-z]{2,}(?:/[^\\s<>\"']*)?)\\b"`

### Tracker Configuration

The bot uses `trackers.json` to define which URL parameters should be removed. This file is automatically created on first run with a comprehensive list of tracking parameters from major companies:

- **Google**: utm_source, utm_medium, utm_campaign, gclid, etc.
- **Meta (Facebook)**: fbclid, fb_action_ids, fb_source, etc.
- **TikTok**: ttclid, tt_content_id, etc.
- **Microsoft**: msclkid, li_fat_id, etc.
- **Twitter**: twclid, ref_src, etc.
- **Reddit**: rdt_cid, rdt_source, etc.
- **Snapchat**: sc_cid, sc_source, etc.
- **Pinterest**: epik, pin_campaign, etc.
- **Amazon**: tag, ascsubtag, etc.
- **Mailchimp**: mc_cid, mc_eid
- **HubSpot**: hsa_acc, hsa_cam, etc.
- **Adobe**: s_cid, ef_id
- **Salesforce**: pi_campaign_id, pi_source, etc.
- **Shopify**: shopify, shopify_app, etc.
- **Email**: mkt_tok, _hsenc, etc.
- **Affiliate**: aff_id, affiliate_id, ref, etc.
- **Analytics**: _ga, _gl, _gid, etc.

You can customize `trackers.json` to add or remove tracking parameters as needed. The file structure is:

```json
{
    "CompanyName": ["param1", "param2", "param3"],
    "AnotherCompany": ["param4", "param5"]
}
```

**Note:** The bot automatically validates and cleans `trackers.json` on startup, ensuring it matches the expected structure. If you add invalid entries, they may be removed.

### Configuration File Details

The configuration files:
- `config.json`: Contains bot token and behavior settings
- `trackers.json`: Contains the list of tracking parameters to remove

Both files:
- Are automatically created on first run if they don't exist
- Are excluded from git (via `.gitignore`) so they won't be overwritten by updates
- Are located in the same directory as `main.py`
- Can be edited at any time - changes take effect after restarting the bot
- Are automatically validated and cleaned on startup

**First-time setup:** Run the bot once with `python3 main.py` (it will fail to start without tokens, but this creates the config files). Then edit `config.json` with your bot token and restart the bot.

## Updating the Bot

### Manual Update

To update the bot to the latest version:

1. Stop the bot service:

```bash
sudo systemctl stop discord-link-cleaner.service
```

2. Navigate to the bot directory:

```bash
cd /path/to/Discord-Link-Cleaner
```

Replace `/path/to/Discord-Link-Cleaner` with the actual path where you installed the bot.

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
sudo systemctl start discord-link-cleaner.service
```

6. Verify the bot is running:

```bash
sudo systemctl status discord-link-cleaner.service
```

**Important Notes:**
- Your configuration in `config.json` and `trackers.json` will never be overwritten by updates because they're excluded from git. The bot will continue to use your custom settings even after updates.
- The bot automatically validates and cleans configuration files on startup, ensuring they match the expected structure.

## Uninstalling the Bot

If you need to remove the bot from your server, follow these steps:

### Step 1: Stop and Disable the Systemd Service

If you created a systemd service, stop and disable it:

```bash
sudo systemctl stop discord-link-cleaner.service
sudo systemctl disable discord-link-cleaner.service
```

### Step 2: Remove the Systemd Service File

```bash
sudo rm /etc/systemd/system/discord-link-cleaner.service
sudo systemctl daemon-reload
```

### Step 3: Remove the Bot Files

Navigate to the bot directory and remove it:

```bash
cd /path/to/Discord-Link-Cleaner
cd ..
rm -rf Discord-Link-Cleaner
```

Replace `/path/to/Discord-Link-Cleaner` with the actual path where you installed the bot.

### Step 4: Remove Bot from Discord Server (Optional)

If you want to remove the bot from your Discord server:

1. Go to your Discord server
2. Right-click on the bot in the member list
3. Select "Kick" or "Ban" to remove it from the server

Alternatively, you can revoke the bot's access in the server settings under "Integrations" or "Members".

### Note

This will remove the bot files and service, but will not uninstall Python or pip packages that may be used by other applications on your system. If you want to remove the Python packages installed for this bot specifically, you can deactivate and remove the virtual environment before deleting the bot directory:

```bash
cd /path/to/Discord-Link-Cleaner
source venv/bin/activate
deactivate
cd ..
rm -rf Discord-Link-Cleaner
```

## Troubleshooting

### Bot doesn't respond to URLs

- Verify the bot is online in your Discord server
- Check that the Message Content Intent is enabled in Discord Developer Portal
- Ensure the bot has "View Channels", "Read Message History", and "Manage Messages" permissions
- Verify `require_links` is set appropriately in `config.json`
- Check bot logs for errors: `sudo journalctl -u discord-link-cleaner.service -f`

### Bot crashes or stops running

- Check systemd logs: `sudo journalctl -u discord-link-cleaner.service -n 50`
- Verify your bot token is correct
- Ensure your server has internet connectivity
- Check if the bot token is valid and hasn't been regenerated
- Verify the regex pattern in `config.json` is valid

### Permission errors

- Make sure the bot has all required permissions in the Discord server
- Verify the bot's role in the server has the necessary channel permissions
- Ensure "Manage Messages" permission is granted so the bot can delete messages

### Bot doesn't remove trackers

- Check that `trackers.json` contains the tracking parameters you expect
- Verify the URL format matches the regex pattern in `config.json`
- Check bot logs to see if URLs are being detected

## Security Notes

- Never commit your bot token to version control
- Keep your bot token secure
- Regularly regenerate tokens if they're accidentally exposed
- The bot requires "Manage Messages" permission to delete and repost messages - only grant this permission if you trust the bot
- The bot automatically validates configuration files on startup to prevent malicious modifications

## License

See LICENSE file for details.
