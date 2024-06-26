import logging
import random
import os
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from aiohttp import ClientSession, TCPConnector
import httpx

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Чтение фраз признаний
with open('love_messages.txt', 'r', encoding='utf-8') as file:
    love_messages = file.readlines()

# Путь к папке с фотографиями котиков
cat_pics_folder = 'cat_pics/'

# Твой user_id
MY_USER_ID = 354635440  # замените на свой фактический user_id

# Настройка прокси
PROXY_URL = "http://196.223.129.21:80"

async def love_confession(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = random.choice(love_messages).strip()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

async def show_cat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cat_pic = random.choice(os.listdir(cat_pics_folder))
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(os.path.join(cat_pics_folder, cat_pic), 'rb'))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'love_confession':
        await love_confession(update, context)
    elif query.data == 'show_cat':
        await show_cat(update, context)

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

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_name = update.message.from_user.username or update.message.from_user.first_name
    user_id = update.message.from_user.id
    notification_message = f"Пользователь {user_name} написал: {user_message}\nChat ID: {user_id}"

    await context.bot.send_message(chat_id=MY_USER_ID, text=notification_message)
    await update.message.reply_text("Ваше сообщение было получено!")

async def send_good_night(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=context.job.chat_id, text="Сладких снов, любимый котёнок")

async def send_good_morning(context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=context.job.chat_id, text="Доброе утро, любимый котёнок, хорошего тебе дня")

def schedule_jobs(application: Application, chat_id: int) -> None:
    job_queue = application.job_queue

    job_queue.run_daily(send_good_night, time=datetime.time(hour=23, minute=59, second=0), data=chat_id)
    job_queue.run_daily(send_good_morning, time=datetime.time(hour=10, minute=0, second=0), data=chat_id)

async def create_application() -> Application:
    connector = TCPConnector(ssl=False)
    async with ClientSession(connector=connector) as session:
        async with httpx.AsyncClient(proxies=PROXY_URL) as client:
            return Application.builder().token("6985004195:AAHjLqBd8TscIR4y68FGViUqI--BieT25bk").httpx_client(client).build()

def main() -> None:
    loop = asyncio.get_event_loop()
    application = loop.run_until_complete(create_application())

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("send", send))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    chat_id = MY_USER_ID  # замените на ваш фактический chat_id
    schedule_jobs(application, chat_id)

    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
