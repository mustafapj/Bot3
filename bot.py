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

# 📊 إحصائيات البوت
bot_stats = {
    "total_users": 0,
    "active_users": set(),
    "group_count": 0,
    "total_plays": 0
}

# 🎵 تخزين حالة التشغيل للمجموعات
playback_status = {}

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
    """إرسال رسالة طلب الاشتراك في القناة بشكل عام"""
    keyboard = [
        [
            InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
            InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    subscription_text = f"""
🔒 **عذراً عزيزي!** 🔒

📢 **للاستفادة من ميزات البوت، يجب الاشتراك في قناتنا الرسمية أولاً**

@{CHANNEL_USERNAME}

⚡ **خطوات الاشتراك:**
1️⃣ انضم إلى القناة بالضغط على الزر أدناه
2️⃣ اضغط على زر "تحقق من الاشتراك"
3️⃣ استمتع بكامل ميزات البوت! 🎉
    """
    
    await update.message.reply_text(subscription_text, reply_markup=reply_markup)

async def update_stats(user_id: int, chat_type: str):
    """تحديث إحصائيات البوت"""
    bot_stats["active_users"].add(user_id)
    bot_stats["total_users"] = len(bot_stats["active_users"])
    
    if chat_type == "group" or chat_type == "supergroup":
        bot_stats["group_count"] += 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء مع التحقق من الاشتراك"""
    user_id = update.effective_user.id
    
    # تحديث الإحصائيات
    chat_type = update.effective_chat.type
    await update_stats(user_id, chat_type)
    
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

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر الإحصائيات للمطور فقط"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط")
        return
    
    stats_text = f"""
📊 **إحصائيات البوت**

👥 **إجمالي المستخدمين:** {bot_stats['total_users']}
🎯 **المستخدمين النشطين:** {len(bot_stats['active_users'])}
📢 **عدد المجموعات:** {bot_stats['group_count']}
🎵 **مرات التشغيل:** {bot_stats['total_plays']}

⚡ **البوت يعمل بشكل ممتاز**
    """
    
    await update.message.reply_text(stats_text)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأزرار"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "check_subscription":
        if await check_channel_subscription(user_id, context.bot):
            await query.message.reply_text("✅ **تم التحقق بنجاح! شكراً لاشتراكك.**\n\nاكتب /start للبدء! 🎉")
        else:
            await query.message.reply_text("❌ **لم يتم العثور على اشتراكك.**\n\nيرجى الانضمام للقناة أولاً ثم اضغط على زر التحقق مرة أخرى.")

# 🎵 أوامر التشغيل في المجموعات
async def handle_play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر شغل"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # تحديث الإحصائيات
    await update_stats(user_id, "group")
    bot_stats["total_plays"] += 1
    
    # التحقق من الاشتراك أولاً
    if not await check_channel_subscription(user_id, context.bot):
        # إرسال رسالة طلب الاشتراك في المجموعة مباشرة
        keyboard = [
            [
                InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
                InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        subscription_text = f"""
🔒 **عذراً [{update.effective_user.first_name}](tg://user?id={user_id})!** 🔒

📢 **للاستفادة من ميزات البوت، يجب الاشتراك في قناتنا الرسمية أولاً**

@{CHANNEL_USERNAME}

⚡ **بعد الاشتراك، اضغط على زر التحقق**
        """
        
        await update.message.reply_text(subscription_text, reply_markup=reply_markup, parse_mode='Markdown')
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
    
    # تحديث الإحصائيات
    await update_stats(user_id, "group")
    
    # التحقق من الاشتراك أولاً
    if not await check_channel_subscription(user_id, context.bot):
        # إرسال رسالة طلب الاشتراك في المجموعة مباشرة
        keyboard = [
            [
                InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
                InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🔒 **عذراً [{update.effective_user.first_name}](tg://user?id={user_id})! يجب الاشتراك في @{CHANNEL_USERNAME} أولاً**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
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
    
    # تحديث الإحصائيات
    await update_stats(user_id, "group")
    
    # التحقق من الاشتراك أولاً
    if not await check_channel_subscription(user_id, context.bot):
        # إرسال رسالة طلب الاشتراك في المجموعة مباشرة
        keyboard = [
            [
                InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}"),
                InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🔒 **عذراً [{update.effective_user.first_name}](tg://user?id={user_id})! يجب الاشتراك في @{CHANNEL_USERNAME} أولاً**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
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
    if not await check_channel_subscription(user_id, context.bot):
        await update.message.reply_text(f"🔒 **عذراً [{update.effective_user.first_name}](tg://user?id={user_id})! يجب الاشتراك في @{CHANNEL_USERNAME} أولاً**", parse_mode='Markdown')
        return
    
    await update.message.reply_text("⏸️ **تم إيقاف التشغيل مؤقتاً**\n\nاكتب `اكمل` لاستئناف التشغيل")

async def handle_resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر اكمل"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_channel_subscription(user_id, context.bot):
        await update.message.reply_text(f"🔒 **عذراً [{update.effective_user.first_name}](tg://user?id={user_id})! يجب الاشتراك في @{CHANNEL_USERNAME} أولاً**", parse_mode='Markdown')
        return
    
    await update.message.reply_text("▶️ **تم استئناف التشغيل**\n\nاكتب `قف` للإيقاف المؤقت")

async def handle_skip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر تخطي"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_channel_subscription(user_id, context.bot):
        await update.message.reply_text(f"🔒 **عذراً [{update.effective_user.first_name}](tg://user?id={user_id})! يجب الاشتراك في @{CHANNEL_USERNAME} أولاً**", parse_mode='Markdown')
        return
    
    await update.message.reply_text("⏭️ **تم تخطي الأغنية**\n\nجاري تشغيل التالية...")

async def handle_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة أمر ايقاف"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # التحقق من الاشتراك أولاً
    if not await check_channel_subscription(user_id, context.bot):
        await update.message.reply_text(f"🔒 **عذراً [{update.effective_user.first_name}](tg://user?id={user_id})! يجب الاشتراك في @{CHANNEL_USERNAME} أولاً**", parse_mode='Markdown')
        return
    
    await update.message.reply_text("⏹️ **تم إيقاف التشغيل**\n\nاكتب `شغل` لتشغيل أغنية جديدة")

async def group_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة ترحيبية عند إضافة البوت للمجموعة"""
    welcome_text = f"""
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

📢 **مهم:** يجب على جميع الأعضاء الاشتراك في @{CHANNEL_USERNAME}
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def set_bot_commands(application):
    """تعيين أوامر البوت في القائمة"""
    commands = [
        BotCommand("start", "بدء استخدام البوت 🚀"),
        BotCommand("stats", "إحصائيات البوت 📊"),
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
    application.add_handler(CommandHandler("stats", stats_command))
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
    print("📊 أمر الإحصائيات: /stats (للمطور فقط)")
    
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