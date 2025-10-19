import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import hashlib
import secrets
from config import DATABASE_NAME,SMTP_SERVER,SMTP_PORT,SMTP_USERNAME,SMTP_PASSWORD,FROM_EMAIL

def init_database():
    """Создать базу данных"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    # Таблица услуг
    c.execute('''CREATE TABLE IF NOT EXISTS clients
                 (instagram_id TEXT PRIMARY KEY,
                  username TEXT,
                  language TEXT,
                  first_contact TEXT,
                  last_contact TEXT,
                  total_messages INTEGER DEFAULT 0,
                  labels TEXT,
                  phone TEXT,
                  name TEXT,
                  status TEXT DEFAULT 'new',
                  source TEXT DEFAULT 'instagram',
                  lifetime_value REAL DEFAULT 0,
                  profile_pic TEXT,
                  notes TEXT,
                  is_pinned INTEGER DEFAULT 0)''')
    
    # Проверяем и добавляем новые колонки если их нет
    try:
        c.execute("ALTER TABLE clients ADD COLUMN profile_pic TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        c.execute("ALTER TABLE clients ADD COLUMN notes TEXT")
    except sqlite3.OperationalError:
        pass
    
    try:
        c.execute("ALTER TABLE clients ADD COLUMN is_pinned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  instagram_id TEXT,
                  message TEXT,
                  sender TEXT,
                  timestamp TEXT,
                  language TEXT,
                  is_read INTEGER DEFAULT 0,
                  message_type TEXT DEFAULT 'text')''')
    
    # Добавляем колонку message_type если её нет
    try:
        c.execute("ALTER TABLE chat_history ADD COLUMN message_type TEXT DEFAULT 'text'")
    except sqlite3.OperationalError:
        pass
    
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  instagram_id TEXT,
                  service_name TEXT,
                  datetime TEXT,
                  phone TEXT,
                  name TEXT,
                  status TEXT,
                  created_at TEXT,
                  completed_at TEXT,
                  revenue REAL DEFAULT 0,
                  notes TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS booking_temp
                 (instagram_id TEXT PRIMARY KEY,
                  service_name TEXT,
                  date TEXT,
                  time TEXT,
                  phone TEXT,
                  name TEXT,
                  step TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS client_interactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  instagram_id TEXT,
                  interaction_type TEXT,
                  timestamp TEXT,
                  metadata TEXT)''')
    
    # Таблица пользователей системы
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  full_name TEXT,
                  email TEXT,
                  role TEXT DEFAULT 'employee',
                  created_at TEXT,
                  last_login TEXT,
                  is_active INTEGER DEFAULT 1)''')
    
    # Таблица сессий
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  session_token TEXT UNIQUE,
                  created_at TEXT,
                  expires_at TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Таблица логов активности
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  action TEXT,
                  entity_type TEXT,
                  entity_id TEXT,
                  details TEXT,
                  timestamp TEXT,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Таблица пользовательских статусов
    c.execute('''CREATE TABLE IF NOT EXISTS custom_statuses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  status_key TEXT UNIQUE NOT NULL,
                  status_label TEXT NOT NULL,
                  status_color TEXT NOT NULL,
                  status_icon TEXT NOT NULL,
                  created_at TEXT,
                  created_by INTEGER,
                  FOREIGN KEY (created_by) REFERENCES users(id))''')
    
    # Создать дефолтного администратора если его нет
    c.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if c.fetchone()[0] == 0:
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        now = datetime.now().isoformat()
        c.execute("""INSERT INTO users 
                     (username, password_hash, full_name, role, created_at)
                     VALUES (?, ?, ?, ?, ?)""",
                  ('admin', password_hash, 'Администратор', 'admin', now))
        print("✅ Создан дефолтный пользователь: admin / admin123")
    

    # После всех CREATE TABLE, перед conn.commit()
    # Таблица услуг
    c.execute('''CREATE TABLE IF NOT EXISTS services
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  service_key TEXT UNIQUE NOT NULL,
                  name TEXT NOT NULL,
                  name_ru TEXT,
                  name_ar TEXT,
                  price REAL NOT NULL,
                  currency TEXT DEFAULT 'AED',
                  category TEXT NOT NULL,
                  description TEXT,
                  description_ru TEXT,
                  description_ar TEXT,
                  benefits TEXT,
                  is_active INTEGER DEFAULT 1,
                  created_at TEXT,
                  updated_at TEXT)''')
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")
    # Мигрируем данные из config.py в БД при первом запуске
    migrate_services_to_db()



def migrate_services_to_db():
    """Перенести услуги из config.py в базу данных (выполняется один раз)"""
    from config import SERVICES
    
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    # Проверяем, есть ли уже услуги
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] > 0:
        conn.close()
        return
    
    now = datetime.now().isoformat()
    
    for key, service in SERVICES.items():
        benefits_json = '|'.join(service.get('benefits', []))
        
        c.execute("""INSERT INTO services 
                     (service_key, name, name_ru, name_ar, price, currency, category,
                      description, description_ru, benefits, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (key, service['name'], service.get('name_ru'), service.get('name_ar'),
                   service['price'], service.get('currency', 'AED'), service['category'],
                   service.get('description'), service.get('description_ru'),
                   benefits_json, now, now))
    
    conn.commit()
    conn.close()
    print("✅ Услуги перенесены в базу данных")


