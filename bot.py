import telebot
import requests
import random
import string
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# إعدادات البوت
TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"  # ❌ استبدل بتوكن البوت الخاص بك
CHANNEL_ID = "@mmmmmuyter"
ADMIN_ID = 5367866254
bot = telebot.TeleBot(TOKEN)

# حالة التشغيل
hunt_active = False
stop_event = threading.Event()

# إعدادات الاصطياد
TARGET_LENGTHS = [2, 3, 4]  # أطوال اليوزرات المطلوبة
HUNT_DELAY = 3  # تأخير بين المحاولات (ثواني)

def generate_rare_username(length):
    """إنشاء يوزر نادر عشوائي"""
    chars = string.ascii_lowercase + string.digits
    while True:
        username = ''.join(random.choice(chars) for _ in range(length))
        if not username.isdigit() and len(set(username)) >= length//2:
            return username

def hunt(username):
    """وظيفة الاصطياد الرئيسية"""
    try:
        # فحص تليجرام
        tg_status = "🟢" if requests.get(f"https://t.me/{username}", timeout=5).text.count("You can contact") else "🔴"
        
        # فحص إنستغرام
        ig_status = "🟢" if requests.get(f"https://www.instagram.com/{username}/", timeout=5).status_code == 404 else "🔴"
        
        if "🟢" in [tg_status, ig_status]:
            report = f"""🎯 يوزر نادر متاح!
@{username}
تليجرام: {tg_status} | إنستغرام: {ig_status}
تليجرام: t.me/{username}
إنستغرام: instagram.com/{username}"""
            
            bot.send_message(CHANNEL_ID, report)
            if tg_status == "🟢":
                bot.send_message(ADMIN_ID, f"🚨 تليجرام متاح!\n{report}")
            if ig_status == "🟢":
                bot.send_message(ADMIN_ID, f"🚨 إنستغرام متاح!\n{report}")
    except:
        pass

def auto_hunt():
    """عملية الاصطياد التلقائي"""
    while hunt_active and not stop_event.is_set():
        username = generate_rare_username(random.choice(TARGET_LENGTHS))
        threading.Thread(target=hunt, args=(username,)).start()
        time.sleep(HUNT_DELAY)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("▶️ تشغيل الاصطياد", callback_data="start_hunt"),
            InlineKeyboardButton("⏹️ إيقاف الاصطياد", callback_data="stop_hunt")
        )
        bot.send_message(message.chat.id, "🛠️ لوحة تحكم بوت الاصطياد:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global hunt_active, stop_event
    
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ غير مصرح لك!")
        return
    
    if call.data == "start_hunt" and not hunt_active:
        hunt_active = True
        stop_event.clear()
        threading.Thread(target=auto_hunt).start()
        bot.edit_message_text("✅ تم تشغيل وضع الاصطياد التلقائي", call.message.chat.id, call.message.message_id)
        
    elif call.data == "stop_hunt" and hunt_active:
        hunt_active = False
        stop_event.set()
        bot.edit_message_text("❌ تم إيقاف الاصطياد", call.message.chat.id, call.message.message_id)
    
    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    print("🔥 البوت يعمل! أرسل /start للتحكم")
    bot.polling()