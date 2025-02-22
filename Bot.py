import telebot
import json
import os
import schedule
import time
import threading
from flask import Flask
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("BOT_TOKEN")  # Загружаем токен из окружения

if TOKEN is None:
    raise ValueError("BOT_TOKEN не найден! Убедитесь, что переменная окружения установлена.")

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render задает PORT автоматически
    app.run(host='0.0.0.0', port=port)

FIRST_VIDEO_URL = "https://drive.google.com/file/d/1hWgxrGfhDbNFpQB_iSCUKP_k69MtGIJodw/view?usp=drive_link"

# Путь к файлу с пользователями
USERS_FILE = 'users.json'
users = set()

# Путь к файлу конфигурации
CONFIG_FILE = 'config.json'

# Список администраторов
administrators = {447640188, 600164937, 339175430}

# Функция загрузки пользователей из файла
def load_users():
    global users
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            users = set(map(int, json.load(file)))  # Преобразуем в int
        print(f"Загружено {len(users)} пользователей: {users}")  # Проверка
    except (FileNotFoundError, json.JSONDecodeError):
        print("Файл users.json не найден или пуст. Создаём новый.")
        users = set()

# Функция сохранения пользователей в файл
def save_users():
    with open(USERS_FILE, 'w', encoding='utf-8') as file:
        json.dump(list(users), file, ensure_ascii=False, indent=4)

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
        # Возвращаем конфигурацию по умолчанию, если файл не найден или пуст
        return {
            "content_type": "text_with_button",
            "text": "Привет! Это новый контент для команды /start.",
            "button_text": "Перейти к видео",
            "button_url": "https://example.com/video",
            "photo": None,
            "video": None,
            "voice": None,
            "document": None
        }

# Сохранение конфигурации
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as file:
        json.dump(config, file, ensure_ascii=False, indent=4)

# Загрузка пользователей при старте бота
load_users()

bot = telebot.TeleBot(TOKEN)

# Обновленный обработчик /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    if user_id not in users:
        add_user(user_id)  # Добавляем пользователя в список и сохраняем его
    
    # Загружаем конфигурацию
    config = load_config()
    markup = InlineKeyboardMarkup()
    
    # Создаем кнопку, если она нужна
    if "button" in config["content_type"]:
        markup.add(InlineKeyboardButton(config["button_text"], url=config["button_url"]))
    
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
        "8. Картинка с текстом и кнопкой"
    )
    bot.reply_to(message, menu)
    bot.register_next_step_handler(message, process_content_type)

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
        "8": "photo_with_text_button"
    }
    
    if content_type not in valid_types:
        bot.reply_to(message, "❌ Некорректный тип контента")
        return
    
    config = load_config()
    config["content_type"] = valid_types[content_type]
    
    # Запрашиваем дополнительные данные в зависимости от типа контента
    if any(t in config["content_type"] for t in ["text", "photo", "video", "voice", "document"]):
        bot.reply_to(message, "📝 Введите основной текст:")
        bot.register_next_step_handler(message, lambda m: process_main_text(m, config))
    
    # Для типов только с медиа
    elif config["content_type"] in ["photo", "video", "voice", "document"]:
        bot.reply_to(message, f"📤 Отправьте {config['content_type']}:")
        bot.register_next_step_handler(message, lambda m: process_media(m, config))

def process_main_text(message, config):
    config["text"] = message.text
    
    if config["content_type"] in ["text_with_button", "text_with_video_button", "photo_with_text_button"]:
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        bot.register_next_step_handler(message, lambda m: process_button_text(m, config))
    
    elif config["content_type"] in ["text_with_video", "text_with_video_button"]:
        bot.reply_to(message, "🎥 Отправьте видео:")
        bot.register_next_step_handler(message, lambda m: process_video(m, config))
    
    elif config["content_type"] == "text_with_voice":
        bot.reply_to(message, "🎤 Отправьте голосовое сообщение:")
        bot.register_next_step_handler(message, lambda m: process_voice(m, config))
    
    elif config["content_type"] == "text_with_document":
        bot.reply_to(message, "📎 Отправьте файл:")
        bot.register_next_step_handler(message, lambda m: process_document(m, config))
    
    elif config["content_type"] in ["photo_with_text", "photo_with_text_button"]:
        bot.reply_to(message, "🖼 Отправьте фото:")
        bot.register_next_step_handler(message, lambda m: process_photo(m, config))
    
    else:
        save_config(config)
        bot.reply_to(message, "✅ Конфигурация обновлена!")

