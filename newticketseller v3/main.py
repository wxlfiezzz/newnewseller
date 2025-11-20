from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, TypeHandler, ApplicationHandlerStop
from telegram import Update
from config import Config
from database.session import init_db
from database.session import Session
from database.models import User
from services.antispam import AntiSpamService
from services.auth import AuthService

async def antispam_middleware(update: Update, context):
    if update.effective_user:
        user_id = update.effective_user.id
        
        session = Session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user and user.is_blocked:
                if update.message:
                    await update.message.reply_text(
                        "🚫 Ваш доступ к боту заблокирован.\n"
                        "Обратитесь к администратору для разъяснений."
                    )
                elif update.callback_query:
                    await update.callback_query.answer(
                        "🚫 Ваш доступ к боту заблокирован.",
                        show_alert=True
                    )
                raise ApplicationHandlerStop
        finally:
            session.close()
        
        if not AuthService.is_admin(user_id):
            if AntiSpamService.check_spam(user_id, "user_action"):
                if update.message:
                    await update.message.reply_text(
                        "⚠️ Вы отправляете слишком много запросов.\n"
                        "Пожалуйста, подождите немного перед следующим действием."
                    )
                elif update.callback_query:
                    await update.callback_query.answer(
                        "⚠️ Слишком много запросов. Подождите немного.",
                        show_alert=True
                    )
                raise ApplicationHandlerStop

def setup_handlers(application):
    from handlers.start import StartHandler
    from handlers.admin import AdminHandler
    from handlers.user import UserHandler
    from handlers.files import FileHandler
    from handlers.callbacks import CallbackHandler
    from handlers.broadcast import BroadcastHandler
    
    application.add_handler(TypeHandler(Update, antispam_middleware), group=-1)
    
    application.add_handler(CommandHandler("start", StartHandler.start))
    application.add_handler(CommandHandler("admin", AdminHandler.admin_panel))
    application.add_handler(CommandHandler("mysub", UserHandler.my_subscription))
    application.add_handler(CommandHandler("myticket", UserHandler.my_ticket))
    application.add_handler(CommandHandler("recover", UserHandler.recover_ticket))
    application.add_handler(CommandHandler("addadmin", AdminHandler.add_admin))
    
    application.add_handler(CommandHandler("sent", BroadcastHandler.send_broadcast))
    application.add_handler(CommandHandler("block", BroadcastHandler.block_user))
    application.add_handler(CommandHandler("unblock", BroadcastHandler.unblock_user))
    
    application.add_handler(MessageHandler(filters.Document.ALL, FileHandler.handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, StartHandler.handle_message))
    
    application.add_handler(CallbackQueryHandler(CallbackHandler.button_handler))

def main():
    if not Config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN не установлен! Добавьте токен в Secrets.")

    Config.create_folders()
    init_db()
    
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    setup_handlers(application)
    
    job_queue = application.job_queue
    from services.file_cleanup import FileCleanupService
    
    job_queue.run_daily(
        FileCleanupService.schedule_cleanup_task,
        time=__import__('datetime').time(hour=3, minute=0)
    )
    
    job_queue.run_daily(
        lambda context: AntiSpamService.cleanup_old_activity(),
        time=__import__('datetime').time(hour=4, minute=0)
    )
    
    from services.logger import bot_logger
    bot_logger.logger.info("Бот запускается...")
    bot_logger.logger.info("Защита от спама: макс. 5 действий в минуту для пользователей")
    bot_logger.logger.info("Автоматическая очистка файлов: каждый день в 03:00")
    bot_logger.logger.info("Автоматическая очистка активности: каждый день в 04:00")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
