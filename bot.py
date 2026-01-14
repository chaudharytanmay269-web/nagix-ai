import telebot
import requests
import json
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- ⚙️ CONFIGURATION ---
TOKEN = "8588395332:AAEmPDTyPA3trRDReoqSv4P8_JPxDb6UYTs"
API_KEY = "AIzaSyB0NM-hXDWr-1s62YaEFvxnfEgK5aCVqCo"
CHANNEL_URL = "https://t.me/+Yo2sUrnHRk45OGFh"
OWNER = "@nagixowner"

bot = telebot.TeleBot(TOKEN)
app = Flask('')
verified_users = set()

@app.route('/')
def home():
    return "NAGIX AI PREMIUM IS ONLINE"

# --- 🏠 START COMMAND ---
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Update Channel", url=CHANNEL_URL)
    btn2 = types.InlineKeyboardButton("✅ Verify & Unlock AI", callback_data="verify")
    markup.add(btn1, btn2)
    
    msg = (
        "✨ **NAGIX AI PREMIUM v2.0** ✨\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👋 **Welcome!** Main ek powerful AI assistant hoon.\n\n"
        "⚠️ **Access Restricted:**\n"
        "Aapko bot use karne ke liye hamara channel join karna hoga aur niche diye gaye button se verify karna hoga.\n\n"
        "🔗 **Join Now:** [Click Here](" + CHANNEL_URL + ")"
    )
    bot.send_message(m.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

# --- ✅ VERIFICATION CALLBACK ---
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_user(call):
    verified_users.add(call.from_user.id)
    bot.answer_callback_query(call.id, "✅ Verified! Welcome to Premium.")
    bot.edit_message_text(
        "🔓 **Verification Successful!**\n\nAb aap mujhse kuch bhi puch sakte hain. Main taiyaar hoon! 🚀",
        call.message.chat.id, 
        call.message.message_id,
        parse_mode="Markdown"
    )

# --- 🤖 AI CHAT LOGIC ---
@bot.message_handler(func=lambda m: True)
def ai_chat(m):
    # Verification Check
    if m.from_user.id not in verified_users:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Click to Verify", callback_data="verify"))
        bot.reply_to(m, "🚫 **Access Denied!**\nPehle verify karein.", reply_markup=markup)
        return

    # Typing Animation
    bot.send_chat_action(m.chat.id, 'typing')
    
    # Stable v1 API (No 404 Guaranteed)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": m.text}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if 'candidates' in data:
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            
            # Interesting Formatting
            header = "🤖 **NAGIX AI:**\n\n"
            footer = f"\n\n━━━━━━━━━━━━━━\n👤 **Owner:** {OWNER}"
            bot.reply_to(m, header + ai_text + footer, parse_mode="Markdown")
        else:
            bot.reply_to(m, "⚠️ AI abhi thoda busy hai, dubara try karein!")
            
    except Exception as e:
        bot.reply_to(m, "❌ Connection Error! Server down hai.")

# --- 🚀 PORT BINDING ---
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling(timeout=60)
