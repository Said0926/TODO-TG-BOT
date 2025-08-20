from telebot import types

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('➕ Добавить задачу', '➕ Добавить несколько задач')
    markup.row("📋 Показать список", "✅ Выполнить задачу")
    markup.row("✏️ Редактировать задачу","🗑 Удалить задачу")
    return markup
