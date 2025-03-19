import telebot
import json
import os
import schedule
import time
import logging
import threading
from urllib.parse import unquote
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7476899739:AAGk7OMz4hdn-BDtP9MjNW1ndAhEBQElgto"

FIRST_VIDEO_URL = "https://drive.google.com/file/d/1hWgxrGfhDbNFpQB_iSCUKP_k69MtGIJodw/view?usp=drive_link"

# Путь к файлу с пользователями
USERS_FILE = 'users.json'
users = set()

with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

# Путь к файлу конфигурации
CONFIG_FILE = 'config.json'

logging.basicConfig(level=logging.INFO)


# Список администраторов
administrators = {447640188, 600164937, 339175430}

# Функция загрузки пользователей из файла
def load_users():
    global users
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            data = file.read()
            if data:
                users = set(map(int, json.loads(data)))  # Преобразуем в int
                print(f"Загружено {len(users)} пользователей: {users}")  # Проверка
            else:
                print("Файл users.json пуст. Создаём новый.")
                users = set()
                save_users()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Ошибка при загрузке файла users.json: {e}")
        users = set()
        save_users() 

# Функция сохранения пользователей в файл
def save_users(users):
    """ Сохраняет список пользователей в файл """
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# Функция добавления пользователя
def add_user(user_id):
    if user_id not in users:
        users.add(user_id)
        save_users()
        print(f"Пользователь {user_id} добавлен в список.")

# Загрузка конфигурации
def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "content_type": "text_with_button",
            "text": "Привет! Это новый контент для команды /start.",
            "button_text": "Перейти к видео",
            "button_url": "https://example.com/video",
            "photo": None,
            "video": None,
            "voice": None,
            "document": None,
            "magnets": {}
        }
# Сохранение конфигурации
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
        json.dump(config, file, ensure_ascii=False, indent=4)

# Загрузка пользователей при старте бота
load_users()

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# Функция для отмены текущего процесса
def cancel_request(message):
    bot.reply_to(message, "Команда отменена.")
    return

# Функция для проверки команды /cancel
def check_cancel(message, next_step_handler, *args):
    if message.text and message.text.strip().lower() == "/cancel":
        cancel_request(message)
        return
    next_step_handler(message, *args)

def check_cancel(message, next_step_handler, *args):
    if message.text and message.text.strip().lower() == "/cancel":
        cancel_request(message)
        return
    next_step_handler(message, *args)

    # Создаем обертку для bot.register_next_step_handler
def register_next_step_handler_with_cancel(message, next_step_handler, *args):
    """
    Обертка для bot.register_next_step_handler, которая автоматически добавляет check_cancel.
    """
    bot.register_next_step_handler(message, lambda m: check_cancel(m, next_step_handler, *args))

