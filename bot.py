from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetHistoryRequest
from flask import Flask
import asyncio
import threading

# === CONFIG ===
API_ID = 123456  # your API ID
API_HASH = 'your_api_hash'
SESSION_STRING = 'your_telethon_session_string'
SOURCE_CHAT = 'source_chat_username_or_id'
DEST_CHAT = 'your_channel_username_or_id'

# === TELETHON CLIENT ===
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# === Flask Server to keep Render alive ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Forward Bot is Running!"

# === Message Forwarding Logic ===
async def forward_all():
    await client.start()
    me = await client.get_me()
    print(f"Logged in as: {me.username or me.first_name}")

    offset_id = 0
    total_forwarded = 0
    limit = 100

    while True:
        try:
            history = await client(GetHistoryRequest(
                peer=SOURCE_CHAT,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))

            messages = history.messages
            if not messages:
                print("No more messages.")
                break

            filtered_messages = [msg for msg in messages if (msg.message or msg.media)]

            if filtered_messages:
                message_ids = [msg.id for msg in filtered_messages]
                await client.forward_messages(DEST_CHAT, message_ids, SOURCE_CHAT)
                print(f"Forwarded {len(message_ids)} messages")
                total_forwarded += len(message_ids)
            else:
                print("No valid messages in this batch.")

            offset_id = messages[-1].id
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

    print(f"Total forwarded: {total_forwarded}")

def run_forward_loop():
    with client:
        client.loop.run_until_complete(forward_all())

def start_telethon():
    thread = threading.Thread(target=run_forward_loop)
    thread.start()

# === Start both Flask and Telethon on startup ===
if __name__ == '__main__':
    start_telethon()
    app.run(host='0.0.0.0', port=8080)
