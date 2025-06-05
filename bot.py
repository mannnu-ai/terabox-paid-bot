from telethon import TelegramClient, events
from redis import Redis
import config

# Create bot client
bot = TelegramClient('bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)

# Connect to Redis
r = Redis(host='localhost', port=6379, db=0)

# --- TeraBox Link Handler ---
@bot.on(events.NewMessage(pattern='https?://.*terabox.*'))
async def handle_link(event):
    user_id = str(event.sender_id)
    used = int(r.get(f"user:{user_id}:used") or 0)

    # Check if user is premium
    if not r.get(f"user:{user_id}:premium"):
        if used >= 2:
            await event.reply(
                "❌ Aapke 2 free downloads ho chuke hain.\n"
                "💎 Premium le kar unlimited access payen ₹49/month.\n"
                "🛒 Use /buy to upgrade."
            )
            return

    try:
        # Forward link to backend bot
        msg = await bot.send_message(config.BACKEND_BOT, event.text)
        await msg.forward_to(event.sender_id)
        r.incr(f"user:{user_id}:used")
    except Exception as e:
        await event.reply("⚠️ Error forwarding link. Try again later.")

# --- /start Command ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = str(event.sender_id)
    used = int(r.get(f"user:{user_id}:used") or 0)
    premium = r.get(f"user:{user_id}:premium")
    status = "✅ Premium User" if premium else f"🆓 Free User ({used}/2 used)"
    await event.reply(
        f"👋 Welcome to TeraBox Downloader Bot!\n\n"
        f"🔹 Status: {status}\n"
        f"📥 Send any TeraBox link to get the file.\n"
        f"💳 Want unlimited access? Use /buy to upgrade to Premium."
    )

# --- /buy Command ---
@bot.on(events.NewMessage(pattern='/buy'))
async def buy(event):
    await event.reply(
        f"💳 *Buy Premium* (₹49/month):\n"
        f"👉 [Click to Pay]({config.RAZORPAY_LINK})",
        link_preview=False
    )

# --- /approve Command for Admin ---
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

# Run the bot
bot.run_until_disconnected()
