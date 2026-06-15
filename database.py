import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Local SSMS ya Railway PostgreSQL — env variable se decide hoga
DATABASE_URL = os.environ.get("DATABASE_URL")

# ----------------------------------------
# Agar DATABASE_URL hai toh PostgreSQL
# Nahi hai toh local SQL Server (SSMS)
# ----------------------------------------
USE_POSTGRES = DATABASE_URL is not None


def get_conn():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL)
    else:
        import pyodbc
        return pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=LETS_GROW\\MSSQLSERVER2025;"
            "DATABASE=TrafficDB;"
            "Trusted_Connection=yes;",
            autocommit=True
        )


def setup_tables():
    """Railway pe pehli baar tables banao"""
    if not USE_POSTGRES:
        return
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
        """ if USE_POSTGRES else """
        INSERT INTO TrafficData
        (step_no, EB0, EB1, EB2, SB0, SB1, SB2, phase, reward)
        VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (step_no, EB0, EB1, EB2, SB0, SB1, SB2, phase, reward)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_latest():
    conn = get_conn()
    cursor = conn.cursor()
    if USE_POSTGRES:
        cursor.execute("SELECT * FROM TrafficData ORDER BY id DESC LIMIT 1")
    else:
        cursor.execute("SELECT TOP 1 * FROM TrafficData ORDER BY id DESC")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_history(n=100):
    conn = get_conn()
    cursor = conn.cursor()
    if USE_POSTGRES:
        cursor.execute(
            "SELECT * FROM (SELECT * FROM TrafficData ORDER BY id DESC LIMIT %s) sub ORDER BY id ASC",
            (n,)
        )
    else:
        cursor.execute(
            "SELECT TOP (?) * FROM TrafficData ORDER BY id DESC",
            (n,)
        )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return list(rows) if USE_POSTGRES else list(reversed(rows))


def save_q_table(q_table):
    conn = get_conn()
    cursor = conn.cursor()
    for state, qvals in q_table.items():
        state_str = str(state)
        a0 = float(qvals[0])
        a1 = float(qvals[1])
        if USE_POSTGRES:
            cursor.execute("""
                INSERT INTO QTable (state, action_0, action_1, updated_at)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (state)
                DO UPDATE SET action_0 = EXCLUDED.action_0,
                              action_1 = EXCLUDED.action_1,
                              updated_at = NOW()
            """, (state_str, a0, a1))
        else:
            cursor.execute("""
                IF EXISTS (SELECT 1 FROM QTable WHERE state = ?)
                    UPDATE QTable SET action_0=?, action_1=?, updated_at=GETDATE() WHERE state=?
                ELSE
                    INSERT INTO QTable (state, action_0, action_1) VALUES (?,?,?)
            """, (state_str, a0, a1, state_str, state_str, a0, a1))
    conn.commit()
    cursor.close()
    conn.close()


def get_q_table():
    conn = get_conn()
    cursor = conn.cursor()
    if USE_POSTGRES:
        cursor.execute("SELECT state, action_0, action_1 FROM QTable ORDER BY updated_at DESC")
    else:
        cursor.execute("SELECT state, action_0, action_1 FROM QTable ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows