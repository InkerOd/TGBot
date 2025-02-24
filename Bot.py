

from datetime import datetime

@bot.message_handler(commands=['delay_message'])
def delay_message(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    # Запрашиваем тип контента
    menu = (
        "Выберите тип контента:\n"
        "1. Текст\n"
        "2. Текст с кнопкой\n"
        "3. Текст с видео\n"
        "4. Текст с видео и кнопкой(пока не работает)\n"
        "5. Текст с голосовым сообщением\n"
        "6. Текст с файлом\n"
        "7. Картинка с текстом\n"
        "8. Картинка с текстом и кнопкой(пока не работает)"
    )
    bot.reply_to(message, menu)
    bot.register_next_step_handler(message, process_delay_content_type)

def process_delay_content_type(message):
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
        bot.reply_to(message, "❌ Некорректный тип контента. Попробуйте снова.")
        return
    
    # Сохраняем выбранный тип контента
    context = {"content_type": valid_types[content_type]}
    
    # Запрашиваем основной текст, если он нужен
    if any(t in context["content_type"] for t in ["text", "photo", "video", "voice", "document"]):
        bot.reply_to(message, "📝 Введите основной текст:")
        bot.register_next_step_handler(message, process_delay_main_text, context)
    else:
        # Если текст не нужен, переходим к следующему шагу
        process_delay_main_text(message, context)

def process_delay_main_text(message, context):
    if "text" in context["content_type"]:
        context["text"] = message.text.strip()
    
    # Запрашиваем дополнительные данные в зависимости от типа контента
    if context["content_type"] in ["text_with_button", "text_with_video_button", "photo_with_text_button"]:
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        bot.register_next_step_handler(message, process_delay_button_text, context)
    elif context["content_type"] in ["text_with_video", "text_with_video_button"]:
        bot.reply_to(message, "🎥 Отправьте видео:")
        bot.register_next_step_handler(message, process_delay_video, context)
    elif context["content_type"] == "text_with_voice":
        bot.reply_to(message, "🎤 Отправьте голосовое сообщение:")
        bot.register_next_step_handler(message, process_delay_voice, context)
    elif context["content_type"] == "text_with_document":
        bot.reply_to(message, "📎 Отправьте файл:")
        bot.register_next_step_handler(message, process_delay_document, context)
    elif context["content_type"] in ["photo_with_text", "photo_with_text_button"]:
        bot.reply_to(message, "🖼 Отправьте фото:")
        bot.register_next_step_handler(message, process_delay_photo, context)
    else:
        # Если дополнительные данные не нужны, запрашиваем дату и время
        bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС:")
        bot.register_next_step_handler(message, process_delay_datetime, context)

def process_delay_button_text(message, context):
    context["button_text"] = message.text.strip()
    bot.reply_to(message, "🔗 Введите ссылку для кнопки:")
    bot.register_next_step_handler(message, process_delay_button_url, context)

def process_delay_button_url(message, context):
    context["button_url"] = message.text.strip()
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС:")
    bot.register_next_step_handler(message, process_delay_datetime, context)

def process_delay_video(message, context):
    if message.content_type != 'video':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видео.")
        return
    context["video"] = message.video.file_id
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС:")
    bot.register_next_step_handler(message, process_delay_datetime, context)

def process_delay_voice(message, context):
    if message.content_type != 'voice':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте голосовое сообщение.")
        return
    context["voice"] = message.voice.file_id
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС:")
    bot.register_next_step_handler(message, process_delay_datetime, context)

def process_delay_document(message, context):
    if message.content_type != 'document':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте файл.")
        return
    context["document"] = message.document.file_id
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС:")
    bot.register_next_step_handler(message, process_delay_datetime, context)

def process_delay_photo(message, context):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте фото.")
        return
    context["photo"] = message.photo[-1].file_id
    bot.reply_to(message, "📅 Введите дату и время отправки в формате ДД-ММ-ГГГГ ЧЧ:ММ:СС:")
    bot.register_next_step_handler(message, process_delay_datetime, context)

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
    except ValueError:
        bot.reply_to(message, "❌ Некорректный формат даты и времени. Используйте формат ДД-ММ-ГГГГ ЧЧ:ММ:СС.")

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
        except Exception as e:
            print(f"Ошибка отправки для {user}: {e}")

@bot.message_handler(commands=['send_all'])
def send_any_content(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    # Запрашиваем тип контента
    menu = (
        "Выберите тип контента:\n"
        "1. Текст\n"
        "2. Текст с кнопкой\n"
        "3. Текст с видео\n"
        "4. Текст с видео и кнопкой(пока не работает)\n"
        "5. Текст с голосовым сообщением\n"
        "6. Текст с файлом\n"
        "7. Картинка с текстом\n"
        "8. Картинка с текстом и кнопкой (пока не работает)"
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
        bot.reply_to(message, "❌ Некорректный тип контента. Попробуйте снова.")
        return
    
    # Сохраняем выбранный тип контента
    context = {"content_type": valid_types[content_type]}
    
    # Запрашиваем основной текст, если он нужен
    if any(t in context["content_type"] for t in ["text", "photo", "video", "voice", "document"]):
        bot.reply_to(message, "📝 Введите основной текст:")
        bot.register_next_step_handler(message, process_main_text, context)
    else:
        # Если текст не нужен, переходим к следующему шагу
        process_main_text(message, context)

def process_main_text(message, context):
    if "text" in context["content_type"]:
        context["text"] = message.text.strip()
    
    # Запрашиваем дополнительные данные в зависимости от типа контента
    if context["content_type"] in ["text_with_button", "text_with_video_button", "photo_with_text_button"]:
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        bot.register_next_step_handler(message, process_button_text, context)
    elif context["content_type"] in ["text_with_video", "text_with_video_button"]:
        bot.reply_to(message, "🎥 Отправьте видео:")
        bot.register_next_step_handler(message, process_video, context)
    elif context["content_type"] == "text_with_voice":
        bot.reply_to(message, "🎤 Отправьте голосовое сообщение:")
        bot.register_next_step_handler(message, process_voice, context)
    elif context["content_type"] == "text_with_document":
        bot.reply_to(message, "📎 Отправьте файл:")
        bot.register_next_step_handler(message, process_document, context)
    elif context["content_type"] in ["photo_with_text", "photo_with_text_button"]:
        bot.reply_to(message, "🖼 Отправьте фото:")
        bot.register_next_step_handler(message, process_photo, context)
    else:
        # Если дополнительные данные не нужны, отправляем контент
        send_content_to_all(message, context)

def process_button_text(message, context):
    context["button_text"] = message.text.strip()
    bot.reply_to(message, "🔗 Введите ссылку для кнопки:")
    bot.register_next_step_handler(message, process_button_url, context)

def process_button_url(message, context):
    context["button_url"] = message.text.strip()
    send_content_to_all(message, context)

def process_video(message, context):
    if message.content_type != 'video':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видео.")
        return
    context["video"] = message.video.file_id
    send_content_to_all(message, context)

def process_voice(message, context):
    if message.content_type != 'voice':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте голосовое сообщение.")
        return
    context["voice"] = message.voice.file_id
    send_content_to_all(message, context)

def process_document(message, context):
    if message.content_type != 'document':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте файл.")
        return
    context["document"] = message.document.file_id
    send_content_to_all(message, context)

def process_photo(message, context):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте фото.")
        return
    context["photo"] = message.photo[-1].file_id
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
        except Exception as e:
            print(f"Ошибка отправки для {user}: {e}")
    
    bot.reply_to(message, "✅ Контент успешно отправлен всем пользователям!")

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
    bot.register_next_step_handler(message, process_magnet_keyword)

def process_magnet_keyword(message):
    keyword = message.text.strip().lower()
    if not keyword:
        bot.reply_to(message, "❌ Кодовое слово не может быть пустым.")
        return
    
    # Сохраняем кодовое слово в контексте
    config = load_config()
    if "magnets" not in config:
        config["magnets"] = {}
    
    if keyword in config["magnets"]:
        bot.reply_to(message, f"❌ Кодовое слово '{keyword}' уже существует.")
        return
    
    config["magnets"][keyword] = {}
    save_config(config)
    
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
    bot.register_next_step_handler(message, lambda m: process_magnet_content_type(m, keyword))

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
        "8": "photo_with_text_button"
    }
    
    if content_type not in valid_types:
        bot.reply_to(message, "❌ Некорректный тип контента")
        return
    
    config = load_config()
    config["magnets"][keyword]["content_type"] = valid_types[content_type]
    save_config(config)
    
    # Запрашиваем дополнительные данные в зависимости от типа контента
    if any(t in config["magnets"][keyword]["content_type"] for t in ["text", "photo", "video", "voice", "document"]):
        bot.reply_to(message, "📝 Введите основной текст:")
        bot.register_next_step_handler(message, lambda m: process_magnet_main_text(m, keyword))
    
    # Для типов только с медиа
    elif config["magnets"][keyword]["content_type"] in ["photo", "video", "voice", "document"]:
        bot.reply_to(message, f"📤 Отправьте {config['magnets'][keyword]['content_type']}:")
        bot.register_next_step_handler(message, lambda m: process_magnet_media(m, keyword))

def process_magnet_main_text(message, keyword):
    config = load_config()
    config["magnets"][keyword]["text"] = message.text
    save_config(config)
    
    if config["magnets"][keyword]["content_type"] in ["text_with_button", "text_with_video_button", "photo_with_text_button"]:
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        bot.register_next_step_handler(message, lambda m: process_magnet_button_text(m, keyword))
    
    elif config["magnets"][keyword]["content_type"] in ["text_with_video", "text_with_video_button"]:
        bot.reply_to(message, "🎥 Отправьте видео:")
        bot.register_next_step_handler(message, lambda m: process_magnet_video(m, keyword))
    
    elif config["magnets"][keyword]["content_type"] == "text_with_voice":
        bot.reply_to(message, "🎤 Отправьте голосовое сообщение:")
        bot.register_next_step_handler(message, lambda m: process_magnet_voice(m, keyword))
    
    elif config["magnets"][keyword]["content_type"] == "text_with_document":
        bot.reply_to(message, "📎 Отправьте файл:")
        bot.register_next_step_handler(message, lambda m: process_magnet_document(m, keyword))
    
    elif config["magnets"][keyword]["content_type"] in ["photo_with_text", "photo_with_text_button"]:
        bot.reply_to(message, "🖼 Отправьте фото:")
        bot.register_next_step_handler(message, lambda m: process_magnet_photo(m, keyword))
    
    else:
        bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_button_text(message, keyword):
    config = load_config()
    config["magnets"][keyword]["button_text"] = message.text
    save_config(config)
    
    bot.reply_to(message, "🔗 Введите ссылку для кнопки:")
    bot.register_next_step_handler(message, lambda m: process_magnet_button_url(m, keyword))

def process_magnet_button_url(message, keyword):
    config = load_config()
    config["magnets"][keyword]["button_url"] = message.text
    save_config(config)
    
    bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_photo(message, keyword):
    if message.content_type != 'photo':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте фото.")
        return
    
    config = load_config()
    config["magnets"][keyword]["photo"] = message.photo[-1].file_id
    save_config(config)
    
    if config["magnets"][keyword]["content_type"] == "photo_with_text_button":
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        bot.register_next_step_handler(message, lambda m: process_magnet_button_text(m, keyword))
    else:
        bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

def process_magnet_video(message, keyword):
    if message.content_type != 'video':
        bot.reply_to(message, "❌ Некорректный тип сообщения. Пожалуйста, отправьте видео.")
        return
    
    config = load_config()
    config["magnets"][keyword]["video"] = message.video.file_id
    save_config(config)
    
    if config["magnets"][keyword]["content_type"] == "text_with_video_button":
        bot.reply_to(message, "🖋 Введите текст для кнопки:")
        bot.register_next_step_handler(message, lambda m: process_magnet_button_text(m, keyword))
    else:
        bot.reply_to(message, f"✅ Кодовое слово '{keyword}' создано!")

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


import re

# Команда /delete_magnet
@bot.message_handler(commands=['delete_magnet'])
def delete_magnet(message):
    if message.chat.id not in administrators:
        bot.reply_to(message, "У вас нет прав для выполнения этой команды.")
        return
    
    bot.reply_to(message, "Введите кодовое слово для удаления:")
    bot.register_next_step_handler(message, process_delete_magnet)

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
        
        elif content_type == "text_with_button":
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(magnet["button_text"], url=magnet["button_url"]))
            bot.send_message(message.chat.id, text_content, reply_markup=markup)
        
        elif content_type == "text_with_video":
            bot.send_video(message.chat.id, magnet["video"], caption=text_content)
        
        elif content_type == "text_with_video_button":
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(magnet["button_text"], url=magnet["button_url"]))
            bot.send_video(message.chat.id, magnet["video"], caption=text_content, reply_markup=markup)
        
        elif content_type == "text_with_voice":
            bot.send_voice(message.chat.id, magnet["voice"], caption=text_content)
        
        elif content_type == "text_with_document":
            bot.send_document(message.chat.id, magnet["document"], caption=text_content)
        
        elif content_type == "photo_with_text":
            bot.send_photo(message.chat.id, magnet["photo"], caption=text_content)
        
        elif content_type == "photo_with_text_button":
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(magnet["button_text"], url=magnet["button_url"]))
            bot.send_photo(message.chat.id, magnet["photo"], caption=text_content, reply_markup=markup)
        
        else:
            bot.send_message(message.chat.id, "❌ Неподдерживаемый тип контента.")
    else:
        bot.send_message(message.chat.id, "❌ Кодовое слово не найдено.")


# Запуск бота
print("Бот запущен")  # Отладка

bot.polling(none_stop=True)
