# This bot requires the 'message_content' intent.

import discord
import vt
import aiohttp
import io
import asyncio
from datetime import datetime, timedelta
import hashlib

# Discord bot token, you can get your own token by creating a bot at https://discord.com/developers/applications, a good guide is available at https://discordpy.readthedocs.io/en/stable/discord.html
bot_token = ''

# VirusTotal API key for scanning, you can get your own key by signing up at https://www.virustotal.com/gui/join-us
virustotal_api_key = ''

# Mention the author of the reply when sending warnings about large files? Set to True to enable.
mention_reply_author = False

# Timeout for waiting for scan results in seconds
timeout_seconds = 300  # 5 minutes

# Maximum number of attempts to check for scan results when an error occurs
max_attempts = 2

# File recieved message
file_recieved_message = ('Attachment `{filename}` received. Submitting for scanning...')

# Warning message for files larger than 1 GB (should not be needed as discord's maximum upload size is 500 mb, but included just in case)
file_too_large_warning = ('Attachment `{filename}` is too large ({file_size} bytes). Maximum allowed size is 1 GB. Proceed with caution')

# Warning message for download errors
download_error_warning = ('Attachment `{filename}` could not be downloaded. Please proceed with caution.')

# File submitted for scanning message
file_submitted_for_scanning_message = ('Attachment `{filename}` has been submitted for scanning. Analysis ID: {analysis_id}')

# Error when scanning file message
file_scanning_error_message = ('Error scanning `{filename}`: {e}')

# Scan results message (\n means new line)
results_recieved_message = ('Scan completed for `{filename}`. \n {malicious_count}/{total_engines} vendors marked this file as malicious. \n More details can be found here: {results_url}')

# Scan timeout message
scan_timeout_message = ('Scan for `{filename}` timed out after waiting for {timeout} seconds. \n You might still be able to check the results here: {results_url}')


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Do not modify any code below this line unless you know what you are doing!
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

vt_client = vt.Client(virustotal_api_key)

class DiscordClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if not message.attachments:
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
                        print(f'Submitted {filename} for scanning. Analysis ID: {analysis.id}')
                        results_sections[idx] = file_submitted_for_scanning_message.format(
                            filename=filename,
                            analysis_id=analysis.id
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
