import logging
import os
import sys
import asyncio
import sqlite3
import random
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder  # Импортируем InlineKeyboardBuilder для создания клавиатур
from logging.handlers import RotatingFileHandler

# =======================
# 1. Настройка логирования
# =======================

# Определяем путь к рабочему столу
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
log_folder = os.path.join(desktop_path, "logs")

# Создаем папку для логов, если она не существует
try:
    os.makedirs(log_folder, exist_ok=True)
    print(f"Папка для логов создана или уже существует: {log_folder}")
except Exception as e:
    print(f"Не удалось создать папку для логов: {e}")
    # Альтернативный путь
    log_folder = os.path.join(os.getcwd(), "logs")
    try:
        os.makedirs(log_folder, exist_ok=True)
        print(f"Папка для логов создана в текущей директории: {log_folder}")
    except Exception as e:
        print(f"Не удалось создать папку для логов в текущей директории: {e}")
        sys.exit(1)  # Завершаем работу, если не удалось создать папку для логов

# Определяем путь к файлу логов
log_file = os.path.join(log_folder, "bot.log")
print(f"Путь к файлу логов: {log_file}")

# Настройка логирования с ротацией файлов
handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8')
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger("bot_logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))

# =======================
# 2. Настройка базы данных
# =======================

# Путь к базе данных
db_path = "game.db"

# Подключаемся к базе данных
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    logger.info("Соединение с базой данных установлено.")
    print("Соединение с базой данных установлено.")

    # Создаем таблицу players, если она не существует
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY,
        cafe_name TEXT,
        balance INTEGER,
        last_income DATE,
        level INTEGER DEFAULT 1
    )
    """)
    conn.commit()
    logger.info("Таблица players готова.")
    print("Таблица players готова.")

    # Создание таблицы buildings, если она не существует
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buildings (
        building_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        base_cost INTEGER,
        income_multiplier INTEGER,
        resource_cost INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    logger.info("Таблица buildings готова.")
    print("Таблица buildings готова.")

    # Добавление зданий, если они ещё не добавлены
    buildings = [
        ("Магазин", 200, 2, 5),
        ("Склад", 300, 3, 3),
        ("Офис", 500, 5, 2)
    ]

    for building in buildings:
        try:
            cursor.execute("""
            INSERT INTO buildings (name, base_cost, income_multiplier, resource_cost)
            VALUES (?, ?, ?, ?)
            """, building)
            conn.commit()
            logger.info(f"Добавлено здание: {building[0]}")
            print(f"Добавлено здание: {building[0]}")
        except sqlite3.IntegrityError:
            # Здание уже существует
            logger.info(f"Здание {building[0]} уже существует.")
            print(f"Здание {building[0]} уже существует.")
except Exception as e:
    logger.error(f"Ошибка при подключении к базе данных: {e}", exc_info=True)
    print(f"Ошибка при подключении к базе данных: {e}")
    # Продолжаем выполнение, чтобы бот мог попытаться работать

# Создаем таблицу user_buildings, если она не существует
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_buildings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        building_name TEXT,
        level INTEGER,
        FOREIGN KEY(user_id) REFERENCES players(user_id)
    )
    """)
    conn.commit()
    logger.info("Таблица user_buildings готова.")
    print("Таблица user_buildings готова.")
except Exception as e:
    logger.error(f"Ошибка при создании таблицы user_buildings: {e}", exc_info=True)
    print(f"Ошибка при создании таблицы user_buildings: {e}")

# Создание таблицы resources, если она не существует
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)
    conn.commit()
    logger.info("Таблица resources готова.")
    print("Таблица resources готова.")

    # Добавление ресурсов, если они ещё не добавлены
    resources = [
        ("Кофейные зерна",),
        ("Молоко",),
        ("Сахар",)
    ]

    for resource in resources:
        try:
            cursor.execute("""
            INSERT INTO resources (name) VALUES (?)
            """, resource)
            conn.commit()
            logger.info(f"Добавлен ресурс: {resource[0]}")
            print(f"Добавлен ресурс: {resource[0]}")
        except sqlite3.IntegrityError:
            # Ресурс уже существует
            logger.info(f"Ресурс {resource[0]} уже существует.")
            print(f"Ресурс {resource[0]} уже существует.")
