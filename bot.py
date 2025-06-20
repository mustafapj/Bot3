from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# بيانات المطور
DEVELOPER_USERNAME = "@pw19k"
BOT_TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"

# تعريف الأزرار الرئيسية
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["الاستفسار", "الاسعار"],
        ["الخدمات"]
    ],
    resize_keyboard=True,
    persistent=True
)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "مرحباً! اختر أحد الخيارات من الأزرار أدناه:",
        reply_markup=MAIN_KEYBOARD
    )

async def handle_messages(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    
    if text == "الاستفسار":
        response_text = f"""
        للاستفسار، يرجى التواصل مع المطور مباشرة:
        {DEVELOPER_USERNAME}
        """
        await update.message.reply_text(response_text)
    
    elif text == "الاسعار":
        prices_text = f"""
        🏷️ أسعار خدمات قنوات تيليجرام:

        • جروب تيليجرام إنشاء 2022: من 5$ إلى 10$
        • إنشاء حساب تيليجرام: (ليس إنشاء جروب) من 1$ إلى 3$
        • جروب تيليجرام إنشاء 2023: من 1$ إلى 3$

        للطلب أو الاستفسار، تواصل مع المطور:
        {DEVELOPER_USERNAME}
        """
        await update.message.reply_text(prices_text)
    
    elif text == "الخدمات":
        services_text = f"""
        🛠️ الخدمات المتاحة:

        1. إنشاء مواقع ويب
        2. إنشاء التطبيقات المصغرة
        3. دعم وزيادة متابعين انستقرام
        4. دعم وزيادة أعضاء تيليجرام

        للطلب أو الاستفسار، تواصل مع المطور:
        {DEVELOPER_USERNAME}
        """
        await update.message.reply_text(services_text)
    
    else:
        await update.message.reply_text(
            "اختر أحد الخيارات من الأزرار أدناه:",
            reply_markup=MAIN_KEYBOARD
        )

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    application.run_polling()

if __name__ == "__main__":
    main()