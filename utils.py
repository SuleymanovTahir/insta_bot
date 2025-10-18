"""
Утилиты для CRM системы
Выносим общие функции сюда, чтобы не дублировать код
"""
import os
import re
import logging
from typing import Optional
from database import get_user_by_session
from fastapi import Cookie

logger = logging.getLogger(__name__)

# ===== АВТОРИЗАЦИЯ =====

async def require_auth(session_token: Optional[str] = Cookie(None)):
    """Проверить авторизацию пользователя"""
    if not session_token:
        return None
    return get_user_by_session(session_token)


# ===== КЛИЕНТЫ =====

def get_client_display_name(client):
    """
    Получить отображаемое имя клиента
    Приоритет: name > username > ID
    """
    if client[3]:  # name
        return client[3]
    elif client[1]:  # username
        return f"@{client[1]}"
    else:
        return client[0][:15] + "..."  # instagram_id


# ===== НЕПРОЧИТАННЫЕ СООБЩЕНИЯ =====

def get_total_unread(get_all_clients_func, get_unread_messages_count_func):
    """
    Получить общее количество непрочитанных сообщений
    
    Args:
        get_all_clients_func: функция из database.py
        get_unread_messages_count_func: функция из database.py
    """
    clients = get_all_clients_func()
    total = 0
    for client in clients:
        total += get_unread_messages_count_func(client[0])
    return total


# ===== СТАТУСЫ =====

def get_all_statuses(base_statuses, get_custom_statuses_func):
    """
    Получить все статусы (базовые + кастомные)
    
    Args:
        base_statuses: CLIENT_STATUSES из config.py
        get_custom_statuses_func: функция из database.py
    """
    statuses = base_statuses.copy()
    custom = get_custom_statuses_func()
    for status in custom:
        statuses[status[1]] = {
            "label": status[2],
            "color": status[3],
            "icon": status[4]
        }
    return statuses


# ===== РАБОТА С ФАЙЛАМИ =====

def ensure_upload_directories():
    """Создать все необходимые директории для загрузок"""
    directories = [
        "static/uploads/images",
        "static/uploads/files",
        "static/uploads/voice"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"✅ Создана/проверена директория: {directory}")


def sanitize_filename(filename: str) -> str:
    """
    Очистить имя файла от опасных символов
    
    Args:
        filename: исходное имя файла
        
    Returns:
        безопасное имя файла
    """
    # Удаляем всё кроме букв, цифр, точек, дефисов и подчёркиваний
    safe_name = re.sub(r'[^\w\s.-]', '', filename)
    # Заменяем пробелы на подчёркивания
    safe_name = safe_name.replace(' ', '_')
    # Ограничиваем длину
    if len(safe_name) > 100:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:100] + ext
    return safe_name


def validate_file_upload(file, max_size_mb: int = 10, allowed_extensions: list = None):
    """
    Валидировать загружаемый файл
    
    Args:
        file: объект файла из FastAPI
        max_size_mb: максимальный размер в MB
        allowed_extensions: список разрешённых расширений (без точки)
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not file:
        return False, "Файл не найден"
    
    # Проверка расширения
    if allowed_extensions:
        ext = file.filename.split('.')[-1].lower()
        if ext not in allowed_extensions:
            return False, f"Недопустимое расширение. Разрешено: {', '.join(allowed_extensions)}"
    
    # Проверка размера (если возможно)
    # Note: file.size не всегда доступен в FastAPI, нужно читать содержимое
    
    return True, None


# ===== ФОРМАТИРОВАНИЕ =====

def format_phone(phone: str) -> str:
    """
    Форматировать номер телефона
    
    Args:
        phone: номер телефона
        
    Returns:
        отформатированный номер
    """
    if not phone:
        return ""
    
    # Убираем всё кроме цифр
    digits = re.sub(r'\D', '', phone)
    
    # Форматируем в зависимости от длины
    if len(digits) == 11:  # российский номер
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:]}"
    elif len(digits) == 12:  # международный с кодом страны
        return f"+{digits[0:2]} ({digits[2:5]}) {digits[5:8]}-{digits[8:10]}-{digits[10:]}"
    else:
        return phone  # возвращаем как есть


def format_currency(amount: float, currency: str = "AED") -> str:
    """
    Форматировать денежную сумму
    
    Args:
        amount: сумма
        currency: валюта (по умолчанию AED)
        
    Returns:
        отформатированная строка
    """
    if not amount:
        return f"0 {currency}"
    
    return f"{amount:,.2f} {currency}".replace(",", " ")


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Обрезать текст до указанной длины
    
    Args:
        text: исходный текст
        max_length: максимальная длина
        suffix: суффикс для обрезанного текста
        
    Returns:
        обрезанный текст
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length].strip() + suffix


# ===== ВАЛИДАЦИЯ =====

def is_valid_email(email: str) -> bool:
    """
    Проверить валидность email
    
    Args:
        email: адрес электронной почты
        
    Returns:
        True если email валиден
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """
    Проверить валидность номера телефона
    
    Args:
        phone: номер телефона
        
    Returns:
        True если номер валиден
    """
    # Убираем всё кроме цифр
    digits = re.sub(r'\D', '', phone)
    # Проверяем длину (от 10 до 15 цифр)
    return 10 <= len(digits) <= 15


def is_valid_instagram_username(username: str) -> bool:
    """
    Проверить валидность Instagram username
    
    Args:
        username: имя пользователя (без @)
        
    Returns:
        True если username валиден
    """
    # Instagram username: буквы, цифры, точки, подчёркивания, до 30 символов
    pattern = r'^[a-zA-Z0-9._]{1,30}$'
    return bool(re.match(pattern, username))


# ===== БЕЗОПАСНОСТЬ =====

def escape_html(text: str) -> str:
    """
    Экранировать HTML символы для предотвращения XSS
    
    Args:
        text: исходный текст
        
    Returns:
        экранированный текст
    """
    if not text:
        return ""
    
    escape_dict = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;'
    }
    
    for char, escaped in escape_dict.items():
        text = text.replace(char, escaped)
    
    return text


# ===== ДЕБАГ =====

def log_function_call(func_name: str, **kwargs):
    """
    Логировать вызов функции с параметрами
    
    Args:
        func_name: имя функции
        **kwargs: параметры функции
    """
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"📞 Вызов: {func_name}({params})")


def log_error(error: Exception, context: str = ""):
    """
    Логировать ошибку с контекстом
    
    Args:
        error: объект исключения
        context: дополнительный контекст
    """
    logger.error(f"❌ Ошибка в {context}: {type(error).__name__}: {str(error)}")
    import traceback
    logger.error(traceback.format_exc())