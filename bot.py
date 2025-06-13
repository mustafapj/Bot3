import telebot
import requests
import random
import string
import time
from threading import Thread

TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"  # ❌ استبدله بتوكن البوت الخاص بك
CHANNEL_ID = "@mmmmmuyter"  # ❌ استبدل بقناتك
ADMIN_ID = 5367866254  # ❌ استبدل برقمك

bot = telebot.TeleBot(TOKEN)

# إعدادات الفحص
DELAY = 5  # تأخير بين الطلبات (تجنب الحظر)
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def generate_username(length):
    """إنشاء يوزر عشوائي نادر"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def check_telegram(username):
    """فحص تليجرام بدقة"""
    try:
        r = requests.get(f"https://t.me/{username}", headers=HEADERS, timeout=10)
        return "available" if "You can contact" in r.text else "taken"
    except Exception as e:
        print(f"Error checking Telegram: {e}")
        return "error"

def check_instagram(username):
    """فحص إنستغرام بدقة"""
    try:
        r = requests.get(f"https://www.instagram.com/{username}/", headers=HEADERS, timeout=10)
        return "available" if r.status_code == 404 else "taken"
    except Exception as e:
        print(f"Error checking Instagram: {e}")
        return "error"

def hunt_and_report(username):
    """فحص اليوزر وإرسال النتائج"""
    tg_status = check_telegram(username)
    ig_status = check_instagram(username)
    
    if "available" in [tg_status, ig_status]:
        report = f"🎯 *يوزر متاح!*\n\n"
        report += f"🔹 `{username}`\n"
        report += f"• تليجرام: {'🟢 متاح' if tg_status == 'available' else '🔴 محجوز'}\n"
        report += f"• إنستغرام: {'🟢 متاح' if ig_status == 'available' else '🔴 محجوز'}\n\n"
        report += f"📎 تليجرام: t.me/{username}\n"
        report += f"📎 إنستغرام: instagram.com/{username}"
        
        try:
            bot.send_message(CHANNEL_ID, report, parse_mode="Markdown")
            bot.send_message(ADMIN_ID, "🚨 تم العثور على يوزر متاح! تفحص القناة.")
        except Exception as e:
            print(f"Error sending message: {e}")

@bot.message_handler(commands=['start_hunt'])
def start_hunt(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "🎣 بدأ الاصطياد... (سيتم إرسال النتائج للقناة)")
        # تشغيل 5 عمليات فحص متوازية
        for _ in range(5):
            length = random.choice([2, 3])  # ثنائي أو ثلاثي
            username = generate_username(length)
            Thread(target=hunt_and_report, args=(username,)).start()
            time.sleep(DELAY)

if __name__ == '__main__':
    print("⚡ البوت يعمل! أرسل /start_hunt للبدء")
    bot.polling()