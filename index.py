import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import google.generativeai as genai

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WHITELISTED_ACCOUNTS = [int(account) for account in os.getenv(
    'WHITELISTED_ACCOUNTS', '').split(',') if account]

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

last_date = ''
complete_message = ''


async def gemini(message):
    response = model.generate_content(message)
    return response.text


async def gemini_summary(message):
    # print(f"Gemini triggered with message: {message}")
    response = model.generate_content(
        f"Please summarize the following text in bullet points that don't use markdown, just preface them with a dash: {message}")
    return response.text

last_date = '1970-01-01 00:00:00+00:00'
complete_message = ''


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Only works for some accounts
    if update.message.chat.id not in WHITELISTED_ACCOUNTS:
        print('REJECTED: not a whitelisted account (id:', update.message.chat.id, ')')
        return

    await context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to mAIella!')


async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_date, complete_message

    # Only works for some accounts
    if update.message.chat.id not in WHITELISTED_ACCOUNTS:
        print('REJECTED: not a whitelisted account (id:', update.message.chat.id, ')')
        return

    if len(update.message.text) < 10:
        print('REJECTED: message was too short at', len(
            update.message.text), 'characters')
        return

    if last_date == update.message.date:
        complete_message += update.message.text
        return
    else:
        complete_message = update.message.text

    last_date = update.message.date

    # The rest of your function continues here
    response = await gemini_summary(complete_message)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_date, complete_message

    # Only works for some accounts
    if update.message.chat.id not in WHITELISTED_ACCOUNTS:
        print('REJECTED: not a whitelisted account (id:', update.message.chat.id, ')')
        return

    if last_date == update.message.date:
        complete_message += update.message.text
        return
    else:
        complete_message = update.message.text

    last_date = update.message.date

    # The rest of your function continues here
    response = await gemini(complete_message)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


if __name__ == '__main__':
    # Initialize the bot
    application = ApplicationBuilder().token(
        TELEGRAM_BOT_TOKEN).build()

    # start handler
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Echo handler
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    # /summarize handler
    summarize_handler = CommandHandler('summarize', summarize)
    s_handler = CommandHandler('s', summarize)
    application.add_handler(summarize_handler)
    application.add_handler(s_handler)

    # Run the bot
    application.run_polling()