def get_all_users():
    """Получить всех пользователей"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("""SELECT id, username, password_hash, full_name, email, role, 
                 created_at, last_login, is_active 
                 FROM users ORDER BY id""")
    
    users = c.fetchall()
    conn.close()
    return users


def delete_user(user_id: int) -> bool:
    """Удалить пользователя"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        # Удаляем сессии
        c.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
        # Удаляем пользователя
        c.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Ошибка удаления пользователя: {e}")
        conn.close()
        return False

def get_all_services(active_only=True):
    """Получить все услуги из БД"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    if active_only:
        c.execute("SELECT * FROM services WHERE is_active = 1 ORDER BY category, name")
    else:
        c.execute("SELECT * FROM services ORDER BY category, name")
    
    services = c.fetchall()
    conn.close()
    return services

def get_service_by_key(service_key):
    """Получить услугу по ключу"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("SELECT * FROM services WHERE service_key = ?", (service_key,))
    service = c.fetchone()
    
    conn.close()
    return service

def create_service(service_key, name, name_ru, price, currency, category, 
                   description=None, description_ru=None, benefits=None):
    """Создать новую услугу"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    benefits_str = '|'.join(benefits) if benefits else ''
    
    try:
        c.execute("""INSERT INTO services 
                     (service_key, name, name_ru, price, currency, category,
                      description, description_ru, benefits, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (service_key, name, name_ru, price, currency, category,
                   description, description_ru, benefits_str, now, now))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def update_service(service_id, **kwargs):
    """Обновить услугу"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    updates = []
    params = []
    
    for key, value in kwargs.items():
        if key == 'benefits' and isinstance(value, list):
            value = '|'.join(value)
        updates.append(f"{key} = ?")
        params.append(value)
    
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    params.append(service_id)
    
    query = f"UPDATE services SET {', '.join(updates)} WHERE id = ?"
    c.execute(query, params)
    
    conn.commit()
    conn.close()
    return True

def delete_service(service_id):
    """Удалить услугу (мягкое удаление)"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("UPDATE services SET is_active = 0 WHERE id = ?", (service_id,))
    
    conn.commit()
    conn.close()
    return True
# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ =====