@bot.message_handler(commands=['list_magnets'])
def list_magnets(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    config = load_config()
    if "magnets" in config and config["magnets"]:
        magnet_list = "\n".join(config["magnets"].keys())
        bot.reply_to(message, f"Список кодовых слов:\n{magnet_list}")
    else:
        bot.reply_to(message, "Список кодовых слов пуст.")


import json
from urllib.parse import unquote

USERS_FILE = "users.json"

# Функция загрузки пользователей из файла
def load_users():
    global users
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            users_data = json.load(file)  # Загружаем как список
            users = set(map(int, users_data))  # Преобразуем в set из int
        print(f"Загружено {len(users)} пользователей: {users}")  # Проверка
    except (FileNotFoundError, json.JSONDecodeError):
        print("Файл users.json не найден или пуст. Создаём новый.")
        users = set()

# Функция сохранения пользователей в файл
def save_users():
    with open(USERS_FILE, 'w', encoding='utf-8') as file:
        json.dump(list(users), file, ensure_ascii=False, indent=4)

        
# Обновленный обработчик /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    global users  # Используем глобальный список пользователей
    user_id = message.chat.id
    param = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None

    # Добавляем пользователя, если его нет
    if user_id not in users:
        users.add(user_id)
        save_users()
        print(f"✅ Добавлен новый пользователь: {user_id}")

         # Отправляем уведомление администраторам
        for admin_id in administrators:
            try:
                bot.send_message(admin_id, f"Новый пользователь добавлен: {user_id}")
            except Exception as e:
                print(f"Не удалось отправить сообщение администратору {admin_id}: {e}")

    if param:
        param = unquote(param)  # Декодируем параметр из URL
        if "magnets" in config and param in config["magnets"]:
            magnet = config["magnets"][param]
            send_magnet_content(user_id, magnet)
        else:
            bot.reply_to(user_id, "❌ Кодовое слово не найдено в конфигурации.")
    else:
        send_welcome(message)


def send_magnet_content(chat_id, magnet):
    content_type = magnet["content_type"]
    text_content = magnet.get("text", "")
    markup = InlineKeyboardMarkup()
    button_url = magnet.get("button_url", "")
    
    # Добавить отладочную информацию
    print(f"Отправка контента: chat_id={chat_id}, content_type={content_type}, text_content={text_content}")

    if button_url:
        markup.add(InlineKeyboardButton(magnet["button_text"], url=button_url))
    
    try:
        if content_type == "text":
            bot.send_message(chat_id, text_content)
        elif content_type == "text_with_button":
            bot.send_message(chat_id, text_content, reply_markup=markup)
        elif content_type == "text_with_video":
            bot.send_video(chat_id, magnet["video"], caption=text_content)
        elif content_type == "text_with_video_button":
            bot.send_video(chat_id, magnet["video"], caption=text_content, reply_markup=markup)
        elif content_type == "text_with_voice":
            bot.send_voice(chat_id, magnet["voice"], caption=text_content)
        elif content_type == "text_with_document":
            bot.send_document(chat_id, magnet["document"], caption=text_content)
        elif content_type == "photo_with_text":
            bot.send_photo(chat_id, magnet["photo"], caption=text_content)
        elif content_type == "photo_with_text_button":
            bot.send_photo(chat_id, magnet["photo"], caption=text_content, reply_markup=markup)
        elif content_type == "text_with_keyword_button":
            keywords = magnet.get("keywords", [])
            if keywords:
               button_data = ",".join(keywords)  # Преобразуем список в строку
               markup.add(InlineKeyboardButton(magnet["button_text"], callback_data=button_data))
            else:
               markup.add(InlineKeyboardButton(magnet["button_text"], callback_data=button_data))  # Безопасное значение 
            bot.send_message(chat_id, text_content, reply_markup=markup)
        elif content_type == "photo_with_text_keyword_button":
            keywords = magnet.get("keywords", [])
            if keywords:
               button_data = ",".join(keywords)  # Преобразуем список в строку
               markup.add(InlineKeyboardButton(magnet["button_text"], callback_data=button_data))
            else:
               markup.add(InlineKeyboardButton(magnet["button_text"], callback_data=button_data))  # Безопасное значение 
            bot.send_photo(chat_id, magnet["photo"], caption=text_content, reply_markup=markup)
        else:
            bot.send_message(chat_id, "⚠️ Неподдерживаемый тип контента.")
    except Exception as e:
        print(f"Ошибка отправки контента для {chat_id}: {e}")
        bot.send_message(chat_id, "⚠️ Ошибка при загрузке контента.")

        

# Функция отправки приветственного сообщения
def send_welcome(message):
    user_id = message.chat.id
    
    
    
    # Загружаем конфигурацию
    config = load_config()
    markup = InlineKeyboardMarkup()
    
    # Инициализируем переменную button_url
    button_url = None  # Или пустая строка: button_url = ""
    
    # Создаем кнопку, если она нужна
    if "button" in config["content_type"]:
        button_url = config.get("button_url")
    
    # Проверяем button_url
    if button_url:
        markup.add(InlineKeyboardButton(config["button_text"], url=button_url))
    elif config["content_type"] in ["text_with_keyword_button", "photo_with_text_keyword_button"]:
        keywords = config.get("button_keywords", [])
        if keywords:
            button_data = ",".join(keywords)  # Преобразуем список в строку
            markup.add(InlineKeyboardButton(config["button_text"], callback_data=button_data))
    
    # Отправка контента в зависимости от типа
    try:
        if config["content_type"] == "text":
            bot.send_message(user_id, config["text"])
        
        elif config["content_type"] == "text_with_button":
            bot.send_message(user_id, config["text"], reply_markup=markup)
        
        elif config["content_type"] == "photo":
            bot.send_photo(user_id, config["photo"])
        
        elif config["content_type"] == "photo_with_button":
            bot.send_photo(user_id, config["photo"], caption=config.get("text", ""), reply_markup=markup)
        
        elif config["content_type"] == "video":
            bot.send_video(user_id, config["video"])
        
        elif config["content_type"] == "voice":
            bot.send_voice(user_id, config["voice"])
        
        elif config["content_type"] == "document":
            bot.send_document(user_id, config["document"])
        
        elif config["content_type"] == "text_with_video":
            bot.send_video(user_id, config["video"], caption=config["text"])
        
        elif config["content_type"] == "text_with_video_button":
            bot.send_video(user_id, config["video"], caption=config["text"], reply_markup=markup)
        
        elif config["content_type"] == "text_with_voice":
            bot.send_voice(user_id, config["voice"], caption=config["text"])
        
        elif config["content_type"] == "text_with_document":
            bot.send_document(user_id, config["document"], caption=config["text"])
        
        elif config["content_type"] == "photo_with_text":
            bot.send_photo(user_id, config["photo"], caption=config["text"])
        
        elif config["content_type"] == "photo_with_text_button":
            bot.send_photo(user_id, config["photo"], caption=config["text"], reply_markup=markup)
        
        elif config["content_type"] == "text_with_keyword_button":
            if keywords:  # Убедимся, что есть ключевые слова
                bot.send_message(user_id, config["text"], reply_markup=markup)
        
        elif config["content_type"] == "photo_with_text_keyword_button":
            if keywords:  # Убедимся, что есть ключевые слова
               bot.send_photo(user_id, config["photo"], caption=config["text"], reply_markup=markup)
        
        else:
            bot.send_message(user_id, "Контент для команды /start не настроен.")
    
    except Exception as e:
        print(f"Ошибка отправки контента: {e}")
        bot.send_message(user_id, "⚠️ Ошибка при загрузке контента.")

@bot.message_handler(func=lambda message: message.text.lower() == "старт")
def handle_text_start(message):
    send_welcome(message)

# Команда для обновления конфигурации
@bot.message_handler(commands=['set_start_content']) 
def set_start_content(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    # Запрашиваем тип контента
    menu = (
        "Выберите тип контента:\n"
        "1. Текст\n"
        "2. Текст с кнопкой\n"
        "3. Текст с видео\n"
        "4. Текст с видео и кнопкой\n"
        "5. Текст с голосовым сообщением\n"
        "6. Текст с файлом\n"
        "7. Картинка с текстом\n"
        "8. Картинка с текстом и кнопкой\n"
        "9. Текст и кнопка с кодовым словом\n"
        "10. Картинка и текст и кнопка с кодовым словом"
    )
    bot.reply_to(message, menu)
    register_next_step_handler_with_cancel(message, process_content_type)

def process_content_type(message):
    content_type = message.text.strip().lower()
    valid_types = {
        "1": "text",
        "2": "text_with_button",
        "3": "text_with_video",
        "4": "text_with_video_button",
        "5": "text_with_voice",
        "6": "text_with_document",
        "7": "photo_with_text",
        "8": "photo_with_text_button",
        "9": "text_with_keyword_button",
        "10": "photo_with_text_keyword_button"
    }
    
    if content_type not in valid_types:
        bot.reply_to(message, "❌ Некорректный тип контента")
        return
    
    config = load_config()
    config["content_type"] = valid_types[content_type]
    
    # Очищаем button_url, если выбран тип с ключевыми словами
    if config["content_type"] in ["text_with_keyword_button", "photo_with_text_keyword_button"]:
        config["button_url"] = None  

    # Фото или видео — сначала запрашиваем файл, затем текст
    if config["content_type"] in ["photo_with_text", "photo_with_text_button", "photo_with_text_keyword_button"]:
        bot.reply_to(message, "🖼 Отправьте фото:")
        register_next_step_handler_with_cancel(message, lambda m: process_photo(m, config))
    elif config["content_type"] in ["text_with_video", "text_with_video_button"]:
        bot.reply_to(message, "🎥 Отправьте видео:")
        register_next_step_handler_with_cancel(message, lambda m: process_video(m, config))
    else:
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_main_text(m, config))

def process_main_text(message, config):
    config["text"] = message.text
    save_config(config)

      # Если требуется голосовое сообщение или документ, запрашиваем их после текста
    if config["content_type"] == "text_with_voice":
        bot.reply_to(message, "🎤 Отправьте голосовое сообщение:")
        register_next_step_handler_with_cancel(message, lambda m: process_voice(m, config))
        return  # ⬅ Убираем лишнее сообщение
    elif config["content_type"] == "text_with_document":
        bot.reply_to(message, "📎 Отправьте файл:")
        register_next_step_handler_with_cancel(message, lambda m: process_document(m, config))
        return  # ⬅ Убираем лишнее сообщение
    elif config["content_type"] in ["text_with_button", "text_with_video_button", "photo_with_text_button", "text_with_keyword_button", "photo_with_text_keyword_button"]:
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_text(m, config))
        return
    else:
        bot.reply_to(message, "✅ Конфигурация обновлена!")

    # Запрашиваем кнопку, если она нужна
    if config["content_type"] in ["text_with_button", "text_with_video_button", "photo_with_text_button", "text_with_keyword_button", "photo_with_text_keyword_button"]:
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_text(m, config))
   

