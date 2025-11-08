{"id":"84231","variant":"standard","title":"Full Fixed Discord Bot Code"}
# bot.py
# Usage:
# 1. Put this file and config.json in the same folder.
# 2. Install discord.py: `py -m pip install discord.py`
# 3. Run: `py bot.py`

import json
import time
import os
import traceback
import discord
from discord.ext import tasks, commands

# ---------- Load config ----------
CFG_PATH = "config.json"
LAST_MSG_PATH = "last_msg.json"

if not os.path.exists(CFG_PATH):
    raise FileNotFoundError(f"{CFG_PATH} not found. Create it with TOKEN and CHANNEL_ID.")

with open(CFG_PATH, "r", encoding="utf-8") as f:
    cfg = json.load(f)

TOKEN = os.getenv("TOKEN") or cfg.get("TOKEN")
CHANNEL_ID = int(cfg.get("CHANNEL_ID", 0))

# Optional image configuration
IMAGE_PATH = cfg.get("IMAGE_PATH")  # local image path
IMAGE_URL = cfg.get("IMAGE_URL")    # URL to image

if not TOKEN:
    raise ValueError("TOKEN not set in config.json")

if not CHANNEL_ID:
    raise ValueError("CHANNEL_ID not set in config.json")

# ---------- Bot setup ----------
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

last_message = None

def save_last_msg_id(msg_id: int):
    try:
        with open(LAST_MSG_PATH, "w", encoding="utf-8") as f:
            json.dump({"last_message_id": msg_id}, f)
    except Exception:
        print("Warning: could not write last_msg.json:", traceback.format_exc())

def load_last_msg_id():
    if not os.path.exists(LAST_MSG_PATH):
        return None
    try:
        with open(LAST_MSG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return int(data.get("last_message_id"))
    except Exception:
        print("Warning: could not read last_msg.json:", traceback.format_exc())
        return None

async def get_channel_safe(channel_id: int):
    ch = bot.get_channel(channel_id)
    if ch is not None:
        return ch
    try:
        ch = await bot.fetch_channel(channel_id)
        return ch
    except discord.NotFound:
        return None
    except Exception as e:
        print("Error fetching channel:", repr(e))
        return None

async def delete_all_bot_messages(channel):
    """Delete all messages sent by this bot in the last 50 messages."""
    try:
        async for m in channel.history(limit=50):
            if m.author and m.author.id == bot.user.id:
                try:
                    await m.delete()
                    print(f"🗑️ Deleted bot message id {m.id}")
                except discord.NotFound:
                    pass
                except discord.Forbidden:
                    print(f"❌ Cannot delete message id {m.id}, missing permission")
    except Exception as e:
        print("Error deleting bot messages:", repr(e))

@bot.event
async def on_ready():
    global last_message
    print(f"✅ Logged in as {bot.user} (id: {bot.user.id})")
    print("Starting message loop (every 15 minutes)...")

    # restore last message from persisted ID
    last_msg_id = load_last_msg_id()
    ch = await get_channel_safe(CHANNEL_ID)
    if last_msg_id and ch:
        try:
            msg = await ch.fetch_message(last_msg_id)
            if msg.author.id == bot.user.id:
                last_message = msg
                print(f"Restored last message id {last_msg_id} from {ch.name}.")
        except discord.NotFound:
            print("Persisted last message not found.")
        except Exception as e:
            print("Error fetching last message:", repr(e))

    send_message.start()

@tasks.loop(minutes=15)
async def send_message():
    global last_message
    channel = await get_channel_safe(CHANNEL_ID)
    if not channel:
        print(f"❌ Channel with ID {CHANNEL_ID} not found or bot cannot access it.")
        return

    # Delete all recent bot messages before sending
    await delete_all_bot_messages(channel)

    content = (
        "# ⚠️ IF YOU’RE ON CONSOLE, DON’T BUY AN UNLOCK — INSTEAD GET CAMO SERVICES ⚠️\n\n"
        "# 🚀BO6/WZ UNLOCK TOOLS — WALLHACKS, AIMBOT, ETC 🚀\n\n"
        " # Receive what you paid for instantly on our website below\n"
        " # ➜ :link: Website (Instant Delivery): <https://astroosservices.shop>\n\n"
        " # ➜ Need Help? Create a ticket here —> <#1403758315347116163>\n\n"
        "**||@everyone|| | ||@here||**"
    )

    try:
        if IMAGE_PATH and os.path.exists(IMAGE_PATH):
            last_message = await channel.send(content, file=discord.File(IMAGE_PATH))
        elif IMAGE_URL:
            embed = discord.Embed()
            embed.set_image(url=IMAGE_URL)
            last_message = await channel.send(content, embed=embed)
        else:
            last_message = await channel.send(content)

        save_last_msg_id(last_message.id)
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"✅ Sent new message in #{channel.name} at {now} (id: {last_message.id})")
    except discord.Forbidden:
        print("❌ Missing permission to send messages or mention. Check bot role.")
    except Exception as e:
        print("Error sending message:", repr(e))

@send_message.before_loop
async def before_sending():
    await bot.wait_until_ready()

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print("Bot crashed with exception:", e)
        with open("error.log", "w", encoding="utf-8") as f:
            f.write("Unhandled exception while running bot:\n")
            f.write(str(e) + "\n\n")
            f.write(traceback.format_exc())
        input("Press Enter to exit...")


