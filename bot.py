import logging
import sys
import asyncio
from datetime import datetime
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# استيراد الإعدادات من config.py
try:
    from config import BOT_TOKEN, CHANNEL_USERNAME, DEVELOPER_USERNAME
    from config import READ_TIMEOUT, WRITE_TIMEOUT, CONNECT_TIMEOUT, POOL_TIMEOUT
    print("✅ تم تحميل الإعدادات بنجاح من config.py")
except ImportError as e:
    print(f"❌ خطأ في تحميل الإعدادات: {e}")
    sys.exit(1)

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# المطورون الأساسيون (صلاحيات في جميع المجموعات)
DEVELOPERS = ["pw19k"]  # يوزرات المطورين

# تخزين مالكي المجموعات
group_owners = {}

# ========== الدوال الأساسية ==========

async def detect_and_store_owner(chat_id, context):
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.status == 'creator':
                owner_id = admin.user.id
                group_owners[chat_id] = owner_id
                print(f"✅ تم التعرف على المالك: {owner_id} للمجموعة: {chat_id}")
                return True
        return False
    except Exception as e:
        print(f"❌ خطأ في التعرف على المالك: {e}")
        return False

async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        if not user or not chat:
            return False
        
        # ✅ المطورون الأساسيون
        if user.username and user.username.lower() in [dev.lower() for dev in DEVELOPERS]:
            return True
        
        # ✅ مالك المجموعة
        chat_id = chat.id
        
        if chat_id not in group_owners:
            await detect_and_store_owner(chat_id, context)
        
        if chat_id in group_owners and user.id == group_owners[chat_id]:
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error in authorization check: {e}")
        return False

# ========== الأوامر الرئيسية ==========

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        welcome_text = f"""
🎊 **مرحباً بك في بوت تايم المطور!**

🤖 **البوت الرسمي للمطور:** @{DEVELOPER_USERNAME}
📢 **قناة البوت:** @{CHANNEL_USERNAME}

⚡ **مميزات البوت:**
• حماية كاملة للمجموعات
• أوامر سريعة ومتقدمة
• تحكم كامل للمالكين
• إشعارات فورية

🎯 **لرؤية الأوامر اكتب:** /help

🔒 **ملاحظة:** الأوامر متاحة فقط لمالك المجموعة

📞 **للتواصل والدعم:** @{DEVELOPER_USERNAME}
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        print("✅ تم إرسال رسالة الترحيب بنجاح")
            
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        print(f"❌ خطأ في start: {e}")
        await update.message.reply_text("🎊 مرحباً بك في بوت تايم المطور!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_authorized(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
            return
            
        help_text = f"""
🎯 **أوامر البوت (للمالك فقط)**

**الأوامر الأساسية:**
/kick - طرد مستخدم (بالرد أو @username)
/mute - كتم مستخدم  
/unmute - إلغاء كتم
/ban - حظر مستخدم

**المطور:** @{DEVELOPER_USERNAME}
**القناة:** @{CHANNEL_USERNAME}

⚡ **مميزات البوت:**
• طرد أي عضو بغض النظر عن رتبته
• إشعارات خاصة للمالك
• أوامر سريعة ومتقدمة
        """
        await update.message.reply_text(help_text)
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await update.message.reply_text("❌ حدث خطأ في عرض المساعدة")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        info_text = f"""
🤖 **معلومات البوت**

📢 **القناة:** @{CHANNEL_USERNAME}
👨‍💻 **المطور:** @{DEVELOPER_USERNAME}

⚡ **البوت يعمل بنجاح!**
🎯 **مخصص لإدارة المجموعات - للمالك فقط**

