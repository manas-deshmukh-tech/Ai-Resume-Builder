"""
Database layer - SQLite with pure Python sqlite3
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "resumes.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS resumes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            email       TEXT,
            data        TEXT NOT NULL,
            ats_score   REAL DEFAULT 0,
            template    TEXT DEFAULT 'modern_blue',
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS ats_reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id   INTEGER REFERENCES resumes(id) ON DELETE CASCADE,
            report      TEXT NOT NULL,
            created_at  TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def save_resume(data_dict, ats_score=0, template="modern_blue"):
    conn = get_conn()
    c = conn.cursor()
    personal = data_dict.get("personal", {})
    now = datetime.now().isoformat()
    c.execute("""
        INSERT INTO resumes (name, email, data, ats_score, template, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        personal.get("name", "Unknown"),
        personal.get("email", ""),
        json.dumps(data_dict),
        ats_score,
        template,
        now, now
    ))
    resume_id = c.lastrowid
    conn.commit()
    conn.close()
    return resume_id

def update_resume(resume_id, data_dict, ats_score=0, template="modern_blue"):
    conn = get_conn()
    c = conn.cursor()
    personal = data_dict.get("personal", {})
    now = datetime.now().isoformat()
    c.execute("""
        UPDATE resumes SET name=?, email=?, data=?, ats_score=?, template=?, updated_at=?
        WHERE id=?
    """, (
        personal.get("name", "Unknown"),
        personal.get("email", ""),
        json.dumps(data_dict),
        ats_score,
        template,
        now, resume_id
    ))
    conn.commit()
    conn.close()

def get_resume(resume_id):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT * FROM resumes WHERE id=?", (resume_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["data"] = json.loads(d["data"])
        return d
    return None

def get_all_resumes():
    conn = get_conn()
    c = conn.cursor()
    rows = c.execute("SELECT id, name, email, ats_score, template, created_at FROM resumes ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_resume(resume_id):
    conn = get_conn()
    conn.execute("DELETE FROM resumes WHERE id=?", (resume_id,))
    conn.commit()
    conn.close()

def save_ats_report(resume_id, report_dict):
    conn = get_conn()
    now = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO ats_reports (resume_id, report, created_at)
        VALUES (?, ?, ?)
    """, (resume_id, json.dumps(report_dict), now))
    conn.commit()
    conn.close()

def get_ats_report(resume_id):
    conn = get_conn()
    row = conn.execute("""
        SELECT report FROM ats_reports WHERE resume_id=?
        ORDER BY created_at DESC LIMIT 1
    """, (resume_id,)).fetchone()
    conn.close()
    if row:
        return json.loads(row["report"])
    return None
