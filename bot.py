import os
import json
import logging
import asyncio
from datetime import datetime
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes, MessageHandler, filters, ChatMemberHandler
)

# الملفات الداخلية
from config import *
from credentials import *
from messages import *
from utils.music_manager import *
from utils.helpers import *

# إعداد السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ShamsMusic")

# بيانات التشغيل المؤقتة
bot_stats = {
    "start_time": datetime.now(),
    "total_plays": 0
}

# ملفات البيانات
USERS_FILE = "data/users.json"
GROUPS_FILE = "data/groups.json"
STATS_FILE = "data/stats.json"

# ========= أدوات تخزين ========= #
def load_json(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write("{}")
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ========= مراقبة المستخدمين والمجموعات ========= #
def add_user(user_id):
    users = load_json(USERS_FILE)
    if str(user_id) not in users:
        users[str(user_id)] = {"joined_at": str(datetime.now())}
        save_json(USERS_FILE, users)

def add_group(chat_id, title):
    groups = load_json(GROUPS_FILE)
    if str(chat_id) not in groups:
        groups[str(chat_id)] = {"title": title, "added_at": str(datetime.now())}
        save_json(GROUPS_FILE, groups)

# ========= الأوامر ========= #
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    # الاشتراك الإجباري
    if not await is_developer(user.id, user.username):
        if not await check_channel_subscription(user.id, context.bot):
            await update.message.reply_text(**msg_subscribe_required())
            return

    # تسجيل المستخدم أو المجموعة
    if chat.type == "private":
        add_user(user.id)
    elif chat.type in ["group", "supergroup"]:
        add_group(chat.id, chat.title)

    await update.message.reply_text(**msg_welcome(user.first_name, context.bot.username))


async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ اكتب اسم الأغنية بعد /play")
        return

    song = " ".join(context.args)
    await update.message.reply_text(**msg_playing(song))
    await add_to_queue(update.effective_chat.id, song)
    bot_stats["total_plays"] += 1


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await pause_music(update.effective_chat.id)
    await update.message.reply_text(**msg_paused())


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await resume_music(update.effective_chat.id)
    await update.message.reply_text(**msg_resumed())


async def queue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    queue = await get_queue(update.effective_chat.id)
    await update.message.reply_text(**msg_queue(queue))


async def now_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = await get_current_track(update.effective_chat.id)
    await update.message.reply_text(**msg_now_playing(current))


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إحصائيات عامة للمطور"""
    user = update.effective_user
    if not await is_developer(user.id, user.username):
        await update.message.reply_text("❌ هذا الأمر للمطور فقط!")
        return

    users = load_json(USERS_FILE)
    groups = load_json(GROUPS_FILE)
    uptime = datetime.now() - bot_stats["start_time"]
    await update.message.reply_text(**msg_status(uptime, users, groups, bot_stats))


# ========= التشغيل الرئيسي ========= #
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("play", play_command))
    app.add_handler(CommandHandler("pause", pause_command))
    app.add_handler(CommandHandler("resume", resume_command))
    app.add_handler(CommandHandler("queue", queue_command))
    app.add_handler(CommandHandler("now", now_command))
    app.add_handler(CommandHandler("status", status_command))

    await app.bot.set_my_commands([
        BotCommand("start", "بدء الاستخدام 🚀"),
        BotCommand("play", "تشغيل موسيقى 🎵"),
        BotCommand("pause", "إيقاف مؤقت ⏸️"),
        BotCommand("resume", "استئناف ▶️"),
        BotCommand("queue", "قائمة الانتظار 📜"),
        BotCommand("now", "ما يُشغل الآن 🎧"),
        BotCommand("status", "إحصائيات عامة 📈")
    ])

    print("✅ ShamsMusic 2.7 Monitor Edition يعمل الآن...")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())