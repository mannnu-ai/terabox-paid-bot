# 🤖 Sakshi - Your Virtual Friend (GPT-powered Telegram Bot)

A Telegram chatbot named **Sakshi** that responds in a friendly, realistic manner using OpenAI's GPT. Includes Razorpay integration for monetization and a free message quota for non-premium users.

## 📦 Features
- GPT-based realistic chatting
- Razorpay ₹49 monthly payment
- Free 2 messages/day for non-premium users
- Admin panel for payments, broadcast
- Hindi + English support
- Hosted on Render 24x7

## 🛠 Setup Instructions

### 1. Clone repo and add config
```bash
git clone https://github.com/yourname/sakshi-bot.git
cd sakshi-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your credentials in `config.py`
```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_ID = 6124538766
RAZORPAY_LINK = "https://razorpay.me/@personalbot"
OPENAI_API_KEY = "YOUR_OPENAI_KEY"
```

### 4. Run the bot
```bash
python main.py
```

### 📡 Hosting on Render
- Connect GitHub repo
- Add `BOT_TOKEN`, `OPENAI_API_KEY` in environment variables
- Use `python main.py` as start command