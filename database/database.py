import datetime
import os
from urllib.parse import urlparse

import psycopg2


def get_connection():
    db_url = os.environ['DATABASE_URL']
    parsed_url = urlparse(db_url)
    user = parsed_url.username
    password = parsed_url.password
    host = parsed_url.hostname
    port = parsed_url.port
    database = parsed_url.path[1:]

    return psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database)


def get_participant(full_name: str) -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT full_name, half_juz_completed, latest_juz_no, latest_juz_part, khatam
        FROM participant
        WHERE full_name = %s
    """
    cursor.execute(query, (full_name,))
    result = cursor.fetchone()

    if result is None:
        return {}

    return {
        'full_name': result[0],
        'half_juz_completed': result[1],
        'latest_juz_no': result[2],
        'latest_juz_part': result[3],
        'khatam': result[4],
    }


def get_participants() -> list:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT id, full_name, half_juz_completed, latest_juz_no, latest_juz_part, khatam
        FROM participant ORDER BY half_juz_completed DESC
    """
    cursor.execute(query)
    result = cursor.fetchall()

    participants = []
    for row in result:
        participants.append({
            'id': row[0],
            'full_name': row[1],
            'half_juz_completed': int(row[2]),
            'latest_juz_no': int(row[3]),
            'latest_juz_part': row[4],
            'khatam': int(row[5]),
        })

    return participants


def get_participant_id_from_name(full_name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    query = """SELECT id FROM participant WHERE full_name = %s"""
    cursor.execute(query, (full_name.lower(),))
    result = cursor.fetchone()

    return result


def get_latest_setoran(participant_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT latest_juz_no, latest_juz_part FROM participant WHERE id = %s LIMIT 1
    """
    cursor.execute(query, (participant_id,))
    result = cursor.fetchone()

    return result[0], result[1]


def add_participant(full_name: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO participant (full_name) VALUES (%s)
    """
    try:
        cursor.execute(insert_query, (full_name,))
        conn.commit()
        row_count = cursor.rowcount

        return row_count
    except psycopg2.errors.UniqueViolation:
        return -1


def add_setoran(participant_id: int, juz_no: int, juz_part: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    iso_datetime_now = str(datetime.datetime.now())

    insert_query = """
        INSERT INTO setoran(participant_id, juz_no, juz_part, setoran_date)
        VALUES (%s, %s, %s, %s)
    """
    insert_parameters = (participant_id, juz_no, juz_part, iso_datetime_now)

    cursor.execute(insert_query, insert_parameters)
    conn.commit()
    count = cursor.rowcount
    print(count, " Setoran succesfully inserted")

    return count > 0


def update_participant_latest_setoran(participant_id: int, juz_no: int, juz_part: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        UPDATE participant SET
            half_juz_completed = half_juz_completed + 1,
            latest_juz_no = %s,
            latest_juz_part = %s
        WHERE id = %s
    """
    cursor.execute(query, (juz_no, juz_part, participant_id))
    conn.commit()
    updated_count = cursor.rowcount

    return updated_count


def increase_khatam(participant_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        UPDATE participant SET
            khatam = khatam + 1
        WHERE id = %s
    """
    cursor.execute(query, (participant_id,))
    conn.commit()
    updated_count = cursor.rowcount
    return updated_count
