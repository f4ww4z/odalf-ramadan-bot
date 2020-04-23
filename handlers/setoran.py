from database.database import get_participant_id_from_name, add_setoran, increase_half_juz_count

WRONG_SETORAN_FORMAT: str = '❌ Format setoran salah. Yang benar:\n\n' \
                            'odalf lapor <nama penuh> juz <1-30> <A-B>\n' \
                            'Contoh: odalf lapor fawwaz juz 1 A'


def validate_setoran(message_string: str, bot, chat_id, message_id):
    nama_dan_juz = message_string.split('odalf lapor ')
    if len(nama_dan_juz) <= 1:
        bot.send_message(chat_id=chat_id,
                         text=WRONG_SETORAN_FORMAT,
                         reply_to_message_id=message_id)
        return

    full_name, juz = nama_dan_juz[1].split(' juz ')
    full_name.strip()
    juz.strip()
    if len(full_name) <= 0 or len(juz) <= 2:
        bot.send_message(chat_id=chat_id,
                         text=WRONG_SETORAN_FORMAT,
                         reply_to_message_id=message_id)
        return

    # check A or B
    juz_number, part = juz.strip().split()
    if (len(juz_number) <= 0) or (part != 'a' and part != 'b'):
        bot.send_message(chat_id=chat_id,
                         text=WRONG_SETORAN_FORMAT,
                         reply_to_message_id=message_id)
        return

    try:
        juz_number = int(juz_number)
    except ValueError:
        bot.send_message(chat_id=chat_id,
                         text=WRONG_SETORAN_FORMAT,
                         reply_to_message_id=message_id)
        return

    participant_id = get_participant_id_from_name(full_name)
    if participant_id is None:
        bot.send_message(chat_id=chat_id,
                         text=f'Anggota bernama {full_name} belum terdaftar. Daftar dahulu sebelum setoran.',
                         reply_to_message_id=message_id)
        return

    is_success = add_setoran(participant_id, juz_number, part)

    if not is_success:
        bot.send_message(chat_id=chat_id,
                         text='❌ Nomor juz salah.',
                         reply_to_message_id=message_id)
        return

    # increase half juz completed count
    increase_half_juz_count(participant_id)

    bot.send_message(chat_id=chat_id,
                     text='✅ Setoran telah dicatat.',
                     reply_to_message_id=message_id)
