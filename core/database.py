import sqlite3
import calendar

DB = "habits.db"


def connect():
    return sqlite3.connect(DB)


def init_db():
    conn = connect()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        month INTEGER,
        year INTEGER,
        habit_type TEXT,
        total_target INTEGER,
        daily_target INTEGER
    )
    """)

    try:
        c.execute("ALTER TABLE habits ADD COLUMN created_day INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass

    c.execute("""
    CREATE TABLE IF NOT EXISTS habit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER,
        day INTEGER,
        completed INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


def get_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def add_habit(name, month, year, habit_type, total_target, daily_target, created_day=1):
    conn = connect()
    c = conn.cursor()

    c.execute("""
        INSERT INTO habits (name, month, year, habit_type, total_target, daily_target, created_day)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, month, year, habit_type, total_target, daily_target, created_day))

    habit_id = c.lastrowid
    days = get_days_in_month(year, month)

    for d in range(1, days + 1):
        c.execute("INSERT INTO habit_logs (habit_id, day) VALUES (?, ?)", (habit_id, d))

    conn.commit()
    conn.close()


def get_habits(month, year):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM habits WHERE month=? AND year=?", (month, year))
    habits = c.fetchall()

    result = []

    for h in habits:
        h_id = h[0]
        name = h[1]
        h_month = h[2]
        h_year = h[3]
        habit_type = h[4]
        total_target = h[5]
        daily_target = h[6]
        created_day = h[7] if len(h) > 7 else 1

        c.execute("SELECT day, completed FROM habit_logs WHERE habit_id=? ORDER BY day", (h_id,))
        logs = c.fetchall()

        result.append({
            "id": h_id,
            "name": name,
            "month": h_month,
            "year": h_year,
            "type": habit_type,
            "total_target": total_target,
            "daily_target": daily_target,
            "created_day": created_day,
            "logs": logs
        })

    conn.close()
    return result


def update_progress(habit_id, day, new_value):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE habit_logs
    SET completed=?
    WHERE habit_id=? AND day=?
    """, (new_value, habit_id, day))

    conn.commit()
    conn.close()


def delete_habit(habit_id):
    conn = connect()
    c = conn.cursor()

    c.execute("DELETE FROM habits WHERE id=?", (habit_id,))
    c.execute("DELETE FROM habit_logs WHERE habit_id=?", (habit_id,))

    conn.commit()
    conn.close()


def get_stats(habit):
    logs = habit["logs"]
    daily_target = habit["daily_target"]
    total_target = habit["total_target"]
    habit_type = habit["type"]

    total_days = len(logs)
    total_reps = sum(x[1] for x in logs)
    
    if habit_type == "daily":
        # Progress based on days completed
        days_met_target = sum(1 for x in logs if x[1] >= daily_target)
        percent = int((days_met_target / total_days) * 100) if total_days else 0
    else:
        # Progress based on total items completed vs total items target
        percent = int((total_reps / total_target) * 100) if total_target else 0
        if percent > 100:
            percent = 100

    streak = 0
    max_streak = 0

    for _, v in logs:
        if v >= daily_target:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    return percent, max_streak, total_reps


def get_all_time_stats():
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT COUNT(id) FROM habits")
    total_habits = c.fetchone()[0]

    c.execute("SELECT SUM(completed) FROM habit_logs")
    total_completions = c.fetchone()[0] or 0

    conn.close()

    return {
        "total_habits": total_habits,
        "total_completions": total_completions,
    }
