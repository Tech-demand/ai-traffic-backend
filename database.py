import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable not set! .env file check karo.")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def setup_tables():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TrafficData (
            id      SERIAL PRIMARY KEY,
            step_no INTEGER,
            EB0     INTEGER,
            EB1     INTEGER,
            EB2     INTEGER,
            SB0     INTEGER,
            SB1     INTEGER,
            SB2     INTEGER,
            phase   INTEGER,
            reward  FLOAT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS QTable (
            id         SERIAL PRIMARY KEY,
            state      TEXT NOT NULL UNIQUE,
            action_0   FLOAT NOT NULL,
            action_1   FLOAT NOT NULL,
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


# Tables setup karo on import
setup_tables()


def insert_data(step_no, EB0, EB1, EB2, SB0, SB1, SB2, phase, reward):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO TrafficData
        (step_no, EB0, EB1, EB2, SB0, SB1, SB2, phase, reward)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (step_no, EB0, EB1, EB2, SB0, SB1, SB2, phase, reward)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_latest():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TrafficData ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_history(n=100):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM (SELECT * FROM TrafficData ORDER BY id DESC LIMIT %s) sub ORDER BY id ASC",
        (n,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return list(rows)


def save_q_table(q_table):
    conn = get_conn()
    cursor = conn.cursor()
    for state, qvals in q_table.items():
        state_str = str(state)
        a0 = float(qvals[0])
        a1 = float(qvals[1])
        cursor.execute("""
            INSERT INTO QTable (state, action_0, action_1, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (state)
            DO UPDATE SET action_0 = EXCLUDED.action_0,
                          action_1 = EXCLUDED.action_1,
                          updated_at = NOW()
        """, (state_str, a0, a1))
    conn.commit()
    cursor.close()
    conn.close()


def get_q_table():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT state, action_0, action_1 FROM QTable ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows