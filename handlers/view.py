from database.database import get_participants, get_latest_setoran


def display_setoran(bot, chat_id):
    participants = get_participants()
    text = ""
    for i in range(len(participants)):
        id = participants[i][0]
        full_name = participants[i][1].capitalize()
        completed_half_juz = participants[i][2]

        juz_no, juz_part = get_latest_setoran(id)

        text += f"""{i + 1}. {full_name} """

        if juz_no > 0:
            text += f"""Juz {juz_no} {juz_part.upper()}"""

        text += f"""\nTotal kholas: {completed_half_juz}\n\n"""

    bot.send_message(chat_id=chat_id, text=text)
