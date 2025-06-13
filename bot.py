import telebot
import requests
import random
import string
import logging
import re
import time
from threading import Thread
from datetime import datetime

# إعدادات البوت
TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
CHANNEL_ID = "@mmmmmuyter"
ADMIN_ID = 5367866254
bot = telebot.TeleBot(TOKEN)

# إعداد المسجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# إعدادات الاصطياد
DELAY = 3
PATTERNS = {'5prem': r'^[a-z]{2}\d[a-z]{2}$'}

def generate_premium_5char():
    while True:
        username = (
            random.choice(string.ascii_lowercase) +
            random.choice(string.ascii_lowercase) +
            random.choice(string.digits) +
            random.choice(string.ascii_lowercase) +
            random.choice(string.ascii_lowercase)
        )
        if re.match(PATTERNS['5prem'], username):
            return username

def check_platform(username, platform):
    try:
        url = f"https://{'t.me' if platform == 'telegram' else 'www.instagram.com'}/{username}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        
        if platform == "telegram":
            return "available" if "You can contact" in response.text else "taken"
        else:
            return "available" if response.status_code == 404 else "taken"
    except Exception as e:
        logger.error(f"Error checking @{username} on {platform}: {e}")
        return "error"

@bot.message_handler(commands=['hunt_premium'])
def hunt_premium(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ ليس لديك صلاحية!")
        return
    
    premium_usernames = [generate_premium_5char() for _ in range(5)]
    bot.reply_to(message, "🎣 بدأ اصطياد اليوزرات الخماسية المميزة...")
    
    results = {"available": [], "taken": []}
    for username in premium_usernames:
        status = check_and_report(username)
        if "available" in status.values():
            results["available"].append(username)
        else:
            results["taken"].append(username)
        time.sleep(DELAY)
    
    # إرسال التقرير النهائي
    send_summary_report(results)

def check_and_report(username):
    status = {
        "telegram": check_platform(username, "telegram"),
        "instagram": check_platform(username, "instagram")
    }
    return status

def send_summary_report(results):
    report = "📊 **تقرير الاصطياد**\n\n"
    
    if results["available"]:
        report += "🟢 **اليوزرات المتاحة:**\n"
        for username in results["available"]:
            report += f"- @{username} (Telegram & Instagram)\n"
    
    if results["taken"]:
        report += "\n🔴 **اليوزرات المحجوزة:**\n"
        for username in results["taken"]:
            tg_status = check_platform(username, "telegram")
            ig_status = check_platform(username, "instagram")
            report += f"- @{username} (TG: {'🟢' if tg_status == 'available' else '🔴'}, IG: {'🟢' if ig_status == 'available' else '🔴'})\n"
    
    try:
        bot.send_message(CHANNEL_ID, report, parse_mode="Markdown")
        if results["available"]:
            bot.send_message(ADMIN_ID, "🚀 يوجد يوزرات متاحة! راجع القناة.")
    except Exception as e:
        logger.error(f"فشل إرسال التقرير: {e}")

if __name__ == '__main__':
    logger.info("🔥 البوت يعمل!")
    try:
        bot.send_message(
            CHANNEL_ID,
            f"🤖 **تم تشغيل البوت بنجاح**\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🔍 جاهز للبحث عن اليوزرات المميزة!",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"فشل إرسال رسالة البدء: {e}")
    
    bot.polling()