from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetHistoryRequest
from flask import Flask
import asyncio
import threading

# === CONFIG ===
API_ID = 27743731  # your API ID
API_HASH = 'f33b0ab78cbec9084e3668df0b3330ff'
SESSION_STRING = '1BVtsOMABu7GaEVai-TiG-z1wM1GYgVrDbEM5fdM-4jLo1IgE5VN0A0j3e_xUzDjmank_mQWme6FT4Fgm8qMGhDP_JkUt2g5zd-MEctwIPhvqP7itvGZGjKmy3Vol8-jB7iYuio5PbJvGTXv4hJ6fqutS59WLwtlqbVet33mrS-2p3_LpUt8rqW6JeExu2OM0o0ZJPXH9Rs0jEOKEmhE9cccezMlaaZgm-3cgLCAxjXAj2cR0hWRx8jGD0zuBoEakrgjzTyOO2mGcFsOFrq1yvioEbSpfJSXXYTU1QCtBrvpomsm-waEyCOyXkxTWtQg_KoglPZ2kLZNq_f1_pNjEkBiLbX9gOX4='
SOURCE_CHAT = '-1002448304352'
DEST_CHAT = '-1002564411877'

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