def process_button_text(message, config):
    config["button_text"] = message.text
    save_config(config)

    # Кодовые слова или URL для кнопки
    if config["content_type"] in ["text_with_keyword_button", "photo_with_text_keyword_button"]:
        bot.reply_to(message, "🔗 Введите кодовые слова для кнопки через запятую:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_keywords(m, config))
    else:
        bot.reply_to(message, "🔗 Введите ссылку для кнопки:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_url(m, config))

def process_button_keywords(message, config):
    config["button_keywords"] = [kw.strip().lower() for kw in message.text.split(',')]
    save_config(config)
    bot.reply_to(message, "✅ Конфигурация обновлена!")

def process_button_url(message, config):
    config["button_url"] = message.text
    save_config(config)
    bot.reply_to(message, "✅ Конфигурация обновлена!")

def process_photo(message, config):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте фото.")
        return

    config["photo"] = message.photo[-1].file_id
    save_config(config)

    # После фото всегда должен быть текст
    bot.reply_to(message, "📝 Введите основной текст:")
    register_next_step_handler_with_cancel(message, lambda m: process_main_text(m, config))

def process_video(message, config):
    if message.content_type != 'video':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видео.")
        return

    config["video"] = message.video.file_id
    save_config(config)

    # Если это "text_with_video_button", сначала запрашиваем основной текст, затем кнопку
    if config["content_type"] == "text_with_video_button":
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_main_text_then_button(m, config))
    else:
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_main_text(m, config))

def process_main_text_then_button(message, config):
    """ Запрашивает основной текст, затем кнопку """
    config["text"] = message.text
    save_config(config)

    bot.reply_to(message, "🖋 Введите текст для кнопки:")
    register_next_step_handler_with_cancel(message, lambda m: process_button_text(m, config))


def process_voice(message, config):
    """ Сохраняет голосовое сообщение """
    if message.content_type != 'voice':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте голосовое сообщение.")
        return

    config["voice"] = message.voice.file_id
    save_config(config)
    bot.reply_to(message, "✅ Конфигурация обновлена!")

def process_document(message, config):
    """ Сохраняет файл """
    if message.content_type != 'document':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте файл.")
        return

    config["document"] = message.document.file_id
    save_config(config)
    bot.reply_to(message, "✅ Конфигурация обновлена!")


@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "Вы не можете назначать администраторов.")
        return
    
    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.reply_to(message, "Используйте формат: /add_admin user_id")
        return
    
    try:
        new_admin_id = int(command_parts[1])
        administrators.add(new_admin_id)
        bot.reply_to(message, f"Пользователь {new_admin_id} добавлен в администраторы.")
    except ValueError:
        bot.reply_to(message, "Некорректный ID пользователя.")

