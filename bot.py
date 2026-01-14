import os
import requests
import telebot
from telebot import types
from flask import Flask, request

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not GEMINI_API_KEY or not WEBHOOK_URL:
    raise Exception("ENV variables missing")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)
verified_users = set()

@bot.message_handler(commands=['start'])
def start(msg):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK),
        types.InlineKeyboardButton("✅ Verify", callback_data="verify_user")
    )
    bot.send_message(msg.chat.id,
        "━━━━━━━━━━━━━━\n🤖 <b>Gemini AI Bot</b>\nVerify first\n━━━━━━━━━━━━━━\nOwner: @nagixowner",
        reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "verify_user")
def verify(call):
    verified_users.add(call.from_user.id)
    bot.answer_callback_query(call.id, "Verified!")
    bot.send_message(call.message.chat.id, "✅ Verified. Ab sawal bhejo.\n\nOwner: @nagixowner")

def ask_gemini(q):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    params = {"key": GEMINI_API_KEY}
    data = {"contents":[{"parts":[{"text": q}]}]}
    try:
        r = requests.post(url, params=params, json=data, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return None

@bot.message_handler(func=lambda m: True)
def chat(msg):
    if msg.from_user.id not in verified_users:
        bot.send_message(msg.chat.id, "⛔ Pehle /start karke verify karo\nOwner: @nagixowner")
        return
    ans = ask_gemini(msg.text)
    if not ans:
        bot.send_message(msg.chat.id, "⚠️ AI busy hai\nOwner: @nagixowner")
        return
    bot.send_message(msg.chat.id, f"━━━━━━━━━━━━━━\n{ans}\n━━━━━━━━━━━━━━\nOwner: @nagixowner")

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def receive():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "ok"

@app.route("/")
def home():
    return "Bot alive"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=10000)
