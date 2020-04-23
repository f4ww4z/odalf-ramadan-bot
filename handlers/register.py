from database.database import add_participant


def register_participant(bot, chat_id, message_id, full_name: str):
    text = 'Sertakan nama penuh'

    if len(full_name) > 0:
        insert_count = add_participant(full_name)

        if insert_count < 0:
            text = f"""Nama '{full_name}' sudah diambil. Tolong daftar dengan nama lain."""
        elif insert_count == 0:
            text = """Tidak berhasil didaftarkan. Coba lagi."""
        else:
            text = """Anda sukses terdaftar. Semoga bisa istiqomah!"""

    bot.send_message(chat_id=chat_id,
                     text=text,
                     reply_to_message_id=message_id)