except Exception as e:
    logger.error(f"Ошибка при создании таблицы resources: {e}", exc_info=True)
    print(f"Ошибка при создании таблицы resources: {e}")

# Создание таблицы user_resources, если она не существует
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        resource_name TEXT,
        quantity INTEGER,
        FOREIGN KEY(user_id) REFERENCES players(user_id),
        FOREIGN KEY(resource_name) REFERENCES resources(name)
    )
    """)
    conn.commit()
    logger.info("Таблица user_resources готова.")
    print("Таблица user_resources готова.")
except Exception as e:
    logger.error(f"Ошибка при создании таблицы user_resources: {e}", exc_info=True)
    print(f"Ошибка при создании таблицы user_resources: {e}")

# Создание таблицы achievements, если она не существует
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        achievement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        description TEXT,
        condition TEXT
    )
    """)
    conn.commit()
    logger.info("Таблица achievements готова.")
    print("Таблица achievements готова.")

    # Добавление достижений, если они ещё не добавлены
    achievements = [
        ("Начинающий Бариста", "Достигните уровня 2 кофейни.", "level >= 2"),
        ("Опытный Бариста", "Достигните уровня 5 кофейни.", "level >= 5"),
        ("Мастер Кофе", "Достигните уровня 10 кофейни.", "level >= 10")
    ]

    for achievement in achievements:
        try:
            cursor.execute("""
            INSERT INTO achievements (name, description, condition)
            VALUES (?, ?, ?)
            """, achievement)
            conn.commit()
            logger.info(f"Добавлено достижение: {achievement[0]}")
            print(f"Добавлено достижение: {achievement[0]}")
        except sqlite3.IntegrityError:
            # Достижение уже существует
            logger.info(f"Достижение {achievement[0]} уже существует.")
            print(f"Достижение {achievement[0]} уже существует.")
except Exception as e:
    logger.error(f"Ошибка при создании таблицы achievements: {e}", exc_info=True)
    print(f"Ошибка при создании таблицы achievements: {e}")

# Создание таблицы user_achievements, если она не существует
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        achievement_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES players(user_id),
        FOREIGN KEY(achievement_id) REFERENCES achievements(achievement_id)
    )
    """)
    conn.commit()
    logger.info("Таблица user_achievements готова.")
    print("Таблица user_achievements готова.")
except Exception as e:
    logger.error(f"Ошибка при создании таблицы user_achievements: {e}", exc_info=True)
    print(f"Ошибка при создании таблицы user_achievements: {e}")

# =======================
# 3. Настройка бота
# =======================

# Указываем токен непосредственно в коде
BOT_TOKEN = "7601337093:AAEPQpZicF5sJ0OtKg_UlEqCeBXSWgCT3lM"  # Замените на ваш реальный токен

# Создаем экземпляр бота
try:
    bot = Bot(token=BOT_TOKEN)
    logger.info("Бот успешно создан с токеном.")
    print("Бот успешно создан с токеном.")
except Exception as e:
    logger.critical(f"Критическая ошибка при создании бота: {e}", exc_info=True)
    print(f"Критическая ошибка при создании бота: {e}")
    sys.exit(1)  # Завершаем работу, если бот не создан

# Создаем экземпляр роутера и диспетчера
router = Router()
dispatcher = Dispatcher()
dispatcher.include_router(router)

# =======================
# 4. Хендлеры команд
# =======================

# Ваш уникальный user_id для администрирования
ADMIN_USER_ID = 1490675453  # Замените на ваш реальный user_id

# Клавиатура для команды /start
main_keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="/start"), types.KeyboardButton(text="/my_cafe")],
        [types.KeyboardButton(text="/upgrade"), types.KeyboardButton(text="/shop")],
        [types.KeyboardButton(text="/collect"), types.KeyboardButton(text="/inventory")],
        [types.KeyboardButton(text="/achievements"), types.KeyboardButton(text="/leaderboard")],
        [types.KeyboardButton(text="/open_game")]  # Новая кнопка
    ],
    resize_keyboard=True
)

# Добавление команды /test для диагностики
@router.message(Command(commands=["test"]))
async def test_handler(message: types.Message):
    await message.answer("Команда /test работает!")
    logger.info(f"Пользователь {message.from_user.id} вызвал команду /test.")
    print(f"Пользователь {message.from_user.id} вызвал команду /test.")

@router.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO players (user_id, cafe_name, balance, last_income, level)
            VALUES (?, ?, ?, ?, ?)
        """, (message.from_user.id, "Street Cafe", 100, None, 1))
        conn.commit()
        logger.info(f"Пользователь {message.from_user.id} зарегистрирован.")
        print(f"Пользователь {message.from_user.id} зарегистрирован.")
        await message.answer("Добро пожаловать в Crypto Coffee! У вас теперь есть маленькая кофейня.", reply_markup=main_keyboard)
    except Exception as e:
        logger.error(f"Ошибка в команде /start для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")