@bot.message_handler(commands=['list_users'])
def list_users(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    # Загружаем пользователей перед выводом списка
    load_users()
    
    if users:
        bot.reply_to(message, "Список пользователей:\n" + "\n".join(map(str, users)))
    else:
        bot.reply_to(message, "Список пользователей пуст.")

from datetime import datetime

@bot.message_handler(commands=['delay_message'])
def delay_message(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    menu = (
        "Выберите тип контента для отложенной отправки:\n"
        "1. Текст\n"
        "2. Текст с кнопкой\n"
        "3. Текст с видео\n"
        "4. Текст с видео и кнопкой\n"
        "5. Текст с голосовым сообщением\n"
        "6. Текст с файлом\n"
        "7. Картинка с текстом\n"
        "8. Картинка с текстом кнопкой\n"
        "9. Текст и кнопка с кодовым словом\n"
        "10. Картинка и текст и кнопка с кодовым словом"
    )
    bot.reply_to(message, menu)
    register_next_step_handler_with_cancel(message, process_content_type_for_delay)

def process_content_type_for_delay(message):
    content_type = message.text.strip().lower()
    valid_types = {
        "1": "text",
        "2": "text_with_button",
        "3": "text_with_video",
        "4": "text_with_video_button",
        "5": "text_with_voice",
        "6": "text_with_document",
        "7": "photo_with_text",
        "8": "photo_with_text_button",
        "9": "text_with_keyword_button",
        "10": "photo_with_text_keyword_button"
    }

    if content_type not in valid_types:
        bot.reply_to(message, "❌ Некорректный тип контента")
        return

    context = {"content_type": valid_types[content_type]}

    if "photo" in context["content_type"]:
        bot.reply_to(message, "📤 Пожалуйста, прикрепите фото.")
        register_next_step_handler_with_cancel(message, lambda m: process_photo_for_delay(m, context))
    elif "video" in context["content_type"]:
        bot.reply_to(message, "🎥 Пожалуйста, прикрепите видео.")
        register_next_step_handler_with_cancel(message, lambda m: process_video_for_delay(m, context))
    elif "voice" in context["content_type"]:
        bot.reply_to(message, "🎤 Пожалуйста, прикрепите голосовое сообщение.")
        register_next_step_handler_with_cancel(message, lambda m: process_voice_for_delay(m, context))
    elif "document" in context["content_type"]:
        bot.reply_to(message, "📎 Пожалуйста, прикрепите файл.")
        register_next_step_handler_with_cancel(message, lambda m: process_document_for_delay(m, context))
    else:
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_main_text_for_delay(m, context))

def process_video_for_delay(message, context):
    if message.content_type != 'video':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видео.")
        return
    context["video"] = message.video.file_id
    bot.reply_to(message, "📝 Введите основной текст:")
    register_next_step_handler_with_cancel(message, lambda m: process_main_text_for_delay(m, context))

def process_photo_for_delay(message, context):
    if message.content_type != "photo":
        bot.reply_to(message, "❌ Пожалуйста, прикрепите фото")
        return

    context["photo"] = message.photo[-1].file_id
    bot.reply_to(message, "📝 Введите основной текст:")
    register_next_step_handler_with_cancel(message, lambda m: process_main_text_for_delay(m, context))

def process_voice_for_delay(message, context):
    if message.content_type != 'voice':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте голосовое сообщение.")
        return
    context["voice"] = message.voice.file_id
    bot.reply_to(message, "📝 Введите основной текст:")
    register_next_step_handler_with_cancel(message, lambda m: process_main_text_for_delay(m, context))

def process_document_for_delay(message, context):
    if message.content_type != 'document':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте файл.")
        return
    context["document"] = message.document.file_id
    bot.reply_to(message, "📝 Введите основной текст:")
    register_next_step_handler_with_cancel(message, lambda m: process_main_text_for_delay(m, context))

def schedule_delayed_message(message, context):
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС")
    register_next_step_handler_with_cancel(message, lambda m: process_delay_datetime(m, context))

def process_main_text_for_delay(message, context):
    context["text"] = message.text

    if any(t in context["content_type"] for t in ["button", "keyword_button"]):
        bot.reply_to(message, "📝 Введите текст для кнопки:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_text_for_delay(m, context))
    else:
        schedule_delayed_message(message, context)

def process_button_text_for_delay(message, context):
    context["button_text"] = message.text

    if "keyword_button" in context["content_type"]:
        bot.reply_to(message, "📝 Введите кодовые слова через запятую:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_keywords_for_delay(m, context))
    else:
        bot.reply_to(message, "📝 Введите URL кнопки:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_url_for_delay(m, context))

def process_button_keywords_for_delay(message, context):
    context["button_keywords"] = message.text
    schedule_delayed_message(message, context)

def process_button_url_for_delay(message, context):
    context["button_url"] = message.text
    schedule_delayed_message(message, context)

def process_delay_button_text(message, context):
    context["button_text"] = message.text.strip()

    if context["content_type"] in ["text_with_keyword_button", "photo_with_text_keyword_button"]:
        bot.reply_to(message, "🔗 Введите кодовые слова для кнопки через запятую:")
        register_next_step_handler_with_cancel(message, process_delay_button_keywords, context)
    else:
        bot.reply_to(message, "🔗 Введите ссылку для кнопки:")
        register_next_step_handler_with_cancel(message, process_delay_button_url, context)

def process_delay_button_keywords(message, context):
    context["button_keywords"] = message.text.lower().replace(" ", "")
    schedule_delayed_message(message, context)
    return

def process_delay_button_url(message, context):
    context["button_url"] = message.text.strip()
    schedule_delayed_message(message, context)
    return

def process_delay_video(message, context):
    if message.content_type != 'video':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видео.")
        return
    context["video"] = message.video.file_id
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС")
    register_next_step_handler_with_cancel(message, process_delay_datetime, context)
    return

def process_delay_voice(message, context):
    if message.content_type != 'voice':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте голосовое сообщение.")
        return
    context["voice"] = message.voice.file_id
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС")
    register_next_step_handler_with_cancel(message, process_delay_datetime, context)
    return

def process_delay_document(message, context):
    if message.content_type != 'document':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте файл.")
        return
    context["document"] = message.document.file_id
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС")
    register_next_step_handler_with_cancel(message, process_delay_datetime, context)
    return

def process_delay_photo(message, context):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте фото.")
        return
    context["photo"] = message.photo[-1].file_id
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС")
    register_next_step_handler_with_cancel(message, process_delay_datetime, context)
    return

def process_delay_datetime(message, context):
    try:
        # Парсим дату и время
        datetime_str = message.text.strip()
        scheduled_time = datetime.strptime(datetime_str, "%d-%m-%Y %H:%M:%S")

        # Проверяем, что время в будущем
        if scheduled_time <= datetime.now():
            bot.reply_to(message, "❌ Время должно быть в будущем. Попробуйте снова.")
            return

        # Сохраняем время отправки
        context["scheduled_time"] = scheduled_time

        # Запускаем отложенную отправку
        threading.Thread(target=send_delayed_content, args=(context,)).start()
        bot.reply_to(message, f"✅ Сообщение будет отправлено {scheduled_time.strftime('%d-%m-%Y %H:%M:%S')}.")
        return
    except ValueError:
        bot.reply_to(message, "❌ Некорректный формат даты и времени. Используйте формат ДД-ММ-ГГГГ ЧЧ:ММ:СС.")
        return

def send_delayed_content(context):
    # Вычисляем задержку в секундах
    delay = (context["scheduled_time"] - datetime.now()).total_seconds()
    if delay > 0:
        time.sleep(delay)

    for user in users:
        try:
            if context["content_type"] == "text":
                bot.send_message(user, context["text"])
            elif context["content_type"] == "text_with_button":
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(context["button_text"], url=context["button_url"]))
                bot.send_message(user, context["text"], reply_markup=markup)
            elif context["content_type"] == "text_with_video":
                bot.send_video(user, context["video"], caption=context["text"])
            elif context["content_type"] == "text_with_video_button":
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(context["button_text"], url=context["button_url"]))
                bot.send_video(user, context["video"], caption=context["text"], reply_markup=markup)
            elif context["content_type"] == "text_with_voice":
                bot.send_voice(user, context["voice"], caption=context["text"])
            elif context["content_type"] == "text_with_document":
                bot.send_document(user, context["document"], caption=context["text"])
            elif context["content_type"] == "photo_with_text":
                bot.send_photo(user, context["photo"], caption=context["text"])
            elif context["content_type"] == "photo_with_text_button":
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(context["button_text"], url=context["button_url"]))
                bot.send_photo(user, context["photo"], caption=context["text"], reply_markup=markup)
            elif context["content_type"] == "text_with_keyword_button":
                markup = InlineKeyboardMarkup()
                button_data = ",".join([kw.strip() for kw in context["button_keywords"].split(',')])
                markup.add(InlineKeyboardButton(context["button_text"], callback_data=button_data))
                bot.send_message(user, context["text"], reply_markup=markup)
            elif context["content_type"] == "photo_with_text_keyword_button":
                markup = InlineKeyboardMarkup()
                button_data = ",".join([kw.strip() for kw in context["button_keywords"].split(',')])
                markup.add(InlineKeyboardButton(context["button_text"], callback_data=button_data))
                bot.send_photo(user, context["photo"], caption=context["text"], reply_markup=markup)
        except Exception as e:
            print(f"Ошибка отправки для {user}: {e}")


@bot.message_handler(commands=['send_all'])
def send_all(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    menu = (
        "Выберите тип контента для отправки всем пользователям:\n"
        "1. Текст\n"
        "2. Текст с кнопкой\n"
        "3. Текст с видео\n"
        "4. Текст с видео и кнопкой\n"
        "5. Текст с голосовым сообщением\n"
        "6. Текст с файлом\n"
        "7. Картинка с текстом\n"
        "8. Картинка с текстом и кнопкой\n"
        "9. Текст и кнопка с кодовым словом\n"
        "10. Картинка и текст и кнопка с кодовым словом"
    )
    bot.reply_to(message, menu)
    register_next_step_handler_with_cancel(message, process_content_type_for_all)

def process_content_type_for_all(message):
    content_type = message.text.strip().lower()
    valid_types = {
        "1": "text",
        "2": "text_with_button",
        "3": "text_with_video",
        "4": "text_with_video_button",
        "5": "text_with_voice",
        "6": "text_with_document",
        "7": "photo_with_text",
        "8": "photo_with_text_button",
        "9": "text_with_keyword_button",
        "10": "photo_with_text_keyword_button"
    }

    if content_type not in valid_types:
        bot.reply_to(message, "❌ Некорректный тип контента")
        return

    context = {"content_type": valid_types[content_type]}

    if "photo" in context["content_type"]:
        bot.reply_to(message, "📤 Пожалуйста, прикрепите фото.")
        register_next_step_handler_with_cancel(message, lambda m: process_photo_for_all(m, context))
    elif "video" in context["content_type"]:
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_main_text_for_all(m, context))
    elif "voice" in context["content_type"]:
        bot.reply_to(message, "🎤 Пожалуйста, прикрепите голосовое сообщение.")
        register_next_step_handler_with_cancel(message, lambda m: check_cancel(m, process_voice_for_all, context))
    elif "document" in context["content_type"]:
        bot.reply_to(message, "📎 Пожалуйста, прикрепите файл.")
        register_next_step_handler_with_cancel(message, lambda m: check_cancel(m, process_document_for_all, context))
    else:
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_main_text_for_all(m, context))

