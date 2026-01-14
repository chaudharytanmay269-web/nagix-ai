import telebot
import requests
import json
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- DETAILS ---
TOKEN = "8588395332:AAEmPDTyPA3trRDReoqSv4P8_JPxDb6UYTs"
API_KEY = "AIzaSyB0NM-hXDWr-1s62YaEFvxnfEgK5aCVqCo"
CHANNEL_URL = "https://t.me/+Yo2sUrnHRk45OGFh"
OWNER_USER = "@nagixowner"

bot = telebot.TeleBot(TOKEN)
app = Flask('')
verified_users = set()

@app.route('/')
def home():
    return "NAGIX AI - RAW MODE ONLINE"

# --- COMMANDS ---
@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id in verified_users:
        bot.send_message(m.chat.id, "✅ **Verified!**", parse_mode="Markdown")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Update Channel", url=CHANNEL_URL)
    btn2 = types.InlineKeyboardButton("✅ Verify Now", callback_data="verify_user")
    markup.add(btn1, btn2)
    
    bot.send_message(m.chat.id, "👋 **NAGIX AI**\n\nAccess ke liye verify karein:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "verify_user")
def verify_cb(call):
    verified_users.add(call.from_user.id)
    bot.answer_callback_query(call.id, "Done!")
    bot.edit_message_text("🔓 **Verified!** Puchiye sawal.", call.message.chat.id, call.message.message_id)

# --- DIRECT API LOGIC (NO LIBRARY) ---
@bot.message_handler(func=lambda m: True)
def chat(m):
    if m.from_user.id not in verified_users:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Verify", callback_data="verify_user"))
        bot.reply_to(m, "⚠️ Verify first!", reply_markup=markup)
        return

    bot.send_chat_action(m.chat.id, 'typing')
    
    # Direct URL - Ye kabhi fail nahi hota
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": m.text}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        
        # Check Response
        if "candidates" in res_json:
            ans = res_json['candidates'][0]['content']['parts'][0]['text']
            footer = f"\n\n━━━━━━━━━━━━━━\n👤 **Owner:** {OWNER_USER}"
            bot.reply_to(m, ans + footer, parse_mode="Markdown")
        else:
            # Agar error aaya toh seedha dikhayega
            bot.reply_to(m, f"⚠️ Error: {res_json}")
            
    except Exception as e:
        bot.reply_to(m, f"❌ Connect Error: {str(e)}")

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
