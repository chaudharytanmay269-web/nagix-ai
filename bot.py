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
    return "NAGIX AI IS TOTALLY ACTIVE"

# --- 🏠 START COMMAND ---
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Update Channel", url=CHANNEL_URL)
    btn2 = types.InlineKeyboardButton("✅ Verify & Start Chatting", callback_data="verify")
    markup.add(btn1, btn2)
    
    msg = (
        "✨ **NAGIX AI PREMIUM v3.0** ✨\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "👋 **Welcome Boss!**\n\n"
        "Main aapka personal AI assistant hoon. Aage badhne ke liye niche diye gaye steps follow karein:\n\n"
        "1️⃣ Hamara channel join karein.\n"
        "2️⃣ **Verify** button par click karein."
    )
    bot.send_message(m.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

# --- ✅ VERIFICATION ---
@bot.callback_query_handler(func=lambda call: call.data == "verify")
def verify_user(call):
    verified_users.add(call.from_user.id)
    bot.answer_callback_query(call.id, "✅ Access Granted!")
    bot.edit_message_text(
        "🔓 **Verification Successful!**\n\nAb aap mujhse koi bhi sawal puch sakte hain. Main taiyaar hoon! 🚀",
        call.message.chat.id, 
        call.message.message_id,
        parse_mode="Markdown"
    )

# --- 🤖 AI CHAT LOGIC ---
@bot.message_handler(func=lambda m: True)
def ai_chat(m):
    if m.from_user.id not in verified_users:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Verify", callback_data="verify"))
        bot.reply_to(m, "🚫 **Access Denied!**\nPehle verify button dabayein.", reply_markup=markup)
        return

    bot.send_chat_action(m.chat.id, 'typing')
    
    # URL and Payload with Safety Settings disabled
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": m.text}]}],
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        data = response.json()
        
        # If successfully answered
        if 'candidates' in data and len(data['candidates']) > 0:
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            footer = f"\n\n━━━━━━━━━━━━━━\n🌟 **Owner:** {OWNER}"
            bot.reply_to(m, ai_text + footer, parse_mode="Markdown")
        
        # Detailed Error Reporting if API fails
        else:
            error_msg = data.get('error', {}).get('message', 'Unknown API Error')
            if "API_KEY_INVALID" in error_msg:
                bot.reply_to(m, "❌ **API Key Galat Hai!**\nNayi API Key banakar code mein update karein.")
            else:
                bot.reply_to(m, f"⚠️ **Google AI Error:**\n`{error_msg}`")
                
    except Exception as e:
        bot.reply_to(m, "❌ **Connection Timeout!**\nRender server busy hai, thodi der mein try karein.")

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
