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
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

BOT_TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"

class UsernameChecker:
    def __init__(self):
        self.checked = set()
        self.session = None
        self.available_usernames = []
    
    async def create_session(self):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(limit=10)
            self.session = aiohttp.ClientSession(timeout=timeout, connector=connector)
    
    async def close_session(self):
        if self.session:
            await self.session.close()
    
    def generate_username(self):
        chars = string.ascii_lowercase + string.digits + '_'
        while True:
            username = ''.join(random.choices(chars, k=5))
            if (not username[0].isdigit() and 
                '__' not in username and
                not username.startswith('_') and
                username not in self.checked):
                self.checked.add(username)
                return username
    
    async def check_username_availability(self, username):
        try:
            await self.create_session()
            url = f"https://t.me/{username}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    text = await response.text()
                    if "If you have <strong>Telegram</strong>" in text or "tgme_username_not_occupied" in text:
                        return True
                    return False
                else:
                    return True
                    
        except Exception as e:
            logging.error(f"خطأ في فحص {username}: {e}")
            return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
    🚀 **بوت توليد اليوزرات الخماسية المتاحة**

⚡ **الأوامر:**
/generate - توليد يوزر واحد
/generate 10 - توليد 10 يوزرات
/stop - إيقاف التوليد
/stats - إحصائيات

📝 البوت يولد يوزرات عشوائية 5 أحرف ويرسل المتاح فقط!
    """
    await update.message.reply_text(welcome_text)

async def generate_usernames(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if 'checker' not in context.bot_data:
        context.bot_data['checker'] = UsernameChecker()
    if 'active_tasks' not in context.bot_data:
        context.bot_data['active_tasks'] = set()
    
    checker = context.bot_data['checker']
    
    if user_id in context.bot_data['active_tasks']:
        await update.message.reply_text("⏳ لديك عملية توليد نشطة بالفعل! استخدم /stop لإيقافها")
        return
    
    count = 1
    if context.args and context.args[0].isdigit():
        count = min(int(context.args[0]), 25)
    
    context.bot_data['active_tasks'].add(user_id)
    
    try:
        progress_msg = await update.message.reply_text(f"🔄 جاري البحث عن {count} يوزر متاح...")
        
        found_count = 0
        attempts = 0
        max_attempts = count * 100
        
        while (found_count < count and 
               attempts < max_attempts and 
               user_id in context.bot_data['active_tasks']):
            
            attempts += 1
            username = checker.generate_username()
            is_available = await checker.check_username_availability(username)
            
            if is_available:
                found_count += 1
                checker.available_usernames.append(username)
                await update.message.reply_text(f"✅ **يوزر متاح:** @{username}")
            
            if attempts % 25 == 0:
                try:
                    await progress_msg.edit_text(
                        f"🔍 جاري البحث...\n"
                        f"• المحاولات: {attempts}\n"
                        f"• تم العثور: {found_count}/{count}"
                    )
                except:
                    pass
            
            await asyncio.sleep(0.5)
        
        if user_id in context.bot_data['active_tasks']:
            if found_count > 0:
                # هذا السطر تم إصلاحه
                await update.message.reply_text(
                    f"🎉 **تم الانتهاء!**\n"
                    f"• المحاولات: {attempts}\n"
                    f"• المتاحة: {found_count}\n"
                    f"• اليوزرات: {', '.join(['@' + name for name in checker.available_usernames[-found_count:]])}"
                )
            else:
                await update.message.reply_text(f"❌ لم أجد يوزرات متاحة بعد {attempts} محاولة")
    
    except Exception as e:
        await update.message.reply_text(f"❌ حدث خطأ: {e}")
    finally:
        context.bot_data['active_tasks'].discard(user_id)

async def stop_generating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in context.bot_data.get('active_tasks', set()):
        context.bot_data['active_tasks'].discard(user_id)
        await update.message.reply_text("⏹️ تم إيقاف التوليد")
    else:
        await update.message.reply_text("⚠️ لا يوجد عملية توليد نشطة")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    checker = context.bot_data.get('checker')
    if checker:
        stats_text = (
            f"📊 **إحصائيات البوت:**\n"
            f"• اليوزرات المفحوصة: {len(checker.checked)}\n"
            f"• اليوزرات المتاحة: {len(checker.available_usernames)}\n"
            f"• المهام النشطة: {len(context.bot_data.get('active_tasks', set()))}"
        )
    else:
        stats_text = "📊 لم تبدأ أي عملية بعد"
    
    await update.message.reply_text(stats_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Error: {context.error}")

def main():
    try:
        print("🚀 بدء تشغيل البوت على Termux...")
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("generate", generate_usernames))
        application.add_handler(CommandHandler("stop", stop_generating))
        application.add_handler(CommandHandler("stats", stats))
        
        application.add_error_handler(error_handler)
        
        print("✅ البوت يعمل الآن! أرسل /start للبدء")
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    main()