def create_user(username: str, password: str, full_name: str = None, 
                email: str = None, role: str = 'employee'):
    """Создать нового пользователя"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    now = datetime.now().isoformat()
    
    try:
        c.execute("""INSERT INTO users 
                     (username, password_hash, full_name, email, role, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (username, password_hash, full_name, email, role, now))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def verify_user(username: str, password: str) -> Optional[Dict]:
    """Проверить логин и пароль"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    c.execute("""SELECT id, username, full_name, email, role 
                 FROM users 
                 WHERE username = ? AND password_hash = ? AND is_active = 1""",
              (username, password_hash))
    
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "full_name": user[2],
            "email": user[3],
            "role": user[4]
        }
    return None




def get_user_by_email(email: str):
    """Получить пользователя по email"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("""SELECT id, username, full_name, email 
                 FROM users 
                 WHERE email = ? AND is_active = 1""", (email,))
    
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "full_name": user[2],
            "email": user[3]
        }
    return None

def create_password_reset_token(user_id: int) -> str:
    """Создать токен для сброса пароля"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    # Создаем таблицу для токенов если её нет
    c.execute('''CREATE TABLE IF NOT EXISTS password_reset_tokens
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  token TEXT UNIQUE,
                  created_at TEXT,
                  expires_at TEXT,
                  used INTEGER DEFAULT 0,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    token = secrets.token_urlsafe(32)
    now = datetime.now()
    expires = (now + timedelta(hours=1)).isoformat()
    
    c.execute("""INSERT INTO password_reset_tokens (user_id, token, created_at, expires_at)
                 VALUES (?, ?, ?, ?)""",
              (user_id, token, now.isoformat(), expires))
    
    conn.commit()
    conn.close()
    
    return token

def verify_reset_token(token: str):
    """Проверить токен сброса пароля"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    c.execute("""SELECT user_id FROM password_reset_tokens
                 WHERE token = ? AND expires_at > ? AND used = 0""",
              (token, now))
    
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else None

def mark_reset_token_used(token: str):
    """Отметить токен как использованный"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("UPDATE password_reset_tokens SET used = 1 WHERE token = ?", (token,))
    
    conn.commit()
    conn.close()

def reset_user_password(user_id: int, new_password: str):
    """Сбросить пароль пользователя"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    
    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
    
    conn.commit()
    conn.close()

    
    return RedirectResponse(url="/login?success=Пароль успешно изменён", status_code=302)

def create_session(user_id: int) -> str:
    """Создать сессию для пользователя"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    session_token = secrets.token_urlsafe(32)
    now = datetime.now()
    expires = (now + timedelta(days=7)).isoformat()
    
    c.execute("""INSERT INTO sessions (user_id, session_token, created_at, expires_at)
                 VALUES (?, ?, ?, ?)""",
              (user_id, session_token, now.isoformat(), expires))
    
    # Обновить last_login
    c.execute("UPDATE users SET last_login = ? WHERE id = ?", (now.isoformat(), user_id))
    
    conn.commit()
    conn.close()
    
    return session_token

def get_user_by_session(session_token: str) -> Optional[Dict]:
    """Получить пользователя по токену сессии"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    c.execute("""SELECT u.id, u.username, u.full_name, u.email, u.role
                 FROM users u
                 JOIN sessions s ON u.id = s.user_id
                 WHERE s.session_token = ? AND s.expires_at > ? AND u.is_active = 1""",
              (session_token, now))
    
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            "id": user[0],
            "username": user[1],
            "full_name": user[2],
            "email": user[3],
            "role": user[4]
        }
    return None

def delete_session(session_token: str):
    """Удалить сессию (выход)"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
    conn.commit()
    conn.close()

def log_activity(user_id: int, action: str, entity_type: str, 
                 entity_id: str, details: str = None):
    """Залогировать действие пользователя"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    
    c.execute("""INSERT INTO activity_log 
                 (user_id, action, entity_type, entity_id, details, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (user_id, action, entity_type, entity_id, details, now))
    
    conn.commit()
    conn.close()

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С КЛИЕНТАМИ =====

def get_client_by_id(instagram_id: str):
    """Получить клиента по ID"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("""SELECT instagram_id, username, phone, name, first_contact, 
                 last_contact, total_messages, labels, status, lifetime_value,
                 profile_pic, notes, is_pinned 
                 FROM clients WHERE instagram_id = ?""", (instagram_id,))
    
    client = c.fetchone()
    conn.close()
    return client

def update_client_info(instagram_id: str, name: str = None, phone: str = None, notes: str = None) -> bool:
    """Обновить информацию о клиенте"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        
        if updates:
            params.append(instagram_id)
            query = f"UPDATE clients SET {', '.join(updates)} WHERE instagram_id = ?"
            c.execute(query, params)
            conn.commit()
        
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка обновления клиента: {e}")
        conn.close()
        return False

def update_client_status(instagram_id: str, status: str):
    """Обновить статус клиента"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("UPDATE clients SET status = ? WHERE instagram_id = ?",
              (status, instagram_id))
    
    conn.commit()
    conn.close()

def pin_client(instagram_id: str, pinned: bool = True):
    """Закрепить/открепить клиента"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("UPDATE clients SET is_pinned = ? WHERE instagram_id = ?",
              (1 if pinned else 0, instagram_id))
    
    conn.commit()
    conn.close()

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С СООБЩЕНИЯМИ =====

def mark_messages_as_read(instagram_id: str, user_id: int = None):
    """Отметить сообщения как прочитанные"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("""UPDATE chat_history 
                 SET is_read = 1 
                 WHERE instagram_id = ? AND sender = 'client' AND is_read = 0""",
              (instagram_id,))
    
    conn.commit()
    conn.close()

def get_unread_messages_count(instagram_id: str) -> int:
    """Получить количество непрочитанных сообщений"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("""SELECT COUNT(*) FROM chat_history 
                 WHERE instagram_id = ? AND sender = 'client' AND is_read = 0""",
              (instagram_id,))
    
    count = c.fetchone()[0]
    conn.close()
    
    return count

# ===== ОСТАЛЬНЫЕ ФУНКЦИИ =====

def get_or_create_client(instagram_id: str, username: str = None):
    """Получить или создать клиента"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("SELECT * FROM clients WHERE instagram_id = ?", (instagram_id,))
    client = c.fetchone()
    
    if not client:
        now = datetime.now().isoformat()
        c.execute("""INSERT INTO clients 
                     (instagram_id, username, first_contact, last_contact, total_messages, labels, status)
                     VALUES (?, ?, ?, ?, 0, ?, ?)""",
                  (instagram_id, username, now, now, "Новый клиент", "new"))
        conn.commit()
        print(f"✨ Новый клиент: {instagram_id}")
    else:
        now = datetime.now().isoformat()
        c.execute("UPDATE clients SET last_contact = ?, total_messages = total_messages + 1 WHERE instagram_id = ?",
                  (now, instagram_id))
        conn.commit()
    
    conn.close()

def save_message(instagram_id: str, message: str, sender: str, language: str = None, message_type: str = 'text'):
    """Сохранить сообщение"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    is_read = 1 if sender == 'bot' else 0
    
    c.execute("""INSERT INTO chat_history 
                 (instagram_id, message, sender, timestamp, language, is_read, message_type)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (instagram_id, message, sender, now, language, is_read, message_type))
    
    conn.commit()
    conn.close()

def get_chat_history(instagram_id: str, limit: int = 10):
    """Получить историю чата"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("""SELECT message, sender, timestamp, message_type FROM chat_history 
                 WHERE instagram_id = ? 
                 ORDER BY timestamp DESC LIMIT ?""",
              (instagram_id, limit))
    
    history = c.fetchall()
    conn.close()
    
    return list(reversed(history))

def get_booking_progress(instagram_id: str) -> Optional[Dict]:
    """Получить прогресс записи"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("SELECT * FROM booking_temp WHERE instagram_id = ?", (instagram_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "instagram_id": row[0],
            "service_name": row[1],
            "date": row[2],
            "time": row[3],
            "phone": row[4],
            "name": row[5],
            "step": row[6]
        }
    return None

def update_booking_progress(instagram_id: str, data: Dict):
    """Обновить прогресс записи"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("""INSERT OR REPLACE INTO booking_temp 
                 (instagram_id, service_name, date, time, phone, name, step)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (instagram_id, data.get('service_name'), data.get('date'),
               data.get('time'), data.get('phone'), data.get('name'), data.get('step')))
    
    conn.commit()
    conn.close()

def clear_booking_progress(instagram_id: str):
    """Очистить прогресс записи"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM booking_temp WHERE instagram_id = ?", (instagram_id,))
    conn.commit()
    conn.close()

def save_booking(instagram_id: str, service: str, datetime_str: str, phone: str, name: str):
    """Сохранить завершённую запись"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO bookings 
                 (instagram_id, service_name, datetime, phone, name, status, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (instagram_id, service, datetime_str, phone, name, "pending", now))
    
    c.execute("UPDATE clients SET status = 'lead', phone = ?, name = ? WHERE instagram_id = ?",
              (phone, name, instagram_id))
    
    conn.commit()
    conn.close()

def update_booking_status(booking_id: int, status: str) -> bool:
    """Обновить статус записи"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        if status == 'completed':
            completed_at = datetime.now().isoformat()
            c.execute("""UPDATE bookings 
                        SET status = ?, completed_at = ? 
                        WHERE id = ?""",
                     (status, completed_at, booking_id))
        else:
            c.execute("UPDATE bookings SET status = ? WHERE id = ?",
                     (status, booking_id))
        
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Ошибка обновления статуса: {e}")
        conn.close()
        return False

def get_all_clients():
    """Получить всех клиентов"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        c.execute("""SELECT instagram_id, username, phone, name, first_contact, 
                     last_contact, total_messages, labels, status, lifetime_value,
                     profile_pic, notes, is_pinned 
                     FROM clients ORDER BY is_pinned DESC, last_contact DESC""")
    except sqlite3.OperationalError:
        # Fallback для старой версии БД
        c.execute("""SELECT instagram_id, username, phone, name, first_contact, 
                     last_contact, total_messages, labels, 'new' as status, 0 as lifetime_value,
                     NULL as profile_pic, NULL as notes, 0 as is_pinned
                     FROM clients ORDER BY last_contact DESC""")
    
    clients = c.fetchall()
    conn.close()
    return clients

def get_all_bookings():
    """Получить все записи"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        c.execute("""SELECT id, instagram_id, service_name, datetime, phone, 
                     name, status, created_at, revenue 
                     FROM bookings ORDER BY created_at DESC""")
    except sqlite3.OperationalError:
        c.execute("""SELECT id, instagram_id, service_name, datetime, phone, 
                     name, status, created_at, 0 as revenue 
                     FROM bookings ORDER BY created_at DESC""")
    
    bookings = c.fetchall()
    conn.close()
    return bookings

def get_all_messages(limit: int = 100):
    """Получить все сообщения"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("""SELECT id, instagram_id, message, sender, timestamp 
                 FROM chat_history ORDER BY timestamp DESC LIMIT ?""", (limit,))
    
    messages = c.fetchall()
    conn.close()
    return messages

def get_stats():
    """Получить статистику"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM clients")
    total_clients = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM bookings WHERE status='completed'")
    completed_bookings = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM bookings WHERE status='pending'")
    pending_bookings = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM chat_history WHERE sender='client'")
    total_client_messages = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM chat_history WHERE sender='bot'")
    total_bot_messages = c.fetchone()[0]
    
    try:
        c.execute("SELECT SUM(revenue) FROM bookings WHERE status='completed'")
        total_revenue = c.fetchone()[0] or 0
    except sqlite3.OperationalError:
        total_revenue = 0
    
    try:
        c.execute("SELECT COUNT(*) FROM clients WHERE status='new'")
        new_clients = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM clients WHERE status='lead'")
        leads = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM clients WHERE status='customer'")
        customers = c.fetchone()[0]
    except sqlite3.OperationalError:
        new_clients = total_clients
        leads = 0
        customers = 0
    
    conn.close()
    
    conversion_rate = (completed_bookings / total_clients * 100) if total_clients > 0 else 0
    
    return {
        "total_clients": total_clients,
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings,
        "pending_bookings": pending_bookings,
        "total_client_messages": total_client_messages,
        "total_bot_messages": total_bot_messages,
        "total_revenue": round(total_revenue, 2),
        "new_clients": new_clients,
        "leads": leads,
        "customers": customers,
        "conversion_rate": round(conversion_rate, 2)
    }

def get_analytics_data(days=30, date_from=None, date_to=None):
    """Получить данные для аналитики с периодом"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    if date_from and date_to:
        start_date = date_from
        end_date = date_to
    else:
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        end_date = datetime.now().isoformat()
    
    c.execute("""SELECT DATE(created_at) as date, COUNT(*) as count
                 FROM bookings 
                 WHERE created_at >= ? AND created_at <= ?
                 GROUP BY DATE(created_at)
                 ORDER BY date""", (start_date, end_date))
    bookings_by_day = c.fetchall()
    
    if not bookings_by_day:
        bookings_by_day = [(datetime.now().strftime('%Y-%m-%d'), 0)]
    
    c.execute("""SELECT service_name, COUNT(*) as count, SUM(revenue) as revenue
                 FROM bookings 
                 WHERE created_at >= ? AND created_at <= ?
                 GROUP BY service_name 
                 ORDER BY count DESC""", (start_date, end_date))
    services_stats = c.fetchall()
    
    if not services_stats:
        services_stats = [("Нет данных", 0, 0)]
    
    c.execute("""SELECT status, COUNT(*) as count
                 FROM bookings 
                 WHERE created_at >= ? AND created_at <= ?
                 GROUP BY status""", (start_date, end_date))
    status_stats = c.fetchall()
    
    if not status_stats:
        status_stats = [("pending", 0)]
    
    c.execute("""SELECT 
                    AVG((julianday(bot.timestamp) - julianday(client.timestamp)) * 24 * 60) as avg_minutes
                 FROM chat_history client
                 JOIN chat_history bot ON client.instagram_id = bot.instagram_id
                 WHERE client.sender = 'client' 
                 AND bot.sender = 'bot'
                 AND bot.id > client.id
                 AND bot.timestamp >= ? AND bot.timestamp <= ?
                 LIMIT 100""", (start_date, end_date))
    
    result = c.fetchone()
    avg_response = result[0] if result and result[0] else 2.5
    
    conn.close()
    
    return {
        "bookings_by_day": bookings_by_day,
        "services_stats": services_stats,
        "status_stats": status_stats,
        "avg_response_time": round(avg_response, 2) if avg_response else 2.5
    }

def get_funnel_data():
    """Получить данные воронки продаж"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM clients")
    total_visitors = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM clients WHERE total_messages > 0")
    engaged = c.fetchone()[0]
    
    c.execute("SELECT COUNT(DISTINCT instagram_id) FROM booking_temp")
    started_booking = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM bookings WHERE status='pending'")
    booked = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM bookings WHERE status='completed'")
    completed = c.fetchone()[0]
    
    conn.close()
    
    total_visitors = max(total_visitors, 1)
    engaged = max(engaged, 1)
    started_booking = max(started_booking, 1)
    booked = max(booked, 1)
    
    return {
        "visitors": total_visitors,
        "engaged": engaged,
        "started_booking": started_booking,
        "booked": booked,
        "completed": completed,
        "conversion_rates": {
            "visitor_to_engaged": round((engaged / total_visitors * 100), 2),
            "engaged_to_booking": round((started_booking / engaged * 100), 2),
            "booking_to_booked": round((booked / started_booking * 100), 2),
            "booked_to_completed": round((completed / booked * 100) if booked > 0 else 0, 2)
        }
    }

# Добавьте эти функции в конец вашего database.py

def get_custom_statuses():
    """Получить все кастомные статусы"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute("SELECT * FROM custom_statuses ORDER BY created_at DESC")
    statuses = c.fetchall()
    
    conn.close()
    return statuses

def create_custom_status(status_key: str, status_label: str, status_color: str, 
                        status_icon: str, created_by: int) -> bool:
    """Создать новый кастомный статус"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        now = datetime.now().isoformat()
        c.execute("""INSERT INTO custom_statuses 
                     (status_key, status_label, status_color, status_icon, created_at, created_by)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (status_key, status_label, status_color, status_icon, now, created_by))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_custom_status(status_key: str) -> bool:
    """Удалить кастомный статус"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM custom_statuses WHERE status_key = ?", (status_key,))
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"Ошибка удаления статуса: {e}")
        conn.close()
        return False

def update_custom_status(status_key: str, status_label: str = None, 
                        status_color: str = None, status_icon: str = None) -> bool:
    """Обновить кастомный статус"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if status_label:
            updates.append("status_label = ?")
            params.append(status_label)
        
        if status_color:
            updates.append("status_color = ?")
            params.append(status_color)
        
        if status_icon:
            updates.append("status_icon = ?")
            params.append(status_icon)
        
        if updates:
            params.append(status_key)
            query = f"UPDATE custom_statuses SET {', '.join(updates)} WHERE status_key = ?"
            c.execute(query, params)
            conn.commit()
        
        conn.close()
        return True
    except Exception as e:
        print(f"Ошибка обновления статуса: {e}")
        conn.close()
        return False


# ===== ДОБАВИТЬ ЭТИ ФУНКЦИИ В database.py =====

def init_bot_settings_table():
    """Создать таблицу для настроек бота"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
                 (id INTEGER PRIMARY KEY,
                  settings TEXT NOT NULL,
                  updated_at TEXT,
                  updated_by INTEGER,
                  FOREIGN KEY (updated_by) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()
    print("✅ Таблица bot_settings создана")


# Добавить вызов в init_database():
# init_bot_settings_table()


def get_bot_settings():
    """Получить настройки бота из базы данных"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        c.execute("SELECT settings FROM bot_settings WHERE id = 1")
        result = c.fetchone()
        conn.close()
        
        if result:
            import json
            return json.loads(result[0])
        return None
    except Exception as e:
        conn.close()
        print(f"Ошибка получения настроек бота: {e}")
        return None


def save_bot_settings(settings, user_id=None):
    """
    Сохранить настройки бота
    
    Args:
        settings: dict с настройками
        user_id: ID пользователя, который сохраняет
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        import json
        from datetime import datetime
        
        settings_json = json.dumps(settings, ensure_ascii=False)
        now = datetime.now().isoformat()
        
        # Удаляем старые настройки
        c.execute("DELETE FROM bot_settings")
        
        # Вставляем новые
        c.execute("""INSERT INTO bot_settings (id, settings, updated_at, updated_by)
                     VALUES (1, ?, ?, ?)""",
                  (settings_json, now, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"Ошибка сохранения настроек бота: {e}")
        return False


def delete_bot_settings():
    """Удалить настройки бота"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM bot_settings")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"Ошибка удаления настроек: {e}")
        return False
    

def add_database_indexes():
    """Добавить индексы для ускорения запросов"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    try:
        # Индексы для chat_history
        c.execute("""CREATE INDEX IF NOT EXISTS idx_chat_instagram_id 
                     ON chat_history(instagram_id)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_chat_timestamp 
                     ON chat_history(timestamp DESC)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_chat_sender 
                     ON chat_history(sender)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_chat_unread 
                     ON chat_history(instagram_id, is_read, sender)""")
        
        # Индексы для clients
        c.execute("""CREATE INDEX IF NOT EXISTS idx_clients_last_contact 
                     ON clients(last_contact DESC)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_clients_status 
                     ON clients(status)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_clients_pinned 
                     ON clients(is_pinned DESC, last_contact DESC)""")
        
        # Индексы для bookings
        c.execute("""CREATE INDEX IF NOT EXISTS idx_bookings_instagram_id 
                     ON bookings(instagram_id)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_bookings_status 
                     ON bookings(status)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_bookings_created 
                     ON bookings(created_at DESC)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_bookings_datetime 
                     ON bookings(datetime)""")
        
        # Индексы для services
        c.execute("""CREATE INDEX IF NOT EXISTS idx_services_category 
                     ON services(category)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_services_active 
                     ON services(is_active)""")
        
        # Индексы для sessions
        c.execute("""CREATE INDEX IF NOT EXISTS idx_sessions_token 
                     ON sessions(session_token)""")
        c.execute("""CREATE INDEX IF NOT EXISTS idx_sessions_expires 
                     ON sessions(expires_at)""")
        
        conn.commit()
        conn.close()
        print("✅ Индексы созданы для оптимизации")
    except Exception as e:
        conn.close()
        print(f"⚠️ Ошибка создания индексов: {e}")