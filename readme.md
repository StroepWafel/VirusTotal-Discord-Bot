# VirusTotal Discord Bot

A Discord bot that automatically scans file attachments using VirusTotal's API to help keep your server safe from malicious files.

## Features

- Automatically scans file attachments posted in Discord channels
- Supports multiple file attachments in a single message
- Provides real-time scan results with links to detailed VirusTotal reports
- Handles large files and timeouts gracefully

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

Edit the `main.py` file and add your credentials:

```bash
nano main.py
```

Find these lines and replace the empty strings with your actual tokens:

```python
bot_token = 'YOUR_DISCORD_BOT_TOKEN_HERE'
virustotal_api_key = 'YOUR_VIRUSTOTAL_API_KEY_HERE'
```

Save the file (Ctrl+X, then Y, then Enter if using nano).

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

You can customize the bot behavior by editing the variables at the top of `main.py`:

- `mention_reply_author`: Set to `True` to mention the original message author in replies
- `timeout_seconds`: How long to wait for scan results (default: 300 seconds / 5 minutes)
- `max_attempts`: Maximum retry attempts when checking scan results (default: 2)
- Various message templates for customizing bot responses

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
