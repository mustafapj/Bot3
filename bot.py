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
        self.REQUEST_TIMEOUT = 5
        self.DELAY_BETWEEN_CHECKS = 1  # تأخير بين الفحوصات (ثانية)
        
        # أنماط اليوزرات لكل موقع
        self.PATTERNS = {
            "instagram": [2, 3, 4],  # ثنائي، ثلاثي، رباعي
            "telegram": [5, 6, 7],    # خماسي، سداسي، سباعي
            "twitter": [3, 4, 5],     # ثلاثي، رباعي، خماسي
            "snapchat": [3, 4, 5],    # ثلاثي، رباعي، خماسي
            "tiktok": [4, 5, 6]       # رباعي، خماسي، سداسي
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

# =============== CHECKER ===============
class Checker:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers = {"User-Agent": "Mozilla/5.0"}

    def check(self, username, platform):
        try:
            if platform == "instagram":
                url = f"https://instagram.com/{username}"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
                return response.status_code == 404
            
            elif platform == "telegram":
                url = f"https://t.me/{username}"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
                return "You can contact" not in response.text
            
            elif platform == "twitter":
                url = f"https://twitter.com/{username}"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
                return response.status_code == 404
            
            elif platform == "snapchat":
                url = f"https://snapchat.com/add/{username}"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
                return response.status_code == 404
            
            elif platform == "tiktok":
                url = f"https://tiktok.com/@{username}"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
                return response.status_code == 404
            
            return False
        except:
            return False

# =============== HUNTER ===============
class Hunter:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.generator = UsernameGenerator(config)
        self.checker = Checker(config)
        self.running = False
    
    def start(self):
        self.running = True
        threading.Thread(target=self.hunt_loop, daemon=True).start()
    
    def stop(self):
        self.running = False
    
    def hunt_loop(self):
        while self.running:
            for platform in self.config.PATTERNS:
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

# =============== أوامر البوت ===============
config = Config()
bot = telebot.TeleBot(config.TOKEN)
hunter = Hunter(bot, config)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != config.ADMIN_ID:
        bot.reply_to(message, "❌ **غير مصرح لك!**")
        return
    
    hunter.start()
    bot.reply_to(message, "✅ **تم تشغيل البوت! اليوزرات ستظهر مباشرة في القناة.**")

@bot.message_handler(commands=['stop'])
def stop(message):
    if message.from_user.id != config.ADMIN_ID:
        bot.reply_to(message, "❌ **غير مصرح لك!**")
        return
    
    hunter.stop()
    bot.reply_to(message, "🛑 **تم إيقاف البوت!**")

# =============== تشغيل البوت ===============
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Bot started...")
    bot.infinity_polling()