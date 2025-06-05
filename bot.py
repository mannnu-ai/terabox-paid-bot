from telethon import TelegramClient, events
from redis import Redis
import config

# Redis setup (make sure Redis is running)
r = Redis(host='localhost', port=6379, db=0)

# Bot client setup
bot = TelegramClient('bot', config.API_ID, config.API_HASH).start(bot_token=config.BOT_TOKEN)

# Free use limit
FREE_LIMIT = 2

@bot.on(events.NewMessage(pattern=r'https?://.*terabox.*'))
async def handle_terabox_link(event):
    user_id = str(event.sender_id)
    used = int(r.get(f"user:{user_id}:used") or 0)
    is_premium = r.get(f"user:{user_id}:premium")

    if not is_premium and used >= FREE_LIMIT:
        await event.reply(
            "❌ Aapke 2 free downloads ho chuke hain.\n"
            "💳 Premium lene ke liye ₹49/month ka plan kharidein.\n"
            "👉 Use /buy to upgrade."
        )
        return

    try:
        # Forward link to backend bot
        msg = await bot.send_message(config.BACKEND_BOT, event.text)
        await msg.forward_to(event.sender_id)
        if not is_premium:
            r.incr(f"user:{user_id}:used")
    except Exception as e:
        await event.reply("❌ Error: Link process nahi hua. Try again later.")

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = str(event.sender_id)
    used = int(r.get(f"user:{user_id}:used") or 0)
    premium = r.get(f"user:{user_id}:premium")
    status = "✅ Premium User" if premium else f"🆓 Free User ({used}/2 used)"

    await event.reply(
        f"👋 Welcome to *TeraBox Downloader Bot*!\n\n"
        f"🔹 Status: {status}\n"
        f"📤 Send a TeraBox link to download.\n"
        f"💳 Want Premium? Use /buy",
        parse_mode='Markdown'
    )

@bot.on(events.NewMessage(pattern='/buy'))
async def buy(event):
    await event.reply(
        f"💳 Buy *Premium* (₹49/month):\n"
        f"👉 [Click to Pay]({config.RAZORPAY_LINK})",
        link_preview=False,
        parse_mode='Markdown'
    )

@bot.on(events.NewMessage(pattern='/approve'))
async def approve(event):
    if event.sender_id != config.ADMIN_ID:
        return
    try:
        user_id = event.message.text.split()[1]
        r.set(f"user:{user_id}:premium", 1)
        await event.reply(f"✅ Approved {user_id} as a Premium user.")
    except:
        await event.reply("❌ Usage: /approve <user_id>")

bot.run_until_disconnected()


