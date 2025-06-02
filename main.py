import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os
from utils.downloader import download_video
from utils.payment import is_premium_user

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6124538766"))
RAZORPAY_LINK = "https://razorpay.me/@personalbot?amount=rZC5NMufSVtgb9QV3szYxw%3D%3D"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, downloads INTEGER DEFAULT 0, premium INTEGER DEFAULT 0)")
    conn.commit()
    conn.close()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton("💳 Buy Premium (₹49)", url=RAZORPAY_LINK))
    await message.answer(
    "👋 Welcome to TeraBox Video Downloader Bot!\n\n"
    "📥 Send any TeraBox link to download videos.\n"
    "🆓 First 2 videos are FREE.\n"
    "💳 Then, pay ₹49/month for unlimited access.\n"
    "👇 Tap below to buy premium:",
    reply_markup=kb
    )
    

@dp.message_handler(lambda msg: "terabox.com" in msg.text)
async def handle_terabox(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT downloads, premium FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO users (id, downloads, premium) VALUES (?, ?, ?)", (user_id, 0, 0))
        conn.commit()
        downloads, premium = 0, 0
    else:
        downloads, premium = row

    if premium or downloads < 2:
        await message.reply("📥 Downloading your video, please wait...")
        video_file = download_video(message.text)
        if video_file:
            await message.reply_document(open(video_file, 'rb'))
            if not premium:
                c.execute("UPDATE users SET downloads = downloads + 1 WHERE id = ?", (user_id,))
                conn.commit()
        else:
            await message.reply("❌ Failed to download video. Invalid link or error occurred.")
    else:
        kb = InlineKeyboardMarkup().add(InlineKeyboardButton("💳 Buy Premium", url=RAZORPAY_LINK))
        await message.reply(
    "🚫 You’ve used your 2 free downloads.\n"
    "💳 Please buy premium to continue using the bot.",
    reply_markup=kb
        )
        
"
                            "💳 Please purchase premium access to continue.", reply_markup=kb)
    conn.close()

@dp.message_handler(commands=['users'])
async def get_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE premium=1")
    premium = c.fetchone()[0]
    conn.close()
    await message.reply(f"👤 Total users: {total}
💎 Premium users: {premium}")

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)
