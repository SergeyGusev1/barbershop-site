from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.context import CryptContext

DATABASE_URL = "sqlite:///./beauty.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    icon = Column(String, default="✨")
    order = Column(Integer, default=0)
    services = relationship("Service", back_populates="category", cascade="all, delete-orphan")


class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    price = Column(String, nullable=False)
    price_prefix = Column(String, default="")
    description = Column(Text, default="")
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    category = relationship("Category", back_populates="services")


class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(AdminUser).count() == 0:
        db.add(AdminUser(
            username="admin",
            password_hash=pwd_context.hash("beauty2024")
        ))

    if db.query(Category).count() == 0:
        categories_data = [
            ("Женские стрижки", "strizhka-f", "✂️", 1),
            ("Мужские стрижки", "strizhka-m", "💈", 2),
            ("Окрашивание", "okrashivanie", "🎨", 3),
            ("Восстановление волос", "vosstanovlenie", "💆", 4),
            ("Укладка", "ukladka", "💇", 5),
            ("Реконструкция волос", "rekonstrukcia", "⚗️", 6),
            ("Маникюр", "manikur", "💅", 7),
            ("Педикюр", "pedicur", "🦶", 8),
            ("Брови и ресницы", "brovi", "👁️", 9),
            ("Наращивание ресниц", "narashivanie", "✨", 10),
            ("Депиляция воском", "depilacia", "🌸", 11),
            ("Массаж", "massazh", "🤲", 12),
            ("Солярий", "solyariy", "☀️", 13),
            ("SPA-программы", "spa", "🛁", 14),
            ("Акции", "akcii", "🎁", 15),
        ]
        cats = {}
        for name, slug, icon, order in categories_data:
            c = Category(name=name, slug=slug, icon=icon, order=order)
            db.add(c)
            db.flush()
            cats[slug] = c.id

        services_data = [
            # Женские стрижки
            ("strizhka-f", "Короткие", "1 100", "", 1),
            ("strizhka-f", "Средние", "1 400", "", 2),
            ("strizhka-f", "Длинные", "1 800", "", 3),
            ("strizhka-f", "Супер-длинные", "2 300", "", 4),
            ("strizhka-f", "Чёлка", "500", "", 5),
            ("strizhka-f", "В один срез", "600", "", 6),
            ("strizhka-f", "Детская", "600", "", 7),
            # Мужские стрижки
            ("strizhka-m", "Классическая", "800", "", 1),
            ("strizhka-m", "Под ноль", "400", "", 2),
            ("strizhka-m", "Под насадку", "500", "", 3),
            ("strizhka-m", "Под две насадки", "600", "", 4),
            ("strizhka-m", "Окантовка", "300", "", 5),
            ("strizhka-m", "Детская", "600", "", 6),
            ("strizhka-m", "Борода", "800", "", 7),
            ("strizhka-m", "Стрижка + борода", "1 500", "", 8),
            ("strizhka-m", "Отец + сын", "1 200", "", 9),
            ("strizhka-m", "Bro + Bro", "1 400", "", 10),
            # Процедуры для мужчин (добавим в мужские)
            ("strizhka-m", "Камуфляж головы", "1 000", "", 11),
            ("strizhka-m", "Камуфляж бороды", "800", "", 12),
            ("strizhka-m", "Королевское бритьё", "1 100", "", 13),
            ("strizhka-m", "Укладка", "500", "", 14),
            ("strizhka-m", "Горячий воск (уши+нос)", "400", "", 15),
            ("strizhka-m", "Чистка лица (скраб+black mask)", "800", "", 16),
            ("strizhka-m", "Мытьё головы", "200", "", 17),
            # Окрашивание
            ("okrashivanie", "Окрашивание в 1 тон — короткие", "3 500", "", 1),
            ("okrashivanie", "Окрашивание в 1 тон — средние", "4 500", "", 2),
            ("okrashivanie", "Окрашивание в 1 тон — длинные", "6 000", "", 3),
            ("okrashivanie", "Окрашивание в 1 тон — супер-длинные", "8 000", "от ", 4),
            ("okrashivanie", "Смывка 1–3 тона", "2 000", "", 5),
            ("okrashivanie", "Корни", "2 500", "", 6),
            ("okrashivanie", "Корни Тотал-Блонд", "4 500", "", 7),
            ("okrashivanie", "Сложное — короткие", "9 000", "", 8),
            ("okrashivanie", "Сложное — средние", "12 000", "", 9),
            ("okrashivanie", "Сложное — длинные", "16 000", "", 10),
            ("okrashivanie", "Сложное — супер-длинные", "20 000", "от ", 11),
            ("okrashivanie", "Корни сложное", "7 500", "", 12),
            ("okrashivanie", "Выход из чёрного — короткие", "11 000", "", 13),
            ("okrashivanie", "Выход из чёрного — средние", "14 000", "", 14),
            ("okrashivanie", "Выход из чёрного — длинные", "18 000", "", 15),
            ("okrashivanie", "Выход из чёрного — супер-длинные", "22 000", "от ", 16),
            # Восстановление волос
            ("vosstanovlenie", "Короткие", "1 200", "", 1),
            ("vosstanovlenie", "Средние", "1 500", "", 2),
            ("vosstanovlenie", "Длинные", "1 800", "", 3),
            ("vosstanovlenie", "Супер-длинные", "2 000", "", 4),
            ("vosstanovlenie", "Обжиг огнём — короткие", "1 500", "", 5),
            ("vosstanovlenie", "Обжиг огнём — средние", "2 000", "", 6),
            ("vosstanovlenie", "Обжиг огнём — длинные", "2 500", "", 7),
            ("vosstanovlenie", "Обжиг огнём — супер-длинные", "2 800", "", 8),
            # Укладка
            ("ukladka", "Короткие", "800", "", 1),
            ("ukladka", "Средние", "1 200", "", 2),
            ("ukladka", "Длинные", "1 500", "", 3),
            ("ukladka", "Супер-длинные", "2 000", "от ", 4),
            ("ukladka", "Мытьё головы с сушкой на стайлер", "500–800", "", 5),
            # Реконструкция волос
            ("rekonstrukcia", "Кератин / Биксипластия / Ботокс — 30 см", "6 000", "", 1),
            ("rekonstrukcia", "Кератин / Биксипластия / Ботокс — 40 см", "8 000", "", 2),
            ("rekonstrukcia", "Кератин / Биксипластия / Ботокс — 50 см", "12 000", "", 3),
            ("rekonstrukcia", "Кератин / Биксипластия / Ботокс — 60 см", "10 000", "", 4),
            ("rekonstrukcia", "Кератин / Биксипластия / Ботокс — 70 см", "14 000", "", 5),
            ("rekonstrukcia", "Кератин / Биксипластия / Ботокс — длиннее 70 см", "18 000", "", 6),
            ("rekonstrukcia", "Пилинг", "500–700", "", 7),
            ("rekonstrukcia", "Питательная подложка (аминокислоты)", "+1 500", "", 8),
            # Маникюр
            ("manikur", "Без покрытия", "1 700", "", 1),
            ("manikur", "С покрытием", "2 800", "", 2),
            ("manikur", "Наращивание", "3 500", "", 3),
            ("manikur", "Мужской", "2 000", "", 4),
            ("manikur", "Дизайн — Френч / Ноготь в стразах", "500", "", 5),
            ("manikur", "Дизайн — Роспись / Стемпинг", "400", "", 6),
            ("manikur", "Дизайн — Слайдеры", "300", "", 7),
            ("manikur", "Снятие (без процедуры)", "300", "", 8),
            # Педикюр
            ("pedicur", "Без покрытия", "2 000", "", 1),
            ("pedicur", "С покрытием", "3 500", "", 2),
            ("pedicur", "Мужской", "2 800", "", 3),
            ("pedicur", "Дизайн — Френч / Ноготь в стразах", "400", "", 4),
            ("pedicur", "Дизайн — Роспись / Стемпинг", "300", "", 5),
            ("pedicur", "Дизайн — Слайдеры", "200", "", 6),
            # Брови и ресницы
            ("brovi", "Коррекция бровей", "700", "", 1),
            ("brovi", "Коррекция + окрашивание", "1 400", "", 2),
            ("brovi", "Окрашивание бровей", "800", "", 3),
            ("brovi", "Окрашивание ресниц", "700", "", 4),
            ("brovi", "Ламинирование бровей", "1 600", "", 5),
            ("brovi", "Ламинирование ресниц", "1 500", "", 6),
            ("brovi", "Ламинирование + окрашивание бровей", "2 200", "", 7),
            ("brovi", "Ламинирование + окрашивание ресниц", "2 200", "", 8),
            # Наращивание ресниц
            ("narashivanie", "Классика", "3 000", "", 1),
            ("narashivanie", "1.5D / Уголки", "3 000", "", 2),
            ("narashivanie", "2D", "3 200", "", 3),
            ("narashivanie", "3D", "3 500", "", 4),
            ("narashivanie", "4D", "3 800", "", 5),
            # Депиляция воском
            ("depilacia", "Лицо (полное)", "2 100", "", 1),
            ("depilacia", "Меж бровка / Над губой / Подбородок / Бакенбарды", "700", "", 2),
            ("depilacia", "Подмышки", "1 000", "", 3),
            ("depilacia", "Живот", "500", "", 4),
            ("depilacia", "Бикини", "3 000", "", 5),
            ("depilacia", "Ноги целиком", "3 000", "", 6),
            ("depilacia", "Бёдра / Голень", "2 000", "", 7),
            ("depilacia", "Руки до локтя", "1 500", "", 8),
            ("depilacia", "Руки целиком", "1 800", "", 9),
            ("depilacia", "Всё тело", "7 000", "", 10),
            # Массаж
            ("massazh", "Классический — 30 мин", "2 000", "", 1),
            ("massazh", "Классический — 60 мин", "3 000", "", 2),
            ("massazh", "Классический — 90 мин", "4 000", "", 3),
            ("massazh", "Спортивный — 30 мин", "3 000", "", 4),
            ("massazh", "Спортивный — 60 мин", "4 000", "", 5),
            ("massazh", "Спортивный — 90 мин", "5 000", "", 6),
            ("massazh", "Массаж лица 30 мин (де-макияж + увлажнение)", "2 500", "", 7),
            ("massazh", "Кедровая бочка — 30 мин", "1 000", "", 8),
            ("massazh", "Аппаратный лимфодренажный", "2 000", "", 9),
            ("massazh", "Аппаратный антицеллюлитный", "2 500", "", 10),
            # Солярий
            ("solyariy", "1 минута", "50", "", 1),
            ("solyariy", "50 минут (абонемент)", "2 250", "", 2),
            ("solyariy", "100 минут (абонемент)", "4 000", "", 3),
            # SPA
            ("spa", "Расслабляющий детокс для тела (1.5 ч)", "5 000", "", 1),
            ("spa", "Медовый комплекс для тела и лица (1.5 ч)", "5 000", "", 2),
            # Акции
            ("akcii", "Шальная императрица — Короткие (стрижка+окраска+восстановление)", "5 000", "", 1),
            ("akcii", "Шальная императрица — Средние", "6 500", "", 2),
            ("akcii", "Шальная императрица — Длинные", "8 000", "", 3),
            ("akcii", "Шальная императрица — Супер-длинные", "10 000", "от ", 4),
        ]

        for slug, name, price, prefix, order in services_data:
            cat_id = cats.get(slug)
            if cat_id:
                db.add(Service(
                    category_id=cat_id,
                    name=name,
                    price=price,
                    price_prefix=prefix,
                    order=order
                ))

    db.commit()
    db.close()
