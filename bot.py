
import telebot
import requests 
import random 
import string
import logging 
import re import time 
import threading 
import json from datetime 
import datetime

=============== CONFIGURATION ===============

class Config: def init(self): self.TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U" self.CHANNEL_ID = "@mmmmmuyter" self.ADMIN_ID = 5367866254 self.MAX_THREADS = 10 self.REQUEST_TIMEOUT = 7 self.BREAK_DURATION = 120  # بعد كل 100 عملية فحص self.PROXY_ENABLED = True self.PROXY_LIST = [ 'http://proxy1.example.com:8080', 'http://proxy2.example.com:8080' ]

self.IG_PATTERNS = {
        'ig2': r'^[a-z]{2}$',
        'ig3': r'^[a-z]{3}$',
        'ig4': r'^[a-z]{3}\d$'
    }

    self.TG_PATTERNS = {
        'tg5': r'^[a-z]{5}$',
        'tg6': r'^[a-z]{6}$',
        'tg7': r'^[a-z]{7}$'
    }

=============== GENERATOR ===============

class UsernameGenerator: def init(self, config): self.config = config self.letters = 'abcdefghijklmnopqrstuvwxyz'

def generate(self, pattern_type):
    if pattern_type.startswith('ig'):
        length = int(pattern_type[2])
        if pattern_type == 'ig4':
            return ''.join(random.choices(self.letters, k=3)) + random.choice('0123456789')
        return ''.join(random.choices(self.letters, k=length))
    elif pattern_type.startswith('tg'):
        length = int(pattern_type[2])
        return ''.join(random.choices('aeioubcdfghklmnprstxz', k=length))

=============== CHECKER ===============

class UsernameChecker: def init(self, config): self.config = config self.session = requests.Session() self.session.headers.update({ 'User-Agent': 'Mozilla/5.0' }) self.counter = 0

def check_instagram(self, username):
    try:
        url = f"https://www.instagram.com/{username}/"
        res = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, proxies=self._proxy())
        return res.status_code == 404
    except:
        return False

def check_telegram(self, username):
    try:
        url = f"https://t.me/{username}"
        res = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, proxies=self._proxy())
        return res.status_code == 404 or "This username isn't available" not in res.text
    except:
        return False

def _proxy(self):
    if self.config.PROXY_ENABLED and self.config.PROXY_LIST:
        return {'http': random.choice(self.config.PROXY_LIST)}
    return None

=============== HUNTER ===============

class Hunter: def init(self, config, bot): self.config = config self.bot = bot self.generator = UsernameGenerator(config) self.checker = UsernameChecker(config) self.active = False

def start(self):
    if not self.active:
        self.active = True
        threading.Thread(target=self._hunt_loop, daemon=True).start()
        return True
    return False

def stop(self):
    self.active = False
    return True

def _hunt_loop(self):
    while self.active:
        try:
            for pattern_dict, checker in [
                (self.config.IG_PATTERNS, self.checker.check_instagram),
                (self.config.TG_PATTERNS, self.checker.check_telegram)
            ]:
                for _ in range(100):
                    if not self.active:
                        return

                    pattern = random.choice(list(pattern_dict.keys()))
                    username = self.generator.generate(pattern)

                    available = checker(username)
                    if available:
                        msg = f"✅ Username Available\n@{username}\nPattern: {pattern}\n🔗 https://t.me/{username}"
                        self.bot.send_message(self.config.CHANNEL_ID, msg)
                    
                    self.checker.counter += 1
                    time.sleep(random.uniform(1.0, 2.0))

                self.bot.send_message(self.config.CHANNEL_ID, f"⏳ استراحة مؤقتة لمدة {self.config.BREAK_DURATION} ثانية...")
                time.sleep(self.config.BREAK_DURATION)

        except Exception as e:
            logging.error(f"Error: {str(e)}")
            time.sleep(10)

=============== BOT SETUP ===============

config = Config() bot = telebot.TeleBot(config.TOKEN) hunter = Hunter(config, bot)

logging.basicConfig(level=logging.INFO)

@bot.message_handler(commands=['start']) def start(message): if message.from_user.id == config.ADMIN_ID: started = hunter.start() bot.reply_to(message, "✅ بدأ الفحص." if started else "⚠️ يعمل بالفعل.") else: bot.reply_to(message, "🚫 غير مصرح")

@bot.message_handler(commands=['stop']) def stop(message): if message.from_user.id == config.ADMIN_ID: hunter.stop() bot.reply_to(message, "🛑 تم إيقاف الفحص.") else: bot.reply_to(message, "🚫 غير مصرح")

if name == 'main': logging.info("👾 Bot is Running...") bot.infinity_polling()

