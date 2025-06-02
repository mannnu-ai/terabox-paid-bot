
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, API_ID, API_HASH, ADMIN_ID
from terabox_downloader import get_direct_link

app = Client("terabox_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

free_users = {}
premium_users = set()

razorpay_link = "https://razorpay.me/@personalbot?amount=rZC5NMufSVtgb9QV3szYxw%3D%3D"

@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    await message.reply(
        "👋 Welcome / स्वागत है!

📥 Send any TeraBox link / टेराबॉक्स लिंक भेजें
🆓 First 2 downloads are FREE / पहले 2 डाउनलोड फ्री!
🔓 Unlock unlimited for ₹49 / ₹49 में अनलिमिटेड डाउनलोड!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Buy Premium ₹49", url=razorpay_link)]
        ])
    )

@app.on_message(filters.private & filters.text)
async def handle_message(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    if str(user_id) in premium_users:
        pass  # Premium user
    else:
        count = free_users.get(user_id, 0)
        if count >= 2:
            await message.reply(
                "🚫 Free limit over / फ्री लिमिट खत्म

💳 Send ₹49 to unlock unlimited / ₹49 भेजें और अनलिमिटेड डाउनलोड पाएं
🔗 Razorpay: " + razorpay_link + "
📤 Then send payment screenshot.",
            )
            return

    if "terabox.com" in text or "1fichier" in text:
        await message.reply("⏳ Processing your link / लिंक प्रोसेस हो रहा है...")
        link = await get_direct_link(text)
        if link:
            if str(user_id) not in premium_users:
                free_users[user_id] = count + 1
            await message.reply(f"✅ Download Link:

{link}")
        else:
            await message.reply("❌ Failed to extract link / लिंक एक्सट्रैक्ट नहीं हो सका")
    else:
        await message.reply("⚠️ Send valid TeraBox link / मान्य टेराबॉक्स लिंक भेजें")

@app.on_message(filters.private & filters.photo)
async def payment_screenshot(client, message):
    user_id = message.from_user.id
    await message.reply("✅ Screenshot received. Awaiting admin approval.

स्क्रीनशॉट मिला, पुष्टि का इंतजार है।")

    await client.send_photo(
        ADMIN_ID, message.photo.file_id,
        caption=f"🧾 Payment screenshot from user ID: {user_id}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
             InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{user_id}")]
        ])
    )

@app.on_callback_query()
async def handle_callback(client, callback_query):
    data = callback_query.data
    if data.startswith("approve_"):
        user_id = int(data.split("_")[1])
        premium_users.add(str(user_id))
        await client.send_message(user_id, "✅ Payment approved! You now have unlimited access.
भुगतान स्वीकृत! अब आपके पास अनलिमिटेड एक्सेस है।")
        await callback_query.message.edit_caption("✅ User approved.")
    elif data.startswith("cancel_"):
        user_id = int(data.split("_")[1])
        await client.send_message(user_id, "❌ Payment not approved. Please try again.
भुगतान अस्वीकृत। कृपया पुनः प्रयास करें।")
        await callback_query.message.edit_caption("❌ Payment declined.")

app.run()
