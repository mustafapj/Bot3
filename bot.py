import telebot
import requests
import random
import string
import logging
import re
import time
import threading
from datetime import datetime

# Configuration
TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
CHANNEL_ID = "@mmmmmuyter"
ADMIN_ID = 5367866254
bot = telebot.TeleBot(TOKEN)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('premium_hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PremiumHunterPro')

# Premium Patterns
PATTERNS = {
    'rare2': r'^[a-z]{2}$',          # ثنائي نادر (aa)
    'gold2': r'^[a-z]\d$',           # شبه ثنائي (a1)
    'vip3': r'^[a-z]{3}$',           # ثلاثي فاخر (aaa)
    'platinum3': r'^[a-z]{2}\d$',    # شبه ثلاثي (aa1)
    'elite4': r'^[a-z]{2}\d{2}$',    # رباعي ذهبي (aa11)
    'premium5': r'^[a-z]{2}\d[a-z]{2}$'  # خماسي مميز (aa1bb)
}

class SmartGenerator:
    @staticmethod
    def generate(pattern):
        """يولد يوزرات ذكية حسب النمط"""
        try:
            if pattern == 'rare2':
                return random.choice('aeioux') + random.choice('bcdfghjklmnpqrstvwxyz')
            elif pattern == 'gold2':
                return random.choice('aeioux') + random.choice('123456789')
            elif pattern == 'vip3':
                return ''.join(random.choice('aeioux') for _ in range(3))
            elif pattern == 'platinum3':
                return random.choice('aeioux')*2 + random.choice('123456789')
            elif pattern == 'elite4':
                return random.choice('aeioux')*2 + random.choice('13579')*2
            elif pattern == 'premium5':
                return random.choice('aeioux')*2 + random.choice('123') + random.choice('aeioux')*2
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None

class TurboScanner:
    @staticmethod
    def check(username):
        """فحص اليوزر بذكاء"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Telegram Check
            tg = requests.get(
                f"https://t.me/{username}",
                headers=headers,
                timeout=10
            ).text
            tg_status = 'available' if "You can contact" in tg else 'taken'
            
            # Instagram Check
            ig = requests.get(
                f"https://instagram.com/{username}",
                headers=headers,
                timeout=10,
                allow_redirects=False
            )
            ig_status = 'available' if ig.status_code == 404 else 'taken'
            
            return {
                'username': username,
                'telegram': tg_status,
                'instagram': ig_status,
                'value': TurboScanner.calculate_value(username),
                'time': datetime.now().strftime("%H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Scan error: {e}")
            return None

    @staticmethod
    def calculate_value(username):
        """حساب قيمة اليوزر"""
        length = len(username)
        pattern_score = {
            'rare2': 100, 'gold2': 80, 'vip3': 70,
            'platinum3': 60, 'elite4': 50, 'premium5': 40
        }.get(next((p for p in PATTERNS if re.match(PATTERNS[p], username)), ''), 0)
        
        vowels = sum(1 for c in username if c in 'aeiou')
        return (pattern_score + vowels * 5) * (10 - length)

class HuntingEngine:
    def __init__(self):
        self.is_active = False
        self.session_count = 0

    def start_hunting(self):
        self.is_active = True
        threading.Thread(target=self._hunt_loop, daemon=True).start()

    def _hunt_loop(self):
        while self.is_active:
            try:
                # مرحلة الصيد النشط (50 يوزر)
                self.session_count += 1
                logger.info(f"🚀 بدأت جلسة الصيد #{self.session_count}")
                
                all_results = []
                for i in range(50):
                    if not self.is_active:
                        break
                        
                    # توليد يوزر عشوائي من أنماط مختلفة
                    pattern = random.choice(list(PATTERNS.keys()))
                    username = SmartGenerator.generate(pattern)
                    
                    if username:
                        result = TurboScanner.check(username)
                        if result:
                            all_results.append(result)
                            self._process_result(result)
                    
                    time.sleep(1)  # تأخير بين كل يوزر
                
                # إرسال التقرير النهائي
                self._send_summary(all_results)
                
                # استراحة 5 دقائق
                if self.is_active:
                    logger.info("⏳ استراحة لمدة 5 دقائق...")
                    time.sleep(300)
                    
            except Exception as e:
                logger.error(f"Error in hunt loop: {e}")
                time.sleep(30)

    def _process_result(self, result):
        """معالجة النتائج الفورية"""
        if result['telegram'] == 'available' or result['instagram'] == 'available':
            report = (
                f"✨ **يوزر متاح!**\n"
                f"🔹 `@{result['username']}`\n"
                f"🏷️ النمط: {next(p for p in PATTERNS if re.match(PATTERNS[p], result['username']))}\n"
                f"💰 القيمة: ${result['value']}\n"
                f"⏰ الوقت: {result['time']}\n"
                f"📱 تليجرام: {'🟢' if result['telegram'] == 'available' else '🔴'}\n"
                f"📷 إنستجرام: {'🟢' if result['instagram'] == 'available' else '🔴'}"
            )
            bot.send_message(CHANNEL_ID, report, parse_mode="Markdown")

    def _send_summary(self, results):
        """إرسال ملخص الجلسة"""
        available = [r for r in results if r['telegram'] == 'available' or r['instagram'] == 'available']
        
        summary = (
            f"📊 **ملخص جلسة الصيد #{self.session_count}**\n"
            f"🔢 عدد اليوزرات المفحوصة: {len(results)}\n"
            f"💎 اليوزرات المتاحة: {len(available)}\n"
            f"🏆 أفضل يوزر: @{max(results, key=lambda x: x['value'])['username']} (${max(r['value'] for r in results)})\n"
            f"⏱️ المدة التالية: 5 دقائق استراحة"
        )
        bot.send_message(CHANNEL_ID, summary, parse_mode="Markdown")

# Bot Commands
hunter = HuntingEngine()

@bot.message_handler(commands=['start_hunt'])
def start_hunting(message):
    if message.from_user.id == ADMIN_ID:
        if not hunter.is_active:
            hunter.start_hunting()
            bot.reply_to(message, "🎯 بدأ الصيد الذكي! (50 يوزر / 5 دقائق استراحة)")
        else:
            bot.reply_to(message, "⚠️ الصيد يعمل بالفعل!")
    else:
        bot.reply_to(message, "⛔ ليس لديك صلاحية!")

@bot.message_handler(commands=['stop_hunt'])
def stop_hunting(message):
    if message.from_user.id == ADMIN_ID:
        if hunter.is_active:
            hunter.is_active = False
            bot.reply_to(message, "🛑 تم إيقاف الصيد!")
        else:
            bot.reply_to(message, "⚠️ الصيد غير نشط بالفعل!")
    else:
        bot.reply_to(message, "⛔ ليس لديك صلاحية!")

if __name__ == '__main__':
    logger.info("🔥 البوت جاهز! أرسل /start_hunt للبدء")
    bot.infinity_polling()