@router.message(Command(commands=["my_cafe"]))
async def my_cafe_handler(message: Message):
    try:
        cursor.execute("""
            SELECT cafe_name, balance, level FROM players WHERE user_id = ?
        """, (message.from_user.id,))
        player = cursor.fetchone()
        if player:
            cafe_name, balance, level = player
            response = f"🏠 **Кофейня:** {cafe_name}\n💰 **Баланс:** {balance} монет\n🔼 **Уровень:** {level}"

            # Получаем список зданий пользователя
            cursor.execute("""
                SELECT building_name, level FROM user_buildings WHERE user_id = ?
            """, (message.from_user.id,))
            buildings = cursor.fetchall()
            if buildings:
                response += "\n\n🏢 **Здания:**"
                for building in buildings:
                    building_name, building_level = building
                    response += f"\n- {building_name} (Уровень {building_level})"
            else:
                response += "\n\n🏢 **Зданий:** Нет"

            # Создаем клавиатуру с кнопкой улучшения
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Улучшить кофейню (50 монет)", callback_data="upgrade")]
            ])

            # Определяем путь к изображению на основе уровня
            image_path = f"images/cafe_level_{level}.jpg"
            if not os.path.exists(image_path):
                image_path = "images/default_cafe.jpg"  # Запасной вариант

            # Проверяем, существует ли изображение
            if os.path.exists(image_path):
                with open(image_path, "rb") as photo:
                    await message.answer_photo(photo, caption=response, parse_mode="Markdown", reply_markup=keyboard)
            else:
                await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)

            logger.info(f"Пользователь {message.from_user.id} просмотрел свою кофейню.")
            print(f"Пользователь {message.from_user.id} просмотрел свою кофейню.")
        else:
            await message.answer("Сначала начните игру командой /start.")
            logger.warning(f"Пользователь {message.from_user.id} попытался просмотреть кофейню без регистрации.")
            print(f"Пользователь {message.from_user.id} попытался просмотреть кофейню без регистрации.")
    except Exception as e:
        logger.error(f"Ошибка в команде /my_cafe для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка при получении информации о кофейне.")

