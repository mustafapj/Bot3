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
    import config
    
    BOT_TOKEN = config.BOT_TOKEN
    CHANNEL_USERNAME = config.CHANNEL_USERNAME
    DEVELOPER_USERNAME = config.DEVELOPER_USERNAME
    READ_TIMEOUT = getattr(config, 'READ_TIMEOUT', 30)
    WRITE_TIMEOUT = getattr(config, 'WRITE_TIMEOUT', 30)
    CONNECT_TIMEOUT = getattr(config, 'CONNECT_TIMEOUT', 30)
    POOL_TIMEOUT = getattr(config, 'POOL_TIMEOUT', 30)
    
except ImportError:
    print("❌ خطأ: لم يتم العثور على ملف config.py")
    exit(1)
except AttributeError as e:
    print(f"❌ خطأ في متغيرات الإعدادات: {e}")
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
            InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("👤 المطور", url=f"https://t.me/{DEVELOPER_USERNAME}")
        ],
        [
            InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    subscription_text = """
🔒 **عذراً عزيزي!** 🔒

📢 **للاستفادة من ميزات البوت، يجب الاشتراك في قناتنا الرسمية أولاً**

⚡ **خطوات الاشتراك:**
1️⃣ انضم إلى القناة بالضغط على الزر أدناه
2️⃣ اضغط على زر "تحقق من الاشتراك"
3️⃣ استمتع بكامل ميزات البوت! 🎉
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
        """
        await update.message.reply_text(welcome_text)
        return
    
    # التحقق من الاشتراك في القناة
    if not await check_channel_subscription(user_id, context.bot):
        await send_subscription_message(update, context)
        return
    
    # إذا كان مشتركاً - عرض القائمة الرئيسية
    welcome_text = """
🎵 **مرحباً بك في بوت تشغيل الموسيقى!** 🎵

✨ **شكراً لاشتراكك في قناتنا الرسمية**

⚡ **يمكنك الآن استخدام كامل ميزات البوت**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📥 أضفني لمجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("👤 التواصل مع المطور", url=f"https://t.me/{DEVELOPER_USERNAME}")
        ],
        [
            InlineKeyboardButton("🎵 تشغيل الموسيقى", callback_data="play_music")
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
    
    elif query.data == "play_music":
        if not await is_developer(user_id, username) and not await check_channel_subscription(user_id, context.bot):
            await send_subscription_message(update, context)
            return
        
        await query.message.reply_text("🎵 **سيتم تشغيل الموسيقى قريباً**\n\nاستخدم الأوامر في القائمة لبدء التشغيل")

async def play_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تشغيل الموسيقى مع التحقق من الاشتراك"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username) and not await check_channel_subscription(user_id, context.bot):
        await send_subscription_message(update, context)
        return
    
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
/play - تشغيل أغنية
/stop - إيقاف التشغيل
/pause - إيقاف مؤقت
/resume - استئناف التشغيل
/next - التالية

🔧 **أوامر أخرى:**
/start - بدء البوت
/help - المساعدة

📢 **مهم:** يجب الاشتراك في قناتنا @MASTFA_20022 لاستخدام البوت
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("👤 المطور", url=f"https://t.me/{DEVELOPER_USERNAME}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup)

async def group_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة ترحيبية عند إضافة البوت للمجموعة"""
    welcome_text = """
🎵 **مرحباً بك في بوت تشغيل الموسيقى!** 🎵

⚡ **شكراً لإضافتي إلى مجموعتك**

📢 **مهم:** يجب على جميع الأعضاء الاشتراك في قناتنا @MASTFA_20022 لاستخدام البوت

🎶 **استمتع بتشغيل الموسيقى مع أصدقائك!**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("👤 المطور", url=f"https://t.me/{DEVELOPER_USERNAME}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

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
    ]
    
    await application.bot.set_my_commands(commands)

def main():
    # ✅ التحقق من وجود التوكن
    if not BOT_TOKEN or BOT_TOKEN == "ضع_التوكن_الحقيقي_هنا":
        print("❌ خطأ: لم تقم بتعيين التوكن في config.py")
        print("📝 يرجى فتح ملف config.py وإضافة التوكن الحقيقي من BotFather")
        return
    
    # 🚀 إنشاء التطبيق
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
    
    # 🔘 معالجة الأزرار
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # 🏷️ معالجة الرسائل في المجموعات
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_start))
    
    # 📝 تعيين أوامر القائمة
    application.post_init = set_bot_commands
    
    print("🎵 بوت الموسيقى يعمل بنجاح!")
    print(f"📢 القناة: @{CHANNEL_USERNAME}")
    print(f"👤 المطور: @{DEVELOPER_USERNAME}")
    
    # ▶️ بدء البوت
    try:
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
    except Exception as e:
        print(f"❌ خطأ: {e}")
        print("🔄 إعادة التشغيل خلال 10 ثواني...")
        asyncio.sleep(10)
        main()

if __name__ == "__main__":
    main()