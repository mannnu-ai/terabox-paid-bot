from telethon import TelegramClient, events
from redis import Redis
import config

# Bot & Redis setup
bot = TelegramClient('bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)
r = Redis(host='localhost', port=6379, db=0)  # Change host/port if Redis is not local

# --- TeraBox link handler ---
@bot.on(events.NewMessage(pattern='https?://.*terabox.*'))
async def handle_link(event):
    user_id = str(event.sender_id)
    used = int(r.get(f"user:{user_id}:used") or 0)

    if r.get(f"user:{user_id}:premium"):
        pass
    elif used >= 2:
        await event.reply("❌ Aapke 2 free downloads ho chuke hain.\n₹49/month ka plan kharidne ke liye /buy use karein.")
        return

    try:
        msg = await bot.send_message(config.BACKEND_BOT, event.text)
        await msg.forward_to(event.sender_id)
    except Exception as e:
        await event.reply("❌ Error forwarding link. Try again later.")

    r.incr(f"user:{user_id}:used")

# --- /start command ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = str(event.sender_id)
    used = int(r.get(f"user:{user_id}:used") or 0)
    premium = r.get(f"user:{user_id}:premium")
    status = "✅ Premium User" if premium else f"🆓 Free User ({used}/2 used)"
    await event.reply(f"""👋 Welcome to TeraBox Downloader!

🔹 Status: {status}
🔗 Send a TeraBox link to download.
💳 Use /buy to get Premium access.""")

# --- /buy command ---
@bot.on(events.NewMessage(pattern='/buy'))
async def buy(event):
    await event.reply(f"💳 Buy Premium (₹49/month):\n👉 [Click to Pay]({config.RAZORPAY_LINK})", link_preview=False)

# --- /approve command (admin only) ---
@bot.on(events.NewMessage(pattern='/approve'))
async def approve(event):
    if event.sender_id != config.ADMIN_ID:
        return
    try:
        user_id = event.text.split()[1]
        r.set(f"user:{user_id}:premium", 1)
        await event.reply(f"✅ Approved user {user_id} as Premium.")
    except IndexError:
        await event.reply("❌ Usage: /approve <user_id>")

# Run the bot
bot.run_until_disconnected()
