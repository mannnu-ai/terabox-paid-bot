import telebot
import re
import requests
from bs4 import BeautifulSoup

API_TOKEN = "7911460719:AAHjIQ5EAlP49uMEGVrNSVZMJw0MW6m5EMg"
ADMIN_ID = 6124538766
FREE_LIMIT = 2
user_data = {}

bot = telebot.TeleBot(API_TOKEN)

def get_direct_link(shared_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        session = requests.Session()
        res = session.get(shared_url, headers=headers, timeout=10)

        if "terabox" not in res.text:
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        scripts = soup.find_all("script")

        for script in scripts:
            if "downloadurl" in script.text:
                match = re.search(r'"downloadurl":"(https:[^"]+)', script.text)
                if match:
                    return match.group(1).replace("\\u002F", "/")

        return None

    except Exception as e:
        print(f"[Error] {e}")
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 
        "👋 Welcome to TeraBox Downloader Bot!\n\n"
        "📥 कोई भी TeraBox लिंक भेजिए और तुरंत डाउनलोड लिंक पाइए।\n"
        "🔓 2 डाउनलोड फ्री मिलते हैं।\n"
        "💰 उसके बाद ₹49/month देकर असीमित डाउनलोड पाइए।\n\n"
        "🛒 खरीदने के लिए: https://razorpay.me/@personalbot",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    user_id = message.from_user.id
    link = message.text.strip()

    if not re.match(r'https?://(teraboxlink|terabox)\.com/s/', link):
        bot.reply_to(message, "❌ कृपया एक सही TeraBox लिंक भेजें।", parse_mode="Markdown")
        return

    if user_id not in user_data:
        user_data[user_id] = {"count": 0, "paid": False}

    if user_data[user_id]['count'] >= FREE_LIMIT and not user_data[user_id]['paid']:
        bot.send_message(user_id,
            "⚠ आपका फ्री लिमिट (2 डाउनलोड) खत्म हो चुका है।\n\n"
            "💳 ₹49/month देकर असीमित डाउनलोड पाइए।\n"
            "🛒 भुगतान लिंक: https://razorpay.me/@personalbot\n\n"
            "📞 भुगतान के बाद Admin से संपर्क करें: @youradminusername",
            parse_mode="Markdown")
        return

    msg = bot.send_message(user_id, "🔄 वीडियो लिंक निकाल रहा हूँ... कृपया प्रतीक्षा करें।")

    video_url = get_direct_link(link)
    if not video_url:
        bot.edit_message_text("❌ वीडियो नहीं मिल सका। लिंक अमान्य या एक्सपायर्ड हो सकता है।", msg.chat.id, msg.message_id)
        return

    bot.edit_message_text(f"✅ डाउनलोड लिंक:\n{video_url}", msg.chat.id, msg.message_id)
    user_data[user_id]['count'] += 1

bot.polling(non_stop=True)
