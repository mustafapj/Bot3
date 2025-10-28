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

# التحقق من أن المرسل هو المالك @pw19k
async def is_owner(update: Update) -> bool:
    try:
        user = update.effective_user
        if not user:
            return False
        
        # التحقق مباشرة من يوزر المالك
        if user.username and user.username.lower() == "pw19k":
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error in owner check: {e}")
        return False

# إرسال رسالة خاصة للمالك بالمعلومات
async def send_private_kick_info(context, target_user, action_type="طرد"):
    try:
        owner_id = "pw19k"  # يوزر المالك
        now = datetime.now()
        
        info_text = f"""
🔔 **إشعار {action_type}**

👤 **المستخدم:**
- الاسم: {target_user.first_name}
- اليوزر: @{target_user.username if target_user.username else 'لا يوجد'}
- الايدي: `{target_user.id}`

⏰ **التوقيت:**
- التاريخ: {now.strftime('%Y-%m-%d')}
- الوقت: {now.strftime('%H:%M:%S')}

📝 **الإجراء: {action_type}**
        """
        
        # إرسال رسالة خاصة للمالك
        await context.bot.send_message(
            chat_id=owner_id,
            text=info_text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error sending private message: {e}")

# معالجة الكلمات الخفية
async def handle_secret_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        return
    
    message_text = update.message.text.strip().lower()
    
    # كتم - للكتم
    if message_text == "كتم" and update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        try:
            # التحقق من صلاحيات البوت
            bot_member = await update.effective_chat.get_member(context.bot.id)
            if not bot_member.can_restrict_members:
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
            await update.message.delete()  # حذف رسالة "كتم"
            
            # إرسال رسالة خاصة للمالك
            await send_private_kick_info(context, target_user, "كتم سري")
            
        except Exception as e:
            logger.error(f"Error in secret mute: {e}")

    # توكل - للطرد
    elif message_text == "توكل" and update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        # منع طرد المالك
        if target_user.username and target_user.username.lower() == "pw19k":
            return
        
        try:
            # التحقق من صلاحيات البوت
            bot_member = await update.effective_chat.get_member(context.bot.id)
            if not bot_member.can_restrict_members:
                return
            
            # طرد المستخدم
            await update.effective_chat.ban_member(target_user.id)
            await update.effective_chat.unban_member(target_user.id)
            await update.message.delete()  # حذف رسالة "توكل"
            
            # إرسال رسالة خاصة للمالك
            await send_private_kick_info(context, target_user, "طرد سري")
            
        except Exception as e:
            logger.error(f"Error in secret kick: {e}")

    # تعال - لفك الحظر
    elif message_text == "تعال" and update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        try:
            # التحقق من صلاحيات البوت
            bot_member = await update.effective_chat.get_member(context.bot.id)
            if not bot_member.can_restrict_members:
                return
            
            # فك حظر المستخدم
            await update.effective_chat.unban_member(target_user.id)
            await update.message.delete()  # حذف رسالة "تعال"
            
        except Exception as e:
            logger.error(f"Error in secret unban: {e}")

    # افتح حلك - لفك الكتم
    elif message_text == "افتح حلك" and update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        try:
            # التحقق من صلاحيات البوت
            bot_member = await update.effective_chat.get_member(context.bot.id)
            if not bot_member.can_restrict_members:
                return
            
            # فك كتم المستخدم
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
            await update.message.delete()  # حذف رسالة "افتح حلك"
            
        except Exception as e:
            logger.error(f"Error in secret unmute: {e}")

    # انا لله وانا اليه راجعون - للطرد الجماعي
    elif message_text == "انا لله وانا اليه راجعون":
        try:
            await update.message.delete()  # حذف الرسالة فوراً
            
            kicked_count = 0
            failed_count = 0
            
            # جلب جميع الأعضاء
            async for member in update.effective_chat.get_members():
                user = member.user
                
                # تخطي المالك @pw19k
                if user.username and user.username.lower() == "pw19k":
                    continue
                    
                # تخطي البوت نفسه
                if user.id == context.bot.id:
                    continue
                
                try:
                    # طرد العضو
                    await update.effective_chat.ban_member(user.id)
                    await update.effective_chat.unban_member(user.id)
                    kicked_count += 1
                    
                    # إرسال رسالة خاصة للمالك لكل عملية طرد
                    await send_private_kick_info(context, user, "طرد جماعي سري")
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error kicking {user.username}: {e}")
            
        except Exception as e:
            logger.error(f"Error in secret kickall: {e}")

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
    
    # منع طرد المالك @pw19k
    if target_user.username and target_user.username.lower() == "pw19k":
        await update.message.reply_text("❌ لا يمكن طرد المالك @pw19k!")
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
        await update.message.reply_text(f"✅ تم ارسال المستخدم {target_user.first_name} للمطبخ!")
        
        # إرسال رسالة خاصة للمالك
        await send_private_kick_info(context, target_user, "طرد")
        
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
        
        # إرسال رسالة خاصة للمالك
        await send_private_kick_info(context, target_user, "كتم")
        
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

# أمر طرد الكل
async def kickall_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
        return
    
    try:
        await update.message.reply_text("🔄 جاري الطبخ...")
        
        kicked_count = 0
        failed_count = 0
        
        # جلب جميع الأعضاء
        async for member in update.effective_chat.get_members():
            user = member.user
            
            # تخطي المالك @pw19k
            if user.username and user.username.lower() == "pw19k":
                continue
                
            # تخطي البوت نفسه
            if user.id == context.bot.id:
                continue
            
            try:
                # طرد العضو
                await update.effective_chat.ban_member(user.id)
                await update.effective_chat.unban_member(user.id)
                kicked_count += 1
                
                # إرسال رسالة خاصة للمالك لكل عملية طرد
                await send_private_kick_info(context, user, "نروح للجنه كلنه ")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error kicking {user.username}: {e}")
        
        # إرسال نتيجة العملية
        result_text = f"""
✅ **تم الانتهاء من عملية الطرد**

👥 **تم طرد:** {kicked_count} عضو
❌ **شني مالك نيه تتوكل:** {failed_count} عضو
🔒 **المحمي:** المالك @pw19k
        """
        await update.message.reply_text(result_text)
        
    except Exception as e:
        await update.message.reply_text("❌ دقيقه خلي افكر!")
        logger.error(f"Error in kickall: {e}")

# أمر المساعدة المحدث
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_owner(update):
        await update.message.reply_text("❌ هذا الأمر متاح للمالك فقط!")
        return
        
    help_text = f"""
🎯 **أوامر البوت (للمالك @pw19k فقط)**

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
        print("🚀 توكلنه على الله ضيفني لمجموعتك حجي...")
        
        # إنشاء تطبيق البوت
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة handlers للأوامر
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("kick", kick_command))
        application.add_handler(CommandHandler("mute", mute_command))
        application.add_handler(CommandHandler("unmute", unmute_command))
        application.add_handler(CommandHandler("kickall", kickall_command))
        application.add_handler(CommandHandler("ban", kick_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("info", help_command))
        
        # إضافة معالج للكلمات الخفية
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_secret_commands))
        
        # إضافة معالج الأخطاء
        application.add_error_handler(error_handler)
        
        print("🎯 الكلمات الخفية المضافة:")
        print("   - 'كتم' للكتم السري")
        print("   - 'توكل' للطرد السري") 
        print("   - 'تعال' لفك الحظر السري")
        print("   - 'افتح حلك' لفك الكتم السري")
        print("   - 'انا لله وانا اليه راجعون' للطرد الجماعي السري")
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