def process_button_text(message, config):
    config["button_text"] = message.text
    bot.reply_to(message, "🔗 Введите ссылку для кнопки:")
    bot.register_next_step_handler(message, lambda m: process_button_url(m, config))

def process_button_url(message, config):
    config["button_url"] = message.text
    save_config(config)
    bot.reply_to(message, "✅ Конфигурация обновлена!")

def process_photo(message, config):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте фото.")
        return
    config["photo"] = message.photo[-1].file_id
    if config["content_type"] == "photo_with_text_button":
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        bot.register_next_step_handler(message, lambda m: process_button_text(m, config))
    else:
        save_config(config)
        bot.reply_to(message, "✅ Конфигурация обновлена!")

def process_video(message, config):
    if message.content_type != 'video':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видео.")
        return
    config["video"] = message.video.file_id
    if config["content_type"] == "text_with_video_button":
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        bot.register_next_step_handler(message, lambda m: process_button_text(m, config))
    else:
        save_config(config)
        bot.reply_to(message, "✅ Конфигурация обновлена!")

def process_voice(message, config):
    if message.content_type != 'voice':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте голосовое сообщение.")
        return
    config["voice"] = message.voice.file_id
    save_config(config)
    bot.reply_to(message, "✅ Конфигурация обновлена!")

def process_document(message, config):
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

@bot.message_handler(commands=['delay_message'])
def delay_message(message):
    if message.chat.id not in administrators:
        return
    msg = bot.reply_to(message, "Отправьте сообщение для отложенной отправки")
    bot.register_next_step_handler(msg, process_delayed_message)

def process_delayed_message(message):
    msg = bot.reply_to(message, "Введите задержку в секундах:")
    bot.register_next_step_handler(msg, lambda m: set_delay(m, message))

def set_delay(message, original_message):
    try:
        delay = int(message.text)
        time.sleep(delay)
        
        # Отправка сохраненного сообщения
        for user in users:
            try:
                send_content(user, original_message)
            except Exception as e:
                print(f"Ошибка отправки: {e}")
    except ValueError:
        bot.reply_to(message, "Некорректное время")

def send_content(chat_id, message):
    if message.content_type == 'text':
        bot.send_message(chat_id, message.text)
    elif message.photo:
        bot.send_photo(chat_id, message.photo[-1].file_id)
    elif message.video:
        bot.send_video(chat_id, message.video.file_id)
    elif message.voice:
        bot.send_voice(chat_id, message.voice.file_id)
    elif message.document:
        bot.send_document(chat_id, message.document.file_id)

@bot.message_handler(commands=['send_all'])
def send_any_content(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    bot.reply_to(message, "Отправьте любой контент (текст/фото/видео/голос/файл) для рассылки:")
    bot.register_next_step_handler(message, process_any_content)

def process_any_content(message):
    content_type = message.content_type
    content = None

    if content_type == 'text':
        content = message.text
    elif content_type == 'photo':
        content = message.photo[-1].file_id
    elif content_type == 'video':
        content = message.video.file_id
    elif content_type == 'voice':
        content = message.voice.file_id
    elif content_type == 'document':
        content = message.document.file_id
    else:
        bot.reply_to(message, "❌ Неподдерживаемый тип контента")
        return

    for user in users:
        try:
            if content_type == 'text':
                bot.send_message(user, content)
            elif content_type == 'photo':
                bot.send_photo(user, content)
            elif content_type == 'video':
                bot.send_video(user, content)
            elif content_type == 'voice':
                bot.send_voice(user, content)
            elif content_type == 'document':
                bot.send_document(user, content)
        except Exception as e:
            print(f"Ошибка отправки для {user}: {e}")

    bot.reply_to(message, "✅ Контент успешно отправлен всем пользователям!")

@bot.message_handler(commands=['send_to_all'])
def send_video_to_all(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    command_parts = message.text.split('"')
    if len(command_parts) < 5:
        bot.reply_to(message, "Используйте формат: /send_to_all \"описание\" \"название кнопки\" ссылка")
        return
    
    description = command_parts[1].strip()
    button_text = command_parts[3].strip()
    video_url = command_parts[4].strip()
    
    if not (video_url.startswith("http://") or video_url.startswith("https://")):
        bot.reply_to(message, "Некорректная ссылка. Убедитесь, что она начинается с http:// или https://")
        return
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(button_text, url=video_url))
    
    for user in users:
        try:
            bot.send_message(user, description, reply_markup=markup)
        except Exception as e:
            print(f"Ошибка при отправке видео пользователю {user}: {e}")

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

bot.polling(none_stop=True)
