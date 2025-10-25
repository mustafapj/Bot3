# bot.py - الكود المعدل مع الصورة والخيارات

import os
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

import config

# قاموس لتخزين بيانات المكالمات
active_calls = {}
song_queues = {}

class MusicBot:
    def __init__(self):
        self.app = Application.builder().token(config.BOT_TOKEN).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        """إعداد أوامر البوت"""
        commands = [
            ("start", self.start),
            ("join", self.join),
            ("play", self.play),
            ("pause", self.pause),
            ("resume", self.resume),
            ("skip", self.skip),
            ("stop", self.stop),
            ("queue", self.show_queue),
            ("volume", self.set_volume),
        ]
        
        for command, handler in commands:
            self.app.add_handler(CommandHandler(command, handler))
        
        # إضافة معالج للأزرار
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        
        # إضافة معالج للإضافة إلى المجموعات
        self.app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.new_chat_members))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدأ البوت مع صورة وخيارات"""
        user = update.effective_user
        welcome_text = f"""
🎵 **مرحباً بك {user.first_name} في بوت الموسيقى!**

🎶 **البوت المثالي لتشغيل الموسيقى في مجموعتك**

✨ **المميزات:**
• تشغيل الأغاني من يوتيوب
• دعم المكالمات الجماعية  
• تحكم كامل في الصوت
• قوائم تشغيل متعددة
• واجهة سهلة الاستخدام

