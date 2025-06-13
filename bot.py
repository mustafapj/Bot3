import telebot
import requests
import random
import string
import logging
import re
import concurrent.futures
from datetime import datetime

# Configuration
TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = "@yourchannel"
ADMIN_ID = YOUR_ADMIN_ID
MAX_WORKERS = 20  # Increased threads for ultra-fast checking
bot = telebot.TeleBot(TOKEN, threaded=True)

# Premium Patterns
PATTERNS = {
    'rare2': r'^[a-z]{2}$',          # ثنائي نادر (aa)
    'vip3': r'^[a-z]{3}$',           # ثلاثي فاخر (aaa)
    'gold4': r'^[a-z]{2}\d{2}$',     # رباعي ذهبي (aa11)
    'premium5': r'^[a-z]{2}\d[a-z]{2}$',  # خماسي مميز (aa1bb)
    'platinum': r'^[a-z]\d[a-z]\d$'  # بلاتينيوم (a1b2)
}

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('premium_hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PremiumHunter')

class EliteUsernameGenerator:
    @staticmethod
    def generate(pattern):
        """يولد يوزرات فاخرة حسب النمط المطلوب"""
        for _ in range(1000):  # محاولات توليد
            if pattern == 'rare2':
                username = random.choice('abcdejklmnpqrstuvwxyz') + random.choice('aeiou')
            elif pattern == 'vip3':
                username = ''.join(random.choice('aeiouxz') for _ in range(3))
            elif pattern == 'gold4':
                username = random.choice(string.ascii_lowercase)*2 + random.choice('13579')*2
            elif pattern == 'premium5':
                username = random.choice('xyz')*2 + random.choice('123') + random.choice('aeiou')*2
            elif pattern == 'platinum':
                username = random.choice('aeiou') + random.choice('123') + random.choice('aeiou') + random.choice('456')
            
            if re.match(PATTERNS[pattern], username):
                return username
        return None

class TurboScanner:
    @staticmethod
    def check(username):
        """فحص اليوزر على جميع المنصات بسرعة فائقة"""
        try:
            # Telegram Check
            tg = requests.get(f"https://t.me/{username}", timeout=5).text
            tg_status = 'available' if "You can contact" in tg else 'taken'
            
            # Instagram Check
            ig = requests.get(f"https://instagram.com/{username}", timeout=5)
            ig_status = 'available' if ig.status_code == 404 else 'taken'
            
            return {
                'username': username,
                'telegram': tg_status,
                'instagram': ig_status,
                'value': TurboScanner.estimate_value(username)
            }
        except Exception as e:
            logger.error(f"Scan error for @{username}: {e}")
            return None

    @staticmethod
    def estimate_value(username):
        """تقدير قيمة اليوزر للسوق السوداء"""
        length = len(username)
        rarity = 0
        
        # حساب الندرة
        if re.match(PATTERNS['rare2'], username):
            rarity = 90
        elif re.match(PATTERNS['vip3'], username):
            rarity = 70
        elif re.match(PATTERNS['gold4'], username):
            rarity = 50
        elif re.match(PATTERNS['premium5'], username):
            rarity = 40
        elif re.match(PATTERNS['platinum'], username):
            rarity = 60
        
        # عوامل القيمة
        vowels = sum(1 for c in username if c in 'aeiou')
        patterns = sum(1 for p in PATTERNS if re.match(PATTERNS[p], username))
        
        return (rarity + (vowels*5) + (patterns*10)) * length

class BusinessManager:
    @staticmethod
    def create_report(results):
        """تقرير احترافي مع تقييم مالي"""
        available = [r for r in results if r and any(r[p] == 'available' for p in ['telegram', 'instagram'])]
        taken = [r for r in results if r and r not in available]
        
        report = "💎 *تقرير اليوزرات الفاخرة*\n\n"
        
        if available:
            report += "🟣 **اليوزرات المتاحة للبيع**\n"
            for r in sorted(available, key=lambda x: -x['value']):
                platforms = []
                if r['telegram'] == 'available':
                    platforms.append(f"TG: ✅ [رابط](https://t.me/{r['username']})")
                if r['instagram'] == 'available':
                    platforms.append(f"IG: ✅ [رابط](https://instagram.com/{r['username']})")
                
                report += (
                    f"✨ @{r['username']}\n"
                    f"📊 القيمة: ${r['value']}\n"
                    f"{' | '.join(platforms)}\n"
                    f"────────────\n"
                )
        
        if taken:
            report += "\n🔴 **اليوزرات المحجوزة**\n"
            for r in taken[:10]:  # عرض أول 10 فقط لتجنب التطويل
                report += f"@{r['username']} (TG: {'✅' if r['telegram'] == 'available' else '❌'} | IG: {'✅' if r['instagram'] == 'available' else '❌'})\n"
        
        report += f"\n💰 *إجمالي اليوزرات القابلة للبيع: {len(available)}*"
        return report

@bot.message_handler(commands=['hunt_vip'])
def hunt_vip(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        pattern = message.text.split()[1] if len(message.text.split()) > 1 else 'rare2'
        count = int(message.text.split()[2]) if len(message.text.split()) > 2 else 20
    except:
        bot.reply_to(message, "⚡ استخدام: /hunt_vip [النوع] [العدد]\n\nأنواع VIP:\nrare2, vip3, gold4, premium5, platinum")
        return
    
    bot.reply_to(message, f"⚡ بدأ الصيد الذكي لـ {count} يوزر {pattern}...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        usernames = [EliteUsernameGenerator.generate(pattern) for _ in range(count)]
        results = list(executor.map(TurboScanner.check, usernames))
    
    report = BusinessManager.create_report(results)
    bot.send_message(CHANNEL_ID, report, parse_mode="Markdown", disable_web_page_preview=True)
    
    # إرسال أفضل 3 يوزرات للمشرف
    top_usernames = sorted([r for r in results if r and any(r[p] == 'available' for p in ['telegram', 'instagram'])], 
                          key=lambda x: -x['value'])[:3]
    if top_usernames:
        alert = "🚀 *أفضل اليوزرات المتاحة*\n"
        for idx, r in enumerate(top_usernames, 1):
            alert += f"{idx}. @{r['username']} (القيمة: ${r['value']})\n"
        bot.send_message(ADMIN_ID, alert, parse_mode="Markdown")

if __name__ == '__main__':
    logger.info("💎 Starting Premium Username Hunter")
    bot.infinity_polling()