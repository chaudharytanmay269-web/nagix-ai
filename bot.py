import telebot
import google.generativeai as genai
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- DETAILS ---
TOKEN = "8588395332:AAEmPDTyPA3trRDReoqSv4P8_JPxDb6UYTs"
API_KEY = "AIzaSyB0NM-hXDWr-1s62YaEFvxnfEgK5aCVqCo"
CHANNEL_URL = "https://t.me/+Yo2sUrnHRk45OGFh"
OWNER_USER = "@nagixowner"

# --- GEMINI SETUP ---
genai.configure(api_key=API_KEY)

# Safety settings (Taaki bot error na de agar koi galat sawal puche)
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

# Naya Model Name
model = genai.GenerativeModel(model_name='gemini-1.5-flash', safety_settings=safety_settings)

bot = telebot.TeleBot(TOKEN)
app = Flask('')
verified_users = set()

@app.route('/')
def home():
    return "NAGIX AI IS UPDATED & LIVE"

# --- START ---
@bot.message_handler(commands=['start'])
def start(m):
    if m.from_user.id in verified_users:
        bot.send_message(m.chat.id, "✅ **Verified!** Puchiye kya puchna hai.", parse_mode="Markdown")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Update Channel", url=CHANNEL_URL)
    btn2 = types.InlineKeyboardButton("✅ Verify Now", callback_data="verify_user")
    markup.add(btn1, btn2)
    
    text = (
        "✨ **WELCOME TO NAGIX AI** ✨\n\n"
        "🔒 **Access Restricted**\n"
        "Bot use karne ke liye verify karein:\n\n"
        "1. Channel Join karein.\n"
        "2. Niche Verify button dabayein."
    )
    bot.send_message(m.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# --- VERIFY ---
@bot.callback_query_handler(func=lambda call: call.data == "verify_user")
def verify_cb(call):
    verified_users.add(call.from_user.id)
    bot.answer_callback_query(call.id, "Success!")
    bot.edit_message_text(
        "🔓 **Verification Successful!**\n\nMain taiyaar hoon. Kuch bhi puchiye!", 
        call.message.chat.id, 
        call.message.message_id
    )

# --- CHAT ---
@bot.message_handler(func=lambda m: True)
def chat(m):
    if m.from_user.id not in verified_users:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Verify Me", callback_data="verify_user"))
        bot.reply_to(m, "⚠️ **Not Verified!**\nPehle verify karein.", reply_markup=markup)
        return

    bot.send_chat_action(m.chat.id, 'typing')
    
    try:
        response = model.generate_content(m.text)
        reply = f"{response.text}\n\n━━━━━━━━━━━━━━\n👤 **Owner:** {OWNER_USER}"
        bot.reply_to(m, reply, parse_mode="Markdown")
        
    except Exception as e:
        # Error handling taaki bot band na ho
        err = str(e)
        if "404" in err:
             bot.reply_to(m, "⚠️ **Model Error:** Render par library update ho rahi hai. 1 minute baad try karein.")
        else:
             bot.reply_to(m, f"⚠️ Error: {err}")

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
