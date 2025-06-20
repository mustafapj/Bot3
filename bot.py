import os
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# الطريقة الصحيحة لقراءة التوكن
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U")
DEVELOPER_USERNAME = "@pw19k"
REQUIRED_CHANNEL = "@e2m_2"

if not BOT_TOKEN:
    raise ValueError("لم يتم تعيين توكن البوت!")

# تعريف الأزرار الرئيسية
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["⚜️ الاستفسار", "⚜️ الاسعار"],
        ["⚜️ الخدمات"]
    ],
    resize_keyboard=True
)

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status not in ['left', 'kicked']
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_subscription(update.effective_user.id, context):
        keyboard = [
            [InlineKeyboardButton("⚜️ اشترك في القناة", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")],
            [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")]
        ]
        await update.message.reply_text(
            f"⚠️ عليك الاشتراك في قناة البوت أولاً:\n{REQUIRED_CHANNEL}",
            reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    await update.message.reply_text(
        "مرحباً بك في بوت الخدمات! اختر أحد الخيارات من الأزرار أدناه:",
        reply_markup=MAIN_KEYBOARD)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_subscription(update.effective_user.id, context):
        await start(update, context)
        return

    text = update.message.text
    
    if "الاستفسار" in text:
        await update.message.reply_text(f"⚜️ للاستفسار، يرجى التواصل مع المطور مباشرة:\n{DEVELOPER_USERNAME}")
    
    elif "الاسعار" in text:
        await update.message.reply_text(f"""⚜️ عروض الأسعار:
        
⚜️ شراء جروبات تيليجرام إنشاء 2022:
من 5 دولار إلى 10 دولار

⚜️ شراء جروبات تيليجرام إنشاء 2023:
من 1 دولار إلى 3 دولار

⚜️ للطلب أو الاستفسار:
{DEVELOPER_USERNAME}""")
    
    elif "الخدمات" in text:
        await update.message.reply_text(f"""⚜️ قائمة الخدمات المتاحة:

⚜️ إنشاء مواقع ويب
⚜️ إنشاء التطبيقات المصغرة
⚜️ إنشاء بوتات تيليجرام
⚜️ دعم وزيادة متابعين انستقرام
⚜️ دعم وزيادة أعضاء تيليجرام

⚜️ للطلب أو الاستفسار:
{DEVELOPER_USERNAME}""")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == "check_sub":
        if await check_subscription(query.from_user.id, context):
            await query.edit_message_text("✅ تم التحقق من اشتراكك بنجاح!")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="مرحباً بك! اختر أحد الخيارات:",
                reply_markup=MAIN_KEYBOARD)
        else:
            await query.answer("⚠️ لم يتم الاشتراك بعد!", show_alert=True)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    application.run_polling()

if __name__ == "__main__":
    main()