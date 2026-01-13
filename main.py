# This bot requires the 'message_content' intent.

import json
import discord
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
import os
import sys

#--------------------------------------------------------------------
# Setup
#--------------------------------------------------------------------


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
TRACKERS_PATH = os.path.join(APP_FOLDER, 'trackers.json')

default_config = {
    "bot_token": "",
    "mention_reply_author": True,
    "require_links": True,
    "regex_keys": "(?i)\\b((?:https?://|www\\.)[^\\s<>\"']+|(?:[a-z0-9-]+\\.)+[a-z]{2,}(?:/[^\\s<>\"']*)?)\\b"
}

default_trackers = {
    "Google": ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "gclid", "gclsrc", "dclid", "wbraid", "gbraid", "gad_source"],
    "Meta": ["fbclid", "fb_action_ids", "fb_action_types", "fb_source", "fb_ref", "fb_ad_id", "fb_adset_id", "fb_campaign_id"],
    "TikTok": ["ttclid", "tt_content_id", "tt_medium", "tt_campaign_id", "tt_ad_id", "tt_adset_id"],
    "Microsoft": ["msclkid", "li_fat_id", "li_source", "li_medium", "li_campaign"],
    "Twitter": ["twclid", "ref_src", "s", "t", "tw_campaign", "tw_source"],
    "Reddit": ["rdt_cid", "rdt_source", "rdt_medium", "rdt_campaign"],
    "Snapchat": ["sc_cid", "sc_source", "sc_medium", "sc_campaign"],
    "Pinterest": ["epik", "pin_campaign", "pin_source"],
    "Amazon": ["tag", "ascsubtag", "asc_source", "creative", "creativeASIN", "linkCode", "th"],
    "Mailchimp": ["mc_cid", "mc_eid"],
    "HubSpot": ["hsa_acc", "hsa_cam", "hsa_grp", "hsa_ad", "hsa_src", "hsa_net", "hsa_ver"],
    "Adobe": ["s_cid", "ef_id"],
    "Salesforce": ["pi_campaign_id", "pi_source", "pi_ad_id"],
    "Shopify": ["shopify", "shopify_app", "shopify_email", "shopify_utm"],
    "Email": ["mkt_tok", "_hsenc", "_hsmi", "trk", "trkCampaign", "campaign", "source"],
    "Affiliate": ["aff_id", "affiliate_id", "ref", "ref_id", "referrer", "partner", "partner_id", "click_id", "clickid", "cid", "subid", "sub_id"],
    "Analytics": ["_ga", "_gl", "_gac", "_gid", "yclid", "rb_clickid", "vero_id", "vero_conv", "oly_anon_id", "oly_enc_id", "appSharePlatform"]
}

ensure_file_exists(CONFIG_PATH, default_config)
ensure_json_valid(CONFIG_PATH, default_config)
ensure_file_exists(TRACKERS_PATH, default_trackers)
ensure_json_valid(TRACKERS_PATH, default_trackers)

with open(CONFIG_PATH, 'r', encoding="utf-8") as f:
    config = json.load(f)

with open(TRACKERS_PATH, 'r', encoding="utf-8") as f:
    trackers = json.load(f)


bot_token = config.get("bot_token", default_config["bot_token"])
mention_reply_author = config.get("mention_reply_author", default_config["mention_reply_author"])
require_links = config.get("require_links", default_config["require_links"])

PARAM_INDEX = {param.lower(): company for company, params in trackers.items() for param in params}

try:
    REGEX = re.compile(
        config.get("regex_keys", default_config["regex_keys"])
    )
except re.error as e:
    raise RuntimeError(f"Invalid regex in config.json: {e}")


#--------------------------------------------------------------------
# Funcs
#--------------------------------------------------------------------

def has_link(message: str) -> bool:
    return bool(REGEX.search(message))

def has_trackers(url):
    parsed = urlparse(url)
    for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in PARAM_INDEX:
            return True
    return False

def build_param_index(tracker_map):
    index = {}
    for company, params in tracker_map.items():
        for param in params:
            index[param] = company
    return index

def clean_url(url):
    parsed = urlparse(url)
    kept = []
    removed = {}

    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        owner = PARAM_INDEX.get(key.lower())
        if owner:
            removed.setdefault(owner, []).append(key)
        else:
            kept.append((key, value))

    cleaned_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(kept),
        parsed.fragment
    ))

    if removed:
        message = f"Removed trackers from {', '.join(removed.keys())}"
    else:
        message = "No trackers found"

    return {
        "clean_url": cleaned_url,
        "removed_trackers": removed,
        "message": message
    }

def format_companies(companies):
    """Return a nicely formatted string with commas and 'and' before the last item."""
    companies = list(companies)  # ensure it's a list
    if len(companies) == 0:
        return ""
    elif len(companies) == 1:
        return companies[0]
    else:
        return ", ".join(companies[:-1]) + f", and {companies[-1]}"
#--------------------------------------------------------------------
# Main Program
#--------------------------------------------------------------------

class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return  

        if not (has_link(message.content) and require_links):
            return  

        urls = re.findall(REGEX, message.content)
        if not urls:
            return

        detected_companies = set()
        sanitized_map = {}  

        for url in urls:
            result = clean_url(url)
            if result["removed_trackers"]:
                detected_companies.update(result["removed_trackers"].keys())
                sanitized_map[url] = result["clean_url"]

        if detected_companies:
            try:
                reply = await message.reply(">>>")
                await message.delete()
                sanitized_message = message.content
                for original, cleaned in sanitized_map.items():
                    sanitized_message = sanitized_message.replace(original, cleaned)

                notice = (
                    f"{message.author.mention} Your message has been reposted without trackers from "
                    f"{format_companies(detected_companies)}:"
                )

                await reply.edit(content=f"{notice}\n{sanitized_message}")
            
            

            except discord.Forbidden:
                print("Bot lacks permission to delete messages.")
            except Exception as e:
                print(f"Error handling message: {e}")



intents = discord.Intents.default()
intents.message_content = True

discord.client = DiscordClient(intents=intents)
discord.client.run(bot_token)
