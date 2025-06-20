from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# بيانات المطور
DEVELOPER_USERNAME = "@pw19k"
BOT_TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"

# تعريف الأزرار الرئيسية
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["⚜️ الاستفسار", "⚜️ الاسعار"],
        ["⚜️ الخدمات"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        "مرحباً! اختر أحد الخيارات من الأزرار أدناه:",
        reply_markup=MAIN_KEYBOARD
    )

async def handle_messages(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    
    if "الاستفسار" in text:
        response_text = f"""
        ⚜️ للاستفسار، يرجى التواصل مع المطور مباشرة:
        {DEVELOPER_USERNAME}
        """
        await update.message.reply_text(response_text)
    
    elif "الاسعار" in text:
        prices_text = f"""
        ⚜️ عروض الأسعار:
        
        ⚜️ شراء جروبات تيليجرام إنشاء 2022:
        من 5 دولار إلى 10 دولار
        
        ⚜️ شراء جروبات تيليجرام إنشاء 2023:
        من 1 دولار إلى 3 دولار

        ⚜️ للطلب أو الاستفسار، تواصل مع المطور:
        {DEVELOPER_USERNAME}
        """
        await update.message.reply_text(prices_text)
    
    elif "الخدمات" in text:
        services_text = f"""
        ⚜️ قائمة الخدمات المتاحة:

        ⚜️ إنشاء مواقع ويب
        ⚜️ إنشاء التطبيقات المصغرة
        ⚜️ إنشاء بوتات تيليجرام
        ⚜️ دعم وزيادة متابعين انستقرام
        ⚜️ دعم وزيادة أعضاء تيليجرام

        ⚜️ للطلب أو الاستفسار، تواصل مع المطور:
        {DEVELOPER_USERNAME}
        """
        await update.message.reply_text(services_text)
    
    else:
        await update.message.reply_text(
            "⚜️ اختر أحد الخيارات من الأزرار أدناه:",
            reply_markup=MAIN_KEYBOARD
        )

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    application.run_polling()

if __name__ == "__main__":
    main()