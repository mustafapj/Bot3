import telebot
import requests
import random
import string

TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"

# ===== إعداد البروكسي =====
telebot.apihelper.proxy = {
    'https': 'socks5h://127.0.0.1:9050'  # بروكسي TOR المحلي
}

bot = telebot.TeleBot(TOKEN)

def generate_user():
    letters = string.ascii_lowercase + string.digits + "._"
    return "".join(random.choice(letters) for _ in range(5))

def check_user(username):
    url = f"https://t.me/{username}"
    try:
        req = requests.get(url, proxies={"https": "socks5h://127.0.0.1:9050"}, timeout=10)
        if "If you have Telegram" in req.text:
            return True
    except:
        return False
    return False

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 بدأ فحص اليوزرات الخماسية عبر بروكسي…")
    
    for _ in range(200):
        user = generate_user()
        if check_user(user):
            bot.send_message(message.chat.id, f"✨ متاح: @{user}")

bot.infinity_polling(skip_pending=True)