def process_photo_for_all(message, context):
    if message.content_type != "photo":
        bot.reply_to(message, "❌ Пожалуйста, прикрепите фото")
        return

    context["photo"] = message.photo[-1].file_id
    bot.reply_to(message, "📝 Введите основной текст:")
    register_next_step_handler_with_cancel(message, lambda m: process_main_text_for_all(m, context))

def process_voice_for_all(message, context):
    if message.content_type != 'voice':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте голосовое сообщение.")
        return

    context["voice"] = message.voice.file_id
    bot.reply_to(message, "📝 Введите основной текст:")
    register_next_step_handler_with_cancel(message, lambda m: check_cancel(m, process_main_text_for_all, context))

def process_document_for_all(message, context):
    if message.content_type != 'document':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте файл.")
        return
    context["document"] = message.document.file_id
    bot.reply_to(message, "📝 Введите основной текст:")
    register_next_step_handler_with_cancel(message, lambda m: check_cancel(m, process_main_text_for_all, context))

def process_video_for_all(message, context):
    if message.content_type != 'video':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видео.")
        return

    context["video"] = message.video.file_id

    if "button" in context["content_type"]:
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_text_for_all(m, context))
    else:
        send_content_to_all(message, context)

def process_main_text_for_all(message, context):
    context["text"] = message.text

    if "video" in context["content_type"]:
        bot.reply_to(message, "🎥 Пожалуйста, прикрепите видео.")
        register_next_step_handler_with_cancel(message, lambda m: process_video_for_all(m, context))
    elif any(t in context["content_type"] for t in ["button", "keyword_button"]):
        bot.reply_to(message, "📝 Введите текст кнопки:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_text_for_all(m, context))
    else:
        send_content_to_all(message, context)

def process_button_text_for_all(message, context):
    context["button_text"] = message.text

    if "keyword_button" in context["content_type"]:
        bot.reply_to(message, "📝 Введите кодовые слова через запятую:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_keywords_for_all(m, context))
    else:
        bot.reply_to(message, "📝 Введите URL кнопки:")
        register_next_step_handler_with_cancel(message, lambda m: process_button_url_for_all(m, context))

def process_button_keywords_for_all(message, context):
    context["button_keywords"] = message.text
    send_content_to_all(message, context)

def process_button_url_for_all(message, context):
    context["button_url"] = message.text
    send_content_to_all(message, context)

def send_content_to_all(message, context):
    content_type = context["content_type"]
    text = context.get("text", "")

    for user in users:
        try:
            if content_type == "text":
                bot.send_message(user, text)
            elif content_type == "text_with_button":
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(context["button_text"], url=context["button_url"]))
                bot.send_message(user, text, reply_markup=markup)
            elif content_type == "text_with_video":
                bot.send_video(user, context["video"], caption=text)
            elif content_type == "text_with_video_button":
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(context["button_text"], url=context["button_url"]))
                bot.send_video(user, context["video"], caption=text, reply_markup=markup)
            elif content_type == "text_with_voice":
                bot.send_voice(user, context["voice"], caption=text)
            elif content_type == "text_with_document":
                bot.send_document(user, context["document"], caption=text)
            elif content_type == "photo_with_text":
                bot.send_photo(user, context["photo"], caption=text)
            elif content_type == "photo_with_text_button":
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton(context["button_text"], url=context["button_url"]))
                bot.send_photo(user, context["photo"], caption=text, reply_markup=markup)
            elif content_type == "text_with_keyword_button":
                markup = InlineKeyboardMarkup()
                button_data = ",".join([kw.strip() for kw in context["button_keywords"].split(',')])
                markup.add(InlineKeyboardButton(context["button_text"], callback_data=button_data))
                bot.send_message(user, text, reply_markup=markup)
            elif content_type == "photo_with_text_keyword_button":
                markup = InlineKeyboardMarkup()
                button_data = ",".join([kw.strip() for kw in context["button_keywords"].split(',')])
                markup.add(InlineKeyboardButton(context["button_text"], callback_data=button_data))
                bot.send_photo(user, context["photo"], caption=text, reply_markup=markup)
        except Exception as e:
            print(f"Ошибка отправки для {user}: {e}")

    bot.reply_to(message, "✅ Контент успешно отправлен всем пользователям!")
    return  # Добавлено прерывание

