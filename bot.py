import os
import threading
import requests
import telebot
from telebot import types
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise Exception("ENV variables missing")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

verified_users = set()

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

@bot.message_handler(commands=['start'])
def start(msg):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK),
        types.InlineKeyboardButton("✅ Verify", callback_data="verify_user")
    )

    text = (
        "━━━━━━━━━━━━━━\n"
        "🤖 <b>Welcome to Gemini AI Bot</b>\n"
        "━━━━━━━━━━━━━━\n\n"
        "Bot use karne se pehle verify karo.\n\n"
        "━━━━━━━━━━━━━━\n"
        "Owner: @nagixowner"
    )
    bot.send_message(msg.chat.id, text, reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data == "verify_user")
def verify(call):
    verified_users.add(call.from_user.id)
    bot.answer_callback_query(call.id, "Verification Successful!")
    bot.send_message(call.message.chat.id,
                     "✅ Verification complete. Ab apna question bhejo.\n\nOwner: @nagixowner")

def ask_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        r = requests.post(url, headers=headers, params=params, json=data, timeout=20)
        if r.status_code != 200:
            return None
        j = r.json()
        return j["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return None

@bot.message_handler(func=lambda m: True)
def chat(msg):
    if msg.from_user.id not in verified_users:
        bot.send_message(msg.chat.id,
                         "⛔ Pehle /start karke Verify karo.\n\nOwner: @nagixowner")
        return

    reply = ask_gemini(msg.text)

    if not reply:
        bot.send_message(msg.chat.id,
                         "⚠️ AI busy hai ya API key galat hai.\n\nOwner: @nagixowner")
        return

    final = (
        "━━━━━━━━━━━━━━\n"
        f"{reply}\n"
        "━━━━━━━━━━━━━━\n"
        "Owner: @nagixowner"
    )
    bot.send_message(msg.chat.id, final)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling(skip_pending=True)
