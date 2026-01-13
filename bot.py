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

# --- GOOGLE GEMINI SETUP ---
# Hum 'gemini-pro' use kar rahe hain jo sabse stable hai
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(TOKEN)
app = Flask('')

# Verification List (Temporary)
verified_users = set()

@app.route('/')
def home():
    return "NAGIX AI IS LIVE"

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start(m):
    # Check if user is already verified
    if m.from_user.id in verified_users:
        bot.send_message(m.chat.id, "✅ **Aap pehle se verified hain!**\nSeedha sawal puchiye.", parse_mode="Markdown")
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📢 Join Update Channel", url=CHANNEL_URL)
    btn2 = types.InlineKeyboardButton("✅ Verify & Start Chatting", callback_data="verify_user")
    markup.add(btn1, btn2)
    
    welcome_text = (
        "✨ **WELCOME TO NAGIX AI** ✨\n\n"
        "🔒 **Access Locked!**\n"
        "Mujhse baat karne ke liye verification zaroori hai.\n\n"
        "👇 **Steps:**\n"
        "1. Channel Join karein.\n"
        "2. **Verify** button dabayein."
    )
    bot.send_message(m.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- VERIFICATION BUTTON ---
@bot.callback_query_handler(func=lambda call: call.data == "verify_user")
def verify_callback(call):
    verified_users.add(call.from_user.id)
    bot.answer_callback_query(call.id, "✅ Verified Successfully!")
    
    bot.edit_message_text(
        "🔓 **Verification Complete!**\n\nAb aap mujhse kuch bhi puch sakte hain.\nTry karein: *Hello AI*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

# --- AI CHAT LOGIC ---
@bot.message_handler(func=lambda m: True)
def ai_chat(m):
    # 1. Verification Check
    if m.from_user.id not in verified_users:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ Verify Me First", callback_data="verify_user"))
        bot.reply_to(m, "⛔ **Rukiye!**\n\nAapne abhi tak verify nahi kiya hai. Niche button dabayein.", reply_markup=markup)
        return

    # 2. Typing Status
    bot.send_chat_action(m.chat.id, 'typing')
    
    try:
        # 3. Generate Response
        response = model.generate_content(m.text)
        
        # Professional Footer
        reply_text = f"{response.text}\n\n━━━━━━━━━━━━━━\n👤 **Owner:** {OWNER_USER}"
        bot.reply_to(m, reply_text, parse_mode="Markdown")
        
    except Exception as e:
        # Agar ab error aaya toh bot aapko exact reason batayega
        error_msg = str(e)
        print(f"ERROR: {error_msg}")
        
        if "400" in error_msg:
             bot.reply_to(m, "⚠️ **API Key Error:** Lagta hai API Key mein kuch issue hai.")
        else:
             # Asli error user ko dikhana taaki hum fix kar sakein
             bot.reply_to(m, f"⚠️ **System Error:**\n`{error_msg}`\n\nIse Owner ko bhejein.", parse_mode="Markdown")

# --- SERVER RUN ---
def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
