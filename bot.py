import asyncio
import logging
import os
import json
from datetime import datetime
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
    "groups": {},  # {chat_id: {"title": "اسم المجموعة", "members": عدد الأعضاء, "added_date": "تاريخ الإضافة"}}
    "total_plays": 0,
    "start_time": datetime.now()
}

# 🎵 رسائل مخصصة للمطور
custom_messages = {
    "welcome": "🎵 **Shams Music**  \n**بوت**  \n\n---\n\n⚡ **إهلا بك حبيبي العضو.**  \n\n✨ **ماذا يمكن لهذا البوت فعله؟**  \n• * بوت تشغيل الموسيقى في الكروبات *  \n• * تشغيل الأغاني من اليوتيوب *  \n• * تحميل المقاطع الصوتية *  \n• * البحث عن الموسيقى *  \n\n🎶 **أرفع آدمن وارسل تفعيل**  \n\n---\n\n👤 **المطور:** @{DEVELOPER_USERNAME}",
    "play": "🎵 **جاري تشغيل:** {song_name}\n\n⚡ يتم التشغيل في المجموعة...",
    "stop": "⏹️ **تم إيقاف التشغيل**\n\nاكتب `شغل` لتشغيل أغنية جديدة",
    "pause": "⏸️ **تم إيقاف التشغيل مؤقتاً**\n\nاكتب `اكمل` لاستئناف التشغيل",
    "resume": "▶️ **تم استئناف التشغيل**\n\nاكتب `قف` للإيقاف المؤقت",
    "skip": "⏭️ **تم تخطي الأغنية**\n\nجاري تشغيل التالية..."
}

# 💾 ملف حفظ البيانات
DATA_FILE = "bot_data.json"
MESSAGES_FILE = "custom_messages.json"

def save_data():
    """حفظ بيانات البوت"""
    try:
        data = {
            "stats": {
                "total_users": bot_stats["total_users"],
                "active_users": list(bot_stats["active_users"]),
                "groups": bot_stats["groups"],
                "total_plays": bot_stats["total_plays"],
                "start_time": bot_stats["start_time"].isoformat()
            },
            "messages": custom_messages
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"خطأ في حفظ البيانات: {e}")

def load_data():
    """تحميل بيانات البوت"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                bot_stats["total_users"] = data["stats"]["total_users"]
                bot_stats["active_users"] = set(data["stats"]["active_users"])
                bot_stats["groups"] = data["stats"]["groups"]
                bot_stats["total_plays"] = data["stats"]["total_plays"]
                bot_stats["start_time"] = datetime.fromisoformat(data["stats"]["start_time"])
                
                # تحميل الرسائل المخصصة إذا كانت موجودة
                if "messages" in data:
                    custom_messages.update(data["messages"])
    except Exception as e:
        logging.error(f"خطأ في تحميل البيانات: {e}")

async def check_channel_subscription(user_id: int, bot) -> bool:
    """التحقق من اشتراك المستخدم في القناة"""
    try:
        chat_member = await bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
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

📢 @{CHANNEL_USERNAME}
    """
    
    await update.message.reply_text(subscription_text, reply_markup=reply_markup)

