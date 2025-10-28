import logging
import sys
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# استيراد التوكن من config.py
try:
    from config import BOT_TOKEN
    print("✅ تم تحميل التوكن بنجاح")
except ImportError as e:
    print(f"❌ خطأ في تحميل التوكن: {e}")
    sys.exit(1)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# التحقق من أن المرسل هو المالك
async def is_owner(update: Update) -> bool:
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        if not user or not chat:
            return False
            
        # الحصول على قائمة المشرفين
        admins = await chat.get_administrators()
        
        # المالك هو أول مشرف في القائمة
        owner = admins[0].user if admins else None
        
        if owner and user.id == owner.id:
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error in owner check: {e}")
        return False

# أمر البدء
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
مرحباً بك في بوت ذا تايم

📌 **الخيارات:**
• أضفني إلى مجموعتك
• قناة البوت  
• التواصل مع المالك
"""
    await update.message.reply_text(welcome_text)

# طرد بالرد
async def handle_kick_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        try:
            await update.effective_chat.ban_member(target_user.id)
            await update.effective_chat.unban_member(target_user.id)
        except Exception as e:
            logger.error(f"Error kicking user: {e}")

# كتم بالرد
async def handle_mute_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        try:
            permissions = ChatPermissions(can_send_messages=False)
            await update.effective_chat.restrict_member(target_user.id, permissions)
        except Exception as e:
            logger.error(f"Error muting user: {e}")

# فك كتم بالرد
async def handle_unmute_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        try:
            permissions = ChatPermissions(can_send_messages=True)
            await update.effective_chat.restrict_member(target_user.id, permissions)
        except Exception as e:
            logger.error(f"Error unmuting user: {e}")

def main():
    try:
        print("🚀 بدء تشغيل البوت...")
        
        application = Application.builder().token(BOT_TOKEN).build()
        
        # أمر البدء فقط
        application.add_handler(CommandHandler("start", start_command))
        
        # معالجة الطرد بالرد
        application.add_handler(MessageHandler(
            filters.TEXT & filters.REPLY & filters.Regex(r'^(طرد|kick)$'), 
            handle_kick_reply
        ))
        
        # معالجة الكتم بالرد
        application.add_handler(MessageHandler(
            filters.TEXT & filters.REPLY & filters.Regex(r'^(كتم|mute)$'), 
            handle_mute_reply
        ))
        
        # معالجة فك الكتم بالرد
        application.add_handler(MessageHandler(
            filters.TEXT & filters.REPLY & filters.Regex(r'^(فك|unmute)$'), 
            handle_unmute_reply
        ))
        
        print("🤖 البوت يعمل الآن...")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    main()