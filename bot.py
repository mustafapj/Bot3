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
        
        self.REQUEST_TIMEOUT = 15
        self.DELAY_BETWEEN_CHECKS = 3
        
        self.PATTERNS = {
            "instagram": [3, 4, 5],
            "telegram": [5, 6, 7],
            "twitter": [4, 5, 6],
            "snapchat": [4, 5, 6],
            "tiktok": [5, 6, 7]
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

# =============== CHECKER (مكتمل) ===============
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
            if response.status_code == 404:
                return True
            elif response.status_code == 200:
                try:
                    data = response.json()
                    return 'graphql' not in data or 'user' not in data['graphql']
                except:
                    return False
            return False
        except Exception as e:
            logging.error(f"Instagram check error: {str(e)}")
            return False

    def check_telegram(self, username):
        try:
            url = f"https://t.me/{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
            unavailable_markers = [
                "tgme_username_link",
                "You can contact",
                "Send Message"
            ]
            return not any(marker in response.text for marker in unavailable_markers)
        except Exception as e:
            logging.error(f"Telegram check error: {str(e)}")
            return False

    def check_twitter(self, username):
        try:
            url = f"https://twitter.com/{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
            return response.status_code in [404, 302]
        except Exception as e:
            logging.error(f"Twitter check error: {str(e)}")
            return False

    def check_snapchat(self, username):
        try:
            url = f"https://www.snapchat.com/add/{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
            return response.status_code == 404
        except Exception as e:
            logging.error(f"Snapchat check error: {str(e)}")
            return False

    def check_tiktok(self, username):
        try:
            url = f"https://www.tiktok.com/@{username}"
            response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, allow_redirects=False)
            return response.status_code == 404
        except Exception as e:
            logging.error(f"TikTok check error: {str(e)}")
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

# ... [بقية الكود بدون تغيير] ...