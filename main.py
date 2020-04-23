import logging
import os
import time

from dotenv import load_dotenv
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from handlers.register import register_participant
from handlers.setoran import validate_setoran
from handlers.view import display_setoran
from handlers.welcome import welcome

load_dotenv(verbose=True)

GROUP_CHAT_ID = int(os.environ['RAMADAN_GROUP_CHAT_ID'])


def help(update, context):
    text = """
Selamat datang di grup odalf special ramadan 1441H\!
Berikut adalah command yang bisa dijalankan:

*Daftar Anggota Baru*
$ odoj daftar _nama penuh_
Contoh: odoj daftar fawwaz

*Setoran*
$ odoj lapor _nama penuh_ juz _1\-30_ _A\-B_
Contoh: odoj lapor fawwaz juz 1 A

*Lihat Progress*
$ odoj list
"""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             parse_mode=ParseMode.MARKDOWN_V2)


def greet(update, context):
    chat_id = update.effective_chat.id
    new_chat_members = update.message.new_chat_members
    for user in new_chat_members:
        # Another user joined the chat
        welcome(context.bot, chat_id, user.full_name)


def echo(update, context):
    chat_id = update.effective_chat.id
    if chat_id != GROUP_CHAT_ID:
        return

    bot = context.bot
    message = update.message
    message_string: str = message.text.lower()

    # check if message is in 'setoran format'
    if message_string.startswith('odalf lapor ') and (' juz ' in message_string):
        validate_setoran(message_string, bot, chat_id, message.message_id)
    elif message_string.startswith('odalf list'):
        display_setoran(bot, chat_id)
    elif message_string.startswith('odalf daftar'):
        full_name = message_string.split('odalf daftar')[1].strip()

        register_participant(bot, chat_id, message.message_id, full_name)


updater = Updater(token=os.environ['TOKEN'], use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s  %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

dispatcher.add_handler(CommandHandler('help', help))
dispatcher.add_handler(MessageHandler(Filters.status_update, greet))
dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, echo))

print('Started Odalf Bot. Listening for messages...')
updater.start_polling()

# if any error, automatically restart
while True:
    if not updater.running:
        print('Restarted Odalf Bot due to crash. Listening for messages...')
        updater.start_polling()

    time.sleep(10)
