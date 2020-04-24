from telegram import ParseMode


def welcome(bot, chat_id, name):
    text = f"""Ahlan wa sahlan, akhi {name}\!
Silahkan ketik \/help untuk lihat cara setoran\."""
    bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2)
