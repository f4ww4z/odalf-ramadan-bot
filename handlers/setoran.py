from database.database import get_participant_id_from_name, add_setoran, \
    update_participant_latest_setoran, get_latest_setoran, increase_khatam

WRONG_SETORAN_FORMAT: str = '❌ Format setoran salah. Yang benar:\n\n' \
                            'odalf lapor <nama penuh> juz <1-30> <A-B>\n' \
                            'Contoh: odalf lapor fawwaz juz 1 A'


def validate_setoran(message_string: str) -> str:
    try:
        nama_dan_juz = message_string.split('odalf lapor ')
        full_name, juz = nama_dan_juz[1].split(' juz ')
        full_name = full_name.strip()
        juz = juz.strip()
        juz_no, juz_part = juz.split()
        juz_no = int(juz_no)

        participant_id = get_participant_id_from_name(full_name)
        if participant_id is None:
            return f'Anggota bernama {full_name} belum terdaftar. Daftar dahulu sebelum setoran.'

        # check latest setoran first
        latest_juz_no, latest_juz_part = get_latest_setoran(participant_id)
        allowed_juz_no, allowed_juz_part = calculate_next_setoran(latest_juz_no,
                                                                  latest_juz_part)
        if latest_juz_no == 0 and latest_juz_part == 'a':
            # first time setoran
            return perform_setoran(participant_id, juz_no, juz_part)

        if juz_no != allowed_juz_no or juz_part != allowed_juz_part:
            return f'❌ Nomor juz salah. Seharusnya juz {allowed_juz_no} {allowed_juz_part.upper()}'

        return perform_setoran(participant_id, juz_no, juz_part)

    except Exception as e:
        print(e)
        return WRONG_SETORAN_FORMAT


def perform_setoran(participant_id: int, juz_no: int, juz_part) -> str:
    is_success = add_setoran(participant_id, juz_no, juz_part)

    if not is_success:
        return WRONG_SETORAN_FORMAT

    # increase half juz completed count
    update_participant_latest_setoran(participant_id, juz_no, juz_part)

    # if juz is 30 B, increase khatam count
    if juz_no == 30 and juz_part == 'b':
        increase_khatam(participant_id)

        return '✅ Setoran telah dicatat. Barakallah, anda baru khatam!'

    return '✅ Setoran telah dicatat.'


def calculate_next_setoran(latest_juz_no, latest_juz_part):
    allowed_juz_no = latest_juz_no if latest_juz_part == 'a' else (latest_juz_no + 1) % 30
    if allowed_juz_no == 0:
        allowed_juz_no = 30
    return allowed_juz_no, 'b' if latest_juz_part == 'a' else 'a'
