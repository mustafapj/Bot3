from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from credentials import DEVELOPER_USERNAME, CHANNEL_USERNAME

def msg_welcome(name, bot_username):
    text = f"""
🎵 **ShamsMusic 2.7 — Monitor Edition**

👋 مرحباً **{name}!**

🎶 استخدم الأوامر التالية للتحكم بالموسيقى:
- `/play [اسم الأغنية]` 🎧
- `/pause` ⏸️
- `/resume` ▶️
- `/queue` 📜
- `/now` 🔊

⚙️ بوت احترافي لتشغيل الموسيقى وإدارتها.
"""
    keyboard = [
        [InlineKeyboardButton("📥 أضفني لمجموعتك", url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            InlineKeyboardButton("👤 المطور", url=f"https://t.me/{DEVELOPER_USERNAME}"),
            InlineKeyboardButton("📢 القناة", url=f"https://t.me/{CHANNEL_USERNAME}")
        ]
    ]
    return {"text": text, "reply_markup": InlineKeyboardMarkup(keyboard), "parse_mode": "Markdown"}

def msg_subscribe_required():
    text = f"❌ يرجى الاشتراك في قناة البوت أولاً\n👉 @{CHANNEL_USERNAME}"
    keyboard = [
        [InlineKeyboardButton("📢 القناة الرسمية", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")]
    ]
    return {"text": text, "reply_markup": InlineKeyboardMarkup(keyboard)}

def msg_playing(song): return {"text": f"🎶 **جاري تشغيل:** `{song}`", "parse_mode": "Markdown"}
def msg_paused(): return {"text": "⏸️ **تم إيقاف الموسيقى مؤقتًا**", "parse_mode": "Markdown"}
def msg_resumed(): return {"text": "▶️ **تم استئناف التشغيل**", "parse_mode": "Markdown"}

def msg_queue(queue):
    if not queue:
        return {"text": "📭 **قائمة الانتظار فارغة.**", "parse_mode": "Markdown"}
    q = "\n".join([f"{i+1}. {song}" for i, song in enumerate(queue)])
    return {"text": f"📜 **قائمة الانتظار:**\n\n{q}", "parse_mode": "Markdown"}

def msg_now_playing(current):
    if not current:
        return {"text": "❌ لا يوجد تشغيل حالياً", "parse_mode": "Markdown"}
    return {"text": f"🎧 **الآن يتم تشغيل:** `{current}`", "parse_mode": "Markdown"}

def msg_status(uptime, users, groups, stats):
    hours = int(uptime.total_seconds() // 3600)
    minutes = int((uptime.total_seconds() % 3600) // 60)
    return {
        "text": f"""
📊 **لوحة مراقبة البوت**

🕒 التشغيل منذ: {hours} ساعة و {minutes} دقيقة
👥 المستخدمين المسجلين: {len(users)}
🏠 المجموعات النشطة: {len(groups)}
🎵 مرات التشغيل: {stats['total_plays']}

🔧 ShamsMusic يعمل بكفاءة تامة ⚡
""",
        "parse_mode": "Markdown"
    }