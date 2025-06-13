import telebot
import requests
import random
import string
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# إعدادات البوت
TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"  # تأكد من صحة التوكن
CHANNEL_ID = "@mmmmmuyter"
ADMIN_ID = 5367866254
bot = telebot.TeleBot(TOKEN)

# حالة التشغيل
hunt_active = False
stop_event = threading.Event()

# إعدادات محسنة للاصطياد
TARGET_LENGTHS = [2, 3]  # ركز على اليوزرات القصيرة الأكثر قيمة
HUNT_DELAY = 5  # زيادة التأخير لتجنب الحظر
PROXY = None  # مثال: {'http': 'http://123.123.123:8080'}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def generate_rare_username(length):
    """إنشاء يوزر نادر بمعايير صارمة"""
    chars = string.ascii_lowercase
    for _ in range(100):  # محاولات أكبر لتوليد يوزرات قيمة
        username = ''.join(random.choice(chars) for _ in range(length))
        # فلترة متقدمة لتجنب اليوزرات غير القابلة للبيع
        if (len(set(username)) >= 2 and  # على الأقل حرفين مختلفين
            not username.isdigit() and
            not username.startswith(('0', '1', '_')) and
            not username.endswith(('0', '1', '_'))):
            return username
    return None

def check_availability(username, platform):
    """فحص التوفر مع إدارة أفضل للأخطاء"""
    try:
        if platform == "telegram":
            url = f"https://t.me/{username}"
            resp = requests.get(url, headers=headers, proxies=PROXY, timeout=10)
            return resp.status_code == 200 and "You can contact" in resp.text
        else:  # instagram
            url = f"https://www.instagram.com/{username}/"
            resp = requests.get(url, headers=headers, proxies=PROXY, timeout=10)
            return resp.status_code == 404
    except:
        return False

def hunt(username):
    """وظيفة الاصطياد المحسنة"""
    try:
        tg_available = check_availability(username, "telegram")
        ig_available = check_availability(username, "instagram")
        
        if tg_available or ig_available:
            report = f"🎯 **يوزر نادر متاح!**\n\n"
            report += f"🔹 `{username}`\n"
            report += f"▫️ تليجرام: {'🟢 متاح' if tg_available else '🔴 محجوز'}\n"
            report += f"▫️ إنستغرام: {'🟢 متاح' if ig_available else '🔴 محجوز'}\n\n"
            report += f"📎 تليجرام: t.me/{username}\n"
            report += f"📎 إنستغرام: instagram.com/{username}"
            
            bot.send_message(CHANNEL_ID, report, parse_mode='Markdown')
            if tg_available:
                bot.send_message(ADMIN_ID, f"🚨 **تنبيه عاجل**\nيوزر تليجرام نادر متاح!\n@{username}\n\nسارع بالحجز قبل الآخرين!", parse_mode='Markdown')
    except Exception as e:
        print(f"Error in hunting: {e}")

def auto_hunt():
    """نظام الاصطياد التلقائي المحسن"""
    while hunt_active and not stop_event.is_set():
        length = random.choice(TARGET_LENGTHS)
        username = generate_rare_username(length)
        if username:
            hunt(username)
            time.sleep(HUNT_DELAY + random.uniform(0, 2))  # تأخير عشوائي إضافي

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        show_control_panel(message.chat.id)

def show_control_panel(chat_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("▶️ بدء الاصطياد", callback_data="start_hunt"),
        InlineKeyboardButton("⏹️ إيقاف", callback_data="stop_hunt")
    )
    markup.row(InlineKeyboardButton("🔄 حالة التشغيل", callback_data="status"))
    bot.send_message(chat_id, "🎣 **لوحة تحكم بوت الاصطياد**\n\nاختر الإجراء المطلوب:", reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global hunt_active, stop_event
    
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ غير مصرح لك!")
        return
    
    if call.data == "start_hunt":
        if not hunt_active:
            hunt_active = True
            stop_event.clear()
            threading.Thread(target=auto_hunt).start()
            bot.edit_message_text("✅ **تم تشغيل الاصطياد التلقائي**\n\nالبوت الآن يبحث عن يوزرات نادرة...", 
                                call.message.chat.id, 
                                call.message.message_id,
                                parse_mode='Markdown')
        else:
            bot.answer_callback_query(call.id, "⚠️ الاصطياد يعمل بالفعل!")
    
    elif call.data == "stop_hunt":
        if hunt_active:
            hunt_active = False
            stop_event.set()
            bot.edit_message_text("❌ **تم إيقاف الاصطياد**\n\nلإعادة التشغيل اضغط ▶️ بدء الاصطياد", 
                                call.message.chat.id, 
                                call.message.message_id,
                                parse_mode='Markdown')
        else:
            bot.answer_callback_query(call.id, "⚠️ الاصطياد متوقف بالفعل!")
    
    elif call.data == "status":
        status = "🟢 **قيد التشغيل**" if hunt_active else "🔴 **متوقف**"
        bot.answer_callback_query(call.id, f"حالة البوت: {status}")
    
    bot.answer_callback_query(call.id)

if __name__ == '__main__':
    print("""
    ░█████╗░██████╗░░█████╗░██╗░░██╗
    ██╔══██╗██╔══██╗██╔══██╗██║░██╔╝
    ███████║██████╦╝██║░░╚═╝█████═╝░
    ██╔══██║██╔══██╗██║░░██╗██╔═██╗░
    ██║░░██║██████╦╝╚█████╔╝██║░╚██╗
    ╚═╝░░╚═╝╚═════╝░░╚════╝░╚═╝░░╚═╝
    """)
    print("🔥 البوت يعمل! أرسل /start للتحكم")
    bot.polling(none_stop=True, interval=1)