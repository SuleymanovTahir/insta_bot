import sqlite3
from config import DATABASE_NAME

def migrate_database():
    """Обновить структуру базы данных"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    print("🔄 Начинаем миграцию базы данных...")
    
    # Добавить новые колонки в clients если их нет
    try:
        c.execute("ALTER TABLE clients ADD COLUMN status TEXT DEFAULT 'new'")
        print("✅ Добавлена колонка 'status' в таблицу clients")
    except sqlite3.OperationalError:
        print("ℹ️  Колонка 'status' уже существует")
    
    try:
        c.execute("ALTER TABLE clients ADD COLUMN source TEXT DEFAULT 'instagram'")
        print("✅ Добавлена колонка 'source' в таблицу clients")
    except sqlite3.OperationalError:
        print("ℹ️  Колонка 'source' уже существует")
    
    try:
        c.execute("ALTER TABLE clients ADD COLUMN lifetime_value REAL DEFAULT 0")
        print("✅ Добавлена колонка 'lifetime_value' в таблицу clients")
    except sqlite3.OperationalError:
        print("ℹ️  Колонка 'lifetime_value' уже существует")
    
    # Добавить новые колонки в bookings если их нет
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN completed_at TEXT")
        print("✅ Добавлена колонка 'completed_at' в таблицу bookings")
    except sqlite3.OperationalError:
        print("ℹ️  Колонка 'completed_at' уже существует")
    
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN revenue REAL DEFAULT 0")
        print("✅ Добавлена колонка 'revenue' в таблицу bookings")
    except sqlite3.OperationalError:
        print("ℹ️  Колонка 'revenue' уже существует")
    
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN notes TEXT")
        print("✅ Добавлена колонка 'notes' в таблицу bookings")
    except sqlite3.OperationalError:
        print("ℹ️  Колонка 'notes' уже существует")
    
    # Создать таблицу client_interactions если её нет
    c.execute('''CREATE TABLE IF NOT EXISTS client_interactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  instagram_id TEXT,
                  interaction_type TEXT,
                  timestamp TEXT,
                  metadata TEXT)''')
    print("✅ Таблица 'client_interactions' готова")
    
    conn.commit()
    conn.close()
    
    print("🎉 Миграция завершена успешно!")

if __name__ == "__main__":
    migrate_database()