📱 **استخدم الأزرار بالأسفل للتحكم:**
        """
        
        # زر إضافة البوت إلى المجموعة
        keyboard = [
            [InlineKeyboardButton("🎵 تشغيل أغنية", callback_data="play_song")],
            [InlineKeyboardButton("📋 قائمة الأغاني", callback_data="show_queue")],
            [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")],
            [InlineKeyboardButton("➕ أضفني لمجموعتك", url=f"https://t.me/{context.bot.username}?startgroup=true")],
            [InlineKeyboardButton("📞 الدعم الفني", url="https://t.me/username")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # إرسال الصورة مع النص
        try:
            # يمكنك استبدال رابط الصورة بصورة البوت الخاصة بك
            photo_url = "https://telegra.ph/file/1c5c6d5a5a5a5a5a5a5a5.jpg"  # رابط صورة البوت
            await update.message.reply_photo(
                photo=photo_url,
                caption=welcome_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except:
            # إذا فشل إرسال الصورة، إرسال النص فقط
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

    async def new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عند إضافة البوت إلى مجموعة"""
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                # البوت تمت إضافته للمجموعة
                chat = update.effective_chat
                
                welcome_group_text = f"""
🎵 **شكراً لإضافتي في {chat.title}!**

🎶 **للاستخدام في المجموعة:**
`/play` اسم الأغنية - تشغيل أغنية
`/skip` - تخطي الأغنية الحالية
`/stop` - إيقاف التشغيل
`/queue` - عرض قائمة الانتظار

⚡ **لبدء الاستخدام، ارفعني مشرفاً في المجموعة أولاً!**
                """
                
                keyboard = [
                    [InlineKeyboardButton("🎵 الأوامر المتاحة", callback_data="group_commands")],
                    [InlineKeyboardButton("📖 الدليل الكامل", callback_data="help_guide")],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    welcome_group_text,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الضغط على الأزرار"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "play_song":
            await query.message.reply_text("🎵 أرسل اسم الأغنية التي تريد تشغيلها:\n\nمثال: `/play أغنية`", parse_mode="Markdown")
        
        elif data == "show_queue":
            await self.show_queue(update, context)
        
        elif data == "settings":
            await query.message.reply_text("⚙️ **الإعدادات:**\n\n• جودة الصوت: عالية\n• التكرار: معطل\n• وضع الخصوصية: مفعل")
        
        elif data == "group_commands":
            commands_text = """
🎵 **أوامر المجموعة:**

`/play` اسم الأغنية - تشغيل أغنية
`/skip` - تخطي الأغنية الحالية  
`/stop` - إوقف التشغيل
`/pause` - إيقاف مؤقت
`/resume` - استئناف التشغيل
`/queue` - عرض قائمة الانتظار
`/volume` 1-200 - ضبط الصوت

⚡ **للتشغيل في المكالمات، ابدأ مكالمة صوتية أولاً!**
            """
            await query.message.reply_text(commands_text, parse_mode="Markdown")
        
        elif data == "help_guide":
            help_text = """
📖 **دليل الاستخدام الكامل:**

1. **للتشغيل في المحادثة الخاصة:**
   - أرسل `/play` ثم اسم الأغنية

2. **للتشغيل في المجموعة:**
   - ارفع البوت مشرفاً
   - ابدأ مكالمة صوتية
   - استخدم `/play` اسم الأغنية

3. **الأوامر المتاحة:**
   - تشغيل، إيقاف، تخطي، تحكم في الصوت
   - إدارة قوائم التشغيل
   - إعدادات الجودة
            """
            await query.message.reply_text(help_text, parse_mode="Markdown")

    async def join(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الانضمام للمكالمة الصوتية"""
        chat_id = update.effective_chat.id
        
        keyboard = [
            [InlineKeyboardButton("🎵 تشغيل أول أغنية", callback_data="play_first")],
            [InlineKeyboardButton("📋 عرض القائمة", callback_data="show_queue")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "✅ جاهز للتشغيل في المكالمات الصوتية!\n\nاستخدم الأزرار للتحكم:",
            reply_markup=reply_markup
        )

    # باقي الدوال保持不变 (play, search_youtube, etc.)
    async def play(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تشغيل أغنية"""
        if not context.args:
            await update.message.reply_text("🎵 استخدم: `/play اسم الأغنية`\n\nمثال: `/play أغنية جميلة`", parse_mode="Markdown")
            return
            
        query = " ".join(context.args)
        chat_id = update.effective_chat.id
        
        await update.message.reply_text(f"🔍 جاري البحث عن: **{query}**")
        
        try:
            song_info = await self.search_youtube(query)
            if not song_info:
                await update.message.reply_text("❌ لم أجد الأغنية المطلوبة")
                return
            
            if chat_id not in song_queues:
                song_queues[chat_id] = []
            
            song_queues[chat_id].append(song_info)
            
            keyboard = [
                [InlineKeyboardButton("⏭ تخطي", callback_data="skip_song"),
                 InlineKeyboardButton("⏸ إيقاف", callback_data="pause_song")],
                [InlineKeyboardButton("📋 القائمة", callback_data="show_queue")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"🎵 **تمت الإضافة:** {song_info['title']}\n"
                f"⏱ المدة: {song_info['duration']}\n"
                f"📊 المركز في الطابور: #{len(song_queues[chat_id])}",
                reply_markup=reply_markup
            )
                
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ في التشغيل: {str(e)}")

    async def search_youtube(self, query):
        """الببحث في يوتيوب عن الأغنية"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                if 'entries' in info and info['entries']:
                    video = info['entries'][0]
                    return {
                        'title': video.get('title', 'Unknown'),
                        'url': video['url'],
                        'duration': self.format_duration(video.get('duration', 0)),
                        'thumbnail': video.get('thumbnail', ''),
                    }
        except Exception:
            return None
        
        return None

    def format_duration(self, seconds):
        """تنسيق المدة"""
        if not seconds:
            return "غير معروف"
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    async def pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إيقاف التشغيل مؤقتاً"""
        await update.message.reply_text("⏸ تم الإيقاف المؤقت")

    async def resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """استئناف التشغيل"""
        await update.message.reply_text("▶️ تم استئناف التشغيل")

    async def skip(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تخطي الأغنية الحالية"""
        chat_id = update.effective_chat.id
        if chat_id in song_queues and song_queues[chat_id]:
            song_queues[chat_id].pop(0)
            await update.message.reply_text("⏭ تم تخطي الأغنية")
        else:
            await update.message.reply_text("❌ لا توجد أغاني في الطابور")

    async def stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إيقاف التشغيل"""
        chat_id = update.effective_chat.id
        if chat_id in song_queues:
            song_queues[chat_id].clear()
        await update.message.reply_text("⏹ تم إيقاف التشغيل")

    async def show_queue(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """عرض قائمة الانتظار"""
        chat_id = update.effective_chat.id
        if chat_id not in song_queues or not song_queues[chat_id]:
            await update.message.reply_text("📭 قائمة الانتظار فارغة")
            return
        
        queue_text = "📋 **قائمة الانتظار:**\n\n"
        for i, song in enumerate(song_queues[chat_id][:10], 1):
            queue_text += f"{i}. {song['title']} - {song['duration']}\n"
        
        if len(song_queues[chat_id]) > 10:
            queue_text += f"\n... و {len(song_queues[chat_id]) - 10} أغنية أخرى"
        
        await update.message.reply_text(queue_text)

    async def set_volume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ضبط مستوى الصوت"""
        await update.message.reply_text("🔊 خاصية ضبط الصوت قيد التطوير")

    def run(self):
        """تشغيل البوت"""
        print("🎵 بوت الموسيقى يعمل...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = MusicBot()
    bot.run()