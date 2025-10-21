import os
import warnings
import sys
import io
from datetime import datetime

os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# ===== ВЕРСИЯ ДЛЯ КЭШИРОВАНИЯ =====
CSS_VERSION = datetime.now().strftime('%Y%m%d%H%M%S')

# ===== ТОКЕНЫ И КЛЮЧИ =====
VERIFY_TOKEN = "taha"
PAGE_ACCESS_TOKEN = "EAAvRUEhJuBoBPk3mfuTp1UxZCYj0plL6ZCZAxxrLI9VX1ezuUYzVhH2ZBrFYURp76hpdjmZC5bMpIBkmEBD2Wbdf4ANUT77r9N2cUMzmK7yKdFbSjewBtZAhTrGPpNYZAorJJsVmkQzzMddBq7ZBWbMbUXuFmvfxloTluQPuAixqP9cQwBlzwtTmBaEzr5uxV0JrZALfe2ZA1MmdOSIvKZCGkMirOpqYgZDZD"
GEMINI_API_KEY = "AIzaSyDlgsahT92pPt-CsSd7XSlQm09uxyMCEHA"

# ===== ИНФОРМАЦИЯ О САЛОНЕ =====
SALON_INFO = {
    "name": "M.Le Diamant Beauty Lounge",
    "name_ar": "صالون M.Le Diamant للتجميل",
    "address": "Shop 13, Amwaj 3 Plaza Level, Jumeirah Beach Residence, Dubai",
    "address_ar": "المحل 13، مستوى أمواج 3 بلازا، جميرا بيتش ريزيدنس، دبي",
    "google_maps": "https://maps.app.goo.gl/r84DsemFhptY8RuC7",
    "hours": "Daily 10:30 - 21:00",
    "hours_ru": "Ежедневно 10:30 - 21:00",
    "hours_ar": "يوميًا 10:30 - 21:00",
    "booking_url": "https://n1314037.alteg.io",
    "phone": "+971 XX XXX XXXX",
    "bot_name": "Diamant",
    "bot_name_en": "Diamant",
    "bot_name_ar": "الماس"
}

