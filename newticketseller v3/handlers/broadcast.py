from telegram import Update
from telegram.ext import ContextTypes
from database.session import Session
from database.models import User
from services.auth import AuthService
from services.logger import bot_logger
from services.antispam import AntiSpamService

class BroadcastHandler:
    
    @staticmethod
    async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if not AuthService.is_admin(user.id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        if AntiSpamService.check_spam(user.id, "broadcast"):
            await update.message.reply_text("⚠️ Пожалуйста, подождите перед следующей рассылкой.")
            return
        
        message = update.message
        
        if not message.reply_to_message and not context.args:
            await message.reply_text(
                "📢 Использование команды /sent:\n\n"
                "1️⃣ /sent Ваше сообщение здесь\n"
                "2️⃣ Ответьте на сообщение командой /sent (для пересылки фото/видео/геолокации)"
            )
            return
        
        session = Session()
        try:
            users = session.query(User).filter(
                User.has_access == True,
                User.is_blocked == False
            ).all()
            
            if not users:
                await message.reply_text("❌ Нет активных пользователей для рассылки.")
                return
            
            sent_count = 0
            failed_count = 0
            
            status_message = await message.reply_text(
                f"📤 Начинаю рассылку {len(users)} пользователям..."
            )
            
            if message.reply_to_message:
                original = message.reply_to_message
                
                for user_obj in users:
                    try:
                        if original.text:
                            await context.bot.send_message(
                                chat_id=user_obj.user_id,
                                text=original.text
                            )
                        elif original.photo:
                            await context.bot.send_photo(
                                chat_id=user_obj.user_id,
                                photo=original.photo[-1].file_id,
                                caption=original.caption
                            )
                        elif original.video:
                            await context.bot.send_video(
                                chat_id=user_obj.user_id,
                                video=original.video.file_id,
                                caption=original.caption
                            )
                        elif original.location:
                            await context.bot.send_location(
                                chat_id=user_obj.user_id,
                                latitude=original.location.latitude,
                                longitude=original.location.longitude
                            )
                        elif original.document:
                            await context.bot.send_document(
                                chat_id=user_obj.user_id,
                                document=original.document.file_id,
                                caption=original.caption
                            )
                        
                        sent_count += 1
                    except Exception as e:
                        failed_count += 1
                        bot_logger.logger.error(f"Ошибка отправки user_id={user_obj.user_id}: {e}")
            
            else:
                broadcast_text = " ".join(context.args)
                
                for user_obj in users:
                    try:
                        await context.bot.send_message(
                            chat_id=user_obj.user_id,
                            text=broadcast_text
                        )
                        sent_count += 1
                    except Exception as e:
                        failed_count += 1
                        bot_logger.logger.error(f"Ошибка отправки user_id={user_obj.user_id}: {e}")
            
            await status_message.edit_text(
                f"✅ Рассылка завершена!\n\n"
                f"📨 Отправлено: {sent_count}\n"
                f"❌ Ошибок: {failed_count}"
            )
            
            bot_logger.log_admin_action(
                user, 
                f"Рассылка сообщений", 
                f"Отправлено: {sent_count}, Ошибок: {failed_count}"
            )
            
        except Exception as e:
            bot_logger.logger.error(f"Ошибка рассылки: {e}")
            await message.reply_text(f"❌ Ошибка при рассылке: {e}")
        finally:
            session.close()
    
    @staticmethod
    async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if not AuthService.is_admin(user.id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "⚠️ Использование: /block USER_ID\n"
                "Пример: /block 123456789"
            )
            return
        
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Неверный формат USER_ID")
            return
        
        session = Session()
        try:
            from datetime import datetime
            
            target_user = session.query(User).filter_by(user_id=target_user_id).first()
            
            if not target_user:
                await update.message.reply_text("❌ Пользователь не найден в базе данных.")
                session.close()
                return
            
            if target_user.is_blocked:
                await update.message.reply_text(
                    f"⚠️ Пользователь {target_user_id} уже заблокирован."
                )
                session.close()
                return
            
            target_user.is_blocked = True
            target_user.blocked_at = datetime.utcnow()
            target_user.blocked_by = user.id
            target_user.has_access = False
            
            session.commit()
            
            await update.message.reply_text(
                f"✅ Пользователь {target_user_id} успешно заблокирован.\n"
                f"Имя: {target_user.first_name or 'Не указано'}\n"
                f"Username: @{target_user.username or 'нет'}"
            )
            
            bot_logger.log_admin_action(
                user, 
                f"Блокировка пользователя", 
                f"Заблокирован user_id={target_user_id}"
            )
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="🚫 Ваш доступ к боту был заблокирован администратором."
                )
            except:
                pass
            
        except Exception as e:
            session.rollback()
            bot_logger.logger.error(f"Ошибка блокировки пользователя: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")
        finally:
            session.close()
    
    @staticmethod
    async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if not AuthService.is_admin(user.id):
            await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "⚠️ Использование: /unblock USER_ID\n"
                "Пример: /unblock 123456789"
            )
            return
        
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Неверный формат USER_ID")
            return
        
        session = Session()
        try:
            target_user = session.query(User).filter_by(user_id=target_user_id).first()
            
            if not target_user:
                await update.message.reply_text("❌ Пользователь не найден в базе данных.")
                session.close()
                return
            
            if not target_user.is_blocked:
                await update.message.reply_text(
                    f"⚠️ Пользователь {target_user_id} не заблокирован."
                )
                session.close()
                return
            
            target_user.is_blocked = False
            target_user.blocked_at = None
            target_user.blocked_by = None
            target_user.has_access = True
            
            session.commit()
            
            await update.message.reply_text(
                f"✅ Пользователь {target_user_id} успешно разблокирован.\n"
                f"Имя: {target_user.first_name or 'Не указано'}\n"
                f"Username: @{target_user.username or 'нет'}"
            )
            
            bot_logger.log_admin_action(
                user, 
                f"Разблокировка пользователя", 
                f"Разблокирован user_id={target_user_id}"
            )
            
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="✅ Ваш доступ к боту восстановлен!"
                )
            except:
                pass
            
        except Exception as e:
            session.rollback()
            bot_logger.logger.error(f"Ошибка разблокировки пользователя: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")
        finally:
            session.close()
