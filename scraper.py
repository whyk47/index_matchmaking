import json
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from telethon import TelegramClient

from models import Message

load_dotenv()

# Your credentials from my.telegram.org
channel_handle = "@NBSntu"  # e.g., 'telegram'
api_id = int(os.getenv("api_id", 0))
api_hash = os.getenv("api_hash", "")
client = TelegramClient("session_name", api_id, api_hash)
cutoff_date = datetime.now(timezone.utc) - timedelta(days=60)


async def main():
    await client.start()  # type: ignore
    entity = await client.get_entity(channel_handle)

    messages = []
    async for message in client.iter_messages(entity):  # type: ignore
        if message.date < cutoff_date:
            break
        msg = Message(
            sender=message.sender.username,
            timestamp=message.date.isoformat(),
            content=message.text,
        ).__dict__
        messages.append(msg)
    print(f"Fetched {len(messages)} messages from {channel_handle}.")

    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(messages[:20], f, ensure_ascii=False, indent=4)


with client:
    client.loop.run_until_complete(main())
