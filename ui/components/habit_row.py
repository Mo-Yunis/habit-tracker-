from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QVBoxLayout, QFrame, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QMouseEvent

from core.database import update_progress, delete_habit, get_stats


# ── CheckCircle ────────────────────────────────────────────────────────────

class CheckCircle(QFrame):
    toggled = pyqtSignal(bool)

    def __init__(self, checked=False, is_past=False, is_locked=False,
                 is_pre_creation=False, accent="#BD93F9"):
        super().__init__()
        self.setFixedSize(22, 22)
        self.checked        = checked
        self.is_past        = is_past
        self.is_locked      = is_locked
        self.is_pre_creation = is_pre_creation
        self.accent         = accent
        self._apply_style()

    def _apply_style(self):
        if self.checked:
            bg     = "#50FA7B"
            border = "#50FA7B"
        elif self.is_pre_creation:
            bg     = "rgba(80,80,120,0.22)"
            border = "transparent"
        elif self.is_past:
            bg     = "rgba(255,85,85,0.45)"
            border = "#FF5555"
        else:
            bg     = "transparent"
            border = "rgba(148,153,195,0.55)"

        hover = "" if (self.is_pre_creation or self.is_past or self.is_locked) else (
            f"QFrame:hover {{ border: 2px solid {self.accent}; }}"
        )

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 11px;
            }}
            {hover}
        """)

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_pre_creation or self.is_past:
            return
        if self.is_locked and not self.checked:
            return
        if event.button() == Qt.LeftButton:
            self.checked = not self.checked
            self._apply_style()
            self.toggled.emit(self.checked)


# ── DayWidget ──────────────────────────────────────────────────────────────

class DayWidget(QFrame):
    clicked = pyqtSignal(str, int)   # log_date, new_val

    def __init__(self, day, log_date, current_val, target_val,
                 is_past=False, is_locked=False, is_pre_creation=False,
                 accent="#BD93F9"):
        super().__init__()
        self.day            = day
        self.log_date       = log_date
        self.val            = current_val
        self.target         = target_val
        self.is_past        = is_past
        self.is_locked      = is_locked
        self.is_pre_creation = is_pre_creation
        self.accent         = accent

        self.setObjectName("DayCard")

        # Dimmed style for pre-creation days
        if is_pre_creation:
            self.setStyleSheet("""
                QFrame#DayCard {
                    background-color: rgba(50,50,80,0.30);
                    border-radius: 12px;
                    border: 1px solid rgba(100,100,140,0.15);
                }
            """)
        else:
            hover_border = "rgba(255,85,85,0.55)" if is_past else accent
            self.setStyleSheet(f"""
                QFrame#DayCard {{
                    background-color: rgba(40,40,70,0.55);
                    border-radius: 12px;
                    border: 1px solid rgba(148,153,195,0.18);
                }}
                QFrame#DayCard:hover {{
                    background-color: rgba(60,60,95,0.75);
                    border: 1px solid {hover_border};
                }}
            """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(7, 7, 7, 7)
        layout.setSpacing(5)

        # Day number label
        day_color = "#555577" if is_pre_creation else (
            "#FF7070" if is_past else "#F8F8F2"
        )
        lbl = QLabel(str(day))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(
            f"color: {day_color}; font-size: 11px; font-weight: 800; background: transparent;"
        )
        layout.addWidget(lbl)

        # Checkboxes
        self.checks = []
        checks_layout = QHBoxLayout()
        checks_layout.setContentsMargins(0, 0, 0, 0)
        checks_layout.setSpacing(4)
        checks_layout.setAlignment(Qt.AlignCenter)

        for i in range(self.target):
            c = CheckCircle(
                checked=(i < self.val),
                is_past=self.is_past,
                is_locked=self.is_locked,
                is_pre_creation=self.is_pre_creation,
                accent=self.accent
            )
            c.toggled.connect(self._on_check_toggled)
            checks_layout.addWidget(c)
            self.checks.append(c)

        layout.addLayout(checks_layout)

    def _on_check_toggled(self, _):
        self.val = sum(1 for c in self.checks if c.checked)
        self.clicked.emit(self.log_date, self.val)


# ── HabitRow ───────────────────────────────────────────────────────────────

class HabitRow(QFrame):
    data_changed  = pyqtSignal()
    habit_deleted = pyqtSignal()

    def __init__(self, habit, view_mode="Month"):
        super().__init__()
        self.habit     = habit
        self.view_mode = view_mode
        self.setObjectName("Card")

        # Lightweight shadow (reduced blur for performance)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 55))
        self.setGraphicsEffect(shadow)

        # Cache stats once (avoids duplicate DB hit inside __init__)
        self._percent, self._streak, self._total_reps = get_stats(habit)
        is_completed = (self._percent >= 100)
        accent = habit.get("accent", "#BD93F9")

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(10)

        # ── HEADER ────────────────────────────────────────────────────────
        top = QHBoxLayout()

        name_lbl = QLabel(habit["name"])
        name_lbl.setStyleSheet(
            "font-size: 20px; font-weight: 800; color: #F8F8F2; background: transparent;"
        )

        sub_text = (
            f"Daily Goal: {habit['daily_target']}" if habit["type"] == "daily"
            else f"Target: {habit['total_target']} Reps"
        )
        sub_lbl = QLabel(sub_text)
        sub_lbl.setStyleSheet(
            "font-size: 12px; color: #9499C3; font-weight: 500; background: transparent;"
        )

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(30, 30)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,85,85,0.10);
                border-radius: 15px;
                color: #FF5555;
                border: 1px solid rgba(255,85,85,0.28);
                font-weight: 900; font-size: 13px;
            }
            QPushButton:hover {
                background: #FF5555;
                color: white;
            }
        """)
        del_btn.clicked.connect(self._delete)

        hdr_col = QVBoxLayout()
        hdr_col.setSpacing(2)
        hdr_col.addWidget(name_lbl)
        hdr_col.addWidget(sub_lbl)

        top.addLayout(hdr_col)
        top.addStretch()
        top.addWidget(del_btn)
        root.addLayout(top)

        # ── STATS + PROGRESS ──────────────────────────────────────────────
        self.stats_lbl = QLabel()
        self.stats_lbl.setStyleSheet(
            "font-size: 11px; color: #BD93F9; font-weight: 700; "
            "margin-bottom: -4px; background: transparent;"
        )
        root.addWidget(self.stats_lbl)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(10)
        self.progress.setTextVisible(False)
        root.addWidget(self.progress)

        root.addSpacing(8)

        # ── DAYS GRID ─────────────────────────────────────────────────────
        days_container = QWidget()
        days_container.setStyleSheet("background: transparent;")
        days_layout = QGridLayout(days_container)
        days_layout.setContentsMargins(0, 0, 0, 0)
        days_layout.setSpacing(8)

        from datetime import datetime
        today_str = datetime.now().strftime("%Y-%m-%d")
        habit_start = habit.get("start_date", "")

        row_i = 0
        col_i = 0
        for day, val, log_date in habit["logs"]:
            if self.view_mode == "Today" and log_date != today_str:
                continue

            is_pre_creation = bool(habit_start and log_date < habit_start)
            is_past         = (not is_pre_creation) and (log_date < today_str)

            dw = DayWidget(
                day, log_date, val, habit["daily_target"],
                is_past=is_past,
                is_locked=is_completed,
                is_pre_creation=is_pre_creation,
                accent=accent
            )
            dw.clicked.connect(self._on_day_clicked)
            days_layout.addWidget(dw, row_i, col_i)
            col_i += 1
            if col_i > 7:
                col_i = 0
                row_i += 1

        root.addWidget(days_container)

        # ── FADE IN ───────────────────────────────────────────────────────
        eff = QGraphicsOpacityEffect()
        self.setGraphicsEffect(eff)
        self._fade = QPropertyAnimation(eff, b"opacity")
        self._fade.setDuration(380)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.OutCubic)
        self._fade.start()

        self._update_progress_bar()

    # ── slots ──────────────────────────────────────────────────────────────

    def _on_day_clicked(self, log_date: str, new_val: int):
        update_progress(self.habit["id"], log_date, new_val)
        for i, (d, v, ld) in enumerate(self.habit["logs"]):
            if ld == log_date:
                self.habit["logs"][i] = (d, new_val, ld)
                break
        self._update_progress_bar()
        self.data_changed.emit()

    def _update_progress_bar(self):
        percent, streak, total_reps = get_stats(self.habit)
        self._percent    = percent
        self._streak     = streak
        self._total_reps = total_reps

        self._anim = QPropertyAnimation(self.progress, b"value")
        self._anim.setDuration(700)
        self._anim.setStartValue(self.progress.value())
        self._anim.setEndValue(percent)
        self._anim.setEasingCurve(QEasingCurve.OutExpo)
        self._anim.start()

        self.stats_lbl.setText(
            f"{percent}% Complete  •  🔥 {streak}-day streak  •  Total: {total_reps}"
        )
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(50,50,90,0.50);
                border-radius: 5px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #BD93F9, stop:1 #FF79C6
                );
                border-radius: 5px;
            }
        """)

    def _delete(self):
        delete_habit(self.habit["id"])
        self.habit_deleted.emit()