# This bot requires the 'message_content' intent.

import json
import discord
import re
import io
import asyncio
from datetime import datetime, timedelta
import hashlib
import os
import sys

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

def has_link(message: str) -> bool:
    return bool(REGEX.search(message))


def build_param_index(tracker_map):
    index = {}
    for company, params in tracker_map.items():
        for param in params:
            index[param] = company
    return index

APP_FOLDER = get_app_folder()
CONFIG_PATH = os.path.join(APP_FOLDER, 'config.json')

default_config = {
    "bot_token": "",
    "mention_reply_author": True,
    "regex_keys": "(?i)\\b((?:https?://|www\\.)[^\\s<>\"']+|(?:[a-z0-9-]+\\.)+[a-z]{2,}(?:/[^\\s<>\"']*)?)\\b"
}

ensure_file_exists(CONFIG_PATH, default_config)
ensure_json_valid(CONFIG_PATH, default_config)

with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
    config = json.load(f)

bot_token = config.get("bot_token", default_config["bot_token"])
mention_reply_author = config.get("mention_reply_author", default_config["mention_reply_author"])

try:
    REGEX = re.compile(
        config.get("regex_keys", default_config["regex_keys"])
    )
except re.error as e:
    raise RuntimeError(f"Invalid regex in config.json: {e}")


class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if not (has_link(message.content)):
            return
        
        await message.reply("link detected", mention_author=mention_reply_author)
        

        



intents = discord.Intents.default()
intents.message_content = True

discord.client = DiscordClient(intents=intents)
discord.client.run(bot_token)
