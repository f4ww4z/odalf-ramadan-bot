from database.database import get_participant_id_from_name, add_setoran, \
    update_participant_latest_setoran, get_latest_setoran, increase_khatam

WRONG_SETORAN_FORMAT: str = '❌ Format setoran salah. Yang benar:\n\n' \
                            'odalf lapor <nama penuh> juz <1-30> <A-B>\n' \
                            'Contoh: odalf lapor fawwaz juz 1 A'


def perform_setoran(message_string: str, bot, chat_id, message_id):
    reply = ''
    try:
        nama_dan_juz = message_string.split('odalf lapor ')
        full_name, juz = nama_dan_juz[1].split(' juz ')
        full_name = full_name.strip()
        juz = juz.strip()
        juz_no, juz_part = juz.split()
        juz_no = int(juz_no)

        participant_id = get_participant_id_from_name(full_name)
        if participant_id is None:
            reply = f'Anggota bernama {full_name} belum terdaftar. Daftar dahulu sebelum setoran.'
        else:
            # check latest setoran first
            latest_juz_no, latest_juz_part = get_latest_setoran(participant_id)
            allowed_juz_no, allowed_juz_part = calculate_next_setoran(latest_juz_no,
                                                                      latest_juz_part)
            if juz_no not in (0, allowed_juz_no) or \
                    juz_part != allowed_juz_part:
                reply = f'❌ Nomor juz salah. Seharusnya juz {allowed_juz_no} {allowed_juz_part.upper()}'
            else:
                is_success = add_setoran(participant_id, juz_no, juz_part)

                if not is_success:
                    reply = WRONG_SETORAN_FORMAT
                else:
                    # increase half juz completed count
                    update_participant_latest_setoran(participant_id, juz_no, juz_part)

                    reply = '✅ Setoran telah dicatat.'

                    # if juz is 30 B, increase khatam count
                    if juz_no == 30 and juz_part == 'b':
                        increase_khatam(participant_id)

                        reply = '✅ Setoran telah dicatat. Barakallah, anda baru khatam!'

    except Exception as e:
        print(e)
        reply = WRONG_SETORAN_FORMAT

    bot.send_message(chat_id=chat_id,
                     text=reply,
                     reply_to_message_id=message_id)


def calculate_next_setoran(latest_juz_no, latest_juz_part):
    allowed_juz_no = latest_juz_no if latest_juz_part == 'a' else (latest_juz_no + 1) % 30
    return allowed_juz_no, 'b' if latest_juz_part == 'a' else 'a'
