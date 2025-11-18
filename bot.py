import telebot, requests, random, string

TOKEN = "8462132430:AAGXN9A94ixI2Ak4x4lB-xCsL1VbNGDtTJc"
bot = telebot.TeleBot(TOKEN)

# توليد يوزر خماسي عشوائي
def generate_user():
    letters = string.ascii_lowercase + string.digits + "._"
    user = "".join(random.choice(letters) for _ in range(5))
    return user

# فحص اليوزر عبر API تيليجرام
def check_user(username):
    url = f"https://t.me/{username}"
    req = requests.get(url)
    if "If you have Telegram" in req.text:
        return True  # اليوزر متاح
    return False     # اليوزر محجوز

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔥 تم تشغيل فحص اليوزرات الخماسية...\nسأرسل لك المتاحة فقط.")

    for _ in range(200):  # عدد الفحوصات
        user = generate_user()
        if check_user(user):
            bot.send_message(message.chat.id, f"✨ متاح: @{user}")
        else:
            pass  # تجاهل المحجوز

bot.infinity_polling()