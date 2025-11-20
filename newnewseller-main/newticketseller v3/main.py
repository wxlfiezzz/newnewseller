from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, TypeHandler, ApplicationHandlerStop
from telegram import Update
from config import Config
from database.session import init_db
from database.session import Session
from database.models import User
from services.antispam import AntiSpamService
from services.auth import AuthService
import datetime
import asyncio

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
    
    # Добавляем middleware первым
    application.add_handler(TypeHandler(Update, antispam_middleware), group=-1)
    
    # Команды
    application.add_handler(CommandHandler("start", StartHandler.start))
    application.add_handler(CommandHandler("admin", AdminHandler.admin_panel))
    application.add_handler(CommandHandler("mysub", UserHandler.my_subscription))
    application.add_handler(CommandHandler("myticket", UserHandler.my_ticket))
    application.add_handler(CommandHandler("recover", UserHandler.recover_ticket))
    application.add_handler(CommandHandler("addadmin", AdminHandler.add_admin))
    
    application.add_handler(CommandHandler("sent", BroadcastHandler.send_broadcast))
    application.add_handler(CommandHandler("block", BroadcastHandler.block_user))
    application.add_handler(CommandHandler("unblock", BroadcastHandler.unblock_user))
    
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.Document.ALL, FileHandler.handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, StartHandler.handle_message))
    
    # Обработчики callback-запросов
    application.add_handler(CallbackQueryHandler(CallbackHandler.button_handler))

async def run_daily_tasks():
    """Запуск ежедневных задач вручную"""
    while True:
        now = datetime.datetime.now()
        # Вычисляем время до следующего запуска (03:00)
        target_time = now.replace(hour=3, minute=0, second=0, microsecond=0)
        if now >= target_time:
            target_time += datetime.timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        
        # Ждем до времени выполнения
        await asyncio.sleep(wait_seconds)
        
        try:
            # Выполняем задачи
            from services.file_cleanup import FileCleanupService
            await FileCleanupService.schedule_cleanup_task()
            AntiSpamService.cleanup_old_activity()
            
            print(f"Ежедневные задачи выполнены в {datetime.datetime.now()}")
        except Exception as e:
            print(f"Ошибка при выполнении ежедневных задач: {e}")

def setup_jobs(application):
    """Настройка периодических задач"""
    job_queue = application.job_queue
    
    if job_queue is None:
        print("Предупреждение: Job Queue недоступна. Используется ручное управление задачами.")
        return False
    
    try:
        from services.file_cleanup import FileCleanupService
        
        # Ежедневная очистка файлов в 03:00
        job_queue.run_daily(
            FileCleanupService.schedule_cleanup_task,
            time=datetime.time(hour=3, minute=0),
            name="daily_file_cleanup"
        )
        
        # Ежедневная очистка активности в 04:00
        job_queue.run_daily(
            AntiSpamService.cleanup_old_activity,
            time=datetime.time(hour=4, minute=0),
            name="daily_activity_cleanup"
        )
        
        print("Периодические задачи настроены через Job Queue")
        return True
    except Exception as e:
        print(f"Ошибка при настройке Job Queue: {e}")
        return False

def main():
    if not Config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN не установлен! Добавьте токен в Secrets.")

    # Инициализация папок и базы данных
    Config.create_folders()
    init_db()
    
    # Создаем Application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Настраиваем обработчики
    setup_handlers(application)
    
    # Пытаемся настроить Job Queue
    job_queue_initialized = setup_jobs(application)
    
    # Если Job Queue не работает, запускаем задачи вручную
    if not job_queue_initialized:
        print("Запуск ежедневных задач в ручном режиме...")
        # Запускаем асинхронную задачу для ежедневных задач
        loop = asyncio.get_event_loop()
        loop.create_task(run_daily_tasks())
    
    # Логирование запуска
    from services.logger import bot_logger
    bot_logger.logger.info("Бот запускается...")
    bot_logger.logger.info("Защита от спама: макс. 5 действий в минуту для пользователей")
    bot_logger.logger.info("Автоматическая очистка файлов: каждый день в 03:00")
    bot_logger.logger.info("Автоматическая очистка активности: каждый день в 04:00")
    
    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()