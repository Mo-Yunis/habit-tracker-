from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QProgressBar, 
    QPushButton, QVBoxLayout, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QMouseEvent

from core.database import update_progress, delete_habit, get_stats

class CheckCircle(QFrame):
    toggled = pyqtSignal(bool)
    
    def __init__(self, checked=False, is_past=False, is_locked=False, is_pre_creation=False):
        super().__init__()
        self.setFixedSize(14, 14)
        self.checked = checked
        self.is_past = is_past
        self.is_locked = is_locked
        self.is_pre_creation = is_pre_creation
        self.update_style()
        
    def update_style(self):
        if self.checked:
            bg = "#50fa7b"
            border = "#50fa7b"
        else:
            if self.is_pre_creation:
                bg = "#383a59"
                border = "#44475a"
            elif self.is_past:
                bg = "#ff5555"
                border = "#ff5555"
            else:
                bg = "#282a36"
                border = "#6272a4"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 7px;
            }}
            QFrame:hover {{
                border: 1px solid #bd93f9;
            }}
        """)

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_pre_creation:
            return
            
        if self.is_past:
            return
            
        if self.is_locked and not self.checked:
            return
            
        if event.button() == Qt.LeftButton:
            self.checked = not self.checked
            self.update_style()
            self.toggled.emit(self.checked)


class DayWidget(QFrame):
    clicked = pyqtSignal(int, int) # day, new_value

    def __init__(self, day, current_val, target_val, is_past=False, is_locked=False, is_pre_creation=False):
        super().__init__()
        self.day = day
        self.val = current_val
        self.target = target_val
        self.is_past = is_past
        self.is_locked = is_locked
        self.is_pre_creation = is_pre_creation
        
        self.setStyleSheet("""
            QFrame {
                background-color: #44475a;
                border-radius: 6px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        lbl = QLabel(str(day))
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color: #f8f8f2; font-size: 10px; font-weight: bold;")
        layout.addWidget(lbl)
        
        # Add checks
        self.checks = []
        checks_layout = QHBoxLayout()
        checks_layout.setContentsMargins(0, 0, 0, 0)
        checks_layout.setSpacing(2)
        
        for i in range(self.target):
            c = CheckCircle(checked=(i < self.val), is_past=self.is_past, is_locked=self.is_locked, is_pre_creation=self.is_pre_creation)
            c.toggled.connect(self.on_check_toggled)
            checks_layout.addWidget(c)
            self.checks.append(c)
            
        checks_layout.addStretch()
        layout.addLayout(checks_layout)
        
    def on_check_toggled(self, state):
        # Recalculate val
        self.val = sum(1 for c in self.checks if c.checked)
        self.clicked.emit(self.day, self.val)


class HabitRow(QFrame):
    data_changed = pyqtSignal()
    habit_deleted = pyqtSignal()

    def __init__(self, habit, view_mode="Month"):
        super().__init__()
        self.habit = habit
        self.view_mode = view_mode

        self.setStyleSheet("""
        HabitRow {
            background-color: #383a59;
            border-radius: 12px;
        }
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)

        # --- HEADER ---
        top = QHBoxLayout()

        title_text = f"{habit['name']} "
        if habit["type"] == "daily":
            title_text += f"<span style='color:#6272a4; font-size:12px;'>(Daily Goal: {habit['daily_target']})</span>"
        else:
            title_text += f"<span style='color:#6272a4; font-size:12px;'>(Monthly Target: {habit['total_target']} | Daily ~{habit['daily_target']})</span>"

        self.name_lbl = QLabel(title_text)
        self.name_lbl.setTextFormat(Qt.RichText)
        self.name_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #f8f8f2;")

        self.delete_btn = QPushButton("✕")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setStyleSheet("""
            QPushButton { background-color: #ff5555; border-radius: 15px; color: white; border: none; font-weight: bold;}
            QPushButton:hover { background-color: #ff6e6e; }
        """)
        self.delete_btn.clicked.connect(self.delete)

        top.addWidget(self.name_lbl)
        top.addStretch()
        top.addWidget(self.delete_btn)

        self.layout.addLayout(top)

        # --- PROGRESS BAR ---
        self.progress = QProgressBar()
        self.progress.setFixedHeight(12)
        self.layout.addWidget(self.progress)

        # --- DAYS GRID ---
        days_layout = QGridLayout()
        days_layout.setSpacing(6)
        
        from datetime import datetime
        now = datetime.now()
        is_past_month = (habit["year"] < now.year) or (habit["year"] == now.year and habit["month"] < now.month)
        is_current_month = (habit["year"] == now.year and habit["month"] == now.month)
        current_day = now.day
        
        percent, _, _ = get_stats(habit)
        is_completed = (percent >= 100)
        
        row = 0
        col = 0
        for day, val in habit["logs"]:
            if self.view_mode == "Today" and (not is_current_month or day != current_day):
                continue
                
            is_past = is_past_month or (is_current_month and day < current_day)
            is_pre_creation = (day < habit.get("created_day", 1))
            
            dw = DayWidget(day, val, habit["daily_target"], is_past=is_past, is_locked=is_completed, is_pre_creation=is_pre_creation)
            dw.clicked.connect(self.on_day_clicked)
            days_layout.addWidget(dw, row, col)
            col += 1
            if col > 7: # 8 items per row to make space for wider day widgets
                col = 0
                row += 1

        self.layout.addLayout(days_layout)

        # FADE IN
        self.opacity = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity)

        self.fade = QPropertyAnimation(self.opacity, b"opacity")
        self.fade.setDuration(500)
        self.fade.setStartValue(0)
        self.fade.setEndValue(1)
        self.fade.start()

        self.update_progress_bar()

    def on_day_clicked(self, day, new_val):
        update_progress(self.habit["id"], day, new_val)
        
        # Update local logs so we don't have to fetch from DB immediately
        for i, (d, v) in enumerate(self.habit["logs"]):
            if d == day:
                self.habit["logs"][i] = (d, new_val)
                break
                
        self.update_progress_bar()
        self.data_changed.emit()

    def update_progress_bar(self):
        percent, streak, total_reps = get_stats(self.habit)
        
        self.anim = QPropertyAnimation(self.progress, b"value")
        self.anim.setDuration(600)
        self.anim.setStartValue(self.progress.value())
        self.anim.setEndValue(percent)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()
        
        self.progress.setFormat(f"{percent}% | 🔥 Streak: {streak} | 🎯 Reps: {total_reps}")
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #282a36;
                border-radius: 6px;
                text-align: center;
                color: #f8f8f2;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #bd93f9, stop:1 #ff79c6);
                border-radius: 6px;
            }
        """)

    def delete(self):
        delete_habit(self.habit["id"])
        self.habit_deleted.emit()