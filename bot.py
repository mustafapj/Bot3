import telebot
import requests
import random
import string
import logging
import re
import time
import threading
import json
from datetime import datetime

class Config:
    def __init__(self):
        self.TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
        self.CHANNEL_ID = "@mmmmmuyter"
        self.ADMIN_ID = 5367866254
        self.MAX_THREADS = 10
        self.REQUEST_TIMEOUT = 7
        self.HUNT_BATCH_SIZE = 100
        self.BREAK_DURATION = 120
        self.PATTERNS = {
            'rare2': r'^[a-z]{2}$',
            'gold2': r'^[a-z]\d$',
            'vip3': r'^[a-z]{3}$',
            'platinum3': r'^[a-z]{2}\d$',
            'elite4': r'^[a-z]{2}\d{2}$',
            'premium5': r'^[a-z]{2}\d[a-z]{2}$'
        }
        self.PROXY_ENABLED = False
        self.PROXY_LIST = []
        self.MIN_PREDICTION_CONFIDENCE = 0.7

class UltimateGenerator:
    def __init__(self, config):
        self.config = config
        self.char_sets = {
            'vowels': 'aeiou',
            'consonants': 'bcdfghjklmnpqrstvwxyz',
            'digits': '123456789',
            'premium': 'aeiouxz'
        }
        self.common_usernames = ['admin', 'user', 'owner', 'official', 'test', 'web', 'mail', 'root', 'support', 'info', 'account', 'service']
    
    def generate(self, pattern_type):
        for _ in range(100):
            username = None
            if pattern_type == 'rare2':
                if random.choice([True, False]):
                    username = random.choice(self.char_sets['vowels']) + random.choice(self.char_sets['consonants'])
                else:
                    username = random.choice(self.char_sets['consonants']) + random.choice(self.char_sets['vowels'])
            elif pattern_type == 'gold2':
                username = random.choice(self.char_sets['premium']) + random.choice(self.char_sets['digits'][::2])
            elif pattern_type == 'vip3':
                username = ''.join(random.choice(self.char_sets['premium']) for _ in range(3))
            elif pattern_type == 'platinum3':
                username = random.choice(self.char_sets['premium']) * 2 + random.choice(self.char_sets['digits'])
            elif pattern_type == 'elite4':
                username = random.choice(self.char_sets['premium']) * 2 + random.choice(self.char_sets['digits'][::2]) * 2
            elif pattern_type == 'premium5':
                username = random.choice(self.char_sets['premium']) * 2 + random.choice(self.char_sets['digits']) + random.choice(self.char_sets['premium']) * 2
            if username and re.match(self.config.PATTERNS[pattern_type], username) and username not in self.common_usernames:
                return username
        return None

class AdvancedChecker:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def check(self, username):
        try:
            if not self._quick_check(username):
                return {'status': 'taken', 'source': 'telegram'}
            ig_status = self._check_instagram(username)
            if ig_status != 'available':
                return {'status': 'taken', 'source': 'instagram'}
            tg_status = self._detailed_telegram_check(username)
            if tg_status != 'available':
                return {'status': 'taken', 'source': 'telegram'}
            return {'status': 'available', 'source': 'both'}
        except Exception as e:
            logging.error(f"Check failed for @{username}: {str(e)}")
            return {'status': 'error', 'details': str(e)}
    
    def _quick_check(self, username):
        try:
            response = self.session.head(
                f"https://t.me/{username}",
                timeout=self.config.REQUEST_TIMEOUT,
                proxies=self._get_proxy()
            )
            return response.status_code == 404
        except:
            return True
    
    def _check_instagram(self, username):
        try:
            response = self.session.get(
                f"https://www.instagram.com/{username}",
                timeout=self.config.REQUEST_TIMEOUT,
                proxies=self._get_proxy(),
                allow_redirects=False
            )
            return 'available' if response.status_code == 404 else 'taken'
        except:
            return 'error'
    
    def _detailed_telegram_check(self, username):
        try:
            response = self.session.get(
                f"https://t.me/{username}",
                timeout=self.config.REQUEST_TIMEOUT,
                proxies=self._get_proxy()
            )
            return 'available' if "You can contact" in response.text else 'taken'
        except:
            return 'error'
    
    def _get_proxy(self):
        if self.config.PROXY_ENABLED and self.config.PROXY_LIST:
            return {'http': random.choice(self.config.PROXY_LIST)}
        return None

