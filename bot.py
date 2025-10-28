import logging
import sys
import asyncio
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

# التحقق من أن المرسل هو المالك
# التحقق من أن المرسل هو المالك @pw19k
async def is_owner(update: Update) -> bool:
    try:
        user = update.effective_user
        if not user:
            return False
        
        # التحقق مباشرة من يوزر المالك
        if user.username and user.username.lower() == "pw19k":
            return True
            
        # تحقق إضافي من صلاحيات المالك في المجموعة
        chat = update.effective_chat
        if chat:
            chat_member = await chat.get_member(user.id)
            if chat_member.status in ['creator', 'administrator']:
                return True
                
        return False
        
    except Exception as e:
        logger.error(f"Error in owner check: {e}")
        return False
            
        # الحصول على قائمة المشرفين
        admins = await chat.get_administrators()
        
        # المالك هو أول مشرف في القائمة
        owner = admins[0].user if admins else None
        
        if owner and user.id == owner.id:
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error in owner check: {e}")
        return False

# أمر الطرد بالرد أو اليوزر
async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
        return
    
    target_user = None
    
    # التحقق إذا كان الأمر عن طريق الرد
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    
    # إذا لم يكن رد، التحقق من اليوزر في الأمر
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
    
    try:
        # التحقق من أن البوت لديه الصلاحيات
        bot_member = await update.effective_chat.get_member(context.bot.id)
        if not bot_member.can_restrict_members:
            await update.message.reply_text("❌ البوت ليس لديه صلاحية طرد الأعضاء!")
            return
        
        # طرد المستخدم
        await update.effective_chat.ban_member(target_user.id)
        await update.effective_chat.unban_member(target_user.id)
        await update.message.reply_text(f"✅ تم طرد المستخدم {target_user.first_name} بنجاح!")
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء محاولة طرد المستخدم!")
        logger.error(f"Error kicking user: {e}")

# أمر الكتم بالرد أو اليوزر
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
        return
    
    target_user = None
    
    # التحقق إذا كان الأمر عن طريق الرد
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    
    # إذا لم يكن رد، التحقق من اليوزر في الأمر
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
    
    try:
        # التحقق من أن البوت لديه الصلاحيات
        bot_member = await update.effective_chat.get_member(context.bot.id)
        if not bot_member.can_restrict_members:
            await update.message.reply_text("❌ البوت ليس لديه صلاحية كتم الأعضاء!")
            return
        
        # كتم المستخدم
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

# أمر إلغاء الكتم بالرد أو اليوزر
async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
        return
    
    target_user = None
    
    # التحقق إذا كان الأمر عن طريق الرد
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    
    # إذا لم يكن رد، التحقق من اليوزر في الأمر
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
    
    try:
        # التحقق من أن البوت لديه الصلاحيات
        bot_member = await update.effective_chat.get_member(context.bot.id)
        if not bot_member.can_restrict_members:
            await update.message.reply_text("❌ البوت ليس لديه صلاحية إلغاء الكتم!")
            return
        
        # إلغاء كتم المستخدم
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

# أمر حظر المستخدم
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
        return
    
    target_user = None
    
    # التحقق إذا كان الأمر عن طريق الرد
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    
    # إذا لم يكن رد، التحقق من اليوزر في الأمر
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
        await update.message.reply_text("⚠️ يرجى الرد على رسالة المستخدم أو كتابة: /ban @username")
        return
    
    try:
        # التحقق من أن البوت لديه الصلاحيات
        bot_member = await update.effective_chat.get_member(context.bot.id)
        if not bot_member.can_restrict_members:
            await update.message.reply_text("❌ البوت ليس لديه صلاحية حظر الأعضاء!")
            return
        
        # حظر المستخدم
        await update.effective_chat.ban_member(target_user.id)
        await update.message.reply_text(f"🚫 تم حظر المستخدم {target_user.first_name} بنجاح!")
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء محاولة حظر المستخدم!")
        logger.error(f"Error banning user: {e}")

# أمر إلغاء الحظر
async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة: /unban @username")
        return
    
    target_username = context.args[0].replace('@', '')
    
    try:
        # التحقق من أن البوت لديه الصلاحيات
        bot_member = await update.effective_chat.get_member(context.bot.id)
        if not bot_member.can_restrict_members:
            await update.message.reply_text("❌ البوت ليس لديه صلاحية إلغاء الحظر!")
            return
        
        # إلغاء حظر المستخدم
        await update.effective_chat.unban_member(target_username)
        await update.message.reply_text(f"✅ تم إلغاء حظر المستخدم @{target_username} بنجاح!")
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء محاولة إلغاء الحظر!")
        logger.error(f"Error unbanning user: {e}")

# أمر معلومات البوت
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = f"""
🤖 **معلومات البوت**

📢 **القناة:** @{CHANNEL_USERNAME}
👨‍💻 **المطور:** @{DEVELOPER_USERNAME}

⚡ **البوت يعمل بنجاح!**
🎯 **مخصص لإدارة المجموعات - للمالك فقط**

📋 **الأوامر المتاحة:**
/kick - طرد مستخدم
/mute - كتم مستخدم  
/unmute - إلغاء كتم
/ban - حظر مستخدم
/unban - إلغاء حظر
/info - معلومات البوت
/help - المساعدة
    """
    await update.message.reply_text(info_text)

# أمر المساعدة
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
        return
        
    help_text = f"""
🎯 **أوامر البوت (للمالك فقط)**

**بالرد أو اليوزر:**
/kick - طرد مستخدم من المجموعة
/mute - كتم مستخدم في المجموعة  
/unmute - إلغاء كتم مستخدم
/ban - حظر مستخدم من المجموعة

**بالأمر فقط:**
/unban @username - إلغاء حظر مستخدم

**معلومات:**
/info - معلومات البوت
/help - عرض هذه الرسالة

📢 **القناة:** @{CHANNEL_USERNAME}
👨‍💻 **المطور:** @{DEVELOPER_USERNAME}

⚡ **مميزات البوت:**
• خاص بالمالك فقط
• يدعم الطرد والكتم بالرد أو اليوزر
• صلاحيات مطلقة للمالك
• آمن وسريع
    """
    await update.message.reply_text(help_text)

# أمر البدء
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await is_owner(update):
        await help_command(update, context)
    else:
        await update.message.reply_text("🔒 هذا البوت خاص بالمالك فقط!")

# معالجة الأخطاء
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    try:
        print("🚀 بدء تشغيل البوت...")
        
        # إنشاء تطبيق البوت مع إعدادات الوقت
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة handlers للأوامر
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("kick", kick_command))
        application.add_handler(CommandHandler("mute", mute_command))
        application.add_handler(CommandHandler("unmute", unmute_command))
        application.add_handler(CommandHandler("ban", ban_command))
        application.add_handler(CommandHandler("unban", unban_command))
        application.add_handler(CommandHandler("info", info_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # إضافة معالج الأخطاء
        application.add_error_handler(error_handler)
        
        print("✅ تم تحميل جميع الأوامر بنجاح")
        print(f"📢 القناة: @{CHANNEL_USERNAME}")
        print(f"👨‍💻 المطور: @{DEVELOPER_USERNAME}")
        print("🤖 البوت يعمل الآن...")
        
        # بدء البوت
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':
    main()