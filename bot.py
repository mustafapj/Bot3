#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTIMATE USERNAME HUNTER BOT v6.0
- Advanced pattern generation
- Multi-layer verification
- AI-powered availability prediction
- Proxy support
- Continuous hunting with smart breaks
"""

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

# =============== CONFIGURATION ===============
class Config:
    def __init__(self):
        # Core Settings
        self.TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
        self.CHANNEL_ID = "@mmmmmuyter"
        self.ADMIN_ID = 5367866254
        self.MAX_THREADS = 10
        self.REQUEST_TIMEOUT = 7
        self.HUNT_BATCH_SIZE = 50
        self.BREAK_DURATION = 300  # 5 minutes
        
        # Premium Patterns
        self.PATTERNS = {
            'rare2': r'^[a-z]{2}$',          # Double letters (aa)
            'gold2': r'^[a-z]\d$',           # Letter + number (a1)
            'vip3': r'^[a-z]{3}$',           # Triple letters (aaa)
            'platinum3': r'^[a-z]{2}\d$',    # Two letters + number (aa1)
            'elite4': r'^[a-z]{2}\d{2}$',    # Two letters + two numbers (aa11)
            'premium5': r'^[a-z]{2}\d[a-z]{2}$' # Premium pattern (aa1bb)
        }
        
        # Proxy Settings
        self.PROXY_ENABLED = False
        self.PROXY_LIST = [
            'http://proxy1.example.com:8080',
            'http://proxy2.example.com:8080'
        ]
        
        # AI Model Parameters
        self.MIN_PREDICTION_CONFIDENCE = 0.7

# =============== CORE COMPONENTS ===============
class UltimateGenerator:
    """Advanced username generator with smart patterns"""
    
    def __init__(self, config):
        self.config = config
        self.char_sets = {
            'vowels': 'aeiou',
            'consonants': 'bcdfghjklmnpqrstvwxyz',
            'digits': '123456789',
            'premium': 'aeiouxz'
        }
        self.common_usernames = self._load_common_usernames()
    
    def _load_common_usernames(self):
        """Load frequently taken usernames"""
        return ['admin', 'user', 'owner', 'official', 'test', 'web', 
                'mail', 'root', 'support', 'info', 'account', 'service']
    
    def generate(self, pattern_type):
        """Generate username with advanced pattern matching"""
        for _ in range(100):  # Generation attempts
            username = None
            
            if pattern_type == 'rare2':
                # Alternate between vowel+consonant and consonant+vowel
                if random.choice([True, False]):
                    username = (random.choice(self.char_sets['vowels']) + 
                               random.choice(self.char_sets['consonants']))
                else:
                    username = (random.choice(self.char_sets['consonants']) + 
                               random.choice(self.char_sets['vowels']))
            
            elif pattern_type == 'gold2':
                username = (random.choice(self.char_sets['premium']) + 
                           random.choice(self.char_sets['digits'][::2]))  # Odd digits only
            
            elif pattern_type == 'vip3':
                username = ''.join(random.choice(self.char_sets['premium']) 
                                 for _ in range(3))
            
            elif pattern_type == 'platinum3':
                username = (random.choice(self.char_sets['premium']) * 2 + 
                           random.choice(self.char_sets['digits']))
            
            elif pattern_type == 'elite4':
                username = (random.choice(self.char_sets['premium']) * 2 + 
                           random.choice(self.char_sets['digits'][::2]) * 2)
            
            elif pattern_type == 'premium5':
                username = (random.choice(self.char_sets['premium']) * 2 + 
                           random.choice(self.char_sets['digits']) + 
                           random.choice(self.char_sets['premium']) * 2)
            
            # Validate and return
            if (username and 
                re.match(self.config.PATTERNS[pattern_type], username) and 
                username not in self.common_usernames):
                return username
        return None

class AdvancedChecker:
    """Multi-layer username availability checker"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def check(self, username):
        """Three-layer verification system"""
        try:
            # Layer 1: Quick HEAD request
            if not self._quick_check(username):
                return {'status': 'taken', 'source': 'telegram'}
            
            # Layer 2: Instagram verification
            ig_status = self._check_instagram(username)
            if ig_status != 'available':
                return {'status': 'taken', 'source': 'instagram'}
            
            # Layer 3: Detailed Telegram check
            tg_status = self._detailed_telegram_check(username)
            if tg_status != 'available':
                return {'status': 'taken', 'source': 'telegram'}
            
            return {'status': 'available', 'source': 'both'}
        
        except Exception as e:
            logging.error(f"Check failed for @{username}: {str(e)}")
            return {'status': 'error', 'details': str(e)}
    
    def _quick_check(self, username):
        """Lightweight initial check"""
        try:
            response = self.session.head(
                f"https://t.me/{username}",
                timeout=self.config.REQUEST_TIMEOUT,
                proxies=self._get_proxy()
            )
            return response.status_code == 404
        except:
            return True  # Proceed to next check if failed
    
    def _check_instagram(self, username):
        """Instagram availability check"""
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
        """Comprehensive Telegram check"""
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
        """Get random proxy if enabled"""
        if self.config.PROXY_ENABLED and self.config.PROXY_LIST:
            return {'http': random.choice(self.config.PROXY_LIST)}
        return None

