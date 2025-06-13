import telebot
import requests
import re
import logging
from threading import Thread

# تكوين الإعدادات
TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"  # استبدله بتوكن بوتك
CHANNEL_ID = "@mmmmmuyter"  # استبدل بإسم قناتك
ADMIN_IDS = [5367866254]  # أضف أي دي حسابك

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TOKEN)

def is_rare_username(username):
    """تصفية اليوزرات النادرة (ثنائية/ثلاثية/رباعية)"""
    return 2 <= len(username) <= 4 and username.isalnum()

def check_username_availability(username):
    """فحص توفر اليوزر عبر طلبات HTTP"""
    try:
        url = f"https://t.me/{username}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if "If you have <strong>Telegram</strong>, you can contact" in response.text:
            return True  # متاح
        return False  # محجوز
    except Exception as e:
        logger.error(f"Error checking @{username}: {str(e)}")
        return None

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ هذا البوت للاستخدام الشخصي فقط")
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    btn1 = telebot.types.KeyboardButton('فحص اليوزرات')
    btn2 = telebot.types.KeyboardButton('المساعدة')
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id,
        "مرحبًا! أنا بوت فحص اليوزرات النادرة (ثنائية/ثلاثية/رباعية).\n\n"
        "اختر أحد الخيارات:",
        reply_markup=markup
    )

@bot.message_handler(func=lambda m: m.text == 'فحص اليوزرات')
def ask_for_usernames(message):
    bot.reply_to(message, "أرسل قائمة اليوزرات التي تريد فحصها (مفصولة بمسافات أو أسطر):")

@bot.message_handler(func=lambda m: m.text and not m.text.startswith('/'))
def process_usernames(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    text = message.text
    usernames = re.findall(r'@?([a-zA-Z0-9_]{2,4})\b', text)
    usernames = list(set(filter(is_rare_username, usernames)))
    
    if not usernames:
        bot.reply_to(message, "⚠️ لم يتم العثور على يوزرات نادرة (2-4 أحرف/أرقام)")
        return
    
    bot.reply_to(message, f"🔍 جارٍ فحص {len(usernames)} يوزر...")
    
    available = []
    unavailable = []
    
    def check_and_save(username):
        if check_username_availability(username):
            available.append(f"@{username}")
        else:
            unavailable.append(f"@{username}")
    
    # فحص متوازي باستخدام Threading
    threads = []
    for username in usernames:
        t = Thread(target=check_and_save, args=(username,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
    
    # إرسال النتائج
    report = "📊 نتائج الفحص:\n\n"
    if available:
        report += f"✅ متاح ({len(available)}):\n" + "\n".join(available) + "\n\n"
    if unavailable:
        report += f"❌ محجوز ({len(unavailable)}):\n" + "\n".join(unavailable)
    
    bot.reply_to(message, report)
    
    # إرسال إلى القناة (إذا وجدت يوزرات متاحة)
    if available:
        channel_report = f"📢 يوزرات متاحة:\n" + " ".join(available)
        try:
            bot.send_message(CHANNEL_ID, channel_report)
        except Exception as e:
            logger.error(f"فشل إرسال إلى القناة: {e}")

if __name__ == '__main__':
    logger.info("Bot is running...")
    bot.polling(none_stop=True)
