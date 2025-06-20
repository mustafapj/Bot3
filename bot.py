from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# إعدادات البوت
BOT_TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"
CHANNEL_USERNAME = "@e2m_2"  # يجب أن يبدأ ب @

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status not in ['left', 'kicked']
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if not await check_subscription(user.id, context):
        await update.message.reply_text(
            "فضلاً عليك الاشتراك في قناة البوت أولاً:\n"
            "https://t.me/e2m_2\n\n"
            "بعد الاشتراك اضغط /start لبدء استخدام البوت"
        )
        return
    
    # إذا كان مشتركاً يعرض الرسالة الترحيبية
    await update.message.reply_text(
        "مرحباً بك في البوت! 🌟\n"
        "الآن يمكنك استخدام جميع الميزات المتاحة"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    
    # يحظر أي رسالة أخرى حتى الاشتراك
    app.add_handler(MessageHandler(filters.ALL, lambda u,c: None))
    
    app.run_polling()

if __name__ == "__main__":
    main()