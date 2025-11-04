# This bot requires the 'message_content' intent.

import json
import discord
import vt
import aiohttp
import io
import asyncio
from datetime import datetime, timedelta
import hashlib
import os
import sys




# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Do not modify any code below this line unless you know what you are doing!
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_app_folder() -> str:
    """
    Determine the application folder path.
    
    Returns:
        str: Path to the application directory (executable dir if frozen, script dir otherwise)
    """
    if getattr(sys, 'frozen', False):
        # When compiled with PyInstaller, return the directory containing the executable
        return os.path.dirname(sys.executable)
    
    # For development/script mode, find the directory containing main.py
    # Start by checking if we can find main.py relative to this file's location
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if main.py is in the parent directory of this file (Src directory)
    parent_dir = os.path.dirname(current_file_dir)
    main_py_path = os.path.join(parent_dir, 'main.py')
    if os.path.exists(main_py_path):
        return parent_dir
    
    # If not found, search from current working directory up the tree
    current_dir = os.path.abspath(os.getcwd())
    search_dir = current_dir
    
    while True:
        main_py_path = os.path.join(search_dir, 'main.py')
        if os.path.exists(main_py_path):
            return search_dir
        
        # Move up one directory
        parent_dir = os.path.dirname(search_dir)
        if parent_dir == search_dir:  # Reached root directory
            break
        search_dir = parent_dir
    
    # Final fallback: return the directory containing this file (helpers directory)
    # and go up one level to get the Src directory
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_file_exists(filepath: str, default_content) -> None:
    """
    Create a file with default content if it doesn't exist.
    
    Args:
        filepath: Path to the file to create
        default_content: Default content to write to the file
    """
    if not os.path.isfile(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(default_content, f, indent=4)
        print(f"Created missing file: {filepath}")

def ensure_json_valid(filepath: str, default_content: dict) -> None:
    """
    Validate and clean a JSON configuration file.
    
    This function ensures the JSON file is valid and contains only expected keys.
    If the file is corrupted or contains extra keys, it will be cleaned up.
    
    Args:
        filepath: Path to the JSON file to validate
        default_content: Default configuration structure to validate against
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # Reset to defaults if file is corrupted
                with open(filepath, 'w', encoding='utf-8') as fw:
                    json.dump(default_content, fw, indent=4)
                print(f"Invalid JSON in {filepath}. Resetting to default.")
                return

        modified = False
        cleaned_data = {}

        # Copy over valid keys from default_config
        for key, default_value in default_content.items():
            if key in data:
                cleaned_data[key] = data[key]
            else:
                cleaned_data[key] = default_value
                modified = True
                print(f"Added missing key '{key}' to {filepath}")

        # Check for and remove extra keys
        extra_keys = set(data.keys()) - set(default_content.keys())
        if extra_keys:
            modified = True
            print(f"Removing extra keys from {filepath}: {extra_keys}")

        if modified:
            # Create a backup before making changes
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{filepath}.backup_{timestamp}.json"
            with open(backup_path, 'w', encoding='utf-8') as backup_file:
                json.dump(data, backup_file, indent=4)
            print(f"Backed up original config file to {backup_path}")

            # Write cleaned data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=4)
            print(f"Successfully cleaned and updated {filepath}")

    except Exception as e:
        print(f"Error validating JSON file {filepath}: {e}")

APP_FOLDER = get_app_folder()
CONFIG_PATH = os.path.join(APP_FOLDER, 'config.json')

default_config = {
    "bot_token": "",
    "virustotal_api_key": "",
    "mention_reply_author": False,
    "timeout_seconds": 300,
    "max_attempts": 2,
    "file_recieved_message": "Attachment `{filename}` received. Submitting for scanning...",
    "file_too_large_warning": "Attachment `{filename}` is too large ({file_size} bytes). Maximum allowed size is 1 GB. Proceed with caution",
    "download_error_warning": "Attachment `{filename}` could not be downloaded. Please proceed with caution.",
    "file_submitted_for_scanning_message": "Attachment `{filename}` has been submitted for scanning. File hash: {file_hash}",
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
        ".png",
        ".webp",
        ".jpeg",
        ".jpg",
        ".yml",
        ".yaml"
    ]
}

ensure_file_exists(CONFIG_PATH, default_config)
ensure_json_valid(CONFIG_PATH, default_config)

with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
    config = json.load(f)

bot_token = config.get("bot_token", default_config["bot_token"])
virustotal_api_key = config.get("virustotal_api_key", default_config["virustotal_api_key"])
mention_reply_author = config.get("mention_reply_author", default_config["mention_reply_author"])
timeout_seconds = config.get("timeout_seconds", default_config["timeout_seconds"])
max_attempts = config.get("max_attempts", default_config["max_attempts"])
file_recieved_message = config.get("file_recieved_message", default_config["file_recieved_message"])
file_too_large_warning = config.get("file_too_large_warning", default_config["file_too_large_warning"])
download_error_warning = config.get("download_error_warning", default_config["download_error_warning"])
file_submitted_for_scanning_message = config.get("file_submitted_for_scanning_message", default_config["file_submitted_for_scanning_message"])
file_scanning_error_message = config.get("file_scanning_error_message", default_config["file_scanning_error_message"])
results_recieved_message = config.get("results_recieved_message", default_config["results_recieved_message"])
scan_timeout_message = config.get("scan_timeout_message", default_config["scan_timeout_message"])
ignored_filetypes = config.get("ignored_filetypes", default_config["ignored_filetypes"])

vt_client = vt.Client(virustotal_api_key)

class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if not message.attachments:
            return

        if any(message.attachments[0].filename.lower().endswith(ext) for ext in ignored_filetypes):
            print(f'Ignoring attachment {message.attachments[0].filename} from {message.author} due to ignored filetype.')
            return

        if len(message.attachments) > 1:
            # Initialize sections with a placeholder for each file
            results_sections = [
                file_recieved_message.format(filename=att.filename)
                for att in message.attachments
            ]

            separator = "\n\n--------------------------------------------------------------------\n\n"
            combined_message = separator.join(results_sections)
            reply_msg = await message.reply(combined_message, mention_author=mention_reply_author)

            # Process each attachment sequentially and live-update the single message
            for idx, attachment in enumerate(message.attachments):
                file_size = attachment.size
                filename = attachment.filename

                print(f'Received attachment: {filename} ({file_size} bytes) from {message.author}')

                if file_size >= 1073741824:
                    results_sections[idx] = file_too_large_warning.format(
                        filename=filename, file_size=file_size
                    )
                    await reply_msg.edit(content=separator.join(results_sections))
                    print(f'Attachment {filename} is too large ({file_size} bytes). Skipping scan.')
                    continue

                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status != 200:
                            results_sections[idx] = download_error_warning.format(filename=filename)
                            await reply_msg.edit(content=separator.join(results_sections))
                            print(f'Failed to download attachment {filename}. HTTP status: {resp.status}')
                            continue
                        file_bytes = await resp.read()

                file_stream = io.BytesIO(file_bytes)
                file_hash = hashlib.sha256(file_bytes).hexdigest()

                try:
                    async with vt.Client(virustotal_api_key) as vt_client:
                        analysis = await vt_client.scan_file_async(file_stream)
                        print(f'Submitted {filename} for scanning. File Hash: {file_hash}')
                        results_sections[idx] = file_submitted_for_scanning_message.format(
                            filename=filename,
                            file_hash=file_hash
                        )
                        await reply_msg.edit(content=separator.join(results_sections))

                        
                        start_time = datetime.now()
                        attempt = 0

                        while True:
                            await asyncio.sleep(10)
                            attempt += 1
                            try:
                                analysis = await vt_client.get_object_async("/analyses/{}", analysis.id)
                            except Exception as e:
                                if attempt < max_attempts:
                                    print(f'Error retrieving analysis for {filename} (attempt {attempt}/{max_attempts}): {e}. Retrying...')
                                    await asyncio.sleep(5)
                                    continue
                                else:
                                    raise

                            if analysis.status == 'completed':
                                stats = analysis.stats
                                malicious_count = stats.get("malicious", 0)
                                total_engines = sum(stats.values())
                                results_url = f'https://www.virustotal.com/gui/file/{file_hash}/detection'
                                results_sections[idx] = results_recieved_message.format(
                                    filename=filename,
                                    malicious_count=malicious_count,
                                    total_engines=total_engines,
                                    results_url=results_url
                                )
                                await reply_msg.edit(content=separator.join(results_sections))
                                print(f'Scan completed for {filename}. {malicious_count}/{total_engines} vendors marked this file as malicious.')
                                break

                            if (datetime.now() - start_time).total_seconds() > timeout_seconds:
                                results_url = f'https://www.virustotal.com/gui/file/{file_hash}/detection'
                                results_sections[idx] = scan_timeout_message.format(
                                    filename=filename,
                                    timeout=timeout_seconds,
                                    results_url=results_url
                                )
                                await reply_msg.edit(content=separator.join(results_sections))
                                print(f'Scan for {filename} timed out after {timeout_seconds} seconds.')
                                break
                except Exception as e:
                    results_sections[idx] = file_scanning_error_message.format(
                        filename=filename,
                        e=e
                    )
                    await reply_msg.edit(content=separator.join(results_sections))
                    print(f'Error scanning {filename}: {e}')

            return

        for attachment in message.attachments:
            file_size = attachment.size
            filename = attachment.filename

            reply_msg = await message.reply(
                file_recieved_message.format(filename=filename),
                mention_author=mention_reply_author
            )

            print(f'Received attachment: {filename} ({file_size} bytes) from {message.author}')

            if file_size >= 1073741824:
                too_large_message = file_too_large_warning.format(
                    filename=filename, file_size=file_size
                )
                await reply_msg.edit(too_large_message)
                print(f'Attachment {filename} is too large ({file_size} bytes). Skipping scan.')
                continue

            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as resp:
                    if resp.status != 200:
                        await reply_msg.edit(
                            download_error_warning.format(filename=filename)
                        )
                        print(f'Failed to download attachment {filename}. HTTP status: {resp.status}')
                        continue
                    file_bytes = await resp.read()

            file_stream = io.BytesIO(file_bytes)

            file_hash = hashlib.sha256(file_bytes).hexdigest()

            try:
                async with vt.Client(virustotal_api_key) as vt_client:
                    analysis = await vt_client.scan_file_async(file_stream)

                    await reply_msg.edit(
                        content = file_submitted_for_scanning_message.format(
                            filename=filename, 
                            analysis_id=analysis.id
                            )
                    )
                    print(f'Submitted {filename} for scanning. Analysis ID: {analysis.id}')

                    start_time = datetime.now()
                    attempt = 0

                    while True:
                        await asyncio.sleep(10)
                        attempt += 1
                        try:
                            analysis = await vt_client.get_object_async("/analyses/{}", analysis.id)
                        except Exception as e:
                            if attempt < max_attempts:
                                print(f'Error retrieving analysis for {filename} (attempt {attempt}/{max_attempts}): {e}. Retrying...')
                                await asyncio.sleep(5)
                                continue
                            else:
                                raise

                        if analysis.status == 'completed':
                            stats = analysis.stats
                            malicious_count = stats.get("malicious", 0)
                            total_engines = sum(stats.values())

                            results_url = f'https://www.virustotal.com/gui/file/{file_hash}/detection'

                            results_message = results_recieved_message.format(
                                filename=filename,
                                malicious_count=malicious_count,
                                total_engines=total_engines,
                                results_url=results_url
                            )

                            await reply_msg.edit(content=results_message)

                            print(f'Scan completed for {filename}. {malicious_count}/{total_engines} vendors marked this file as malicious.')
                            break

                        if (datetime.now() - start_time).total_seconds() > timeout_seconds:
                            results_url = f'https://www.virustotal.com/gui/file/{file_hash}/detection'
                            timeout_message = scan_timeout_message.format(
                                filename=filename,
                                timeout=timeout_seconds,
                                results_url=results_url
                            )
                            await reply_msg.edit(content=timeout_message)

                            print(f'Scan for {filename} timed out after {timeout_seconds} seconds.')
                            break
            except Exception as e:
                await reply_msg.edit(content = file_scanning_error_message.format(
                    filename=filename,
                    e=e
                ))
                print(f'Error scanning {filename}: {e}')


intents = discord.Intents.default()
intents.message_content = True

discord.client = DiscordClient(intents=intents)
discord.client.run(bot_token)
