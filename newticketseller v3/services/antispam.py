from datetime import datetime, timedelta
from database.session import Session
from database.models import UserActivity
from services.logger import bot_logger

class AntiSpamService:
    SPAM_THRESHOLD = 5
    TIME_WINDOW = 60
    
    @staticmethod
    def check_spam(user_id: int, action_type: str = "message") -> bool:
        session = Session()
        try:
            cutoff_time = datetime.utcnow() - timedelta(seconds=AntiSpamService.TIME_WINDOW)
            
            recent_actions = session.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.action_type == action_type,
                UserActivity.timestamp > cutoff_time
            ).count()
            
            if recent_actions >= AntiSpamService.SPAM_THRESHOLD:
                bot_logger.logger.warning(f"Спам обнаружен: user_id={user_id}, действий={recent_actions}")
                return True
            
            activity = UserActivity(
                user_id=user_id,
                action_type=action_type
            )
            session.add(activity)
            session.commit()
            
            return False
            
        except Exception as e:
            session.rollback()
            bot_logger.logger.error(f"Ошибка проверки спама: {e}")
            return False
        finally:
            session.close()
    
    @staticmethod
    def cleanup_old_activity(days=7):
        session = Session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = session.query(UserActivity).filter(
                UserActivity.timestamp < cutoff_date
            ).delete()
            session.commit()
            bot_logger.logger.info(f"Удалено {deleted} старых записей активности")
            return deleted
        except Exception as e:
            session.rollback()
            bot_logger.logger.error(f"Ошибка очистки активности: {e}")
            return 0
        finally:
            session.close()