@router.message(Command(commands=["upgrade"]))
async def upgrade_handler(message: Message):
    try:
        cursor.execute("""
            SELECT balance, level FROM players WHERE user_id = ?
        """, (message.from_user.id,))
        player = cursor.fetchone()
        if player and player[0] >= 50:
            new_balance = player[0] - 50
            new_level = player[1] + 1
            cursor.execute("""
                UPDATE players SET balance = ?, level = ?
                WHERE user_id = ?
            """, (new_balance, new_level, message.from_user.id))

            # Проверка достижений
            cursor.execute("""
                SELECT achievement_id, name, condition FROM achievements
            """)
            achievements = cursor.fetchall()
            earned_achievements = []
            for achievement in achievements:
                achievement_id, name, condition = achievement
                # Парсим условие (предполагается, что условие в формате "level >= X")
                if "level >=" in condition:
                    required_level = int(condition.split(">=")[1].strip())
                    if new_level >= required_level:
                        # Проверяем, было ли уже достигнуто
                        cursor.execute("""
                            SELECT id FROM user_achievements WHERE user_id = ? AND achievement_id = ?
                        """, (message.from_user.id, achievement_id))
                        if not cursor.fetchone():
                            # Добавляем достижение
                            cursor.execute("""
                                INSERT INTO user_achievements (user_id, achievement_id)
                                VALUES (?, ?)
                            """, (message.from_user.id, achievement_id))
                            earned_achievements.append(name)

            conn.commit()
            await message.answer(f"Кофейня улучшена до уровня {new_level}! Теперь вы зарабатываете больше.")
            if earned_achievements:
                achievements_text = ", ".join(earned_achievements)
                await message.answer(f"🎉 Поздравляем! Вы достигли: {achievements_text}")
            logger.info(f"Пользователь {message.from_user.id} улучшил кофейню до уровня {new_level}. Остаток баланса: {new_balance}")
            print(f"Пользователь {message.from_user.id} улучшил кофейню до уровня {new_level}. Остаток баланса: {new_balance}")
        else:
            await message.answer("Недостаточно монет для улучшения. Нужно 50 монет.")
            logger.warning(f"Пользователь {message.from_user.id} попытался улучшить кофейню без достаточного баланса.")
            print(f"Пользователь {message.from_user.id} недостаточно монет для улучшения.")
    except Exception as e:
        logger.error(f"Ошибка в команде /upgrade для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка при улучшении кофейни.")

@router.message(Command(commands=["shop"]))
async def shop_handler(message: Message):
    try:
        logger.info(f"Пользователь {message.from_user.id} вызвал команду /shop")
        cursor.execute("SELECT name, base_cost FROM buildings")
        buildings = cursor.fetchall()
        logger.info(f"Найдено зданий: {buildings}")

        if buildings:
            response = "🏪 **Доступные здания для покупки:**\n"
            for name, cost in buildings:
                response += f"- *{name}*: Стоимость - {cost} монет\n"

            # Создаём клавиатуру с помощью InlineKeyboardBuilder
            builder = InlineKeyboardBuilder()
            for name, cost in buildings:
                callback_data = f"buy_{name.replace(' ', '_')}"
                button = InlineKeyboardButton(text=f"Купить {name} ({cost} монет)", callback_data=callback_data)
                builder.add(button)

            # Преобразуем builder в InlineKeyboardMarkup
            keyboard = builder.as_markup()

            await message.answer(response, parse_mode="Markdown", reply_markup=keyboard)
            logger.info(f"Пользователь {message.from_user.id} открыл магазин.")
            print(f"Пользователь {message.from_user.id} открыл магазин.")
        else:
            await message.answer("На данный момент доступных зданий нет.")
            logger.info(f"Пользователь {message.from_user.id} открыл магазин, но зданий нет.")
    except Exception as e:
        logger.error(f"Ошибка в команде /shop для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка при получении списка зданий.")

