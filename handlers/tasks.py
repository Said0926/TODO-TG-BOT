from datetime import datetime
from telebot import types
from database.db import add_task, get_tasks, mark_done, delete_task, update_task_text
from utils.keyboards import main_menu
import logging


# Словарь для хранения состояния редактирования задач
user_edit_state = {}
# словарь для хранения состояния добавления нескольких задач
user_bulk_state = {}



def register(bot):
    # /start
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        logging.info(f'User {message.chat.id} нажал /start')
        try:
            bot.send_message(
                message.chat.id,
                "👋 Привет! Я твой ToDo-бот. Используй меню ниже ⬇️",
                reply_markup=main_menu()
            )
        except Exception as e:
            # print(f"[ERROR handle_start] {e}")
            logging.error(f'Ошибка при выполнении команды start: {e}')
            bot.send_message(message.chat.id, "❗ Ошибка при выполнении команды /start.")


    # Показать список
    @bot.message_handler(func=lambda msg: msg.text == '📋 Показать список')
    def handle_list_button(message):
        logging.info(f'User {message.chat.id} нажал на кнопку Показать список')
        try:
            user_id = message.chat.id
            tasks = get_tasks(user_id)

            if not tasks:
                logging.info(f'User {user_id} не имеет активных задач')
                bot.send_message(user_id, "📭 У тебя нет активных задач.")
                return

            text = "📋 Твои задачи:\n\n"
            for i, (task_id, task_text, task_date) in enumerate(tasks, 1):
                text += f"{i}. {task_text} ({task_date})\n"

            bot.send_message(user_id, text)
        except Exception as e:
            logging.error(f'Ошибка при выполнении команды Показать список: {e}')
            bot.send_message(user_id, "❗ Ошибка при получении списка задач.")


    # Добавить задачу (шаг 1 — нажата кнопка)
    @bot.message_handler(func=lambda msg: msg.text == "➕ Добавить задачу")
    def handle_add_button(message):
        logging.info(f'User {message.chat.id} нажал Добавить задачу')
        try:
            bot.send_message(message.chat.id, "📝 Введи текст задачи:")
            bot.register_next_step_handler(message, process_task_text)
        except Exception as e:
            logging.error(f'Ошибка при добавлении задачи: {e}')
            bot.send_message(message.chat.id, "❗ Ошибка при добавлении задачи.")


    # Добавить задачу (шаг 2 — ввод текста)
    def process_task_text(message):
        try:
            user_id = message.chat.id
            task_text = message.text.strip()
            from datetime import datetime
            today = datetime.now().strftime('%d.%m.%Y %H:%M')

            add_task(user_id, task_text, today)
            bot.send_message(user_id, f"✅ Задача добавлена: {task_text}")
        except Exception as e:
            logging.error(f"Ошибка при сохранении задачи: {e}")
            bot.send_message(message.chat.id, "❗ Ошибка при сохранении задачи.")
            
            
    # Добавить несколько задач (шаг 1 — нажата кнопка)
    @bot.message_handler(func=lambda msg: msg.text == '➕ Добавить несколько задач')
    def handle_bulk_add_button(message):
        logging.info(f'User {message.chat.id} нажал Добавить несколько задач')
        user_id = message.chat.id
        user_bulk_state[user_id] = True
        bot.send_message(user_id, '📝 Введи список задач, каждую с новой строки:')
        
        
    # Добавить несколько задач (шаг 2 — ввод текста)
    @bot.message_handler(func=lambda msg: msg.from_user.id in user_bulk_state)
    def process_bulk_add(message):
        user_id = message.from_user.id
        try:
            tasks = [task.strip() for task in message.text.split('\n') if task.strip()] # каждая строка – новая задача
            for task_text in tasks:
                    add_task(user_id, task_text.strip(), datetime.now().strftime('%d.%m.%Y %H:%M'))
            bot.send_message(user_id, f'✅ Добавлено {len(tasks)} задач!')
        except Exception as e:
            logging.error(f'Ошибка при добавлении задач: {e}')
            bot.send_message(user_id, '❗ Ошибка при добавлении задач')
        finally:
            user_bulk_state.pop(user_id, None)
                

    # Выполнить задачу
    @bot.message_handler(func=lambda msg: msg.text == "✅ Выполнить задачу")
    def handle_done_button(message):
        logging.info(f'User {message.chat.id} нажал Выполнить задачу')
        try:
            user_id = message.chat.id
            tasks = get_tasks(user_id)

            if not tasks:
                bot.send_message(user_id, "📭 У тебя нет активных задач.")
                return

            text = "✅ Выбери задачу для выполнения:\n\n"
            markup = types.InlineKeyboardMarkup()
            for i, (task_id, task_text, task_date) in enumerate(tasks, 1):
                markup.add(types.InlineKeyboardButton(f"{i}. {task_text}", callback_data=f"done_{task_id}"))

            bot.send_message(user_id, text, reply_markup=markup)
        except Exception as e:
            logging.error(f"Ошибка при выполнении задачи: {e}")
            bot.send_message(message.chat.id, "❗ Ошибка при выполнении задачи.")
    
    
    # обработчик нажатия кнопки ВЫПОЛНИТЬ
    @bot.callback_query_handler(func=lambda call: call.data.startswith('done_'))
    def hendle_done_callback(call):
        try:
            task_id = int(call.data.split('_')[1])
            mark_done(task_id)
            bot.answer_callback_query(call.id, '✅ Задача выполнена!')
            bot.send_message(call.message.chat.id, "Задача отмечена как выполненная ✅")
        except Exception as e:
            logging.error(f'Ошибка при выполнении задачи {e}')
            bot.answer_callback_query(call.id, '❗ Ошибка при выполнении задачи')

            
    # Удалить задачу
    @bot.message_handler(func=lambda msg: msg.text == "🗑 Удалить задачу")
    def handle_delete_button(message):
        logging.info(f'User {message.chat.id} нажал Удалить задачу')
        try:
            user_id = message.chat.id
            tasks = get_tasks(user_id)

            if not tasks:
                bot.send_message(user_id, "📭 У тебя нет активных задач для удаления.")
                return

            text = "🗑 Выбери задачу для удаления:\n\n"
            markup = types.InlineKeyboardMarkup()
            for i, (task_id, task_text, task_date) in enumerate(tasks, 1):
                markup.add(types.InlineKeyboardButton(f"{i}. {task_text}", callback_data=f"delete_{task_id}"))

            bot.send_message(user_id, text, reply_markup=markup)
        except Exception as e:
            logging.error(f"Ошибка при удалении задачи: {e}")
            bot.send_message(message.chat.id, "❗ Ошибка при удалении задачи.")


    # обработчик нажатия кнопки УДАЛИТЬ
    @bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
    def hendle_delete_callback(call):
        try:
            task_id = int(call.data.split('_')[1])
            delete_task(task_id)
            bot.answer_callback_query(call.id, "🗑 Задача удалена!")
            bot.send_message(call.message.chat.id, "Задача успешно удалена 🗑")
        except Exception as e:
            logging.error(f'Ошибка при удалении задачи: {e}')
            bot.answer_callback_query(call.id, '❗ Ошибка при удалении задачи')
            
            
    # Редактировать задачу
    @bot.message_handler(func=lambda msg: msg.text == '✏️ Редактировать задачу')
    def handle_edit_button(message):
        logging.info(f'User {message.chat.id} нажал Редактировать задачу')
        try:
            user_id = message.chat.id
            tasks = get_tasks(user_id)
            
            if not tasks:
                bot.send_message(user_id, '📭 У тебя нет активных задач для редактирования.')
                return
            
            text = '✏️ Выбери задачу для редактирования:\n\n'
            markup = types.InlineKeyboardMarkup()
            for i, (task_id, task_text, task_date) in enumerate(tasks, 1):
                markup.add(types.InlineKeyboardButton(f'{i}. {task_text}', callback_data=f'edit_{task_id}'))
            
            bot.send_message(user_id, text, reply_markup=markup)
        except Exception as e:
            logging.error(f'Ошибка при редактирование задачи: {e}')
            bot.send_message(message.chat.id, '❗ Ошибка при редактирование задачи.')
            
            
    # обработчик нажатия кнопки РЕДАКТИРОВАТЬ
    @bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
    def hendle_edit_callback(call):
        try:
            task_id = int(call.data.split('_')[1])
            bot.answer_callback_query(call.id, 'Введите новый текст задачи:')
            
            # Сохраняем task_id в словарь, чтобы использовать при следующем сообщении
            user_edit_state[call.from_user.id] = task_id
        except Exception as e:
            logging(f'Ошибка при редактировании задачи: {e}')
            bot.answer_callback_query(call.id, '❗ Ошибка при редактировании задачи')
    
    
    # Получение нового текста задачи
    @bot.message_handler(func=lambda msg: msg.from_user.id in user_edit_state)
    def process_edit_text(message):
        try:
            task_id = user_edit_state.pop(message.from_user.id)
            new_text = message.text
            update_task_text(task_id, new_text)
            bot.send_message(message.chat.id, f'✏️ Задача обновлена: {new_text}')
        except Exception as e:
            logging.error(f'Ошибка при изменении текста задачи: {e}')
            bot.send_message(message.chat.id, '❗ Ошибка при изменении текста задачи.')
