import asyncio
import logging
import os
import yt_dlp
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

# 🎵 تخزين حالة التشغيل للمجموعات
playback_status = {}

# 🔍 إعدادات yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
}

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
🎵 **مرحباً بك في بوت تشغيل الموسيقى!** 🎵

📢 **للاستفادة من ميزات البوت، يجب الاشتراك في قناتنا الرسمية أولاً**

⚡ **خطوات الاشتراك:**
1️⃣ انضم إلى القناة بالضغط على الزر أدناه
2️⃣ اضغط على زر "تحقق من الاشتراك"
3️⃣ استمتع بكامل ميزات البوت! 🎉
    """
    
    # إرسال صورة ترحيبية إذا كانت موجودة
    try:
        if os.path.exists("welcome.jpg"):
            await update.message.reply_photo(
                photo=open("welcome.jpg", "rb"),
                caption=subscription_text,
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(subscription_text, reply_markup=reply_markup)
    except:
        await update.message.reply_text(subscription_text, reply_markup=reply_markup)

async def send_private_subscription_message(user_id: int, bot):
    """إرسال رسالة طلب الاشتراك للعضو خاص"""
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

📢 **للاستفادة من ميزات البوت في المجموعة، يجب الاشتراك في قناتنا الرسمية أولاً**

⚡ **خطوات الاشتراك:**
1️⃣ انضم إلى القناة بالضغط على الزر أدناه
2️⃣ اضغط على زر "تحقق من الاشتراك"
3️⃣ يمكنك استخدام البوت في المجموعة! 🎉
    """
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=subscription_text,
            reply_markup=reply_markup
        )
    except Exception as e:
        logging.error(f"Failed to send private message: {e}")

async def check_member_subscription(user_id: int, chat_id: int, bot, update: Update = None):
    """التحقق من اشتراك العضو في القناة وإرسال رسالة إذا لم يكن مشترك"""
    if await is_developer(user_id, ""):
        return True
    
    if await check_channel_subscription(user_id, bot):
        return True
    else:
        # إرسال رسالة طلب الاشتراك للعضو خاص
        await send_private_subscription_message(user_id, bot)
        
        # إرسال رسالة في المجموعة لإعلامه
        if update and update.message:
            await update.message.reply_text(
                f"👋 [{update.effective_user.first_name}](tg://user?id={user_id})\n"
                "📢 تم إرسال رسالة لك خاص، يرجى متابعتها لإكمال التحقق",
                parse_mode='Markdown'
            )
        return False

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

⚡ **الآن يمكنك استخدام كامل ميزات البوت**
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📥 أضفني لمجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("👤 التواصل مع المطور", url=f"https://t.me/{DEVELOPER_USERNAME}")
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

# 🎵 أوامر التشغيل في المجموعات
async def handle_play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر شغل"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_member_subscription(user_id, chat_id, context.bot, update):
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `شغل`\nمثال: `شغل حسام الرسام`")
        return
    
    song_name = " ".join(context.args)
    
    # محاكاة عملية التشغيل
    await update.message.reply_text(f"🎵 **جاري تشغيل:** {song_name}\n\n⚡ يتم التشغيل في المجموعة...")

async def handle_search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر ابحث"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_member_subscription(user_id, chat_id, context.bot, update):
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `ابحث`\nمثال: `ابحث اغنية حزينة`")
        return
    
    song_name = " ".join(context.args)
    
    # محاكاة عملية البحث
    await update.message.reply_text(f"🔍 **جاري البحث عن:** {song_name}\n\n📋 سيتم عرض النتائج قريباً...")

async def handle_youtube_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر يوت"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_member_subscription(user_id, chat_id, context.bot, update):
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `يوت`\nمثال: `يوت اغنية رومانسية`")
        return
    
    song_name = " ".join(context.args)
    
    # محاكاة عملية التحميل
    await update.message.reply_text(f"📥 **جاري تحميل:** {song_name}\n\n⏳ المدة: دقيقة واحدة\nسيتم إرسالها كملف صوتي...")