@router.callback_query(lambda c: c.data and c.data.startswith('buy_'))
async def buy_building_callback(query: types.CallbackQuery):
    user_id = query.from_user.id
    building_name = query.data.split('_', 1)[1].replace('_', ' ')
    try:
        logger.info(f"Пользователь {user_id} пытается купить здание: {building_name}")
        # Получаем информацию о здании
        cursor.execute("""
            SELECT base_cost, income_multiplier, resource_cost FROM buildings WHERE name = ?
        """, (building_name,))
        building = cursor.fetchone()
        if not building:
            await query.answer("Такого здания не существует.", show_alert=True)
            logger.warning(f"Здание {building_name} не найдено в базе данных.")
            return
        base_cost, income_multiplier, resource_cost = building

        # Получаем баланс пользователя
        cursor.execute("SELECT balance FROM players WHERE user_id = ?", (user_id,))
        player = cursor.fetchone()
        if not player:
            await query.answer("Сначала начните игру командой /start.", show_alert=True)
            logger.warning(f"Пользователь {user_id} не зарегистрирован.")
            return
        balance = player[0]

        # Проверяем, достаточно ли монет
        if balance < base_cost:
            await query.answer("Недостаточно монет для покупки этого здания.", show_alert=True)
            logger.info(f"Пользователь {user_id} имеет баланс {balance}, недостаточно для покупки {building_name}")
            return

        # Определяем необходимый ресурс
        if building_name == "Магазин":
            required_resource = "Кофейные зерна"
        elif building_name == "Склад":
            required_resource = "Молоко"
        elif building_name == "Офис":
            required_resource = "Сахар"
        else:
            required_resource = None

        if required_resource:
            cursor.execute("SELECT quantity FROM user_resources WHERE user_id = ? AND resource_name = ?", (user_id, required_resource))
            resource = cursor.fetchone()
            if not resource or resource[0] < resource_cost:
                await query.answer(f"Недостаточно {required_resource} для покупки этого здания.", show_alert=True)
                logger.info(f"Пользователь {user_id} имеет {resource[0] if resource else 0} {required_resource}, недостаточно для покупки {building_name}")
                return

            # Списываем ресурсы
            new_resource_quantity = resource[0] - resource_cost
            cursor.execute("UPDATE user_resources SET quantity = ? WHERE user_id = ? AND resource_name = ?", (new_resource_quantity, user_id, required_resource))

        # Проверяем, есть ли уже это здание у пользователя
        cursor.execute("SELECT id, level FROM user_buildings WHERE user_id = ? AND building_name = ?", (user_id, building_name))
        user_building = cursor.fetchone()
        if user_building:
            building_id, level = user_building
            cursor.execute("UPDATE user_buildings SET level = level + 1 WHERE id = ?", (building_id,))
            new_level = level + 1
            logger.info(f"Пользователь {user_id} повысил уровень здания {building_name} до {new_level}")
        else:
            cursor.execute("INSERT INTO user_buildings (user_id, building_name, level) VALUES (?, ?, ?)", (user_id, building_name, 1))
            new_level = 1
            logger.info(f"Пользователь {user_id} купил новое здание {building_name} на уровне {new_level}")

        # Обновляем баланс пользователя
        new_balance = balance - base_cost
        cursor.execute("UPDATE players SET balance = ? WHERE user_id = ?", (new_balance, user_id))

        conn.commit()

        await query.answer(f"Вы успешно купили {building_name}! Ваш баланс: {new_balance} монет.", show_alert=True)
        logger.info(f"Пользователь {user_id} купил {building_name}. Остаток баланса: {new_balance}")
    except Exception as e:
        logger.error(f"Ошибка при покупке здания {building_name} пользователем {user_id}: {e}", exc_info=True)
        await query.answer("Произошла ошибка при покупке здания.", show_alert=True)

