import logging
import sys
import asyncio
from datetime import datetime
from telegram import Update, ChatPermissions, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# استيراد الإعدادات من config.py
try:
    from config import BOT_TOKEN, CHANNEL_USERNAME, DEVELOPER_USERNAME
    from config import READ_TIMEOUT, WRITE_TIMEOUT, CONNECT_TIMEOUT, POOL_TIMEOUT
    print("✅ تم تحميل الإعدادات بنجاح من config.py")
except ImportError as e:
    print(f"❌ خطأ في تحميل الإعدادات: {e}")
    sys.exit(1)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# المطورون الأساسيون (صلاحيات في جميع المجموعات)
DEVELOPERS = ["pw19k"]  # يوزرات المطورين

# تخزين مالكي المجموعات
group_owners = {}

# مسار صورة البوت (يمكن تغييرها)
BOT_IMAGE_PATH = "bot_image.jpg"  # ضع الصورة في نفس مجلد البوت

# أمر البدء مع الصورة
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # إرسال الصورة أولاً
        try:
            with open(BOT_IMAGE_PATH, 'rb') as photo:
                await update.message.reply_photo(
                    photo=InputFile(photo),
                    caption=f"""
🎊 **مرحباً بك في بوت تايم المطور!**

🤖 **البوت الرسمي للمطور:** @{DEVELOPER_USERNAME}
📢 **قناة البوت:** @{CHANNEL_USERNAME}

⚡ **مميزات البوت:**
• حماية كاملة للمجموعات
• أوامر سريعة ومتقدمة
• تحكم كامل للمالكين
• إشعارات فورية

🎯 **الأوامر المتاحة:**
/kick - طرد عضو من المجموعة
/mute - كتم عضو في المجموعة  
/unmute - إلغاء كتم عضو
/ban - حظر عضو من المجموعة

🔒 **ملاحظة:** الأوامر متاحة فقط لمالك المجموعة

📞 **للتواصل والدعم:** @{DEVELOPER_USERNAME}
                    """,
                    parse_mode='Markdown'
                )
        except FileNotFoundError:
            # إذا لم توجد الصورة، إرسال الرسالة فقط
            await update.message.reply_text(f"""
🎊 **مرحباً بك في بوت تايم المطور!**

🤖 **البوت الرسمي للمطور:** @{DEVELOPER_USERNAME}
📢 **قناة البوت:** @{CHANNEL_USERNAME}

⚡ **مميزات البوت:**
• حماية كاملة للمجموعات
• أوامر سريعة ومتقدمة
• تحكم كامل للمالكين
• إشعارات فورية

🎯 **الأوامر المتاحة:**
/kick - طرد عضو من المجموعة
/mute - كتم عضو في المجموعة  
/unmute - إلغاء كتم عضو
/ban - حظر عضو من المجموعة

🔒 **ملاحظة:** الأوامر متاحة فقط لمالك المجموعة

📞 **للتواصل والدعم:** @{DEVELOPER_USERNAME}
            """, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("❌ حدث خطأ في عرض معلومات البوت")

# أمر المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
        return
        
    help_text = f"""
🎯 **أوامر البوت (للمالك فقط)**

**الأوامر الأساسية:**
/kick - طرد مستخدم (بالرد أو @username)
/mute - كتم مستخدم  
/unmute - إلغاء كتم
/ban - حظر مستخدم

**المطور:** @{DEVELOPER_USERNAME}
**القناة:** @{CHANNEL_USERNAME}

⚡ **مميزات البوت:**
• طرد أي عضو بغض النظر عن رتبته
• إشعارات خاصة للمالك
• أوامر سريعة ومتقدمة
    """
    await update.message.reply_text(help_text)

# أمر المعلومات
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = f"""
🤖 **معلومات البوت**

📢 **القناة:** @{CHANNEL_USERNAME}
👨‍💻 **المطور:** @{DEVELOPER_USERNAME}

⚡ **البوت يعمل بنجاح!**
🎯 **مخصص لإدارة المجموعات - للمالك فقط**

🔧 **المميزات:**
• حماية كاملة للمجموعات
• أوامر سريعة ومتقدمة
• تحكم كامل للمالكين
• إشعارات فورية

📞 **للتواصل والدعم:** @{DEVELOPER_USERNAME}
    """
    await update.message.reply_text(info_text)

# باقي الكود (الدوال الأخرى) يبقى كما هو...

def main():
    try:
        print("🚀 بدء تشغيل بوت تايم المطور...")
        print(f"🤖 المطور: @{DEVELOPER_USERNAME}")
        print(f"📢 القناة: @{CHANNEL_USERNAME}")
        print("🎯 جاري تحميل الميزات...")
        
        # إنشاء تطبيق البوت
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة handlers للأوامر
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("info", info_command))
        application.add_handler(CommandHandler("kick", kick_command))
        application.add_handler(CommandHandler("mute", mute_command))
        application.add_handler(CommandHandler("unmute", unmute_command))
        application.add_handler(CommandHandler("ban", kick_command))
        
        # إضافة معالج للكلمات الخفية
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_secret_commands))
        
        # إضافة معالج لدخول البوت لمجموعات جديدة
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, auto_detect_owner))
        
        # إضافة معالج الأخطاء
        application.add_error_handler(error_handler)
        
        print("✅ تم تحميل جميع الميزات بنجاح")
        print("🎯 الميزات المتاحة:")
        print("   - رسالة ترحيب مع الصورة")
        print("   - التعرف التلقائي على المالك")
        print("   - أوامر الطرد والكتم")
        print("   - إشعارات فورية للمطور")
        print("🤖 البوت يعمل الآن...")
        
        # بدء البوت
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    main()