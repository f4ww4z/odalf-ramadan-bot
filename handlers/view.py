import datetime as dt
import locale

from hijri_converter import convert as hijri_convert
from telegram import Bot, ParseMode, Chat

from database.database import get_participants, get_participant

locale.setlocale(locale.LC_TIME, 'id_ID')

FOOTER = """
📖 \= Jumlah kholas 1/2 juz
📔 \= Jumlah khatam al\-Qur'an

*Keep istiqomah\!*
Komunitas One Day One Juz Indonesia
"""


def display_group_setoran(bot: Bot, chat: Chat):
    participants = get_participants()
    now = dt.datetime.utcnow() + dt.timedelta(hours=7)
    today_hijri = hijri_convert.Gregorian.fromdate(now.date()).to_hijri()
    masehi_str = now.strftime('%d %B %Y')
    hijri_str = f'{today_hijri.day + 1 if now.time().hour >= 18 else today_hijri.day} {today_hijri.month_name()} {today_hijri.year}H'

    final_text = f"""o  ⁠⁠⁠بِسْـــــــــمِ اللهِ الرَّحْمَٰنِ الرَّحِيْمِ    o

📊📊📊📊📊📊📊📊📊📊
*LAPORAN {chat.title}*

Periode: 
{masehi_str} \/ *{hijri_str}*

"""
    for participant in participants:
        full_name: str = participant['full_name'].capitalize()
        full_name = full_name.replace(".", "\.")
        half_juz_completed = participant['half_juz_completed']
        latest_juz_no = participant['latest_juz_no']
        latest_juz_part = participant['latest_juz_part']
        khatam = participant['khatam']

        # formatting
        khatam = '{:02d}'.format(khatam)
        half_juz_completed = '{:03d}'.format(half_juz_completed)

        final_text += f"📔 {khatam} 📖 {half_juz_completed} \| 👨 {full_name} "

        if latest_juz_no > 0:
            final_text += f"\(Juz {latest_juz_no} {latest_juz_part.upper()}\)"

        final_text += "\n"

    final_text += f"""
\(urutan sesuai jumlah kholas\)

Jumlah member \= {len(participants)} orang
{FOOTER}
"""

    bot.send_message(chat_id=chat.id, text=final_text, parse_mode=ParseMode.MARKDOWN_V2)


def display_individual_setoran(bot: Bot, chat: Chat, message_id, full_name: str):
    p = get_participant(full_name)

    if p == {}:
        reply = f"Tidak ditemukan member bernama _\'{full_name}\'_\."
    else:
        reply = f"""o  ⁠⁠⁠بِسْـــــــــمِ اللهِ الرَّحْمَٰنِ الرَّحِيْمِ    o

*Laporan 👨 {full_name.capitalize()}*

📔 {p['khatam']}
📖 {p['half_juz_completed']}
"""
        if p['latest_juz_no'] > 0:
            reply += f"Terkini: *Juz {p['latest_juz_no']} {p['latest_juz_part'].upper()}*"

    reply += f"\n{FOOTER}"

    bot.send_message(chat_id=chat.id,
                     text=reply,
                     reply_to_message_id=message_id,
                     parse_mode=ParseMode.MARKDOWN_V2)
