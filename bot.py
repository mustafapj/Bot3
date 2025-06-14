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
        
        self.REQUEST_TIMEOUT = 10  # زيادة المهلة
        self.DELAY_BETWEEN_CHECKS = 2  # زيادة التأخير
        
        self.PATTERNS = {
            "instagram": [2, 3, 4],
            "telegram": [5, 6, 7],
            "twitter": [3, 4, 5],
            "snapchat": [3, 4, 5],
            "tiktok": [4, 5, 6]
        }

# =============== CHECKER FIXED ===============
class Checker:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }

    def check(self, username, platform):
        try:
            if platform == "instagram":
                url = f"https://www.instagram.com/{username}/?__a=1"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
                return response.status_code == 404
            
            elif platform == "telegram":
                url = f"https://t.me/{username}"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT)
                return "tgme_username_link" not in response.text
            
            elif platform == "twitter":
                url = f"https://twitter.com/{username}"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT, 
                                          allow_redirects=False)
                return response.status_code in [404, 302]
            
            elif platform == "snapchat":
                url = f"https://www.snapchat.com/add/{username}"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT,
                                          allow_redirects=False)
                return response.status_code == 404
            
            elif platform == "tiktok":
                url = f"https://www.tiktok.com/@{username}"
                response = self.session.get(url, timeout=self.config.REQUEST_TIMEOUT,
                                          allow_redirects=False)
                return response.status_code == 404
            
            return False
        except Exception as e:
            logging.error(f"Error checking {platform}: {str(e)}")
            return False

# ... [بقية الكود كما هو بدون تغيير] ...