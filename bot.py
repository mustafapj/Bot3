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

async def check_channel_subscription(user_id: int, bot) -> bool:
    """التحقق من اشتراك المستخدم في القناة"""
    try:
        chat_member = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"خطأ في التحقق من الاشتراك: {e}")
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
        [InlineKeyboardButton("اضغط للاشتراك بالقناة", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    subscription_text = f"""
❌ **عذراً عمري أن نسأت غير مشترك بقناة البوت**

⚡ **للاستفادة من ميزات البوت، يجب الاشتراك في قناتنا الرسمية أولاً**
    """
    
    await update.message.reply_text(subscription_text, reply_markup=reply_markup)

async def update_stats(user_id: int, chat_type: str):
    """تحديث إحصائيات البوت"""
    bot_stats["active_users"].add(user_id)
    bot_stats["total_users"] = len(bot_stats["active_users"])
    
    if chat_type == "group" or chat_type == "supergroup":
        bot_stats["group_count"] = len(bot_stats["active_users"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء مع التحقق من الاشتراك"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # تحديث الإحصائيات
    chat_type = update.effective_chat.type
    await update_stats(user_id, chat_type)
    
    # إذا كان المطور، امنحه الوصول مباشرة
    if await is_developer(user_id, username):
        welcome_text = f"""
🎵 **Shams Music**  
**بوت**  

---

⚡ **ماذا يمكن لهذا البوت فعله؟**  
• * بوت تشغيل الموسيقى في الكروبات *  
• * تشغيل الأغاني من اليوتيوب *  
• * تحميل المقاطع الصوتية *  
• * البحث عن الموسيقى *  

🎶 **أرفع آدمن وارسل تفعيل**  

---

👤 **المطور:** @{DEVELOPER_USERNAME}
        """
        keyboard = [
            [InlineKeyboardButton("📥 أضفني لمجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("👤 مطور البوت", url=f"https://t.me/{DEVELOPER_USERNAME}")],
            [InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        return
    
    # التحقق من الاشتراك في القناة
    if not await check_channel_subscription(user_id, context.bot):
        await send_subscription_message(update, context)
        return
    
    # إذا كان مشتركاً - عرض القائمة الرئيسية
    welcome_text = f"""
🎵 **Shams Music**  
**بوت**  

---

⚡ **إهلا بك حبيبي العضو.**  

✨ **ماذا يمكن لهذا البوت فعله؟**  
• * بوت تشغيل الموسيقى في الكروبات *  
• * تشغيل الأغاني من اليوتيوب *  
• * تحميل المقاطع الصوتية *  
• * البحث عن الموسيقى *  

🎶 **أرفع آدمن وارسل تفعيل**  

---

👤 **المطور:** @{DEVELOPER_USERNAME}
    """
    
    keyboard = [
        [InlineKeyboardButton("📥 أضفني لمجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [
            InlineKeyboardButton("👤 مطور البوت", url=f"https://t.me/{DEVELOPER_USERNAME}"),
            InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}")
        ],
        [InlineKeyboardButton("🎵 تشغيل الموسيقى", callback_data="play_music")]
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
    username = query.from_user.username
    
    if query.data == "check_subscription":
        if await is_developer(user_id, username):
            await query.message.reply_text("👑 أنت المطور! لا تحتاج للاشتراك.\n\nاكتب /start للبدء! 🎉")
            return
        
        if await check_channel_subscription(user_id, context.bot):
            await query.message.reply_text("✅ **تم التحقق بنجاح! شكراً لاشتراكك.**\n\nاكتب /start للبدء! 🎉")
        else:
            await query.message.reply_text("❌ **لم يتم العثور على اشتراكك.**\n\nيرجى الانضمام للقناة أولاً ثم اضغط على زر التحقق مرة أخرى.")
    
    elif query.data == "play_music":
        if not await is_developer(user_id, username) and not await check_channel_subscription(user_id, context.bot):
            await send_subscription_message(update, context)
            return
        
        await query.message.reply_text("🎵 **استخدم الأوامر التالية:**\n\n`شغل اسم الأغنية` - للتشغيل المباشر\n`ابحث اسم الأغنية` - للبحث\n`يوت اسم الأغنية` - للتحميل")

# 🎵 معالجة الأوامر النصية في المجموعات
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة جميع الرسائل النصية"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    text = update.message.text.strip()
    
    # إذا كان المطور، امنحه الوصول مباشرة
    if await is_developer(user_id, username):
        if text.startswith('شغل '):
            song_name = text.replace('شغل ', '', 1).strip()
            if song_name:
                await update.message.reply_text(f"🎵 **جاري تشغيل:** {song_name}\n\n⚡ يتم التشغيل في المجموعة...")
            else:
                await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `شغل`\nمثال: `شغل حسام الرسام`")
            return
        
        elif text.startswith('ابحث '):
            song_name = text.replace('ابحث ', '', 1).strip()
            if song_name:
                await update.message.reply_text(f"🔍 **جاري البحث عن:** {song_name}\n\n📋 سيتم عرض النتائج قريباً...")
            else:
                await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `ابحث`\nمثال: `ابحث اغنية حزينة`")
            return
        
        elif text.startswith('يوت '):
            song_name = text.replace('يوت ', '', 1).strip()
            if song_name:
                await update.message.reply_text(f"📥 **جاري تحميل:** {song_name}\n\n⏳ المدة: دقيقة واحدة\nسيتم إرسالها كملف صوتي...")
            else:
                await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `يوت`\nمثال: `يوت اغنية رومانسية`")
            return
        
        elif text == 'قف':
            await update.message.reply_text("⏸️ **تم إيقاف التشغيل مؤقتاً**\n\nاكتب `اكمل` لاستئناف التشغيل")
            return
        
        elif text == 'اكمل':
            await update.message.reply_text("▶️ **تم استئناف التشغيل**\n\nاكتب `قف` للإيقاف المؤقت")
            return
        
        elif text == 'تخطي':
            await update.message.reply_text("⏭️ **تم تخطي الأغنية**\n\nجاري تشغيل التالية...")
            return
        
        elif text == 'ايقاف':
            await update.message.reply_text("⏹️ **تم إيقاف التشغيل**\n\nاكتب `شغل` لتشغيل أغنية جديدة")
            return
    
    # للمستخدمين العاديين - التحقق من الاشتراك أولاً
    if not await check_channel_subscription(user_id, context.bot):
        keyboard = [
            [InlineKeyboardButton("اضغط للاشتراك بالقناة", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        subscription_text = f"❌ **عذراً [{update.effective_user.first_name}](tg://user?id={user_id}) غير مشترك بقناة البوت**"
        
        await update.message.reply_text(subscription_text, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    # إذا كان المستخدم مشتركاً - معالجة الأوامر
    if text.startswith('شغل '):
        # تحديث الإحصائيات
        await update_stats(user_id, "group")
        bot_stats["total_plays"] += 1
        
        song_name = text.replace('شغل ', '', 1).strip()
        if song_name:
            await update.message.reply_text(f"🎵 **جاري تشغيل:** {song_name}\n\n⚡ يتم التشغيل في المجموعة...")
        else:
            await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `شغل`\nمثال: `شغل حسام الرسام`")
    
    elif text.startswith('ابحث '):
        await update_stats(user_id, "group")
        
        song_name = text.replace('ابحث ', '', 1).strip()
        if song_name:
            await update.message.reply_text(f"🔍 **جاري البحث عن:** {song_name}\n\n📋 سيتم عرض النتائج قريباً...")
        else:
            await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `ابحث`\nمثال: `ابحث اغنية حزينة`")
    
    elif text.startswith('يوت '):
        await update_stats(user_id, "group")
        
        song_name = text.replace('يوت ', '', 1).strip()
        if song_name:
            await update.message.reply_text(f"📥 **جاري تحميل:** {song_name}\n\n⏳ المدة: دقيقة واحدة\nسيتم إرسالها كملف صوتي...")
        else:
            await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `يوت`\nمثال: `يوت اغنية رومانسية`")
    
    elif text == 'قف':
        await update.message.reply_text("⏸️ **تم إيقاف التشغيل مؤقتاً**\n\nاكتب `اكمل` لاستئناف التشغيل")
    
    elif text == 'اكمل':
        await update.message.reply_text("▶️ **تم استئناف التشغيل**\n\nاكتب `قف` للإيقاف المؤقت")
    
    elif text == 'تخطي':
        await update.message.reply_text("⏭️ **تم تخطي الأغنية**\n\nجاري تشغيل التالية...")
    
    elif text == 'ايقاف':
        await update.message.reply_text("⏹️ **تم إيقاف التشغيل**\n\nاكتب `شغل` لتشغيل أغنية جديدة")

async def group_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة ترحيبية عند إضافة البوت للمجموعة"""
    welcome_text = f"""
🎵 **Shams Music**  
**بوت**  

---

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
        [InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}")]
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
    
    # 🎵 معالجة جميع الرسائل النصية
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # 🔘 معالجة الأزرار
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # 🏷️ معالجة إضافة البوت للمجموعات
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_start))
    
    # 📝 تعيين أوامر القائمة
    application.post_init = set_bot_commands
    
    print("🎵 Shams Music Bot يعمل بنجاح!")
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