async def update_stats(user_id: int, chat_id: int, chat_type: str, chat_title: str = None, member_count: int = None):
    """تحديث إحصائيات البوت"""
    bot_stats["active_users"].add(user_id)
    bot_stats["total_users"] = len(bot_stats["active_users"])
    
    if chat_type == "group" or chat_type == "supergroup":
        if chat_id not in bot_stats["groups"]:
            bot_stats["groups"][chat_id] = {
                "title": chat_title or "مجموعة بدون اسم",
                "members": member_count or 0,
                "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "last_activity": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            bot_stats["groups"][chat_id]["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if member_count:
                bot_stats["groups"][chat_id]["members"] = member_count
            if chat_title:
                bot_stats["groups"][chat_id]["title"] = chat_title
    
    save_data()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء مع التحقق من الاشتراك"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title
    chat_type = update.effective_chat.type
    
    # تحديث الإحصائيات
    try:
        member_count = await update.effective_chat.get_member_count()
    except:
        member_count = 0
        
    await update_stats(user_id, chat_id, chat_type, chat_title, member_count)
    
    # إذا كان المطور، امنحه الوصول مباشرة
    if await is_developer(user_id, username):
        welcome_text = custom_messages["welcome"].format(DEVELOPER_USERNAME=DEVELOPER_USERNAME)
        keyboard = [
            [InlineKeyboardButton("📥 أضفني لمجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("👤 مطور البوت", url=f"https://t.me/{DEVELOPER_USERNAME}")],
            [InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{CHANNEL_USERNAME}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        return
    
    # التحقق من الاشتراك في القناة
    is_subscribed = await check_channel_subscription(user_id, context.bot)
    if not is_subscribed:
        await send_subscription_message(update, context)
        return
    
    # إذا كان مشتركاً - عرض القائمة الرئيسية
    welcome_text = custom_messages["welcome"].format(DEVELOPER_USERNAME=DEVELOPER_USERNAME)
    
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

# 🛠️ أوامر المطور الخاصة
async def set_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل رسالة الترحيب - للمطور فقط"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط")
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة رسالة الترحيب الجديدة\nمثال: `/setwelcome مرحباً بك في البوت 🌹`", parse_mode='Markdown')
        return
    
    new_welcome = " ".join(context.args)
    custom_messages["welcome"] = new_welcome
    save_data()
    
    await update.message.reply_text("✅ **تم تحديث رسالة الترحيب بنجاح!**")

async def set_play_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل رسالة التشغيل - للمطور فقط"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط")
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة رسالة التشغيل الجديدة\nمثال: `/setplaymsg 🎶 جاري تشغيل: {song_name}`", parse_mode='Markdown')
        return
    
    new_play_msg = " ".join(context.args)
    custom_messages["play"] = new_play_msg
    save_data()
    
    await update.message.reply_text("✅ **تم تحديث رسالة التشغيل بنجاح!**")

async def set_stop_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تعديل رسالة الإيقاف - للمطور فقط"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط")
        return
    
    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة رسالة الإيقاف الجديدة\nمثال: `/setstopmsg ⏹️ تم إيقاف التشغيل`", parse_mode='Markdown')
        return
    
    new_stop_msg = " ".join(context.args)
    custom_messages["stop"] = new_stop_msg
    save_data()
    
    await update.message.reply_text("✅ **تم تحديث رسالة الإيقاف بنجاح!**")

async def show_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الإعدادات الحالية - للمطور فقط"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط")
        return
    
    settings_text = f"""
⚙️ **الإعدادات الحالية:**

📝 **رسالة الترحيب:**
{custom_messages['welcome']}

🎵 **رسالة التشغيل:**
{custom_messages['play']}

⏹️ **رسالة الإيقاف:**
{custom_messages['stop']}

⏸️ **رسالة الإيقاف المؤقت:**
{custom_messages['pause']}

▶️ **رسالة الاستئناف:**
{custom_messages['resume']}

⏭️ **رسالة التخطي:**
{custom_messages['skip']}
    """
    
    await update.message.reply_text(settings_text)

async def reset_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إعادة تعيين الرسائل - للمطور فقط"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط")
        return
    
    # الرسائل الافتراضية
    default_messages = {
        "welcome": "🎵 **Shams Music**  \n**بوت**  \n\n---\n\n⚡ **إهلا بك حبيبي العضو.**  \n\n✨ **ماذا يمكن لهذا البوت فعله؟**  \n• * بوت تشغيل الموسيقى في الكروبات *  \n• * تشغيل الأغاني من اليوتيوب *  \n• * تحميل المقاطع الصوتية *  \n• * البحث عن الموسيقى *  \n\n🎶 **أرفع آدمن وارسل تفعيل**  \n\n---\n\n👤 **المطور:** @{DEVELOPER_USERNAME}",
        "play": "🎵 **جاري تشغيل:** {song_name}\n\n⚡ يتم التشغيل في المجموعة...",
        "stop": "⏹️ **تم إيقاف التشغيل**\n\nاكتب `شغل` لتشغيل أغنية جديدة",
        "pause": "⏸️ **تم إيقاف التشغيل مؤقتاً**\n\nاكتب `اكمل` لاستئناف التشغيل",
        "resume": "▶️ **تم استئناف التشغيل**\n\nاكتب `قف` للإيقاف المؤقت",
        "skip": "⏭️ **تم تخطي الأغنية**\n\nجاري تشغيل التالية..."
    }
    
    custom_messages.update(default_messages)
    save_data()
    
    await update.message.reply_text("✅ **تم إعادة تعيين جميع الرسائل إلى الإعدادات الافتراضية!**")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر الإحصائيات مع تفاصيل المجموعات - للمطور فقط"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    if not await is_developer(user_id, username):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط")
        return
    
    # حساب مدة التشغيل
    uptime = datetime.now() - bot_stats["start_time"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # تفاصيل المجموعات
    groups_list = ""
    for i, (chat_id, group_info) in enumerate(list(bot_stats["groups"].items())[:10], 1):  # عرض أول 10 مجموعات فقط
        groups_list += f"{i}. {group_info['title']} - {group_info['members']} عضو\n"
    
    if len(bot_stats["groups"]) > 10:
        groups_list += f"\n... و {len(bot_stats['groups']) - 10} مجموعة أخرى"
    
    stats_text = f"""
📊 **إحصائيات البوت**

👥 **إجمالي المستخدمين:** {bot_stats['total_users']}
🎯 **المستخدمين النشطين:** {len(bot_stats['active_users'])}
📢 **عدد المجموعات:** {len(bot_stats['groups'])}
🎵 **مرات التشغيل:** {bot_stats['total_plays']}

⏰ **مدة التشغيل:** {hours} ساعة {minutes} دقيقة
🕒 **بدء التشغيل:** {bot_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}

📋 **المجموعات النشطة:**
{groups_list if groups_list else "لا توجد مجموعات نشطة"}

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
        
        is_subscribed = await check_channel_subscription(user_id, context.bot)
        if is_subscribed:
            await query.message.reply_text("✅ **تم التحقق بنجاح! شكراً لاشتراكك.**\n\nاكتب /start للبدء! 🎉")
        else:
            await query.message.reply_text("❌ **لم يتم العثور على اشتراكك.**\n\nيرجى الانضمام للقناة أولاً ثم اضغط على زر التحقق مرة أخرى.")
    
    elif query.data == "play_music":
        if not await is_developer(user_id, username):
            is_subscribed = await check_channel_subscription(user_id, context.bot)
            if not is_subscribed:
                await send_subscription_message(update, context)
                return
        
        await query.message.reply_text("🎵 **استخدم الأوامر التالية:**\n\n`شغل اسم الأغنية` - للتشغيل المباشر\n`بحث اسم الأغنية` - للبحث\n`يوت اسم الأغنية` - للتحميل")

# 🎵 معالجة الأوامر النصية في المجموعات
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة جميع الرسائل النصية"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title
    text = update.message.text.strip()
    
    # تحديث الإحصائيات
    try:
        member_count = await update.effective_chat.get_member_count()
    except:
        member_count = 0
        
    await update_stats(user_id, chat_id, update.effective_chat.type, chat_title, member_count)
    
    # إذا كان المطور، امنحه الوصول مباشرة
    if await is_developer(user_id, username):
        if text.startswith('شغل '):
            song_name = text.replace('شغل ', '', 1).strip()
            if song_name:
                bot_stats["total_plays"] += 1
                save_data()
                
                play_msg = custom_messages["play"].format(song_name=song_name)
                await update.message.reply_text(play_msg)
            else:
                await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `شغل`\nمثال: `شغل حسام الرسام`")
            return
        
        elif text.startswith('بحث ') or text.startswith('ابحث '):
            if text.startswith('بحث '):
                song_name = text.replace('بحث ', '', 1).strip()
            else:
                song_name = text.replace('ابحث ', '', 1).strip()
                
            if song_name:
                await update.message.reply_text(f"🔍 **جاري البحث عن:** {song_name}\n\n📋 سيتم عرض النتائج قريباً...")
            else:
                await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `بحث`\nمثال: `بحث حسام الرسام`")
            return
        
        elif text.startswith('يوت '):
            song_name = text.replace('يوت ', '', 1).strip()
            if song_name:
                await update.message.reply_text(f"📥 **جاري تحميل:** {song_name}\n\n⏳ المدة: دقيقة واحدة\nسيتم إرسالها كملف صوتي...")
            else:
                await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `يوت`\nمثال: `يوت اغنية رومانسية`")
            return
        
        # أوامر التحكم
        elif text in ['قف', 'اكمل', 'تخطي', 'ايقاف']:
            await handle_control_commands(update, text)
            return
    
    # للمستخدمين العاديين - التحقق من الاشتراك أولاً
    is_subscribed = await check_channel_subscription(user_id, context.bot)
    if not is_subscribed:
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
        bot_stats["total_plays"] += 1
        save_data()
        
        song_name = text.replace('شغل ', '', 1).strip()
        if song_name:
            play_msg = custom_messages["play"].format(song_name=song_name)
            await update.message.reply_text(play_msg)
        else:
            await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `شغل`\nمثال: `شغل حسام الرسام`")
    
    elif text.startswith('بحث ') or text.startswith('ابحث '):
        if text.startswith('بحث '):
            song_name = text.replace('بحث ', '', 1).strip()
        else:
            song_name = text.replace('ابحث ', '', 1).strip()
            
        if song_name:
            await update.message.reply_text(f"🔍 **جاري البحث عن:** {song_name}\n\n📋 سيتم عرض النتائج قريباً...")
        else:
            await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `بحث`\nمثال: `بحث حسام الرسام`")
    
    elif text.startswith('يوت '):
        song_name = text.replace('يوت ', '', 1).strip()
        if song_name:
            await update.message.reply_text(f"📥 **جاري تحميل:** {song_name}\n\n⏳ المدة: دقيقة واحدة\nسيتم إرسالها كملف صوتي...")
        else:
            await update.message.reply_text("❌ يرجى كتابة اسم الأغنية بعد كلمة `يوت`\nمثال: `يوت اغنية رومانسية`")
    
    elif text in ['قف', 'اكمل', 'تخطي', 'ايقاف']:
        await handle_control_commands(update, text)

async def handle_control_commands(update: Update, command: str):
    """معالجة أوامر التحكم"""
    responses = {
        'قف': custom_messages["pause"],
        'اكمل': custom_messages["resume"],
        'تخطي': custom_messages["skip"],
        'ايقاف': custom_messages["stop"]
    }
    
    await update.message.reply_text(responses.get(command, "❌ أمر غير معروف"))

async def group_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة ترحيبية عند إضافة البوت للمجموعة"""
    welcome_text = f"""
🎵 **Shams Music**  
**بوت**  

---

⚡ **شكراً لإضافتي إلى مجموعتك**

🎶 **أوامر التشغيل:**
`شغل + اسم الأغنية` - تشغيل مباشر
`بحث + اسم الأغنية` - بحث في اليوتيوب
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
    # ✅ تحميل البيانات المحفوظة
    load_data()
    
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
    
    # 🛠️ أوامر المطور
    application.add_handler(CommandHandler("setwelcome", set_welcome_message))
    application.add_handler(CommandHandler("setplaymsg", set_play_message))
    application.add_handler(CommandHandler("setstopmsg", set_stop_message))
    application.add_handler(CommandHandler("settings", show_settings))
    application.add_handler(CommandHandler("resetmsgs", reset_messages))
    
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
    print("⚡ الأوامر الجاهزة: شغل، بحث، يوت، قف، اكمل، تخطي، ايقاف")
    print("🛠️ أوامر المطور: /setwelcome, /setplaymsg, /setstopmsg, /settings, /resetmsgs")
    print("💾 نظام حفظ البيانات مفعل")
    
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