# 🎵 أوامر التحكم في التشغيل
async def handle_pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر قف"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_member_subscription(user_id, chat_id, context.bot, update):
        return
    
    await update.message.reply_text("⏸️ **تم إيقاف التشغيل مؤقتاً**\n\nاكتب `اكمل` لاستئناف التشغيل")

async def handle_resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر اكمل"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_member_subscription(user_id, chat_id, context.bot, update):
        return
    
    await update.message.reply_text("▶️ **تم استئناف التشغيل**\n\nاكتب `قف` للإيقاف المؤقت")

async def handle_skip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر تخطي"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_member_subscription(user_id, chat_id, context.bot, update):
        return
    
    await update.message.reply_text("⏭️ **تم تخطي الأغنية**\n\nجاري تشغيل التالية...")

async def handle_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر ايقاف"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_member_subscription(user_id, chat_id, context.bot, update):
        return
    
    await update.message.reply_text("⏹️ **تم إيقاف التشغيل**\n\nاكتب `شغل` لتشغيل أغنية جديدة")

async def group_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة ترحيبية عند إضافة البوت للمجموعة"""
    welcome_text = """
🎵 **مرحباً بك في بوت تشغيل الموسيقى!** 🎵

⚡ **شكراً لإضافتي إلى مجموعتك**

🎶 **أوامر التشغيل:**
`شغل + اسم الأغنية` - تشغيل مباشر
`ابحث + اسم الأغنية` - بحث في اليوتيوب
`يوت + اسم الأغنية` - تحميل كملف صوتي

⏯️ **أوامر التحكم:**
`قف` - إيقاف مؤقت
`اكمل` - استئناف التشغيل
`تخطي` - التالية
`ايقاف` - إيقاف كامل

📢 **مهم:** يجب على جميع الأعضاء الاشتراك في @MASTFA_20022
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("👤 المطور", url=f"https://t.me/{DEVELOPER_USERNAME}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def set_bot_commands(application):
    """تعيين أوامر البوت في القائمة"""
    commands = [
        BotCommand("start", "بدء استخدام البوت 🚀"),
        BotCommand("play", "تشغيل الموسيقى 🎵"),
        BotCommand("stop", "إيقاف التشغيل ⏹️"),
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
    
    # ➕ إضافة المعالجات للأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    
    # 🎵 معالجة الأوامر النصية في المجموعات
    application.add_handler(MessageHandler(filters.Regex(r'^شغل\s+.+'), handle_play_command))
    application.add_handler(MessageHandler(filters.Regex(r'^ابحث\s+.+'), handle_search_command))
    application.add_handler(MessageHandler(filters.Regex(r'^يوت\s+.+'), handle_youtube_command))
    application.add_handler(MessageHandler(filters.Regex(r'^قف$'), handle_pause_command))
    application.add_handler(MessageHandler(filters.Regex(r'^اكمل$'), handle_resume_command))
    application.add_handler(MessageHandler(filters.Regex(r'^تخطي$'), handle_skip_command))
    application.add_handler(MessageHandler(filters.Regex(r'^ايقاف$'), handle_stop_command))
    
    # 🔘 معالجة الأزرار
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # 🏷️ معالجة إضافة البوت للمجموعات
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_start))
    
    # 📝 تعيين أوامر القائمة
    application.post_init = set_bot_commands
    
    print("🎵 بوت الموسيقى يعمل بنجاح!")
    print(f"📢 القناة: @{CHANNEL_USERNAME}")
    print(f"👤 المطور: @{DEVELOPER_USERNAME}")
    print("⚡ الأوامر الجاهزة: شغل، ابحث، يوت، قف، اكمل، تخطي، ايقاف")
    
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
    # إنشاء مجلد التحميلات
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    main()