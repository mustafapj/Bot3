import asyncio
import logging
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

# 📁 استيراد الإعدادات من ملف config
try:
    from config import *
except ImportError:
    print("❌ خطأ: لم يتم العثور على ملف config.py")
    print("📝 يرجى إنشاء ملف config.py وإضافة التوكن والإعدادات")
    exit(1)

# 🔧 إعدادات البوت
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def check_channel_subscription(user_id: int, bot) -> bool:
    """التحقق من اشتراك المستخدم في القناة"""
    try:
        member = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Error checking subscription: {e}")
        return False

async def is_developer(user_id: int, username: str) -> bool:
    """التحقق إذا كان المستخدم هو المطور"""
    try:
        return username == DEVELOPER_USERNAME
    except:
        return False

async def send_subscription_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال رسالة طلب الاشتراك في القناة"""
    keyboard = [
        [
            InlineKeyboardButton("📢 قناة البوت الرسمية", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("🆘 الدعم الفني", url=f"https://t.me/{DEVELOPER_USERNAME}")
        ],
        [
            InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    subscription_text = """
🔒 **عذراً عزيزي!** 🔒

📢 **للاستفادة من ميزات البوت، يجب الاشتراك في قناتنا الرسمية أولاً:**

✨ **لماذا الاشتراك؟**
• الحصول على آخر التحديثات
• دعم استمرارية البوت
• ميزات حصرية للأعضاء

⚡ **خطوات الاشتراك:**
1️⃣ انضم إلى القناة بالضغط على الزر أدناه
2️⃣ اضغط على زر "تحقق من الاشتراك"
3️⃣ استمتع بكامل ميزات البوت! 🎉

🆘 **للتواصل والدعم:** @pw19k
    """
    
    if update.message:
        await update.message.reply_text(subscription_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text(subscription_text, reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء مع التحقق من الاشتراك"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # التحقق إذا كان المستخدم هو المطور
    if await is_developer(user_id, username):
        welcome_text = """
👑 **مرحباً سيادة المطور!** 👑

⚡ **البوت يعمل بشكل ممتاز**
📊 **يمكنك متابعة إحصائيات البوت**

🔧 **أوامر المطور:**
/status - حالة البوت
/stats - إحصائيات المستخدمين
        """
        await update.message.reply_text(welcome_text)
        return
    
    # التحقق من الاشتراك في القناة
    if not await check_channel_subscription(user_id, context.bot):
        await send_subscription_message(update, context)
        return
    
    # إذا كان مشتركاً - عرض القائمة الرئيسية
    welcome_text = """
🎊 **أهلاً وسهلاً بك!** 🎊

✨ **شكراً لاشتراكك في قناتنا الرسمية** ✨

🎵 **قائمة أوامر الموسيقى:**
/play - تشغيل أغنية 🎵
/stop - إيقاف التشغيل ⏹️
/next - التالية ▶️
/pause - إيقاف مؤقت ⏸️
/resume - استئناف التشغيل 🔊

📋 **أوامر أخرى:**
/help - المساعدة 🆘
/settings - الإعدادات ⚙️
/info - معلومات البوت ℹ️

🆘 **للتواصل والدعم:** @pw19k
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🎵 تشغيل", callback_data="play"),
            InlineKeyboardButton("⏹️ إيقاف", callback_data="stop")
        ],
        [
            InlineKeyboardButton("📢 قناتنا", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("🆘 الدعم", url=f"https://t.me/{DEVELOPER_USERNAME}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    username = query.from_user.username
    
    if query.data == "check_subscription":
        if await is_developer(user_id, username):
            await query.message.reply_text("👑 أنت المطور! لا تحتاج للاشتراك.")
            return
        
        if await check_channel_subscription(user_id, context.bot):
            await query.message.reply_text("✅ **تم التحقق بنجاح! شكراً لاشتراكك.**\n\nاكتب /start للبدء! 🎉")
        else:
            await query.message.reply_text("❌ **لم يتم العثور على اشتراكك.**\n\nيرجى الانضمام للقناة أولاً ثم اضغط على زر التحقق مرة أخرى.")

async def play_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تشغيل الموسيقى مع التحقق من الاشتراك"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username) and not await check_channel_subscription(user_id, context.bot):
        await send_subscription_message(update, context)
        return
    
    # هنا كود تشغيل الموسيقى الفعلي
    await update.message.reply_text("🎵 **جاري التشغيل...**\n\nسيتم تشغيل طلبك قريباً!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر المساعدة"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username) and not await check_channel_subscription(user_id, context.bot):
        await send_subscription_message(update, context)
        return
    
    help_text = """
🆘 **مركز المساعدة**

🎵 **أوامر الموسيقى:**
/play [اسم الأغنية] - تشغيل أغنية
/stop - إيقاف التشغيل
/pause - إيقاف مؤقت
/resume - استئناف التشغيل
/next - التالية

⚙️ **أوامر أخرى:**
/start - بدء البوت
/settings - الإعدادات
/info - معلومات

📢 **مهم:** يجب الاشتراك في قناتنا @MASTFA_20022 لاستخدام البوت

🆘 **الدعم:** @pw19k
    """
    await update.message.reply_text(help_text)

async def set_bot_commands(application):
    """تعيين أوامر البوت في القائمة"""
    commands = [
        BotCommand("start", "بدء استخدام البوت 🚀"),
        BotCommand("play", "تشغيل الموسيقى 🎵"),
        BotCommand("stop", "إيقاف التشغيل ⏹️"),
        BotCommand("pause", "إيقاف مؤقت ⏸️"),
        BotCommand("resume", "استئناف التشغيل 🔊"),
        BotCommand("next", "الأغنية التالية ▶️"),
        BotCommand("help", "المساعدة والدعم 🆘"),
        BotCommand("settings", "إعدادات البوت ⚙️"),
        BotCommand("info", "معلومات البوت ℹ️"),
    ]
    
    await application.bot.set_my_commands(commands)

def main():
    # ✅ التحقق من وجود التوكن
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or BOT_TOKEN == "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz":
        print("❌ خطأ: لم تقم بتعيين التوكن في config.py")
        print("📝 يرجى فتح ملف config.py وإضافة التوكن الحقيقي")
        return
    
    # 🚀 إنشاء التطبيق مع إعدادات محسنة
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(READ_TIMEOUT)
        .write_timeout(WRITE_TIMEOUT)
        .connect_timeout(CONNECT_TIMEOUT)
        .pool_timeout(POOL_TIMEOUT)
        .build()
    )
    
    # ➕ إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play_music))
    application.add_handler(CommandHandler("stop", play_music))
    application.add_handler(CommandHandler("pause", play_music))
    application.add_handler(CommandHandler("resume", play_music))
    application.add_handler(CommandHandler("next", play_music))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", help_command))
    application.add_handler(CommandHandler("info", help_command))
    
    # 🔘 معالجة الأزرار
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # 📝 تعيين أوامر القائمة
    application.post_init = set_bot_commands
    
    print("""
🎉 **البوت يعمل بنجاح!** 🎉

✨ **الميزات المضمنة:**
✅ التحقق من الاشتراك في القناة
✅ استثناء المطور من الاشتراك
✅ واجهة مستخدم احترافية
✅ قائمة أوامر تلقائية
✅ أزرار تفاعلية
✅ دعم فني مباشر

📢 **القناة:** @MASTFA_20022
👤 **المطور:** @pw19k
    """)
    
    # ▶️ بدء البوت
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()