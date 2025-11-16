import logging
import random
import string
import asyncio
import aiohttp
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 🔑 ضع التوكن الجديد هنا
BOT_TOKEN = "ضع_التوكن_الجديد_هنا"

class UsernameChecker:
    def __init__(self):
        self.checked = set()
        self.session = None
    
    async def create_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    def generate_username(self):
        chars = string.ascii_lowercase + string.digits + '_'
        while True:
            username = ''.join(random.choices(chars, k=5))
            if (not username[0].isdigit() and 
                '__' not in username and
                username not in self.checked):
                self.checked.add(username)
                return username
    
    async def check_username_availability(self, username):
        try:
            await self.create_session()
            url = f"https://t.me/{username}"
            async with self.session.get(url) as response:
                text = await response.text()
                if "If you have <strong>Telegram</strong>" in text:
                    return True
                return False
        except:
            return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 البوت يعمل! أرسل /generate")

async def generate_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    checker = UsernameChecker()
    await update.message.reply_text("🔍 جاري البحث عن يوزرات متاحة...")
    
    for i in range(10):
        username = checker.generate_username()
        if await checker.check_username_availability(username):
            await update.message.reply_text(f"✅ @{username}")
        await asyncio.sleep(1)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("generate", generate_usernames))
    print("🚀 البوت يعمل...")
    application.run_polling()

if __name__ == '__main__':
    main()