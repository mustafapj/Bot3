from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# بيانات المطور
DEVELOPER_USERNAME = "@pw19k"
BOT_TOKEN = "7087784225:AAF-TUMXou11lHOr5VLRq37PgCEbOBqKH3U"

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("الاستفسار", callback_data='inquiry')],
        [InlineKeyboardButton("الاسعار", callback_data='prices')],
        [InlineKeyboardButton("الخدمات", callback_data='services')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('مرحباً! اختر أحد الخيارات:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == 'inquiry':
        response_text = """
        للاستفسار، يرجى التواصل مع المطور مباشرة:
        {}
        """.format(DEVELOPER_USERNAME)
        query.edit_message_text(text=response_text)
    
    elif query.data == 'prices':
        prices_text = """
        🏷️ أسعار خدمات قنوات تيليجرام:

        • جروب تيليجرام إنشاء 2022: من 5$ إلى 10$
        • جروب تيليجرام إنشاء 2023: من 1$ إلى 3$

        للطلب أو الاستفسار، تواصل مع المطور:
        {}
        """.format(DEVELOPER_USERNAME)
        query.edit_message_text(text=prices_text)
    
    elif query.data == 'services':
        services_text = """
        🛠️ الخدمات المتاحة:

        1. إنشاء مواقع ويب
        2. إنشاء التطبيقات المصغرة
        3. دعم وزيادة متابعين انستقرام
        4. دعم وزيادة أعضاء تيليجرام

        للطلب أو الاستفسار، تواصل مع المطور:
        {}
        """.format(DEVELOPER_USERNAME)
        query.edit_message_text(text=services_text)

def main() -> None:
    updater = Updater(BOT_TOKEN)
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()