@bot.message_handler(commands=['send_selfie'])
def send_selfie_request(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    # Запрос на отправку видеосообщения
    bot.reply_to(message, "Пожалуйста, отправьте видеосообщение.")

# Обработка видеосообщений
@bot.message_handler(content_types=['video_note'])
def send_selfie_to_all(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    # Получаем ID видеосообщения
    video_note_id = message.video_note.file_id

    # Отправляем видеосообщение всем пользователям
    for user in users:
        try:
            bot.send_video_note(user, video_note_id)
        except Exception as e:
            print(f"Ошибка при отправке видеосообщения пользователю {user}: {e}")

            # Команда /create_magnet
@bot.message_handler(commands=['create_magnet'])
def create_magnet(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return

    bot.reply_to(message, "Придумайте кодовое слово:")
    register_next_step_handler_with_cancel(message, process_magnet_keyword)

def process_magnet_keyword(message):
    keyword = message.text.strip().lower()
    if not keyword:
        bot.reply_to(message, "❌ Кодовое слово не может быть пустым.")
        return

    config = load_config()
    if "magnets" not in config:
        config["magnets"] = {}

    if keyword in config["magnets"]:
        bot.reply_to(message, f"❌ Кодовое слово '{keyword}' уже существует.")
        return

    config["magnets"][keyword] = {"keyword": keyword}
    save_config(config)

    menu = (
        "Выберите тип контента для магнита:\n"
        "1. Текст\n"
        "2. Текст с кнопкой\n"
        "3. Текст с видео\n"
        "4. Текст и видео с кнопкой\n"
        "5. Текст с голосовым сообщением\n"
        "6. Текст с файлом\n"
        "7. Картинка с текстом\n"
        "8. Картинка и текст с кнопкой\n"
        "9. Текст и кнопка с кодовым словом\n"
        "10. Картинка и текст и кнопка с кодовым словом\n"
        "11. Видеосообщение"
    )
    bot.reply_to(message, menu)
    register_next_step_handler_with_cancel(message, lambda m: process_magnet_content_type(m, keyword))

def process_magnet_content_type(message, keyword):
    content_type = message.text.strip().lower()
    valid_types = {
        "1": "text",
        "2": "text_with_button",
        "3": "text_with_video",
        "4": "text_with_video_button",
        "5": "text_with_voice",
        "6": "text_with_document",
        "7": "photo_with_text",
        "8": "photo_with_text_button",
        "9": "text_with_keyword_button",
        "10": "photo_with_text_keyword_button",
        "11": "video_message"
    }

    if content_type not in valid_types:
        bot.reply_to(message, "❌ Некорректный тип контента")
        return

    config = load_config()
    config["magnets"][keyword]["content_type"] = valid_types[content_type]
    save_config(config)

    if valid_types[content_type] == "text":
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_main_text(m, keyword))
    elif valid_types[content_type] == "text_with_button":
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_main_text_with_button(m, keyword))
    elif valid_types[content_type] in ["text_with_video", "text_with_video_button"]:
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_main_text_with_video(m, keyword))
    elif valid_types[content_type] == "text_with_voice":
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_main_text_with_voice(m, keyword))
    elif valid_types[content_type] == "text_with_document":
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_main_text_with_document(m, keyword))
    elif valid_types[content_type] == "video_message":
        bot.reply_to(message, "🎥 Отправьте видеосообщение:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_video_message(m, keyword))
    elif valid_types[content_type] in ["photo_with_text", "photo_with_text_button", "photo_with_text_keyword_button"]:
        bot.reply_to(message, "🖼 Отправьте фото:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_photo(m, keyword))
    elif valid_types[content_type] in ["text_with_keyword_button", "photo_with_text_keyword_button"]:
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_main_text_with_keyword_button(m, keyword))
    else:
        bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_main_text_with_video(message, keyword):
    config = load_config()
    config["magnets"][keyword]["text"] = message.text
    save_config(config)
    bot.reply_to(message, "🎥 Отправьте видео:")
    register_next_step_handler_with_cancel(message, lambda m: process_magnet_video(m, keyword))

def process_magnet_main_text_with_voice(message, keyword):
    config = load_config()
    config["magnets"][keyword]["text"] = message.text
    save_config(config)
    bot.reply_to(message, "🎤 Отправьте голосовое сообщение:")
    register_next_step_handler_with_cancel(message, lambda m: process_magnet_voice(m, keyword))

def process_magnet_main_text_with_document(message, keyword):
    config = load_config()
    config["magnets"][keyword]["text"] = message.text
    save_config(config)
    bot.reply_to(message, "📎 Отправьте файл:")
    register_next_step_handler_with_cancel(message, lambda m: process_magnet_document(m, keyword))

def process_magnet_main_text(message, keyword):
    config = load_config()
    config["magnets"][keyword]["text"] = message.text
    save_config(config)
    bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_main_text_with_button(message, keyword):
    config = load_config()
    config["magnets"][keyword]["text"] = message.text
    save_config(config)
    bot.reply_to(message, "🖋 Введите текст для кнопки:")
    register_next_step_handler_with_cancel(message, lambda m: process_magnet_button_text(m, keyword))

def process_magnet_main_text_with_keyword_button(message, keyword):
    config = load_config()
    config["magnets"][keyword]["text"] = message.text
    save_config(config)
    bot.reply_to(message, "🖋 Введите текст для кнопки:")
    register_next_step_handler_with_cancel(message, lambda m: process_magnet_button_text_with_keywords(m, keyword))

def process_magnet_button_text(message, keyword):
    config = load_config()
    config["magnets"][keyword]["button_text"] = message.text
    save_config(config)
    bot.reply_to(message, "🔗 Введите ссылку для кнопки:")
    register_next_step_handler_with_cancel(message, lambda m: process_magnet_button_url(m, keyword))

def process_magnet_button_text_with_keywords(message, keyword):
    config = load_config()
    config["magnets"][keyword]["button_text"] = message.text
    save_config(config)
    bot.reply_to(message, "🔗 Введите кодовые слова для кнопки через запятую:")
    register_next_step_handler_with_cancel(message, lambda m: process_magnet_button_keywords(m, keyword))

def process_magnet_button_url(message, keyword):
    config = load_config()
    config["magnets"][keyword]["button_url"] = message.text
    save_config(config)
    bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_button_keywords(message, keyword):
    config = load_config()
    config["magnets"][keyword]["keywords"] = [kw.strip().lower() for kw in message.text.split(',')]
    save_config(config)
    bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_video(message, keyword):
    if message.content_type != 'video':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видео.")
        return

    config = load_config()
    config["magnets"][keyword]["video"] = message.video.file_id  # Сохраняем file_id видео
    save_config(config)

    # Убираем повторный запрос текста
    if config["magnets"][keyword]["content_type"] == "text_with_video_button":
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_button_text(m, keyword))
    else:
        bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_photo(message, keyword):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте фото.")
        return

    config = load_config()
    config["magnets"][keyword]["photo"] = message.photo[-1].file_id  # Сохраняем file_id фото
    save_config(config)

    if config["magnets"][keyword]["content_type"] == "photo_with_text_button":
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_main_text_with_button(m, keyword))
    elif config["magnets"][keyword]["content_type"] == "photo_with_text_keyword_button":
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_main_text_with_keyword_button(m, keyword))
    else:
        bot.reply_to(message, "📝 Введите основной текст:")
        register_next_step_handler_with_cancel(message, lambda m: process_magnet_main_text(m, keyword))

