import telebot
import requests
import random
import string
import logging
import re
import time
import concurrent.futures
from datetime import datetime

# Configuration
TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
CHANNEL_ID = "@mmmmmuyter"
ADMIN_ID = 5367866254
MAX_WORKERS = 10  # عدد الثريدات المتوازية
REQUEST_TIMEOUT = 5
bot = telebot.TeleBot(TOKEN, threaded=True)

# Advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('UltraHunter')

# Premium Generator
class UsernameGenerator:
    @staticmethod
    def generate_premium():
        while True:
            username = f"{random.choice(string.ascii_lowercase)}{random.choice(string.ascii_lowercase)}" \
                      f"{random.choice(string.digits)}" \
                      f"{random.choice(string.ascii_lowercase)}{random.choice(string.ascii_lowercase)}"
            if re.match(r'^[a-z]{2}\d[a-z]{2}$', username):
                return username

# Turbo Checker
class TurboChecker:
    @staticmethod
    def check_username(username):
        results = {
            'username': username,
            'telegram': TurboChecker._check_telegram(username),
            'instagram': TurboChecker._check_instagram(username)
        }
        return results

    @staticmethod
    def _check_telegram(username):
        try:
            response = requests.get(
                f"https://t.me/{username}",
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=REQUEST_TIMEOUT
            )
            return 'available' if "You can contact" in response.text else 'taken'
        except Exception as e:
            logger.error(f"Telegram check failed for @{username}: {str(e)}")
            return 'error'

    @staticmethod
    def _check_instagram(username):
        try:
            response = requests.get(
                f"https://www.instagram.com/{username}",
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=REQUEST_TIMEOUT
            )
            return 'available' if response.status_code == 404 else 'taken'
        except Exception as e:
            logger.error(f"Instagram check failed for @{username}: {str(e)}")
            return 'error'

# Report Generator
class ReportEngine:
    @staticmethod
    def generate_report(results):
        available = [r for r in results if 'available' in [r['telegram'], r['instagram']]]
        taken = [r for r in results if r not in available]

        report = "🔥 *تقرير الصيد السريع*\n\n"
        
        if available:
            report += "🎯 *اليوزرات المتاحة*\n"
            for r in available:
                platforms = []
                if r['telegram'] == 'available':
                    platforms.append("Telegram")
                if r['instagram'] == 'available':
                    platforms.append("Instagram")
                report += f"🟢 @{r['username']} ({' & '.join(platforms)})\n"

        if taken:
            report += "\n⛔ *اليوزرات المحجوزة*\n"
            for r in taken:
                tg_status = '🟢' if r['telegram'] == 'available' else '🔴'
                ig_status = '🟢' if r['instagram'] == 'available' else '🔴'
                report += f"🔴 @{r['username']} (TG: {tg_status}, IG: {ig_status})\n"

        return report

# Bot Commands
@bot.message_handler(commands=['hunt'])
def hunt_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Unauthorized!")
        return

    try:
        count = int(message.text.split()[1]) if len(message.text.split()) > 1 else 10
        count = min(count, 50)  # Maximum limit
    except:
        count = 10

    bot.reply_to(message, f"🚀 بدأ الصيد السريع لـ {count} يوزر...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        usernames = [UsernameGenerator.generate_premium() for _ in range(count)]
        results = list(executor.map(TurboChecker.check_username, usernames))

    report = ReportEngine.generate_report(results)
    bot.send_message(CHANNEL_ID, report, parse_mode="Markdown")

    if any('available' in [r['telegram'], r['instagram']] for r in results):
        bot.send_message(ADMIN_ID, "🎉 يوجد يوزرات متاحة! راجع القناة.")

# Startup
if __name__ == '__main__':
    logger.info("🚀 Starting Ultra Hunter Bot")
    try:
        bot.send_message(
            CHANNEL_ID,
            f"⚡ *Ultra Hunter Bot Activated*\n"
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"💎 جاهز لصيد اليوزرات المميزة!",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to send startup message: {str(e)}")

    bot.infinity_polling()