@router.message(Command(commands=["collect"]))
async def collect_handler(message: Message):
    try:
        # Пример: случайным образом начисляем ресурсы
        resources = ["Кофейные зерна", "Молоко", "Сахар"]
        collected_resource = random.choice(resources)
        collected_amount = random.randint(1, 5)  # Количество собранных ресурсов

        # Проверяем, зарегистрирован ли пользователь
        cursor.execute("""
            SELECT balance FROM players WHERE user_id = ?
        """, (message.from_user.id,))
        player = cursor.fetchone()
        if not player:
            await message.answer("Сначала начните игру командой /start.")
            return

        # Проверяем, есть ли уже у пользователя этот ресурс
        cursor.execute("""
            SELECT quantity FROM user_resources WHERE user_id = ? AND resource_name = ?
        """, (message.from_user.id, collected_resource))
        user_resource = cursor.fetchone()
        if user_resource:
            new_quantity = user_resource[0] + collected_amount
            cursor.execute("""
                UPDATE user_resources SET quantity = ? WHERE user_id = ? AND resource_name = ?
            """, (new_quantity, message.from_user.id, collected_resource))
        else:
            cursor.execute("""
                INSERT INTO user_resources (user_id, resource_name, quantity)
                VALUES (?, ?, ?)
            """, (message.from_user.id, collected_resource, collected_amount))

        conn.commit()

        await message.answer(f"Вы собрали {collected_amount} x {collected_resource}!")
        logger.info(f"Пользователь {message.from_user.id} собрал {collected_amount} x {collected_resource}.")
        print(f"Пользователь {message.from_user.id} собрал {collected_amount} x {collected_resource}.")
    except Exception as e:
        logger.error(f"Ошибка в команде /collect для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка при сборе ресурсов.")

@router.message(Command(commands=["inventory"]))
async def inventory_handler(message: Message):
    try:
        cursor.execute("""
            SELECT resource_name, quantity FROM user_resources WHERE user_id = ?
        """, (message.from_user.id,))
        user_resources = cursor.fetchall()
        if user_resources:
            response = "📦 **Ваши ресурсы:**\n"
            for resource_name, quantity in user_resources:
                response += f"- {resource_name}: {quantity}\n"
            await message.answer(response)
        else:
            await message.answer("У вас пока нет собранных ресурсов. Используйте команду /collect для сбора.")
    except Exception as e:
        logger.error(f"Ошибка в команде /inventory для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка при получении ваших ресурсов.")

@router.message(Command(commands=["achievements"]))
async def achievements_handler(message: Message):
    try:
        cursor.execute("""
            SELECT a.name, a.description FROM achievements a
            JOIN user_achievements ua ON a.achievement_id = ua.achievement_id
            WHERE ua.user_id = ?
        """, (message.from_user.id,))
        achievements = cursor.fetchall()
        if achievements:
            response = "🎖️ **Ваши достижения:**\n"
            for name, description in achievements:
                response += f"- *{name}*: {description}\n"
            await message.answer(response, parse_mode="Markdown")
        else:
            await message.answer("У вас пока нет достижений. Улучшайте кофейню, чтобы получать достижения!")
    except Exception as e:
        logger.error(f"Ошибка в команде /achievements для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка при получении ваших достижений.")

@router.message(Command(commands=["leaderboard"]))
async def leaderboard_handler(message: Message):
    try:
        cursor.execute("""
            SELECT cafe_name, balance, level FROM players
            ORDER BY balance DESC
            LIMIT 10
        """)
        top_players = cursor.fetchall()
        if top_players:
            response = "🏆 **Топ 10 игроков:**\n"
            for idx, (cafe_name, balance, level) in enumerate(top_players, start=1):
                response += f"{idx}. {cafe_name} - Баланс: {balance} монет, Уровень: {level}\n"
            await message.answer(response)
        else:
            await message.answer("На данный момент в игре нет игроков.")
    except Exception as e:
        logger.error(f"Ошибка в команде /leaderboard для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка при получении лидерборда.")

# =======================
# 5. Новые хендлеры команд
# =======================

