import telebot
import re
import requests

API_TOKEN = "7911460719:AAHjIQ5EAlP49uMEGVrNSVZMJw0MW6m5EMg"

ADMIN_ID = 6124538766
FREE_LIMIT = 2

user_data = {}

bot = telebot.TeleBot(API_TOKEN)

def get_direct_link(shared_url):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = session.get(shared_url, headers=headers, timeout=10, allow_redirects=True)
        if "terabox.com" not in resp.url:
            return None
    except Exception:
        return None

    match = re.search(r's/([a-zA-Z0-9_-]+)', resp.url)
    if not match:
        return None
    share_id = match.group(1)

    api_url = f"https://www.terabox.com/share/list?app_id=250528&shorturl={share_id}&root=1"
    try:
        res = session.get(api_url, headers=headers)
        json_data = res.json()
        files = json_data.get("list", [])
        if not files:
            return None
        first_file = files[0]
        dlink = first_file.get("dlink")
        return dlink
    except:
        return None

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(
        message.chat.id,
        "👋 Welcome to the TeraBox Downloader Bot!\n\n"
        "📥 Send me a TeraBox video link and I’ll fetch the direct download link.\n\n"
        "🔓 You get 2 downloads for FREE!\n"
        "💰 After that, pay ₹49/month to continue.\n\n"
        "To buy: https://razorpay.me/@personalbot?amount=rZC5NMufSVtgb9QV3szYxw%3D%3D"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    link = message.text.strip()

    if not re.match(r'https?://(terabox\.com|teraboxlink\.com)/s/', link):
        bot.reply_to(message, "❌ Please send a valid TeraBox share link.")
        return

    if user_id not in user_data:
        user_data[user_id] = {'count': 0, 'paid': False}

    if user_data[user_id]['count'] >= FREE_LIMIT and not user_data[user_id]['paid']:
        bot.send_message(
            user_id,
            "⚠️ You have reached the free limit of 2 downloads.\n\n"
            "💳 Pay ₹49/month to unlock unlimited access:\n"
            "https://razorpay.me/@personalbot?amount=rZC5NMufSVtgb9QV3szYxw%3D%3D\n\n"
            "After payment, contact admin to activate access."
        )
        return

    msg = bot.send_message(message.chat.id, "⏳ Fetching your video... Please wait.")

    video_url = get_direct_link(link)
    if not video_url:
        bot.edit_message_text("❌ Couldn't fetch video. Link may be invalid or unsupported.", msg.chat.id, msg.message_id)
        return

    try:
        bot.send_message(user_id, f"✅ Download Link:\n{video_url}")
        user_data[user_id]['count'] += 1
    except Exception:
        bot.edit_message_text("❌ Failed to send the video link.", msg.chat.id, msg.message_id)

bot.polling(non_stop=True)
