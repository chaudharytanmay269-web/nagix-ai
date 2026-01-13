import telebot
import google.generativeai as genai
from telebot import types
from flask import Flask
from threading import Thread
import os

# --- CONFIGURATION ---
TOKEN = "8588395332:AAEmPDTyPA3trRDReoqSv4P8_JPxDb6UYTs"
API_KEY = "AIzaSyB0NM-hXDWr-1s62YaEFvxnfEgK5aCVqCo"
CHANNEL_URL = "https://t.me/+Yo2sUrnHRk45OGFh"
OWNER_USER = "@nagixowner"

# Gemini AI Setup
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# User verification list
verified_users = set()

@app.route('/')
def home():
    return "NAGIX AI IS RUNNING ON RENDER"

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(m):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Update Channel", url=CHANNEL_URL)
    btn2 = types.InlineKeyboardButton("✅ Verify & Start Chatting", callback_data="verify_user")
    markup.add(btn1, btn2)
    
    welcome_text = (
        "✨ **WELCOME TO NAGIX AI PREMIUM** ✨\n\n"
        "Main ek powerful AI assistant hoon. Bot use karne ke liye aapko verify hona zaroori hai.\n\n"
        "📍 **Steps:**\n"
        "1. Upar diye gaye button se channel join karein.\n"
        "2. **Verify & Start Chatting** par click karein."
    )
    bot.send_message(m.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- VERIFICATION LOGIC ---
@bot.callback_query_handler(func=lambda call: call.data == "verify_user")
def verify(call):
    verified_users.add(call.from_user.id)
    bot.answer_callback_query(call.id, "✅ Verified Successfully!")
    
    # Update message to show access granted
    bot.edit_message_text(
        "✨ **Access Granted!**\n\nAb aap mujhse kuch bhi puch sakte hain. Main taiyaar hoon! 🤖",
        call.message.chat.id, 
        call.message.message_id
    )

# --- AI CHAT LOGIC ---
@bot.message_handler(func=lambda m: True)
def ai_reply(m):
    # Check if user is verified
    if m.from_user.id not in verified_users:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Verify Karein", callback_data="verify_user"))
        bot.reply_to(m, "⚠️ **Verification Required!**\n\nPehle niche diye gaye button se verify karein.", reply_markup=markup)
        return

    # Professional typing action
    bot.send_chat_action(m.chat.id, 'typing')
    
    try:
        response = model.generate_content(m.text)
        
        # Attractive Footer
        footer = f"\n\n━━━━━━━━━━━━━━\n🌟 *Owner: {OWNER_USER}*"
        final_msg = response.text + footer
        
        bot.reply_to(m, final_msg, parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(m, "❌ API temporarily busy. Please try again in 1 minute.")

# --- SERVER START ---
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling(timeout=60)
