import telebot
import requests
import random
import string
import logging
import time
import threading
from datetime import datetime

# =============== CONFIG ===============
class Config:
    def __init__(self):
        self.TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
        self.CHANNEL_ID = "@mmmmmuyter"
        self.ADMIN_ID = 5367866254
        
        # إعدادات الفحص
        self.REQUEST_TIMEOUT = 10
        self.DELAY_BETWEEN_CHECKS = 5  # تأخير أكبر بين الطلبات
        
        # أنماط اليوزرات
        self.PATTERNS = {
            "instagram": [3, 4, 5],  # ثلاثي، رباعي، خماسي
            "telegram": [5, 6, 7],   # خماسي، سداسي، سباعي
            "twitter": [4, 5, 6],    # رباعي، خماسي، سداسي
            "snapchat": [4, 5, 6],   # رباعي، خماسي، سداسي
            "tiktok": [5, 6, 7]      # خماسي، سداسي، سباعي
        }

# =============== GENERATOR ===============
class UsernameGenerator:
    def __init__(self, config):
        self.config = config
    
    def generate(self, platform):
        length = random.choice(self.config.PATTERNS[platform])
        if platform == "telegram":
            chars = string.ascii_lowercase + string.digits + "_"
        else:
            chars = string.ascii_lowercase + string.digits
        return ''.join(random.choices(chars, k=length))

# =============== CHECKER (بدون بروكسي) ===============
class Checker:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }

    def check_instagram(self, username):
        try:
            url = f"https://www.instagram.com/{username}/?__a=1"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            return response.status_code == 404
        except:
            return False

    def check_telegram(self, username):
        try:
            url = f"https://t.me/{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            return "tgme_username_link" not in response.text
        except:
            return False

    def check_twitter(self, username):
        try:
            url = f"https://twitter.com/{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
            return response.status_code in [404, 302]
        except:
            return False

    def check_snapchat(self, username):
        try:
            url = f"https://www.snapchat.com/add/{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
            return response.status_code == 404
        except:
            return False

    def check_tiktok(self, username):
        try:
            url = f"https://www.tiktok.com/@{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
            return response.status_code == 404
        except:
            return False

    def check(self, username, platform):
        if platform == "instagram":
            return self.check_instagram(username)
        elif platform == "telegram":
            return self.check_telegram(username)
        elif platform == "twitter":
            return self.check_twitter(username)
        elif platform == "snapchat":
            return self.check_snapchat(username)
        elif platform == "tiktok":
            return self.check_tiktok(username)
        return False

# =============== HUNTER ===============
class Hunter:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.generator = UsernameGenerator(config)
        self.checker = Checker(config)
        self.running = False
        self.active_platforms = set()

    def start(self, platform=None):
        if platform:
            self.active_platforms.add(platform)
        self.running = True
        if not hasattr(self, 'thread') or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.hunt_loop, daemon=True)
            self.thread.start()
        return True

    def stop(self, platform=None):
        if platform:
            self.active_platforms.discard(platform)
            if not self.active_platforms:
                self.running = False
        else:
            self.active_platforms.clear()
            self.running = False
        return True

    def hunt_loop(self):
        while self.running:
            if not self.active_platforms:
                time.sleep(1)
                continue
                
            for platform in list(self.active_platforms):
                username = self.generator.generate(platform)
                if self.checker.check(username, platform):
                    self.send_result(username, platform)
            time.sleep(self.config.DELAY_BETWEEN_CHECKS)
    
    def send_result(self, username, platform):
        message = (
            f"🎉 **يوزر متاح!**\n"
            f"📌 **الموقع:** {platform.capitalize()}\n"
            f"🔖 **اليوزر:** @{username}\n"
            f"⏰ **الوقت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🔗 **رابط الحساب:**\n"
            f"https://{'instagram.com' if platform == 'instagram' else 't.me' if platform == 'telegram' else 'twitter.com' if platform == 'twitter' else 'snapchat.com/add' if platform == 'snapchat' else 'tiktok.com/@'}/{username}"
        )
        try:
            self.bot.send_message(self.config.CHANNEL_ID, message, parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Error sending message: {e}")

# =============== BOT COMMANDS ===============
config = Config()
bot = telebot.TeleBot(config.TOKEN)
hunter = Hunter(bot, config)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != config.ADMIN_ID:
        bot.reply_to(message, "❌ غير مصرح لك!")
        return
    
    hunter.start()
    bot.reply_to(message, "✅ تم تشغيل البوت على جميع المنصات!")

@bot.message_handler(commands=['stop'])
def stop(message):
    if message.from_user.id != config.ADMIN_ID:
        bot.reply_to(message, "❌ غير مصرح لك!")
        return
    
    hunter.stop()
    bot.reply_to(message, "🛑 تم إيقاف البوت على جميع المنصات!")

@bot.message_handler(commands=['telegram', 'instagram', 'twitter', 'snapchat', 'tiktok'])
def handle_platform(message):
    if message.from_user.id != config.ADMIN_ID:
        bot.reply_to(message, "❌ غير مصرح لك!")
        return
    
    platform = message.text[1:]  # إزالة علامة الـ /
    
    if platform in ['telegram', 'instagram', 'twitter', 'snapchat', 'tiktok']:
        if platform in hunter.active_platforms:
            hunter.stop(platform)
            bot.reply_to(message, f"⏸️ تم إيقاف الصيد على {platform.capitalize()}")
        else:
            hunter.start(platform)
            bot.reply_to(message, f"▶️ تم بدء الصيد على {platform.capitalize()}")
    else:
        bot.reply_to(message, "⚠️ أمر غير صحيح!")

@bot.message_handler(commands=['status'])
def status(message):
    if message.from_user.id != config.ADMIN_ID:
        bot.reply_to(message, "❌ غير مصرح لك!")
        return
    
    status_msg = "📊 حالة المنصات:\n"
    for platform in ['telegram', 'instagram', 'twitter', 'snapchat', 'tiktok']:
        status_msg += f"{platform.capitalize()}: {'🟢 نشط' if platform in hunter.active_platforms else '🔴 متوقف'}\n"
    
    bot.reply_to(message, status_msg)

@bot.message_handler(commands=['help'])
def help(message):
    help_text = """
⚡ أوامر البوت:
/start - بدء الصيد على جميع المنصات
/stop - إيقاف الصيد على جميع المنصات
/status - عرض حالة المنصات

🔧 أوامر المنصات (تشغيل/إيقاف):
/telegram - تيليجرام
/instagram - إنستجرام
/twitter - تويتر
/snapchat - سناب شات
/tiktok - تيك توك
"""
    bot.reply_to(message, help_text)

# =============== RUN BOT ===============
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Bot started...")
    bot.infinity_polling()