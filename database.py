from datetime import datetime
import mysql.connector
import uuid

DB_CONFIG = {
    "host": "localhost",
    "user": "rohan",                  # replace with your MySQL username
    "password": "Advaitha@123",       # replace with your MySQL password
    "database": "meeting_app"          # make sure this DB exists
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def save_meeting(
    filename,
    transcript,
    summary,
    key_points=None,
    action_points=None,
    meeting_date=None,
    start_time=None,
    end_time=None
):
    meeting_id = str(uuid.uuid4())

    # Default timestamps if not provided
    now = datetime.now()
    meeting_date = meeting_date or now.date()
    start_time = start_time or now.time().strftime("%H:%M:%S")
    end_time = end_time or now.time().strftime("%H:%M:%S")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO meetings 
        (id, filename, transcript, summary, key_points, action_points, meeting_date, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        meeting_id,
        filename,
        transcript,
        summary,
        "\n".join(key_points) if key_points else "No more points mentioned.",
        "\n".join(action_points) if action_points else "No more points mentioned.",
        meeting_date,
        start_time,
        end_time
    ))
    conn.commit()
    cur.close()
    conn.close()
    return meeting_id

def get_all_meetings():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, filename, summary, key_points, action_points, meeting_date, start_time, end_time
        FROM meetings
        ORDER BY meeting_date DESC, start_time DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0],
            "filename": r[1],
            "summary": r[2],
            "key_points": r[3].split("\n") if r[3] else ["No more points mentioned."],
            "action_points": r[4].split("\n") if r[4] else ["No more points mentioned."],
            "meeting_date": str(r[5]),
            "start_time": str(r[6]),
            "end_time": str(r[7])
        } for r in rows
    ]

def get_meeting_by_id(meeting_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, filename, transcript, summary, key_points, action_points, meeting_date, start_time, end_time
        FROM meetings
        WHERE id = %s
    """, (meeting_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "filename": row[1],
        "transcript": row[2],
        "summary": row[3],
        "key_points": row[4].split("\n") if row[4] else ["No more points mentioned."],
        "action_points": row[5].split("\n") if row[5] else ["No more points mentioned."],
        "meeting_date": str(row[6]),
        "start_time": str(row[7]),
        "end_time": str(row[8])
    }