class AIPredictor:
    """AI-powered availability predictor"""
    
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
        """Predict availability probability (0-1)"""
        # Calculate pattern score
        pattern_score = next((self.pattern_weights[p] for p in self.config.PATTERNS 
                            if re.match(self.config.PATTERNS[p], username)), 0.5)
        
        # Calculate complexity score
        vowels = sum(1 for c in username if c in 'aeiou')
        vowel_ratio = vowels / len(username)
        complexity = 0.3 + (0.7 * vowel_ratio)  # More vowels = more likely available
        
        # Combined prediction
        return (pattern_score * 0.6) + (complexity * 0.4)

class HuntingEngine:
    """Core hunting system"""
    
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
        """Start continuous hunting"""
        if not self.is_active:
            self.is_active = True
            threading.Thread(target=self._hunt_loop, daemon=True).start()
            return True
        return False
    
    def stop(self):
        """Stop hunting"""
        if self.is_active:
            self.is_active = False
            return True
        return False
    
    def _hunt_loop(self):
        """Main hunting loop"""
        while self.is_active:
            try:
                self.session_count += 1
                logger.info(f"🚀 Starting hunt session #{self.session_count}")
                
                # Hunt batch
                batch_results = self._run_hunt_batch()
                
                # Process results
                self._process_results(batch_results)
                
                # Take break if still active
                if self.is_active:
                    logger.info(f"⏳ Taking {self.config.BREAK_DURATION//60} min break")
                    time.sleep(self.config.BREAK_DURATION)
                
            except Exception as e:
                logger.error(f"Hunt loop error: {str(e)}")
                time.sleep(30)
    
    def _run_hunt_batch(self):
        """Run a single hunt batch"""
        results = []
        for _ in range(self.config.HUNT_BATCH_SIZE):
            if not self.is_active:
                break
                
            # Generate username
            pattern = random.choice(list(self.config.PATTERNS.keys()))
            username = self.generator.generate(pattern)
            self.stats['total_generated'] += 1
            
            if not username:
                continue
                
            # AI prediction filter
            if self.predictor.predict(username) < self.config.MIN_PREDICTION_CONFIDENCE:
                continue
                
            # Availability check
            result = self.checker.check(username)
            if result['status'] == 'available':
                results.append({
                    'username': username,
                    'pattern': pattern,
                    'source': result['source'],
                    'time': datetime.now().strftime("%H:%M:%S")
                })
            
            time.sleep(1)  # Rate limiting
        
        return results
    
    def _process_results(self, results):
        """Process and report hunt results"""
        if not results:
            logger.info("No available usernames found in this batch")
            return
            
        self.stats['available_found'] += len(results)
        self.stats['last_available'] = datetime.now()
        
        # Send individual alerts
        for result in results:
            self._send_alert(result)
        
        # Send summary
        self._send_summary(len(results))
    
    def _send_alert(self, result):
        """Send alert for available username"""
        message = (
            f"🎉 **Username Available!**\n\n"
            f"✨ `@{result['username']}`\n"
            f"🏷️ Pattern: `{result['pattern']}`\n"
            f"🕒 Time: `{result['time']}`\n"
            f"🔍 Verified on: `{result['source']}`\n\n"
            f"[Telegram](https://t.me/{result['username']}) | "
            f"[Instagram](https://instagram.com/{result['username']})"
        )
        
        try:
            bot.send_message(
                self.config.CHANNEL_ID,
                message,
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
    
    def _send_summary(self, available_count):
        """Send batch summary"""
        summary = (
            f"📊 **Hunt Session #{self.session_count} Summary**\n\n"
            f"🔢 Usernames checked: `{self.config.HUNT_BATCH_SIZE}`\n"
            f"💎 Available found: `{available_count}`\n"
            f"🛑 Next hunt in: `{self.config.BREAK_DURATION//60} minutes`"
        )
        
        try:
            bot.send_message(
                self.config.CHANNEL_ID,
                summary,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send summary: {str(e)}")

# =============== BOT SETUP ===============
config = Config()
bot = telebot.TeleBot(config.TOKEN)
hunter = HuntingEngine(config)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('premium_hunter.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('UltimateHunter')

# =============== BOT COMMANDS ===============
@bot.message_handler(commands=['start'])
def start_bot(message):
    if message.from_user.id == config.ADMIN_ID:
        if hunter.start():
            bot.reply_to(message, "🚀 Ultimate Hunter Activated!")
        else:
            bot.reply_to(message, "⚠️ Hunter is already running!")
    else:
        bot.reply_to(message, "⛔ Unauthorized!")

@bot.message_handler(commands=['stop'])
def stop_bot(message):
    if message.from_user.id == config.ADMIN_ID:
        if hunter.stop():
            bot.reply_to(message, "🛑 Hunter Stopped!")
        else:
            bot.reply_to(message, "⚠️ Hunter isn't running!")
    else:
        bot.reply_to(message, "⛔ Unauthorized!")

@bot.message_handler(commands=['stats'])
def show_stats(message):
    if message.from_user.id == config.ADMIN_ID:
        stats = hunter.stats
        last = stats['last_available'].strftime("%Y-%m-%d %H:%M") if stats['last_available'] else "Never"
        
        report = (
            f"📈 **Hunter Statistics**\n\n"
            f"🔢 Total Generated: `{stats['total_generated']}`\n"
            f"💎 Available Found: `{stats['available_found']}`\n"
            f"🕒 Last Available: `{last}`\n"
            f"🏷️ Current Session: `#{hunter.session_count}`"
        )
        
        bot.reply_to(message, report, parse_mode="Markdown")
    else:
        bot.reply_to(message, "⛔ Unauthorized!")

# =============== MAIN EXECUTION ===============
if __name__ == '__main__':
    logger.info("🔥 Ultimate Username Hunter Bot Starting...")
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")