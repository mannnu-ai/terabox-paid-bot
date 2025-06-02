
import telebot
import json
import os
import requests
from telebot import types

API_TOKEN = '7513615944:AAEv7AB2jVFLqFUr7azQDxcWMJEuKiYddrM'
ADMIN_ID = 6124538766
RAZORPAY_LINK = 'https://razorpay.me/@personalbot?amount=rZC5NMufSVtgb9QV3szYxw%3D%3D'

bot = telebot.TeleBot(API_TOKEN)

if not os.path.exists('users.json'):
    with open('users.json', 'w') as f:
        json.dump({}, f)

def load_users():
    with open('users.json', 'r') as f:
        return json.load(f)

def save_users(data):
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=2)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome to the Terabox Video Downloader Bot!\n\nSend a Terabox video link to download. You get 2 free downloads. After that, pay ₹49 to continue.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    text = message.text
    users = load_users()

    if text.startswith("http") and "terabox" in text:
        if user_id not in users:
            users[user_id] = {"downloads": 0, "paid": False}

        if users[user_id]['downloads'] < 2 or users[user_id]['paid']:
            bot.send_message(message.chat.id, "⏳ Fetching your video... Please wait.")
            video_url = get_terabox_video(text)
            if video_url:
                try:
                    bot.send_video(message.chat.id, video_url)
                    if not users[user_id]['paid']:
                        users[user_id]['downloads'] += 1
                        save_users(users)
                except:
                    bot.send_message(message.chat.id, "⚠️ Failed to send video. It may be too large for Telegram.")
            else:
                bot.send_message(message.chat.id, "❌ Couldn't fetch video. Link may be invalid or unsupported.")
        else:
            markup = types.InlineKeyboardMarkup()
            pay_btn = types.InlineKeyboardButton("Pay ₹49", url=RAZORPAY_LINK)
            done_btn = types.InlineKeyboardButton("I’ve Paid", callback_data='paid_check')
            markup.add(pay_btn)
            markup.add(done_btn)
            bot.send_message(message.chat.id, "💳 Your free limit is over. To continue, pay ₹49 for monthly access:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "⚠️ Please send a valid Terabox video link.")

@bot.callback_query_handler(func=lambda call: call.data == 'paid_check')
def handle_payment_check(call):
    bot.send_message(call.message.chat.id, "✅ Please enter the name or email used for Razorpay payment. Admin will verify and approve shortly.")
    bot.register_next_step_handler(call.message, collect_payment_info)

def collect_payment_info(message):
    user_id = message.from_user.id
    name = message.text
    bot.send_message(ADMIN_ID, f"🆕 Payment Check Request:\nUser ID: {user_id}\nUsername: @{message.from_user.username}\nName/Email: {name}\n\nReply with /approve {user_id} to approve this user.")
    bot.send_message(message.chat.id, "🕐 Payment submitted. Please wait while admin verifies it.")

@bot.message_handler(commands=['approve'])
def approve_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = message.text.split()[1]
        users = load_users()
        if user_id in users:
            users[user_id]['paid'] = True
            save_users(users)
            bot.send_message(int(user_id), "✅ Your payment is verified. You now have unlimited access for 1 month!")
            bot.reply_to(message, f"✅ Approved user {user_id}")
        else:
            bot.reply_to(message, "❌ User not found.")
    except:
        bot.reply_to(message, "❌ Invalid command format. Use /approve <user_id>")

def get_terabox_video(link):
    try:
        session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = session.get(link, headers=headers)
        if 'videoUrl' in response.text:
            import re
            match = re.search(r'"videoUrl":"(.*?)"', response.text)
            if match:
                return match.group(1).replace('\u002F', '/').replace('\', '')
    except:
        return None
    return None

print("Bot is running...")
bot.infinity_polling()
