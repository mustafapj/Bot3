import logging
import sys
import asyncio
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# استيراد الإعدادات من config.py
try:
    from config import BOT_TOKEN, DEVELOPER_USERNAME
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

# تخزين مالكي المجموعات
group_owners = {}

# ========== الدوال الأساسية ==========

async def detect_and_store_owner(chat_id, context):
    """التعرف على مالك المجموعة وتخزينه"""
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.status == 'creator':
                owner_id = admin.user.id
                owner_username = admin.user.username or admin.user.first_name
                group_owners[chat_id] = owner_id
                print(f"✅ تم التعرف على المالك: {owner_username} (ID: {owner_id}) للمجموعة: {chat_id}")
                return True
        print(f"❌ لم يتم العثور على مالك للمجموعة: {chat_id}")
        return False
    except Exception as e:
        print(f"❌ خطأ في التعرف على المالك: {e}")
        return False

async def is_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق إذا كان المستخدم هو مالك المجموعة"""
    try:
        user = update.effective_user
        chat = update.effective_chat
        
        if not user or not chat:
            return False
        
        chat_id = chat.id
        
        # إذا لم يتم التعرف على المالك بعد، نحاول التعرف عليه
        if chat_id not in group_owners:
            await detect_and_store_owner(chat_id, context)
        
        # التحقق إذا كان المستخدم هو المالك
        if chat_id in group_owners and user.id == group_owners[chat_id]:
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error in owner check: {e}")
        return False

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """الحصول على المستخدم المستهدف من الأمر"""
    target_user = None
    
    # إذا تم الرد على رسالة
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
    
    # إذا تم استخدام اليوزرنيم
    elif context.args:
        try:
            username = context.args[0].replace('@', '')
            # البحث عن المستخدم في الأعضاء
            async for member in update.effective_chat.get_members():
                if member.user.username and member.user.username.lower() == username.lower():
                    target_user = member.user
                    break
        except Exception as e:
            logger.error(f"Error finding user: {e}")
    
    return target_user

# ========== الأوامر الرئيسية ==========

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر البدء"""
    try:
        chat = update.effective_chat
        
        if chat.type == "private":
            await update.message.reply_text("🔒 هذا البوت مخصص لإدارة المجموعات فقط!")
            return
        
        # التعرف على المالك
        await detect_and_store_owner(chat.id, context)
        
        welcome_text = f"""
🎊 **مرحباً بك في بوت الحماية الحصري!**

🤖 **مطور البوت:** @{DEVELOPER_USERNAME}

⚡ **مميزات البوت:**
• حماية كاملة للمجموعة
• أوامر طرد وكتم حصرية للمالك
• تحكم كامل في جميع الأعضاء بغض النظر عن رتبهم

🎯 **الأوامر المتاحة:**
/kick - طرد عضو (بالرد أو @username)
/mute - كتم عضو  
/unmute - إلغاء كتم عضو

🔒 **ملاحظة:** الأوامر متاحة فقط لمالك المجموعة

📞 **للتواصل والدعم:** @{DEVELOPER_USERNAME}
        """
        
        await update.message.reply_text(welcome_text)
        print(f"✅ تم تفعيل البوت في المجموعة: {chat.id}")
            
    except Exception as e:
        logger.error(f"Error in start command: {e}")

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر الطرد المطلق - للمالك فقط"""
    try:
        # التحقق إذا كان المالك
        if not await is_owner(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط لمالك المجموعة!")
            return
        
        # الحصول على المستخدم المستهدف
        target_user = await get_target_user(update, context)
        
        if not target_user:
            await update.message.reply_text("⚠️ يرجى الرد على رسالة العضو أو كتابة: /kick @username")
            return
        
        # منع طرد المالك نفسه فقط
        chat_id = update.effective_chat.id
        if target_user.id == group_owners.get(chat_id):
            await update.message.reply_text("❌ لا يمكنك طرد نفسك (مالك المجموعة)!")
            return
        
        # ⚡ طرد مطلق بدون التحقق من الصلاحيات
        try:
            # محاولة الطرد المباشر
            await update.effective_chat.ban_member(target_user.id)
            await update.effective_chat.unban_member(target_user.id)
            
            # تحديد نوع المستخدم
            user_type = "بوت" if target_user.is_bot else "عضو"
            
            await update.message.reply_text(
                f"⚡ تم طرد {user_type} [{target_user.first_name}](tg://user?id={target_user.id}) بنجاح!\n"
                f"🛡️ بغض النظر عن رتبته!", 
                parse_mode='Markdown'
            )
            print(f"✅ تم طرد {user_type}: {target_user.id} بواسطة المالك: {update.effective_user.id}")
            
        except Exception as kick_error:
            # إذا فشل الطرد العادي، نحاول طرق بديلة
            logger.error(f"طريقة الطرد الأولى فشلت: {kick_error}")
            
            # محاولة ثانية بطريقة مختلفة
            try:
                await context.bot.ban_chat_member(chat_id, target_user.id)
                await asyncio.sleep(1)
                await context.bot.unban_chat_member(chat_id, target_user.id)
                
                user_type = "بوت" if target_user.is_bot else "عضو"
                await update.message.reply_text(f"✅ تم طرد {user_type} باستخدام الطريقة البديلة!")
                
            except Exception as final_error:
                # إذا فشل كل شيء
                logger.error(f"جميع محاولات الطرد فشلت: {final_error}")
                await update.message.reply_text("❌ فشل الطرد! قد يكون المستخدم غير موجود أو هناك قيود خاصة")
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ غير متوقع!")
        logger.error(f"Error in absolute kick: {e}")

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر الكتم المطلق - للمالك فقط"""
    try:
        # التحقق إذا كان المالك
        if not await is_owner(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط لمالك المجموعة!")
            return
        
        # الحصول على المستخدم المستهدف
        target_user = await get_target_user(update, context)
        
        if not target_user:
            await update.message.reply_text("⚠️ يرجى الرد على رسالة العضو أو كتابة: /mute @username")
            return
        
        # منع كتم المالك نفسه فقط
        chat_id = update.effective_chat.id
        if target_user.id == group_owners.get(chat_id):
            await update.message.reply_text("❌ لا يمكنك كتم نفسك (مالك المجموعة)!")
            return
        
        # ⚡ كتم مطلق
        try:
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
            
            user_type = "بوت" if target_user.is_bot else "عضو"
            await update.message.reply_text(
                f"🔇 تم كتم {user_type} [{target_user.first_name}](tg://user?id={target_user.id}) بنجاح!\n"
                f"🛡️ بغض النظر عن رتبته!", 
                parse_mode='Markdown'
            )
            print(f"✅ تم كتم {user_type}: {target_user.id} بواسطة المالك: {update.effective_user.id}")
            
        except Exception as mute_error:
            logger.error(f"خطأ في الكتم: {mute_error}")
            await update.message.reply_text("❌ فشل الكتم! قد يكون المستخدم غير موجود أو هناك قيود خاصة")
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ غير متوقع!")
        logger.error(f"Error in absolute mute: {e}")

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر إلغاء الكتم - للمالك فقط"""
    try:
        # التحقق إذا كان المالك
        if not await is_owner(update, context):
            await update.message.reply_text("❌ هذا الأمر متاح فقط لمالك المجموعة!")
            return
        
        # الحصول على المستخدم المستهدف
        target_user = await get_target_user(update, context)
        
        if not target_user:
            await update.message.reply_text("⚠️ يرجى الرد على رسالة العضو أو كتابة: /unmute @username")
            return
        
        # ⚡ إلغاء كتم مطلق
        try:
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
            
            user_type = "بوت" if target_user.is_bot else "عضو"
            await update.message.reply_text(
                f"🔊 تم إلغاء كتم {user_type} [{target_user.first_name}](tg://user?id={target_user.id}) بنجاح!", 
                parse_mode='Markdown'
            )
            print(f"✅ تم إلغاء كتم {user_type}: {target_user.id} بواسطة المالك: {update.effective_user.id}")
            
        except Exception as unmute_error:
            logger.error(f"خطأ في إلغاء الكتم: {unmute_error}")
            await update.message.reply_text("❌ فشل إلغاء الكتم! قد يكون المستخدم غير موجود")
        
    except Exception as e:
        await update.message.reply_text("❌ حدث خطأ غير متوقع!")
        logger.error(f"Error in unmute: {e}")

# ========== التعرف التلقائي على المالك ==========

async def auto_detect_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التعرف التلقائي على المالك عند إضافة البوت"""
    try:
        if update.message.new_chat_members:
            for user in update.message.new_chat_members:
                if user.id == context.bot.id:
                    chat_id = update.effective_chat.id
                    await detect_and_store_owner(chat_id, context)
                    
                    # ترحيب بالبوت
                    welcome_msg = f"""
🎊 تم تفعيل بوت الحماية الحصري بنجاح!

🤖 **مطور البوت:** @{DEVELOPER_USERNAME}

🔒 الأوامر متاحة فقط لمالك المجموعة
⚡ اكتب /start لرؤية الأوامر المتاحة

📞 **الدعم:** @{DEVELOPER_USERNAME}
                    """
                    
                    await update.message.reply_text(welcome_msg)
                    break
    except Exception as e:
        logger.error(f"Error in auto detect owner: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء"""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """الدالة الرئيسية لتشغيل البوت"""
    try:
        print("🚀 بدء تشغيل بوت الحماية الحصري...")
        print(f"🤖 المطور: @{DEVELOPER_USERNAME}")
        print("🎯 جاري تحميل الميزات...")
        
        application = Application.builder().token(BOT_TOKEN).build()
        
        # إضافة الأوامر
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("kick", kick_command))
        application.add_handler(CommandHandler("mute", mute_command))
        application.add_handler(CommandHandler("unmute", unmute_command))
        
        # التعرف على المالك عند إضافة البوت
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