import os
from datetime import datetime, timedelta
from database.session import Session
from database.models import File
from services.logger import bot_logger
from config import Config

class FileCleanupService:
    @staticmethod
    def delete_old_files(months=6):
        session = Session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
            old_files = session.query(File).filter(
                File.upload_date < cutoff_date
            ).all()
            
            deleted_count = 0
            for file in old_files:
                try:
                    if file.file_path and os.path.exists(file.file_path):
                        os.remove(file.file_path)
                    
                    if file.backup_path and os.path.exists(file.backup_path):
                        os.remove(file.backup_path)
                    
                    session.delete(file)
                    deleted_count += 1
                    
                except Exception as e:
                    bot_logger.logger.error(f"Ошибка удаления файла {file.id}: {e}")
            
            session.commit()
            bot_logger.logger.info(f"Удалено {deleted_count} старых файлов (старше {months} месяцев)")
            return deleted_count
            
        except Exception as e:
            session.rollback()
            bot_logger.logger.error(f"Ошибка очистки файлов: {e}")
            return 0
        finally:
            session.close()
    
    @staticmethod
    async def schedule_cleanup_task(context):
        FileCleanupService.delete_old_files()
