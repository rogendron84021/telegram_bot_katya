import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import os
import datetime

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Чтение фраз признаний
with open('love_messages.txt', 'r', encoding='utf-8') as file:
    love_messages = file.readlines()

# Путь к папке с фотографиями котиков
cat_pics_folder = 'cat_pics/'

# Твой user_id
MY_USER_ID = 354635440  # замените на свой фактический user_id

# Функция для отправки случайной фразы признания
async def love_confession(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = random.choice(love_messages).strip()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# Функция для отправки случайной фотографии котика
async def show_cat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cat_pic = random.choice(os.listdir(cat_pics_folder))
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(os.path.join(cat_pics_folder, cat_pic), 'rb'))

# Обработчик кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'love_confession':
        await love_confession(update, context)
    elif query.data == 'show_cat':
        await show_cat(update, context)

# Команда /start для начала работы с ботом
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    logger.info(f"Chat ID: {chat_id}")
    
    keyboard = [
        [
            InlineKeyboardButton("Признание в любви", callback_data='love_confession'),
            InlineKeyboardButton("Покажи котика", callback_data='show_cat')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выбери действие:', reply_markup=reply_markup)

# Команда /send для отправки сообщения пользователю
async def send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id == MY_USER_ID:
        if context.args:
            target_user_id = int(context.args[0])
            message = ' '.join(context.args[1:])
            await context.bot.send_message(chat_id=target_user_id, text=message)
        else:
            await update.message.reply_text('Использование: /send <user_id> <сообщение>')
    else:
        await update.message.reply_text('У вас нет прав для использования этой команды.')

# Обработчик всех текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_name = update.message.from_user.username or update.message.from_user.first_name
    user_id = update.message.from_user.id
    notification_message = f"Пользователь {user_name} написал: {user_message}\nChat ID: {user_id}"
    
    # Отправка уведомления тебе
    await context.bot.send_message(chat_id=MY_USER_ID, text=notification_message)
    
    # Ответ пользователю
    await update.message.reply_text("Ваше сообщение было получено!")

# Периодические сообщения
async def send_good_night(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=context.job.chat_id, text="Сладких снов, любимый котёнок")

async def send_good_morning(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=context.job.chat_id, text="Доброе утро, любимый котёнок, хорошего тебе дня")

def schedule_jobs(application: Application, chat_id: int) -> None:
    job_queue = application.job_queue

    job_queue.run_daily(send_good_night, time=datetime.time(hour=0, minute=0, second=0), chat_id=chat_id)
    job_queue.run_daily(send_good_morning, time=datetime.time(hour=10, minute=0, second=0), chat_id=chat_id)

def main() -> None:
    # Вставь сюда свой токен
    application = Application.builder().token("6985004195:AAHjLqBd8TscIR4y68FGViUqI--BieT25bk").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("send", send))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота и планировщик
    chat_id = 354635440  # замените на ваш фактический chat_id
    schedule_jobs(application, chat_id)
    
    application.run_polling()

if __name__ == '__main__':
    main()
