import telebot
import requests
import random
import string
import logging
import re
import time
import threading
from datetime import datetime

# =============== CONFIGURATION ===============
class Config:
    def __init__(self):
        self.TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
        self.CHANNEL_ID = "@mmmmmuyter"
        self.ADMIN_ID = 5367866254
        self.REQUEST_TIMEOUT = 7
        self.BREAK_DURATION = 10  # تقليل لسرعة التجربة (يمكن تغييره)
        self.MAX_THREADS = 5

        # أنماط يوزرات إنستجرام الثنائية والثلاثية والرباعية فقط
        self.INSTAGRAM_PATTERNS = [
            r'^[a-z]{2}$',      # ثنائية حروف
            r'^[a-z]{3}$',      # ثلاثية حروف
            r'^[a-z]{4}$'       # رباعية حروف
        ]

        # تيليجرام: خماسية سداسية سباعية مميزة (حروف وأرقام)
        self.TG_LENGTHS = [5,6,7]

# =============== USERNAME GENERATOR ===============
class UsernameGenerator:
    def __init__(self, config):
        self.config = config
        self.chars = string.ascii_lowercase + string.digits

    def generate_telegram(self):
        length = random.choice(self.config.TG_LENGTHS)
        # توليد يوزر مميز عشوائي مكون من حروف وأرقام
        username = ''.join(random.choices(self.chars, k=length))
        return username

    def generate_instagram(self):
        # توليد يوزر انستجرام بحسب الأنماط المحددة
        pattern = random.choice(self.config.INSTAGRAM_PATTERNS)
        length = int(pattern.strip('^$').replace('{','').replace('}',''))
        username = ''.join(random.choices(string.ascii_lowercase, k=length))
        return username

# =============== CHECKER ===============
class Checker:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0'
        })

    def check_instagram(self, username):
        try:
            url = f"https://www.instagram.com/{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
            # إذا رد 404 فهذا يعني اليوزر متاح
            return response.status_code == 404
        except:
            return False

    def check_telegram(self, username):
        try:
            url = f"https://t.me/{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            # إذا كان نص الصفحة يحتوي على "You can contact" هذا يعني أن اليوزر محجوز
            # وإلا متاح
            return "You can contact" not in response.text
        except:
            return False

# =============== HUNTING ENGINE ===============
class HuntingEngine:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.generator = UsernameGenerator(config)
        self.checker = Checker(config)
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return False
        self.running = True
        self.thread = threading.Thread(target=self.hunt_loop)
        self.thread.start()
        return True

    def stop(self):
        if not self.running:
            return False
        self.running = False
        if self.thread:
            self.thread.join()
        return True

    def hunt_loop(self):
        while self.running:
            # فحص يوزرات انستجرام (ثنائية، ثلاثية، رباعية)
            ig_username = self.generator.generate_instagram()
            ig_available = self.checker.check_instagram(ig_username)

            if ig_available:
                self.send_result(ig_username, platform="Instagram")

            # فحص يوزرات تيليجرام (خماسية، سداسية، سباعية)
            tg_username = self.generator.generate_telegram()
            tg_available = self.checker.check_telegram(tg_username)

            if tg_available:
                self.send_result(tg_username, platform="Telegram")

            time.sleep(1)  # تهدئة بين الفحوصات

    def send_result(self, username, platform):
        message = (
            f"🎉 Username Available!\n"
            f"🌐 Platform: {platform}\n"
            f"🔖 Username: @{username}\n"
            f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🔗 https://{'instagram.com' if platform == 'Instagram' else 't.me'}/{username}"
        )
        try:
            self.bot.send_message(self.config.CHANNEL_ID, message)
        except Exception as e:
            logging.error(f"Failed to send message: {e}")

# =============== BOT SETUP ===============
config = Config()
bot = telebot.TeleBot(config.TOKEN)
hunter = HuntingEngine(bot, config)

# =============== BOT COMMANDS ===============
@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id != config.ADMIN_ID:
        bot.reply_to(message, "⛔ Unauthorized!")
        return

    started = hunter.start()
    if started:
        bot.reply_to(message, "🚀 Hunting started! The bot is now scanning usernames.")
    else:
        bot.reply_to(message, "⚠️ Hunter is already running.")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    if message.from_user.id != config.ADMIN_ID:
        bot.reply_to(message, "⛔ Unauthorized!")
        return

    stopped = hunter.stop()
    if stopped:
        bot.reply_to(message, "🛑 Hunting stopped.")
    else:
        bot.reply_to(message, "⚠️ Hunter isn't running.")

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, "/start - Start hunting\n/stop - Stop hunting")

# =============== MAIN ===============
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Bot started...")
    bot.infinity_polling()