from telegram import Bot, ParseMode

from database.database import get_participants, get_latest_setoran


def display_setoran(bot: Bot, chat_id):
    participants = get_participants()

    final_text = """o  ⁠⁠⁠بِسْـــــــــمِ اللهِ الرَّحْمَٰنِ الرَّحِيْمِ    o
    *LAPORAN KHATAM QUR'AN RAMADHAN 1441H*
    
    """
    for i in range(len(participants)):
        id = participants[i][0]
        full_name = participants[i][1].capitalize()
        completed_half_juz = participants[i][2]

        juz_no, juz_part = get_latest_setoran(id)

        final_text += f"""{i + 1}. {full_name} """

        if juz_no > 0:
            final_text += f"""Juz {juz_no} {juz_part.upper()}"""

        final_text += f"""\nTotal kholas: {completed_half_juz}\n\n"""

    bot.send_message(chat_id=chat_id, text=final_text, parse_mode=ParseMode.MARKDOWN_V2)