@router.message(Command(commands=["open_game"]))
async def open_game_handler(message: Message):
    WEB_APP_URL = "https://crypto-coffee.netlify.app"  # Замените на ваш актуальный URL

    # Создаем InlineKeyboardMarkup с кнопкой-ссылкой
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Open Game", url=WEB_APP_URL)]
    ])
    
    await message.answer("Нажмите кнопку ниже, чтобы открыть игру:", reply_markup=keyboard)
    logger.info(f"Пользователь {message.from_user.id} запросил доступ к игре.")
    print(f"Пользователь {message.from_user.id} запросил доступ к игре.")

# =======================
# 6. Административные команды
# =======================

@router.message(Command(commands=["add_coins"]))
async def add_coins_handler(message: Message, command: Command):
    logger.info(f"Получена команда /add_coins от пользователя {message.from_user.id}")
    print(f"Получена команда /add_coins от пользователя {message.from_user.id}")

    # Проверяем, является ли пользователь администратором
    if message.from_user.id != ADMIN_USER_ID:
        await message.answer("У вас нет прав для использования этой команды.")
        logger.warning(f"Пользователь {message.from_user.id} попытался использовать команду /add_coins без прав.")
        print(f"Пользователь {message.from_user.id} попытался использовать команду /add_coins без прав.")
        return

    # Проверяем, предоставлены ли аргументы
    args = command.args
    if not args:
        await message.answer("Пожалуйста, укажите количество монет для добавления.\nПример: /add_coins 1000")
        logger.warning(f"Пользователь {message.from_user.id} отправил команду /add_coins без аргументов.")
        print(f"Пользователь {message.from_user.id} отправил команду /add_coins без аргументов.")
        return

    try:
        coins_to_add = int(args)
        if coins_to_add <= 0:
            raise ValueError("Количество монет должно быть положительным числом.")
        logger.info(f"Количество монет для добавления: {coins_to_add}")
        print(f"Количество монет для добавления: {coins_to_add}")
    except ValueError:
        await message.answer("Пожалуйста, введите корректное положительное число монет.")
        logger.warning(f"Пользователь {message.from_user.id} ввёл некорректное количество монет: {args}")
        print(f"Пользователь {message.from_user.id} ввёл некорректное количество монет: {args}")
        return

    try:
        cursor.execute("""
            SELECT balance FROM players WHERE user_id = ?
        """, (message.from_user.id,))
        player = cursor.fetchone()
        if player:
            new_balance = player[0] + coins_to_add
            cursor.execute("""
                UPDATE players SET balance = ? WHERE user_id = ?
            """, (new_balance, message.from_user.id))
            conn.commit()
            await message.answer(f"Ваш баланс успешно пополнен на {coins_to_add} монет. Теперь ваш баланс: {new_balance} монет.")
            logger.info(f"Администратор {message.from_user.id} пополнил свой баланс на {coins_to_add} монет.")
            print(f"Администратор {message.from_user.id} пополнил свой баланс на {coins_to_add} монет.")
        else:
            await message.answer("Вы не зарегистрированы в системе. Пожалуйста, используйте команду /start.")
            logger.warning(f"Администратор {message.from_user.id} попытался пополнить баланс, но не зарегистрирован.")
            print(f"Администратор {message.from_user.id} попытался пополнить баланс, но не зарегистрирован.")
    except Exception as e:
        logger.error(f"Ошибка при пополнении баланса администратора {message.from_user.id}: {e}", exc_info=True)
        print(f"Ошибка при пополнении баланса администратора {message.from_user.id}: {e}")
        await message.answer("Произошла ошибка при пополнении баланса.")

# =======================
# 7. Запуск Бота
# =======================

async def main():
    try:
        await dispatcher.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка во время запуска бота: {e}", exc_info=True)
        print(f"Критическая ошибка во время запуска бота: {e}")
    finally:
        await bot.session.close()
        conn.close()
        logger.info("Соединение с базой данных закрыто.")
        print("Соединение с базой данных закрыто.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную.")
        print("Бот остановлен вручную.")
