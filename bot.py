# bot.py - الكود المعدل بدون pytgcalls

import os
import asyncio
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# إزالة استيراد pytgcalls
# from pytgcalls import PyTgCalls
# from pytgcalls.types import AudioPiped
# from pytgcalls.types.input_stream import InputAudioStream

import config

# قاموس لتخزين بيانات المكالمات
active_calls = {}
song_queues = {}

class MusicBot:
    def __init__(self):
        self.app = Application.builder().token(config.BOT_TOKEN).build()
        # إزالة pytgcalls
        # self.pytgcalls = PyTgCalls(client=None)
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

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """بدأ البوت"""
        welcome_text = """
        🎵 **مرحباً بك في بوت الموسيقى!**
        
        **الأوامر المتاحة:**
        /join - انضمام للمكالمة
        /play [اسم الأغنية] - تشغيل أغنية
        /pause - إيقاف مؤقت
        /resume - استئناف التشغيل
        /skip - تخطي الأغنية
        /stop - إوقف التشغيل
        /queue - عرض قائمة الانتظار
        /volume [1-200] - ضبط الصوت
        
        🌟 استمتع بالموسيقى!
        """
        await update.message.reply_text(welcome_text)

    async def join(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """الانضمام للمكالمة الصوتية"""
        chat_id = update.effective_chat.id
        await update.message.reply_text("✅ خاصية المكالمات الصوتية قيد التطوير")

    async def play(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """تشغيل أغنية"""
        if not context.args:
            await update.message.reply_text("🎵 استخدم: /play اسم الأغنية أو رابط يوتيوب")
            return
            
        query = " ".join(context.args)
        chat_id = update.effective_chat.id
        
        await update.message.reply_text(f"🔍 جاري البحث عن: **{query}**")
        
        try:
            # البحث عن الأغنية وتحويلها
            song_info = await self.search_youtube(query)
            if not song_info:
                await update.message.reply_text("❌ لم أجد الأغنية المطلوبة")
                return
            
            # إضافة للأغنية للطابور
            if chat_id not in song_queues:
                song_queues[chat_id] = []
            
            song_queues[chat_id].append(song_info)
            
            await update.message.reply_text(
                f"🎵 تمت الإضافة: **{song_info['title']}**\n"
                f"⏱ المدة: {song_info['duration']}\n"
                f"📊 Position in queue: #{len(song_queues[chat_id])}"
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
            return "Unknown"
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    async def pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إيقاف التشغيل مؤقتاً"""
        await update.message.reply_text("⏸ خاصية الإيقاف قيد التطوير")

    async def resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """استئناف التشغيل"""
        await update.message.reply_text("▶️ خاصية الاستئناف قيد التطوير")

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