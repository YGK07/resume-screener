import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "resume_data.db"
)


def initialize_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resume_results(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        candidate TEXT,

        score REAL,

        semantic_score REAL,

        skill_score REAL,

        experience INTEGER,

        projects INTEGER,

        education_score INTEGER,

        certification_score INTEGER,

        matched_skills TEXT,

        missing_skills TEXT,

        analyzed_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()
    conn.close()


def save_result(result):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO resume_results(

        candidate,

        score,

        semantic_score,

        skill_score,

        experience,

        projects,

        education_score,

        certification_score,

        matched_skills,

        missing_skills

    )

    VALUES(?,?,?,?,?,?,?,?,?,?)

    """,

    (

        result["name"],

        result["score"],

        result["semantic_score"],

        result["skill_score"],

        result["experience"],

        result["projects"],

        result["education_score"],

        result["certification_score"],

        ",".join(result["matched"]),

        ",".join(result["missing"])

    )

    )

    conn.commit()

    conn.close()


def load_history(
    search="",
    min_score=0,
    min_experience=0
):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM resume_results

        WHERE candidate LIKE ?
        AND score >= ?
        AND experience >= ?

        ORDER BY analyzed_on DESC
        """,

        (
            f"%{search}%",
            min_score,
            min_experience
        )
    )

    rows = cursor.fetchall()

    conn.close()

    return rows