def process_magnet_voice(message, keyword):
    if message.content_type != 'voice':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте голосовое сообщение.")
        return

    config = load_config()
    config["magnets"][keyword]["voice"] = message.voice.file_id
    save_config(config)
    bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_document(message, keyword):
    if message.content_type != 'document':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте файл.")
        return

    config = load_config()
    config["magnets"][keyword]["document"] = message.document.file_id
    save_config(config)
    bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_video_message(message, keyword):
    if message.content_type != 'video_note':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видеосообщение.")
        return

    config = load_config()
    config["magnets"][keyword]["video_message"] = message.video_note.file_id
    save_config(config)
    bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")


import re

# Команда /delete_magnet
@bot.message_handler(commands=['delete_magnet'])
def delete_magnet(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    bot.reply_to(message, "Введите кодовое слово для удаления:")
    register_next_step_handler_with_cancel(message, process_delete_magnet)

def process_delete_magnet(message):
    keyword = message.text.strip().lower()
    config = load_config()
    
    if "magnets" in config and keyword in config["magnets"]:
        del config["magnets"][keyword]
        save_config(config)
        bot.reply_to(message, f'✅ Кодовое слово "{keyword}" и все связанные данные удалены.')
    else:
        bot.reply_to(message, f'❌ Кодовое слово "{keyword}" не найдено.')

        # Обработка кодовых слов
@bot.message_handler(func=lambda message: True)
def handle_keywords(message):
    text = message.text.strip().lower()
    config = load_config()

    if "magnets" in config and text in config["magnets"]:
        magnet = config["magnets"][text]
        content_type = magnet["content_type"]
        text_content = magnet.get("text", "")
        
        if content_type == "text":
            bot.send_message(message.chat.id, text_content)

        elif content_type == "video_message":
            bot.send_video_note(message.chat.id, magnet["video_message"])    
        
        elif content_type == "text_with_button":
            markup = InlineKeyboardMarkup()
            button_url = magnet.get("button_url", "")
            if button_url:
                markup.add(InlineKeyboardButton(magnet["button_text"], url=button_url))
            bot.send_message(message.chat.id, text_content, reply_markup=markup)
        
        elif content_type == "text_with_video":
            bot.send_video(message.chat.id, magnet["video"], caption=text_content)
        
        elif content_type == "text_with_video_button":
            markup = InlineKeyboardMarkup()
            button_url = magnet.get("button_url", "")
            if button_url:
                markup.add(InlineKeyboardButton(magnet["button_text"], url=button_url))
            bot.send_video(message.chat.id, magnet["video"], caption=text_content, reply_markup=markup)
        
        elif content_type == "text_with_voice":
            bot.send_voice(message.chat.id, magnet["voice"], caption=text_content)
        
        elif content_type == "text_with_document":
            bot.send_document(message.chat.id, magnet["document"], caption=text_content)
        
        elif content_type == "photo_with_text":
            bot.send_photo(message.chat.id, magnet["photo"], caption=text_content)
        
        elif content_type == "photo_with_text_button":
            markup = InlineKeyboardMarkup()
            button_url = magnet.get("button_url", "")
            if button_url:
                markup.add(InlineKeyboardButton(magnet["button_text"], url=button_url))
            bot.send_photo(message.chat.id, magnet["photo"], caption=text_content, reply_markup=markup)
        
        elif content_type == "text_with_keyword_button":
            markup = InlineKeyboardMarkup()
            keywords = magnet.get("keywords", [])
            if keywords:
                button_data = ",".join(keywords)
                markup.add(InlineKeyboardButton(magnet["button_text"], callback_data=button_data))
            bot.send_message(message.chat.id, text_content, reply_markup=markup)
        elif content_type == "video_message":
             bot.send_video_note(message.chat.id, magnet["video_message"])    
        
        elif content_type == "photo_with_text_keyword_button":
            markup = InlineKeyboardMarkup()
            keywords = magnet.get("keywords", [])
            if keywords:
                button_data = ",".join(keywords)
                markup.add(InlineKeyboardButton(magnet["button_text"], callback_data=button_data))
            bot.send_photo(message.chat.id, magnet["photo"], caption=text_content, reply_markup=markup)
        
        else:
            bot.send_message(message.chat.id, "❌ Неподдерживаемый тип контента.")
    else:
        bot.send_message(message.chat.id, "❌ Кодовое слово не найдено.")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    config = load_config()
    data = call.data.strip().lower()
    keywords = [kw.strip() for kw in data.split(',')]  # Удаляем пробелы в каждом слове

    found = False
    for keyword in keywords:
        if "magnets" in config and keyword in config["magnets"]:
            magnet = config["magnets"][keyword]
            content_type = magnet["content_type"]
            text_content = magnet.get("text", "")

            try:
                if content_type == "text":
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_message(call.message.chat.id, text_content)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                elif content_type == "text_with_button":
                    markup = InlineKeyboardMarkup()
                    button_url = magnet.get("button_url", "")
                    if button_url:
                        markup.add(InlineKeyboardButton(magnet["button_text"], url=button_url))
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_message(call.message.chat.id, text_content, reply_markup=markup)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                elif content_type == "video_message":
                    bot.send_video_note(call.message.chat.id, magnet["video_message"])
                    # Текстовое сообщение не отправляется, если текст отсутствует
                    if text_content:  # Если текст есть, отправляем его
                        bot.send_message(call.message.chat.id, text_content)
                elif content_type == "text_with_video":
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_video(call.message.chat.id, magnet["video"], caption=text_content)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                elif content_type == "text_with_video_button":
                    markup = InlineKeyboardMarkup()
                    button_url = magnet.get("button_url", "")
                    if button_url:
                        markup.add(InlineKeyboardButton(magnet["button_text"], url=button_url))
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_video(call.message.chat.id, magnet["video"], caption=text_content, reply_markup=markup)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                elif content_type == "text_with_voice":
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_voice(call.message.chat.id, magnet["voice"], caption=text_content)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                elif content_type == "text_with_document":
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_document(call.message.chat.id, magnet["document"], caption=text_content)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                elif content_type == "photo_with_text":
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_photo(call.message.chat.id, magnet["photo"], caption=text_content)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                elif content_type == "photo_with_text_button":
                    markup = InlineKeyboardMarkup()
                    button_url = magnet.get("button_url", "")
                    if button_url:
                        markup.add(InlineKeyboardButton(magnet["button_text"], url=button_url))
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_photo(call.message.chat.id, magnet["photo"], caption=text_content, reply_markup=markup)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                elif content_type == "text_with_keyword_button":
                    markup = InlineKeyboardMarkup()
                    keywords = magnet.get("keywords", [])
                    if keywords:
                        button_data = ",".join(keywords)
                        markup.add(InlineKeyboardButton(magnet["button_text"], callback_data=button_data))
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_message(call.message.chat.id, text_content, reply_markup=markup)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                elif content_type == "photo_with_text_keyword_button":
                    markup = InlineKeyboardMarkup()
                    keywords = magnet.get("keywords", [])
                    if keywords:
                        button_data = ",".join(keywords)
                        markup.add(InlineKeyboardButton(magnet["button_text"], callback_data=button_data))
                    if text_content:  # Проверяем, есть ли текст
                        bot.send_photo(call.message.chat.id, magnet["photo"], caption=text_content, reply_markup=markup)
                    else:
                        print(f"❌ Текст отсутствует для кодового слова '{keyword}'")
                else:
                    bot.send_message(call.message.chat.id, "❌ Неподдерживаемый тип контента.")
                found = True
            except Exception as e:
                print(f"Ошибка отправки контента для {call.message.chat.id}: {e}")
                bot.send_message(call.message.chat.id, "⚠️ Ошибка при загрузке контента.")

    if not found:
        print(f"❌ Кодовое слово '{data}' не найдено в конфиге: {list(config['magnets'].keys())}")
        bot.send_message(call.message.chat.id, "❌ Кодовое слово не найдено.")


# Запуск бота
print("Бот запущен")  # Отладка

while True:
    try:
        print("🔄 Бот запущен...")
        for admin_id in administrators:  # 🔥 Используем готовый список админов
            try:
                bot.send_message(admin_id, "✅ Бот успешно запущен!")
            except:
                print(f"⚠ Не удалось отправить сообщение админу {admin_id}")

        bot.polling(none_stop=True)

    except Exception as e:
        error_text = f"❌ Ошибка: {e}\n🔄 Бот перезапускается..."
        print(error_text)

        for admin_id in administrators:
            try:
                bot.send_message(admin_id, error_text)  # 🔥 Отправка ошибки всем администраторам
            except:
                print(f"⚠ Не удалось отправить сообщение админу {admin_id}")

        time.sleep(5)  # Подождать 5 секунд перед перезапуском
