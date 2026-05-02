import sqlite3
from datetime import datetime, timedelta
import calendar

DB = "habits.db"

def connect():
    return sqlite3.connect(DB)

def init_db():
    conn = connect()
    c = conn.cursor()

    # Reset DB if old schema exists
    c.execute("DROP TABLE IF EXISTS habits")
    c.execute("DROP TABLE IF EXISTS habit_logs")

    c.execute("""
    CREATE TABLE habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        habit_type TEXT,
        total_target INTEGER,
        daily_target INTEGER,
        start_date TEXT, -- YYYY-MM-DD
        status TEXT DEFAULT 'active'
    )
    """)

    c.execute("""
    CREATE TABLE habit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER,
        log_date TEXT, -- YYYY-MM-DD
        completed INTEGER DEFAULT 0,
        FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

def add_habit(name, habit_type, total_target, daily_target, start_date=None):
    if not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")

    conn = connect()
    c = conn.cursor()

    c.execute("""
        INSERT INTO habits (name, habit_type, total_target, daily_target, start_date)
        VALUES (?, ?, ?, ?, ?)
    """, (name, habit_type, total_target, daily_target, start_date))

    habit_id = c.lastrowid

    # Initial log population
    if habit_type == "daily":
        # For daily habits, populate ALL days of the start month (day 1 to last day)
        # Days before start_date will be shown but locked in the UI
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        days_in_month = calendar.monthrange(start_dt.year, start_dt.month)[1]
        for d in range(1, days_in_month + 1):
            log_date = f"{start_dt.year}-{start_dt.month:02d}-{d:02d}"
            c.execute("INSERT INTO habit_logs (habit_id, log_date) VALUES (?, ?)", (habit_id, log_date))
    else:
        # For total_goal, calculate exactly how many days are needed
        days_needed = (total_target + daily_target - 1) // daily_target
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        for i in range(days_needed):
            log_date = (start_dt + timedelta(days=i)).strftime("%Y-%m-%d")
            c.execute("INSERT INTO habit_logs (habit_id, log_date) VALUES (?, ?)", (habit_id, log_date))

    conn.commit()
    conn.close()
    return habit_id

def get_habits(month, year):
    conn = connect()
    c = conn.cursor()

    # Calculate month boundary
    first_day = f"{year}-{month:02d}-01"
    last_day_num = calendar.monthrange(year, month)[1]
    last_day = f"{year}-{month:02d}-{last_day_num:02d}"
    month_str = f"{year}-{month:02d}%"

    # 1. Find ALL active daily habits (regardless of start_date vs this month)
    #    and total habits that started before or during this month
    c.execute("""
        SELECT * FROM habits
        WHERE status = 'active'
    """)

    habits = c.fetchall()

    # 2. For each habit, ensure logs exist for this month if it's daily
    for h in habits:
        h_id, name, h_type, total_target, daily_target, start_date, status = h
        if h_type == "daily":
            # Check if logs exist for this month
            c.execute("SELECT COUNT(*) FROM habit_logs WHERE habit_id=? AND log_date LIKE ?", (h_id, month_str))
            if c.fetchone()[0] == 0:
                # Create logs for ALL days of this month (locked state is handled in UI)
                for d in range(1, last_day_num + 1):
                    log_date = f"{year}-{month:02d}-{d:02d}"
                    c.execute("INSERT OR IGNORE INTO habit_logs (habit_id, log_date) VALUES (?, ?)", (h_id, log_date))
                conn.commit()

    # 3. Now fetch the habits again but only those that have logs in this month
    c.execute("""
        SELECT DISTINCT h.* FROM habits h
        JOIN habit_logs l ON h.id = l.habit_id
        WHERE l.log_date LIKE ?
    """, (month_str,))

    habits = c.fetchall()
    result = []

    for h in habits:
        h_id, name, h_type, total_target, daily_target, start_date, status = h

        c.execute("""
            SELECT log_date, completed FROM habit_logs
            WHERE habit_id=? AND log_date LIKE ?
            ORDER BY log_date
        """, (h_id, month_str))

        logs = c.fetchall()

        ui_logs = []
        for log_date, completed in logs:
            day = int(log_date.split("-")[2])
            ui_logs.append((day, completed, log_date))

        result.append({
            "id": h_id,
            "name": name,
            "type": h_type,
            "total_target": total_target,
            "daily_target": daily_target,
            "start_date": start_date,
            "status": status,
            "logs": ui_logs
        })

    conn.close()
    return result

def update_progress(habit_id, log_date, new_value):
    conn = connect()
    c = conn.cursor()

    c.execute("""
    UPDATE habit_logs
    SET completed=?
    WHERE habit_id=? AND log_date=?
    """, (new_value, habit_id, log_date))

    conn.commit()
    conn.close()

    # After update, we might need to "overflow"
    check_and_overflow(habit_id)

def check_and_overflow(habit_id):
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT habit_type, total_target, daily_target FROM habits WHERE id=?", (habit_id,))
    h = c.fetchone()
    if not h or h[0] == "daily":
        conn.close()
        return

    h_type, total_target, daily_target = h

    c.execute("SELECT SUM(completed) FROM habit_logs WHERE habit_id=?", (habit_id,))
    total_done = c.fetchone()[0] or 0

    if total_done >= total_target:
        conn.close()
        return

    remaining = total_target - total_done
    days_needed = (remaining + daily_target - 1) // daily_target

    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM habit_logs WHERE habit_id=? AND log_date >= ?", (habit_id, today))
    days_open = c.fetchone()[0]

    if days_open < days_needed:
        c.execute("SELECT MAX(log_date) FROM habit_logs WHERE habit_id=?", (habit_id,))
        last_date_str = c.fetchone()[0]
        last_dt = datetime.strptime(last_date_str, "%Y-%m-%d")

        for i in range(1, days_needed - days_open + 1):
            new_date = (last_dt + timedelta(days=i)).strftime("%Y-%m-%d")
            c.execute("INSERT INTO habit_logs (habit_id, log_date) VALUES (?, ?)", (habit_id, new_date))

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
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT completed FROM habit_logs WHERE habit_id=? ORDER BY log_date", (habit["id"],))
    all_logs = [x[0] for x in c.fetchall()]
    conn.close()

    total_reps = sum(all_logs)
    daily_target = habit["daily_target"]
    total_target = habit["total_target"]

    if habit["type"] == "daily":
        days_met = sum(1 for x in all_logs if x >= daily_target)
        total_days = len(all_logs)
        percent = int((days_met / total_days) * 100) if total_days else 0
    else:
        percent = int((total_reps / total_target) * 100) if total_target else 0
        if percent > 100: percent = 100

    streak = 0
    max_streak = 0
    for v in all_logs:
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
    return {"total_habits": total_habits, "total_completions": total_completions}

def get_full_history():
    """Returns detailed per-habit history for the History page."""
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM habits ORDER BY id DESC")
    habits_raw = c.fetchall()

    today = datetime.now().strftime("%Y-%m-%d")
    result = []

    for h in habits_raw:
        h_id, name, h_type, total_target, daily_target, start_date, status = h

        c.execute(
            "SELECT log_date, completed FROM habit_logs WHERE habit_id=? ORDER BY log_date",
            (h_id,)
        )
        all_logs = c.fetchall()

        total_completions = sum(v for _, v in all_logs)

        # Best streak
        streak = 0
        best_streak = 0
        for _, v in all_logs:
            if v >= daily_target:
                streak += 1
                best_streak = max(best_streak, streak)
            else:
                streak = 0

        # Completion percent
        if h_type == "daily":
            past_logs = [(ld, v) for ld, v in all_logs if ld <= today]
            days_met = sum(1 for _, v in past_logs if v >= daily_target)
            pct = int((days_met / len(past_logs)) * 100) if past_logs else 0
        else:
            pct = int((total_completions / total_target) * 100) if total_target else 0
            if pct > 100: pct = 100

        # Last 30 days heatmap data
        heatmap = {}
        for ld, v in all_logs:
            heatmap[ld] = v

        result.append({
            "id": h_id,
            "name": name,
            "type": h_type,
            "total_target": total_target,
            "daily_target": daily_target,
            "start_date": start_date,
            "status": status,
            "total_completions": total_completions,
            "best_streak": best_streak,
            "percent": pct,
            "heatmap": heatmap,
        })

    conn.close()
    return result
