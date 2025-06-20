from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, Application

# بيانات المطور
DEVELOPER_USERNAME = "@pw19k"
BOT_TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("الاستفسار", callback_data='inquiry')],
        [InlineKeyboardButton("الاسعار", callback_data='prices')],
        [InlineKeyboardButton("الخدمات", callback_data='services')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('مرحباً! اختر أحد الخيارات:', reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'inquiry':
        response_text = f"""
        للاستفسار، يرجى التواصل مع المطور مباشرة:
        {DEVELOPER_USERNAME}
        """
        await query.edit_message_text(text=response_text)
    
    elif query.data == 'prices':
        prices_text = f"""
        🏷️ أسعار خدمات قنوات تيليجرام:

        • جروب تيليجرام إنشاء 2022: من 5$ إلى 10$
        • جروب تيليجرام إنشاء 2023: من 1$ إلى 3$

        للطلب أو الاستفسار، تواصل مع المطور:
        {DEVELOPER_USERNAME}
        """
        await query.edit_message_text(text=prices_text)
    
    elif query.data == 'services':
        services_text = f"""
        🛠️ الخدمات المتاحة:

        1. إنشاء مواقع ويب
        2. إنشاء التطبيقات المصغرة
        3. دعم وزيادة متابعين انستقرام
        4. دعم وزيادة أعضاء تيليجرام

        للطلب أو الاستفسار، تواصل مع المطور:
        {DEVELOPER_USERNAME}
        """
        await query.edit_message_text(text=services_text)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()