📞 **للتواصل والدعم:** @{DEVELOPER_USERNAME}
        """
        await update.message.reply_text(info_text)
    except Exception as e:
        logger.error(f"Error in info command: {e}")
        await update.message.reply_text("❌ حدث خطأ في عرض المعلومات")

# ========== أوامر الإدارة ==========

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_authorized(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
            return
        
        target_user = None
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        elif context.args:
            target_username = context.args[0].replace('@', '')
            try:
                async for member in update.effective_chat.get_members():
                    if member.user.username and member.user.username.lower() == target_username.lower():
                        target_user = member.user
                        break
            except Exception as e:
                logger.error(f"Error finding user: {e}")
        
        if not target_user:
            await update.message.reply_text("⚠️ يرجى الرد على رسالة المستخدم أو كتابة: /kick @username")
            return
        
        # منع طرد المطورين
        if target_user.username and target_user.username.lower() in [dev.lower() for dev in DEVELOPERS]:
            await update.message.reply_text("❌ لا يمكن طرد المطور!")
            return
        
        bot_member = await update.effective_chat.get_member(context.bot.id)
        if not bot_member.can_restrict_members:
            await update.message.reply_text("❌ البوت ليس لديه صلاحية طرد الأعضاء!")
            return
        
        await update.effective_chat.ban_member(target_user.id)
        await update.effective_chat.unban_member(target_user.id)
        await update.message.reply_text(f"✅ تم طرد المستخدم {target_user.first_name} بنجاح!")
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء محاولة طرد المستخدم!")
        logger.error(f"Error kicking user: {e}")

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_authorized(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
            return
        
        target_user = None
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        elif context.args:
            target_username = context.args[0].replace('@', '')
            try:
                async for member in update.effective_chat.get_members():
                    if member.user.username and member.user.username.lower() == target_username.lower():
                        target_user = member.user
                        break
            except Exception as e:
                logger.error(f"Error finding user: {e}")
        
        if not target_user:
            await update.message.reply_text("⚠️ يرجى الرد على رسالة المستخدم أو كتابة: /mute @username")
            return
        
        bot_member = await update.effective_chat.get_member(context.bot.id)
        if not bot_member.can_restrict_members:
            await update.message.reply_text("❌ البوت ليس لديه صلاحية كتم الأعضاء!")
            return
        
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        )
        
        await update.effective_chat.restrict_member(target_user.id, permissions)
        await update.message.reply_text(f"🔇 تم كتم المستخدم {target_user.first_name} بنجاح!")
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء محاولة كتم المستخدم!")
        logger.error(f"Error muting user: {e}")

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_authorized(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
            return
        
        target_user = None
        
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        elif context.args:
            target_username = context.args[0].replace('@', '')
            try:
                async for member in update.effective_chat.get_members():
                    if member.user.username and member.user.username.lower() == target_username.lower():
                        target_user = member.user
                        break
            except Exception as e:
                logger.error(f"Error finding user: {e}")
        
        if not target_user:
            await update.message.reply_text("⚠️ يرجى الرد على رسالة المستخدم أو كتابة: /unmute @username")
            return
        
        bot_member = await update.effective_chat.get_member(context.bot.id)
        if not bot_member.can_restrict_members:
            await update.message.reply_text("❌ البوت ليس لديه صلاحية إلغاء الكتم!")
            return
        
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=False,
            can_invite_users=False,
            can_pin_messages=False
        )
        
        await update.effective_chat.restrict_member(target_user.id, permissions)
        await update.message.reply_text(f"🔊 تم إلغاء كتم المستخدم {target_user.first_name} بنجاح!")
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء محاولة إلغاء كتم المستخدم!")
        logger.error(f"Error unmuting user: {e}")

# ========== الكلمات السرية ==========

async def handle_secret_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not await is_authorized(update, context):
            return
        
        message_text = update.message.text.strip()
        
        # كتم - للكتم
        if message_text == "كتم" and update.message.reply_to_message:
            await update.message.delete()
            await mute_command(update, context)

        # توكل - للطرد
        elif message_text == "توكل" and update.message.reply_to_message:
            await update.message.delete()
            await kick_command(update, context)

    except Exception as e:
        logger.error(f"Error in secret commands: {e}")

# ========== التشغيل الرئيسي ==========

async def auto_detect_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.new_chat_members:
            for user in update.message.new_chat_members:
                if user.id == context.bot.id:
                    chat_id = update.effective_chat.id
                    await detect_and_store_owner(chat_id, context)
                    break
    except Exception as e:
        logger.error(f"Error in auto detect owner: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    try:
        print("🚀 بدء تشغيل بوت تايم المطور...")
        print(f"🤖 المطور: @{DEVELOPER_USERNAME}")
        print(f"📢 القناة: @{CHANNEL_USERNAME}")
        print("🎯 جاري تحميل الميزات...")
        
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة الأوامر
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("info", info_command))
        application.add_handler(CommandHandler("kick", kick_command))
        application.add_handler(CommandHandler("mute", mute_command))
        application.add_handler(CommandHandler("unmute", unmute_command))
        application.add_handler(CommandHandler("ban", kick_command))
        
        # الكلمات السرية
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_secret_commands))
        
        # التعرف على المالك
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, auto_detect_owner))
        
        application.add_error_handler(error_handler)
        
        print("✅ تم تحميل جميع الميزات بنجاح")
        print("🤖 البوت يعمل الآن...")
        
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    main()