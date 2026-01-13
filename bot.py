import telebot
import requests

# Details (Inhe badal dena)
TOKEN = "8588395332:AAEmPDTyPA3trRDReoqSv4P8_JPxDb6UYTs"
API_KEY = "AIzaSyB0NM-hXDWr-1s62YaEFvxnfEgK5aCVqCo"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(m):
    # Professional Button
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📢 Channel Join Karein", url="https://t.me/+WvZ1Z3dpsT83NDYx"))
    
    text = "👋 **Welcome to NAGIX AI!**\n\nMain ek professional AI bot hoon. Aap mujhse sawal puch sakte hain."
    bot.send_message(m.chat.id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def ai_logic(m):
    # Professional Typing Status
    bot.send_chat_action(m.chat.id, 'typing')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    try:
        r = requests.post(url, json={"contents": [{"parts": [{"text": m.text}]}]})
        answer = r.json()['candidates'][0]['content']['parts'][0]['text']
        bot.reply_to(m, answer)
    except:
        bot.reply_to(m, "❌ Server busy hai, thodi der baad try karein.")

bot.infinity_polling()