class AIPredictor:
    def __init__(self, config):
        self.config = config
        self.pattern_weights = {
            'rare2': 0.95,
            'gold2': 0.85,
            'vip3': 0.75,
            'platinum3': 0.70,
            'elite4': 0.65,
            'premium5': 0.60
        }
    
    def predict(self, username):
        pattern_score = next((self.pattern_weights[p] for p in self.config.PATTERNS if re.match(self.config.PATTERNS[p], username)), 0.5)
        vowels = sum(1 for c in username if c in 'aeiou')
        vowel_ratio = vowels / len(username)
        complexity = 0.3 + (0.7 * vowel_ratio)
        return (pattern_score * 0.6) + (complexity * 0.4)

class HuntingEngine:
    def __init__(self, config):
        self.config = config
        self.generator = UltimateGenerator(config)
        self.checker = AdvancedChecker(config)
        self.predictor = AIPredictor(config)
        self.is_active = False
        self.session_count = 0
        self.stats = {
            'total_generated': 0,
            'available_found': 0,
            'last_available': None
        }
    
    def start(self):
        if not self.is_active:
            self.is_active = True
            threading.Thread(target=self._hunt_loop, daemon=True).start()
            return True
        return False
    
    def stop(self):
        if self.is_active:
            self.is_active = False
            return True
        return False
    
    def _hunt_loop(self):
        while self.is_active:
            try:
                self.session_count += 1
                batch_results = self._run_hunt_batch()
                self._process_results(batch_results)
                if self.is_active:
                    time.sleep(self.config.BREAK_DURATION)
            except Exception as e:
                logger.error(f"Hunt loop error: {str(e)}")
                time.sleep(30)
    
    def _run_hunt_batch(self):
        results = []
        for _ in range(self.config.HUNT_BATCH_SIZE):
            if not self.is_active:
                break
            pattern = random.choice(list(self.config.PATTERNS.keys()))
            username = self.generator.generate(pattern)
            self.stats['total_generated'] += 1
            if not username:
                continue
            if self.predictor.predict(username) < self.config.MIN_PREDICTION_CONFIDENCE:
                continue
            result = self.checker.check(username)
            if result['status'] == 'available':
                results.append({
                    'username': username,
                    'pattern': pattern,
                    'source': result['source'],
                    'time': datetime.now().strftime("%H:%M:%S")
                })
            time.sleep(1)
        return results
    
    def _process_results(self, results):
        if not results:
            return
        self.stats['available_found'] += len(results)
        self.stats['last_available'] = datetime.now()
        for result in results:
            self._send_alert(result)
        self._send_summary(len(results))
    
    def _send_alert(self, result):
        message = (
            f"🎉 Username Available!\n\n"
            f"✨ @{result['username']}\n"
            f"🏷️ Pattern: {result['pattern']}\n"
            f"🕒 Time: {result['time']}\n"
            f"🔍 Verified on: {result['source']}\n\n"
            f"https://t.me/{result['username']} | https://instagram.com/{result['username']}"
        )
        try:
            bot.send_message(
                self.config.CHANNEL_ID,
                message,
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
    
    def _send_summary(self, available_count):
        summary = (
            f"📊 Hunt Session #{self.session_count} Summary\n\n"
            f"🔢 Usernames checked: {self.config.HUNT_BATCH_SIZE}\n"
            f"💎 Available found: {available_count}\n"
            f"🛑 Next hunt in: {self.config.BREAK_DURATION // 60} minutes"
        )
        try:
            bot.send_message(
                self.config.CHANNEL_ID,
                summary
            )
        except Exception as e:
            logger.error(f"Failed to send summary: {str(e)}")

config = Config()
bot = telebot.TeleBot(config.TOKEN)
hunter = HuntingEngine(config)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('premium_hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('UltimateHunter')

@bot.message_handler(commands=['start'])
def start_bot(message):
    if message.from_user.id == config.ADMIN_ID:
        if hunter.start():
            bot.reply_to(message, "Ultimate Hunter Activated!")
        else:
            bot.reply_to(message, "Hunter is already running!")
    else:
        bot.reply_to(message, "Unauthorized!")

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    if message.from_user.id == config.ADMIN_ID:
        if hunter.stop():
            bot.reply_to(message, "Hunter Stopped!")
        else:
            bot.reply_to(message, "Hunter isn't running!")
    else:
        bot.reply_to(message, "Unauthorized!")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id == config.ADMIN_ID:
        stats = hunter.stats
        last = stats['last_available'].strftime("%Y-%m-%d %H:%M") if stats['last_available'] else "Never"
        report = (
            f"Hunter Statistics\n\n"
            f"Total Generated: {stats['total_generated']}\n"
            f"Available Found: {stats['available_found']}\n"
            f"Last Available: {last}\n"
            f"Current Session: #{hunter.session_count}"
        )
        bot.reply_to(message, report)
    else:
        bot.reply_to(message, "Unauthorized!")

if __name__ == '__main__':
    logger.info("Ultimate Username Hunter Bot Starting...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")