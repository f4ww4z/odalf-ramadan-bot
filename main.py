import logging
import os

from dotenv import load_dotenv
from telegram import ParseMode, Update, Message, Bot, Chat
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

from handlers.register import register_participant
from handlers.setoran import validate_setoran
from handlers.view import display_group_setoran, display_individual_setoran
from handlers.welcome import welcome

load_dotenv(verbose=True)

APP_NAME = "odalf-ramadan-bot"
TOKEN = os.environ.get('TOKEN')
PORT = os.environ.get('PORT', 8443)
GROUP_CHAT_ID = int(os.environ['RAMADAN_GROUP_CHAT_ID'])
DEBUG = os.environ.get('DEBUG', '') != ''


def help(update, context):
    chat = update.effective_chat
    text = f"""
Selamat datang di grup {chat.title}\.
Berikut adalah command yang bisa dijalankan:

*Daftar Anggota Baru*
$ odalf daftar _nama penuh_
Contoh: odalf daftar fawwaz

*Setoran*
$ odalf lapor _nama penuh_ juz _1\-30_ _A\-B_
Contoh: odalf lapor fawwaz juz 1 A

*Lihat Progress Grup*
$ odalf list

*Lihat Progress Individu*
$ odalf list _nama penuh_
Contoh: odalf list fawwaz

"""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             parse_mode=ParseMode.MARKDOWN_V2)


def greet(update, context):
    chat_id = update.effective_chat.id
    new_chat_members = update.message.new_chat_members
    for user in new_chat_members:
        # Another user joined the chat
        welcome(context.bot, chat_id, user.first_name)


def on_message(update: Update, context: CallbackContext):
    chat: Chat = update.effective_chat
    if chat.id != GROUP_CHAT_ID:
        return

    bot: Bot = context.bot
    message: Message = update.message
    message_string: str = message.text.strip().lower()

    # check if message is in correct 'setoran format'
    if message_string.startswith('odalf lapor'):
        reply_text = validate_setoran(message_string)
        bot.send_message(chat_id=chat.id,
                         text=reply_text,
                         reply_to_message_id=message.message_id)

    elif message_string.startswith('odoj'):
        bot.send_message(chat_id=chat.id,
                         text='Tukar \'odoj\' dengan \'odalf\'.',
                         reply_to_message_id=message.message_id)

    elif message_string.startswith('odalf list'):
        if len(message_string) > len('odalf list '):
            name = message_string.split('odalf list ')[1].strip()
            display_individual_setoran(bot, chat, message.message_id, name)
        else:
            display_group_setoran(bot, chat)
    elif message_string.startswith('odalf daftar'):
        full_name = message_string.split('odalf daftar')[1].strip()

        register_participant(bot, chat.id, message.message_id, full_name)


if __name__ == '__main__':
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s  %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(MessageHandler(Filters.status_update, greet))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, on_message))

    if DEBUG:
        print('Started Odalf Bot. Listening for messages...')
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0",
                              port=int(PORT),
                              url_path=TOKEN)
        updater.bot.set_webhook(f"https://{APP_NAME}.herokuapp.com/{TOKEN}")
    updater.idle()
