import openai
import telebot
import json
from config import BOT_TOKEN, ADMIN_ID, RAZORPAY_LINK, OPENAI_API_KEY

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

DB_FILE = "database.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

users = load_db()

def is_premium(user_id):
    return users.get(str(user_id), {}).get("premium", False)

def increment_free(user_id):
    user = users.setdefault(str(user_id), {"free_count": 0, "premium": False})
    user["free_count"] += 1
    save_db(users)

@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "👋 Hi! I'm Sakshi, your virtual friend. Let's talk!

💸 Unlock unlimited chat for ₹49:
" + RAZORPAY_LINK)

@bot.message_handler(commands=["approve"])
def approve_user(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(message.text.split()[1])
        users[str(uid)] = {"premium": True}
        save_db(users)
        bot.send_message(uid, "✅ You are now a premium user! Chat unlimited.")
        bot.reply_to(message, "User approved.")
    except:
        bot.reply_to(message, "❌ Failed to approve user.")

@bot.message_handler(commands=["broadcast"])
def broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text.split(" ", 1)[1]
    for uid in users:
        try:
            bot.send_message(uid, text)
        except:
            continue
    bot.reply_to(message, "📢 Broadcast sent.")

@bot.message_handler(func=lambda m: True)
def handle_chat(message):
    uid = message.from_user.id
    if not is_premium(uid):
        if users.get(str(uid), {}).get("free_count", 0) >= 2:
            bot.reply_to(message, "🚫 Free limit reached. Get premium: " + RAZORPAY_LINK)
            return
        increment_free(uid)

    prompt = message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        reply = response['choices'][0]['message']['content']
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, "❌ Error: " + str(e))

bot.infinity_polling()