# ===== ПОЛНЫЙ ПРАЙС-ЛИСТ УСЛУГ =====
SERVICES = {
    # Permanent Makeup
    "permanent_lips": {
        "name": "Permanent Lips",
        "name_ru": "Перманентный макияж губ",
        "name_ar": "شفاه دائمة",
        "price": 800,
        "currency": "AED",
        "category": "Permanent Makeup",
        "description": "Long-lasting lip color enhancement",
        "description_ru": "Долговременное окрашивание губ с естественным эффектом",
        "benefits": ["Стойкий результат до 2 лет", "Естественный цвет", "Коррекция формы губ"]
    },
    "permanent_brows": {
        "name": "Permanent Brows",
        "name_ru": "Перманентный макияж бровей",
        "name_ar": "حواجب دائمة",
        "price": 700,
        "currency": "AED",
        "category": "Permanent Makeup",
        "description": "Perfect eyebrows that last",
        "description_ru": "Идеальные брови навсегда - микроблейдинг или пудровое напыление",
        "benefits": ["Стойкость до 2 лет", "Естественная форма", "Без ежедневного макияжа"]
    },
    "lashliner": {
        "name": "Lashliner",
        "name_ru": "Межресничная стрелка",
        "price": 500,
        "currency": "AED",
        "category": "Permanent Makeup",
        "description": "Natural lash enhancement",
        "description_ru": "Деликатная прорисовка межресничного пространства",
        "benefits": ["Визуальная густота ресниц", "Естественный эффект", "Стойкость до 1.5 лет"]
    },
    "eyeliner": {
        "name": "Eyeliner",
        "name_ru": "Перманентная подводка",
        "price": 1000,
        "currency": "AED",
        "category": "Permanent Makeup",
        "description": "Perfect eyeliner every day",
        "description_ru": "Идеальные стрелки на каждый день",
        "benefits": ["Яркий выразительный взгляд", "Водостойкая", "До 2 лет стойкости"]
    },
    "pm_correction": {
        "name": "PM Correction",
        "name_ru": "Коррекция перманента",
        "price": 500,
        "currency": "AED",
        "category": "Permanent Makeup",
        "description": "Touch-up for permanent makeup",
        "description_ru": "Обновление и коррекция существующего перманента",
        "benefits": ["Освежение цвета", "Коррекция формы", "Поддержание результата"]
    },
    
    # Facial Treatments
    "deep_facial": {
        "name": "Deep Facial Cleaning",
        "name_ru": "Глубокая чистка лица",
        "price": 400,
        "currency": "AED",
        "category": "Facial",
        "description": "Professional deep cleansing",
        "description_ru": "Профессиональная глубокая очистка пор",
        "benefits": ["Удаление черных точек", "Очищение пор", "Свежая кожа"]
    },
    "medical_facial": {
        "name": "Medical Facial Cleaning for Problem Skin",
        "name_ru": "Медицинская чистка проблемной кожи",
        "price": 450,
        "currency": "AED",
        "category": "Facial",
        "description": "Specialized treatment for problematic skin",
        "description_ru": "Специализированная чистка для проблемной кожи",
        "benefits": ["Лечение акне", "Профессиональный подход", "Заметный результат"]
    },
    "face_lift_massage": {
        "name": "Face Lift Massage with Mask",
        "name_ru": "Лифтинг-массаж лица с маской",
        "price": 250,
        "currency": "AED",
        "category": "Facial",
        "description": "Anti-aging facial massage and mask",
        "description_ru": "Омолаживающий массаж лица с питательной маской",
        "benefits": ["Подтяжка овала лица", "Улучшение тонуса", "Сияющая кожа"]
    },
    "peeling_300": {
        "name": "Peeling",
        "name_ru": "Пилинг",
        "price": 300,
        "currency": "AED",
        "price_range": "300-400 AED",
        "category": "Facial",
        "description": "Chemical or mechanical skin exfoliation",
        "description_ru": "Химический или механический пилинг - обновление кожи",
        "benefits": ["Обновление кожи", "Ровный тон", "Гладкая текстура"]
    },
    "spa_relax": {
        "name": "Time Of Relax SPA",
        "name_ru": "СПА-релакс программа",
        "price": 250,
        "currency": "AED",
        "category": "Facial",
        "description": "Relaxing spa treatment",
        "description_ru": "Расслабляющая СПА-программа для лица",
        "benefits": ["Глубокое расслабление", "Увлажнение кожи", "Снятие стресса"]
    },
    
    # Massage Services
    "head_massage": {
        "name": "Head Massage 40min",
        "name_ru": "Массаж головы 40 минут",
        "price": 100,
        "currency": "AED",
        "category": "Massage",
        "description": "Relaxing head and scalp massage",
        "description_ru": "Расслабляющий массаж головы и кожи головы",
        "benefits": ["Снятие напряжения", "Улучшение кровообращения", "Релаксация"]
    },
    "extremities_massage": {
        "name": "Massage (legs/feet/hands) 40min",
        "name_ru": "Массаж ног/стоп/рук 40 минут",
        "price": 150,
        "currency": "AED",
        "category": "Massage",
        "description": "Targeted massage for extremities",
        "description_ru": "Локальный массаж конечностей",
        "benefits": ["Снятие усталости", "Улучшение циркуляции", "Легкость в ногах"]
    },
    "back_massage": {
        "name": "Back Massage 30min",
        "name_ru": "Массаж спины 30 минут",
        "price": 180,
        "currency": "AED",
        "category": "Massage",
        "description": "Therapeutic back massage",
        "description_ru": "Терапевтический массаж спины",
        "benefits": ["Снятие напряжения", "Расслабление мышц", "Улучшение осанки"]
    },
    "body_massage": {
        "name": "Body Massage 40min",
        "name_ru": "Массаж всего тела 40 минут",
        "price": 260,
        "currency": "AED",
        "category": "Massage",
        "description": "Full body relaxation massage",
        "description_ru": "Полный расслабляющий массаж тела",
        "benefits": ["Общее расслабление", "Снятие стресса", "Улучшение самочувствия"]
    },
    "sculpture_massage": {
        "name": "Sculpture Body Massage",
        "name_ru": "Скульптурирующий массаж тела",
        "price": 370,
        "currency": "AED",
        "category": "Massage",
        "description": "Body contouring massage",
        "description_ru": "Моделирующий массаж для коррекции фигуры",
        "benefits": ["Коррекция фигуры", "Подтяжка кожи", "Дренажный эффект"]
    },
    "anticellulite_massage": {
        "name": "Anti-Cellulite Massage 60min",
        "name_ru": "Антицеллюлитный массаж 60 минут",
        "price": 300,
        "currency": "AED",
        "category": "Massage",
        "description": "Specialized cellulite reduction massage",
        "description_ru": "Специализированный массаж против целлюлита",
        "benefits": ["Уменьшение целлюлита", "Улучшение текстуры кожи", "Дренаж"]
    },
    "hotstone_massage": {
        "name": "Hotstone Massage",
        "name_ru": "Стоун-массаж горячими камнями",
        "price": 310,
        "currency": "AED",
        "category": "Massage",
        "description": "Hot stone therapy massage",
        "description_ru": "Расслабляющий массаж горячими вулканическими камнями",
        "benefits": ["Глубокое расслабление", "Снятие мышечного напряжения", "Терапевтический эффект"]
    },
    
    # Manicure & Nails
    "manicure_no_polish": {
        "name": "Manicure no polish",
        "name_ru": "Маникюр без покрытия",
        "price": 80,
        "currency": "AED",
        "category": "Nails",
        "description": "Basic manicure service",
        "description_ru": "Уход за ногтями и кутикулой без покрытия",
        "benefits": ["Аккуратные ногти", "Уход за кутикулой", "Здоровые ногти"]
    },
    "manicure_normal": {
        "name": "Manicure normal polish",
        "name_ru": "Маникюр с обычным лаком",
        "price": 100,
        "currency": "AED",
        "category": "Nails",
        "description": "Manicure with regular polish",
        "description_ru": "Классический маникюр с покрытием обычным лаком",
        "benefits": ["Идеальная форма", "Яркий цвет", "Ухоженные руки"]
    },
    "manicure_gelish": {
        "name": "Gelish manicure",
        "name_ru": "Маникюр гель-лак",
        "price": 130,
        "currency": "AED",
        "category": "Nails",
        "description": "Long-lasting gel manicure",
        "description_ru": "Стойкий маникюр гель-лаком до 3 недель",
        "benefits": ["Стойкость до 3 недель", "Глянцевый блеск", "Быстрая сушка"]
    },
    "baby_manicure": {
        "name": "Baby manicure",
        "name_ru": "Детский маникюр",
        "price": 50,
        "currency": "AED",
        "category": "Nails",
        "description": "Gentle manicure for kids",
        "description_ru": "Деликатный уход за детскими ногтями",
        "benefits": ["Безопасно для детей", "Аккуратные ногти", "Приятная процедура"]
    },
    "nail_extension": {
        "name": "Nail Extension Full Set",
        "name_ru": "Наращивание ногтей полный сет",
        "price": 350,
        "currency": "AED",
        "category": "Nails",
        "description": "Complete nail extension service",
        "description_ru": "Полное наращивание ногтей гелем",
        "benefits": ["Идеальная длина", "Прочные ногти", "Любой дизайн"]
    },
    "remove_gel": {
        "name": "Remove Old Extension Gel",
        "name_ru": "Снятие старого гель-лака",
        "price": 50,
        "currency": "AED",
        "category": "Nails",
        "description": "Safe gel removal",
        "description_ru": "Безопасное снятие гель-покрытия",
        "benefits": ["Безопасное снятие", "Без повреждений", "Уход за ногтями"]
    },
    
    # Pedicure
    "pedicure_no_polish": {
        "name": "Pedicure no Polish",
        "name_ru": "Педикюр без покрытия",
        "price": 100,
        "currency": "AED",
        "category": "Nails",
        "description": "Basic pedicure service",
        "description_ru": "Уход за ногтями ног без покрытия",
        "benefits": ["Гладкие пяточки", "Аккуратные ногти", "Уход за стопами"]
    },
    "pedicure_normal": {
        "name": "Pedicure normal Polish",
        "name_ru": "Педикюр с обычным лаком",
        "price": 120,
        "currency": "AED",
        "category": "Nails",
        "description": "Pedicure with regular polish",
        "description_ru": "Педикюр с покрытием обычным лаком",
        "benefits": ["Красивые ногти", "Ухоженные стопы", "Яркий цвет"]
    },
    "pedicure_gelish": {
        "name": "Pedicure gelish",
        "name_ru": "Педикюр гель-лак",
        "price": 160,
        "currency": "AED",
        "category": "Nails",
        "description": "Long-lasting gel pedicure",
        "description_ru": "Стойкий педикюр с гель-лаком",
        "benefits": ["Стойкость до 4 недель", "Идеальный педикюр", "Гладкие пятки"]
    },
    
    # Hair Services
    "full_color": {
        "name": "Full Color and Blow Dry",
        "name_ru": "Полное окрашивание + укладка",
        "price": 350,
        "price_range": "350-500 AED",
        "currency": "AED",
        "category": "Hair",
        "description": "Complete hair coloring with styling",
        "description_ru": "Полное окрашивание волос по длине + укладка феном",
        "benefits": ["Равномерный цвет", "Профессиональные краски", "Стильная укладка"]
    },
    "balayage": {
        "name": "Balayage",
        "name_ru": "Балаяж",
        "price": 700,
        "price_range": "700-1200 AED",
        "currency": "AED",
        "category": "Hair",
        "description": "Natural-looking highlights",
        "description_ru": "Натуральное окрашивание в технике балаяж",
        "benefits": ["Естественный эффект", "Минимум обслуживания", "Модный стиль"]
    },
    "ombre": {
        "name": "Ombre/Shatush/Air-Touch",
        "name_ru": "Омбре/Шатуш/Аир-тач",
        "price": 1000,
        "price_range": "1000-1500 AED",
        "currency": "AED",
        "category": "Hair",
        "description": "Gradient coloring techniques",
        "description_ru": "Градиентное окрашивание в современных техниках",
        "benefits": ["Плавный переход", "Визуальный объем", "Трендовое окрашивание"]
    },
    "bleach_hair": {
        "name": "Bleach Hair",
        "name_ru": "Осветление волос",
        "price": 1300,
        "price_range": "1300-2300 AED",
        "currency": "AED",
        "category": "Hair",
        "description": "Professional hair bleaching",
        "description_ru": "Профессиональное осветление (цена зависит от сложности)",
        "benefits": ["Равномерное осветление", "Минимум повреждений", "Яркий блонд"]
    },
    "hair_treatment": {
        "name": "Hair Treatment",
        "name_ru": "Лечение волос",
        "price": 600,
        "price_range": "600-1500 AED",
        "currency": "AED",
        "category": "Hair",
        "description": "Restorative hair treatment",
        "description_ru": "Восстанавливающий уход для волос",
        "benefits": ["Восстановление структуры", "Блеск и мягкость", "Здоровые волосы"]
    },
    "hair_cut": {
        "name": "Hair Cut and Blow Dry",
        "name_ru": "Стрижка + укладка",
        "price": 250,
        "price_range": "250-300 AED",
        "currency": "AED",
        "category": "Hair",
        "description": "Haircut with styling",
        "description_ru": "Модельная стрижка с укладкой феном",
        "benefits": ["Модная стрижка", "Подбор формы", "Стильная укладка"]
    },
    
    # Lashes & Brows
    "classic_lashes": {
        "name": "Classic Volume Lashes",
        "name_ru": "Классическое наращивание ресниц",
        "price": 180,
        "currency": "AED",
        "category": "Lashes",
        "description": "Natural lash extension",
        "description_ru": "Естественное наращивание ресниц 1:1",
        "benefits": ["Естественный объем", "До 4 недель носки", "Выразительный взгляд"]
    },
    "2d_lashes": {
        "name": "2D Volume Lashes",
        "name_ru": "2D объем ресницы",
        "price": 230,
        "currency": "AED",
        "category": "Lashes",
        "description": "Enhanced volume lashes",
        "description_ru": "Объемное наращивание 2D",
        "benefits": ["Заметный объем", "Пушистые ресницы", "Долговременный эффект"]
    },
    "3d_lashes": {
        "name": "3D Volume Lashes",
        "name_ru": "3D объем ресницы",
        "price": 260,
        "currency": "AED",
        "category": "Lashes",
        "description": "Dramatic volume lashes",
        "description_ru": "Драматический объем 3D",
        "benefits": ["Максимальный объем", "Яркий эффект", "Голливудский взгляд"]
    },
    "mega_lashes": {
        "name": "4-5D Volume Lashes",
        "name_ru": "Мега объем 4-5D",
        "price": 290,
        "currency": "AED",
        "category": "Lashes",
        "description": "Mega volume lashes",
        "description_ru": "Мега-объемное наращивание 4-5D",
        "benefits": ["Максимальная густота", "Эффект накладных ресниц", "Роскошный взгляд"]
    },
    "brow_lamination": {
        "name": "Eyebrows Lamination",
        "name_ru": "Ламинирование бровей",
        "price": 200,
        "currency": "AED",
        "category": "Brows",
        "description": "Brow lamination treatment",
        "description_ru": "Долговременная укладка бровей",
        "benefits": ["Идеальная форма до 2 месяцев", "Ухоженный вид", "Без ежедневной укладки"]
    },
    "lash_lamination": {
        "name": "Eyelashes Lamination",
        "name_ru": "Ламинирование ресниц",
        "price": 200,
        "currency": "AED",
        "category": "Lashes",
        "description": "Lash lift and tint",
        "description_ru": "Подкручивание и окрашивание ресниц",
        "benefits": ["Изгиб до 2 месяцев", "Визуальное удлинение", "Отменяет тушь"]
    },
    "combo_lamination": {
        "name": "Combo package (Eyebrow and eyelash lamination)",
        "name_ru": "Комбо: брови + ресницы",
        "price": 300,
        "currency": "AED",
        "category": "Combo",
        "description": "Complete lamination package",
        "description_ru": "Комплексное ламинирование бровей и ресниц",
        "benefits": ["Экономия 100 AED", "Полный эффект", "Выразительный взгляд"]
    },
    
    # Waxing
    "full_bikini": {
        "name": "Full Bikini Wax",
        "name_ru": "Полная эпиляция бикини",
        "price": 150,
        "currency": "AED",
        "category": "Waxing",
        "description": "Complete bikini waxing",
        "description_ru": "Полная восковая эпиляция зоны бикини",
        "benefits": ["Гладкая кожа до 4 недель", "Деликатный воск", "Профессионально"]
    },
    "bikini_line": {
        "name": "Bikini Line Wax",
        "name_ru": "Эпиляция линии бикини",
        "price": 100,
        "currency": "AED",
        "category": "Waxing",
        "description": "Bikini line waxing",
        "description_ru": "Эпиляция по линии белья",
        "benefits": ["Быстро", "Аккуратно", "Без раздражения"]
    },
    "full_legs": {
        "name": "Full Legs Wax",
        "name_ru": "Эпиляция ног полностью",
        "price": 150,
        "currency": "AED",
        "category": "Waxing",
        "description": "Complete leg waxing",
        "description_ru": "Полная эпиляция ног",
        "benefits": ["Гладкие ноги", "До 4 недель", "Комфортно"]
    },
    "half_legs": {
        "name": "Half Legs Wax",
        "name_ru": "Эпиляция голеней",
        "price": 80,
        "currency": "AED",
        "category": "Waxing",
        "description": "Lower leg waxing",
        "description_ru": "Эпиляция голеней",
        "benefits": ["Быстрая процедура", "Эффективно", "Долгий результат"]
    },
    "full_body": {
        "name": "Full Body Wax",
        "name_ru": "Эпиляция всего тела",
        "price": 400,
        "currency": "AED",
        "category": "Waxing",
        "description": "Complete body waxing",
        "description_ru": "Полная эпиляция тела",
        "benefits": ["Идеально гладкая кожа", "Комплексный уход", "Экономия времени"]
    }
}

# ===== СТАТУСЫ КЛИЕНТОВ =====
CLIENT_STATUSES = {
    "new": {"label": "Новый", "color": "#3b82f6", "icon": "user-plus"},
    "contacted": {"label": "Связались", "color": "#8b5cf6", "icon": "phone"},
    "interested": {"label": "Заинтересован", "color": "#f59e0b", "icon": "star"},
    "lead": {"label": "Лид", "color": "#f59e0b", "icon": "user-clock"},
    "booking_started": {"label": "Начал запись", "color": "#10b981", "icon": "calendar-plus"},
    "booked": {"label": "Записан", "color": "#06b6d4", "icon": "calendar-check"},
    "customer": {"label": "Клиент", "color": "#10b981", "icon": "user-check"},
    "vip": {"label": "VIP", "color": "#ec4899", "icon": "crown"},
    "inactive": {"label": "Неактивен", "color": "#6b7280", "icon": "user-minus"},
    "blocked": {"label": "Заблокирован", "color": "#ef4444", "icon": "ban"}
}

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "ii3391609@gmail.com"
SMTP_PASSWORD = "hkfw qruh hxur ghta"
FROM_EMAIL = "ii3391609@gmail.com"

DATABASE_NAME = 'salon_bot.db'