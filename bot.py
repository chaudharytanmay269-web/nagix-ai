import telebot
import requests
from flask import Flask
from threading import Thread
import os
import json

# --- CONFIGURATION ---
TOKEN = "8588395332:AAEmPDTyPA3trRDReoqSv4P8_JPxDb6UYTs"
# Maine aapki API Key check ki hai, ye sahi honi chahiye. 
# Agar phir bhi error aaye toh ek baar Google AI Studio se 'Gemini 1.5 Flash' ki nayi key bana lena.
API_KEY = "AIzaSyB0NM-hXDWr-1s62YaEFvxnfEgK5aCVqCo"
CHANNEL_URL = "https://t.me/+WvZ1Z3dpsT83NDYx" # Naya link yahan paste kar dena
OWNER_ID = "@nagixowner"

bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "NAGIX AI STATUS: RUNNING"

@bot.message_handler(commands=['start'])
def start(m):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn1 = telebot.types.InlineKeyboardButton("📢 Join Update Channel", url=CHANNEL_URL)
    btn2 = telebot.types.InlineKeyboardButton("👤 Contact Owner", url="https://t.me/nagixowner")
    markup.add(btn1, btn2)
    
    text = (f"👋 **Welcome to NAGIX AI!**\n\n"
            f"Main ek professional AI bot hoon.\n\n"
            f"📢 **Channel:** [Join Here]({CHANNEL_URL})\n"
            f"👤 **Owner:** {OWNER_ID}\n\n"
            "Ab aap mujhse kuch bhi puch sakte hain!")
    bot.send_message(m.chat.id, text, reply_markup=markup, parse_mode="Markdown", disable_web_page_preview=False)

@bot.message_handler(func=lambda m: True)
def ai_reply(m):
    if m.text.startswith('/'): return
    
    bot.send_chat_action(m.chat.id, 'typing')
    
    # Gemini API URL with Flash model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # Advanced Payload for stability
    payload = {
        "contents": [{
            "parts": [{"text": m.text}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        data = response.json()
        
        # Checking if AI gave a valid response
        if 'candidates' in data and len(data['candidates']) > 0:
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            # Message send logic (Split if too long)
            if len(ai_text) > 4000:
                for x in range(0, len(ai_text), 4000):
                    bot.reply_to(m, ai_text[x:x+4000])
            else:
                bot.reply_to(m, ai_text)
        elif 'error' in data:
            bot.reply_to(m, f"⚠️ **API Key Issue:** {data['error']['message']}")
        else:
            bot.reply_to(m, "⚠️ AI abhi samajh nahi paya. Ek baar phir puchiye.")
            
    except Exception as e:
        bot.reply_to(m, "❌ Connection Error! Server thoda busy hai.")

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    print("Bot is Live on Render!")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
