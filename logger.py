"""
Централизованная система логирования для CRM
Создайте этот файл: logger.py
"""
import logging
import sys
from pathlib import Path

def setup_logger(name: str = "crm", log_file: str = "app.log") -> logging.Logger:
    """
    Настраивает и возвращает централизованный logger
    
    Args:
        name: Имя логгера (по умолчанию "crm")
        log_file: Имя файла для логов
        
    Returns:
        Настроенный logger
    """
    # Создаём директорию для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Создаём logger
    logger = logging.getLogger(name)
    
    # Если уже настроен - возвращаем
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # Формат логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Handler для файла
    file_handler = logging.FileHandler(
        log_dir / log_file, 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Добавляем handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Создаём глобальный экземпляр логгера
logger = setup_logger()


# Вспомогательные функции для быстрого логирования
def log_info(message: str, module: str = "main"):
    """Логирует INFO сообщение"""
    logger.info(f"[{module}] {message}")


def log_error(message: str, module: str = "main", exc_info: bool = False):
    """Логирует ERROR сообщение"""
    logger.error(f"[{module}] {message}", exc_info=exc_info)


def log_warning(message: str, module: str = "main"):
    """Логирует WARNING сообщение"""
    logger.warning(f"[{module}] {message}")


def log_debug(message: str, module: str = "main"):
    """Логирует DEBUG сообщение"""
    logger.debug(f"[{module}] {message}")


# logger.py - дополнение
def send_telegram_alert(message):
    """Отправка критических ошибок в Telegram"""
    import requests
    TELEGRAM_BOT_TOKEN = "your_token"
    TELEGRAM_CHAT_ID = "your_chat_id"
    
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message}
    )

def log_critical(message, module, exc_info=True):
    logger.critical(f"[{module}] {message}", exc_info=exc_info)
    send_telegram_alert(f"🚨 CRITICAL: {message}")


# Декоратор для логирования функций
def log_function_call(func):
    """
    Декоратор для автоматического логирования вызовов функций
    
    Использование:
        @log_function_call
        def my_function():
            pass
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module_name = func.__module__
        
        logger.info(f"[{module_name}] Вызов функции: {func_name}")
        
        try:
            result = func(*args, **kwargs)
            logger.info(f"[{module_name}] Функция {func_name} успешно выполнена")
            return result
        except Exception as e:
            logger.error(
                f"[{module_name}] Ошибка в функции {func_name}: {str(e)}", 
                exc_info=True
            )
            raise
    
    return wrapper


# Экспортируем всё необходимое
__all__ = [
    'logger',
    'setup_logger',
    'log_info',
    'log_error',
    'log_warning',
    'log_debug',
    'log_critical',
    'log_function_call'
]