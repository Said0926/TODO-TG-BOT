import telebot
from config import TOKEN
from handlers import tasks
from database.db import init_db
import logging

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

# Создает таблицу если ее нет
init_db()

# Регистрируем все команды, связанные с задачами
tasks.register(bot)

# Настрока логов
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8',
)



# Запуск бота
if __name__ == "__main__":
    print("successfully")
    bot.infinity_polling()
