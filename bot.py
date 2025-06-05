from telethon import TelegramClient, events
from redis import Redis
import config

# Setup bot client and Redis
bot = TelegramClient('bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)
r = Redis(host='localhost', port=6379, db=0)

# Handle TeraBox link
@bot.on(events.NewMessage(pattern=r'https?://.*terabox.*'))
async def handle_link(event):
    user_id = str(event.sender_id)
    used = int(r.get(f"user:{user_id}:used") or 0)
    premium = r.get(f"user:{user_id}:premium")

    if not premium and used >= 2:
        await event.reply("❌ Aapke 2 free downloads ho chuke hain.\n💳 Premium (₹49/month) lene ke liye /buy command ka use karein.")
        return

    try:
        # Forward link to backend bot
        sent = await bot.send_message(config.BACKEND_BOT, event.text)
        # Wait for response
        @bot.on(events.NewMessage(from_users=config.BACKEND_BOT))
        async def reply_handler(reply_event):
            if reply_event.reply_to_msg_id == sent.id:
                await bot.send_message(event.sender_id, reply_event.message)
                bot.remove_event_handler(reply_handler)
        # Increment usage
        if not premium:
            r.incr(f"user:{user_id}:used")
    except Exception as e:
        await event.reply("❌ Error processing your request. Try again later.")

# Start command
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

# Buy command
@bot.on(events.NewMessage(pattern='/buy'))
async def buy(event):
    await event.reply(f"""💳 Buy Premium (₹49/month):
👉 [Click to Pay]({config.RAZORPAY_LINK})""", link_preview=False)

# Approve premium users (admin only)
@bot.on(events.NewMessage(pattern='/approve'))
async def approve(event):
    if event.sender_id != config.ADMIN_ID:
        return
    try:
        user_id = event.text.split()[1]
        r.set(f"user:{user_id}:premium", 1)
        await event.reply(f"✅ Approved user {user_id} as Premium.")
    except:
        await event.reply("❌ Usage: /approve <user_id>")

bot.run_until_disconnected()


