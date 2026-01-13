import telebot
import requests
from flask import Flask
from threading import Thread
import os

# --- AAPKI DETAILS ---
TOKEN = "8588395332:AAEmPDTyPA3trRDReoqSv4P8_JPxDb6UYTs"
API_KEY = "AIzaSyB0NM-hXDWr-1s62YaEFvxnfEgK5aCVqCo"
CHANNEL_URL = "https://t.me/+WvZ1Z3dpsT83NDYx"
OWNER_ID = "@nagixowner"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "NAGIX AI IS ONLINE"

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn1 = telebot.types.InlineKeyboardButton("📢 Join Update Channel", url=CHANNEL_URL)
    btn2 = telebot.types.InlineKeyboardButton("👤 Contact Owner", url=f"https://t.me/nagixowner")
    markup.add(btn1, btn2)
    
    text = f"👋 **Welcome to NAGIX AI!**\n\nMain Render server par 24/7 active hoon.\n\nOwner: {OWNER_ID}\n\nAb aap mujhse sawal puch sakte hain."
    bot.send_message(m.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def ai_reply(m):
    # Professional Typing Animation
    bot.send_chat_action(m.chat.id, 'typing')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": m.text}]}]}
    
    try:
        r = requests.post(url, json=payload)
        data = r.json()
        if 'candidates' in data:
            answer = data['candidates'][0]['content']['parts'][0]['text']
            bot.reply_to(m, answer)
        else:
            bot.reply_to(m, "⚠️ AI Response error!")
    except Exception as e:
        bot.reply_to(m, "❌ Server Error! Please wait.")

# --- SERVER START ---
def run():
    # Render default port 10000 use karta hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("Bot is starting...")
    bot.infinity_polling()
