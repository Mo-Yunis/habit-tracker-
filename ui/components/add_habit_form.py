from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QStackedWidget, QSpinBox, QPushButton, QFrame, QHBoxLayout
)
from PyQt5.QtCore import pyqtSignal, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class AddHabitForm(QWidget):
    habit_added = pyqtSignal(str, str, int, int)

    def __init__(self, theme_colors):
        super().__init__()
        self.theme_colors = theme_colors
        self._init_ui()

    def _init_ui(self):
        container = QVBoxLayout(self)
        container.setContentsMargins(0, 4, 0, 4)

        # Glass card
        self.card = QFrame()
        self.card.setObjectName("GlassPanel")

        card_lay = QVBoxLayout(self.card)
        card_lay.setContentsMargins(14, 14, 14, 14)
        card_lay.setSpacing(10)

        # Section label
        sec_lbl = QLabel("NEW HABIT")
        sec_lbl.setStyleSheet(
            "font-size: 9px; font-weight: 800; letter-spacing: 1.5px; "
            "color: #9499C3; background: transparent;"
        )
        card_lay.addWidget(sec_lbl)

        # Name field
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Habit name…")
        self.input_name.setFixedHeight(38)
        card_lay.addWidget(self.input_name)

        # Type combo
        from PyQt5.QtWidgets import QListView
        self.type_box = QComboBox()
        self.type_box.setView(QListView())
        self.type_box.addItem("📅  Daily Repeating", "daily")
        self.type_box.addItem("🎯  Total Goal", "total")
        self.type_box.setFixedHeight(38)
        self.type_box.currentIndexChanged.connect(self._on_type_changed)
        card_lay.addWidget(self.type_box)

        # Stacked inputs
        self.stacked = QStackedWidget()

        # Page 0 — Daily
        page_daily = QWidget()
        pd_lay = QVBoxLayout(page_daily)
        pd_lay.setContentsMargins(0, 0, 0, 0)
        pd_lay.setSpacing(4)
        pd_lay.addWidget(self._field_label("Goal per day"))
        self.daily_spin = QSpinBox()
        self.daily_spin.setRange(1, 1000)
        self.daily_spin.setFixedHeight(38)
        self.daily_spin.setButtonSymbols(2)
        pd_lay.addWidget(self.daily_spin)

        # Page 1 — Total Goal
        page_total = QWidget()
        pt_lay = QVBoxLayout(page_total)
        pt_lay.setContentsMargins(0, 0, 0, 0)
        pt_lay.setSpacing(4)
        pt_lay.addWidget(self._field_label("Total reps goal"))
        self.total_spin = QSpinBox()
        self.total_spin.setRange(1, 99999)
        self.total_spin.setValue(30)
        self.total_spin.setFixedHeight(38)
        self.total_spin.setButtonSymbols(2)
        pt_lay.addWidget(self.total_spin)
        pt_lay.addWidget(self._field_label("Daily pace"))
        self.pace_spin = QSpinBox()
        self.pace_spin.setRange(1, 1000)
        self.pace_spin.setFixedHeight(38)
        self.pace_spin.setButtonSymbols(2)
        pt_lay.addWidget(self.pace_spin)

        self.stacked.addWidget(page_daily)
        self.stacked.addWidget(page_total)
        card_lay.addWidget(self.stacked)

        # Create button
        accent = self.theme_colors.get("accent", "#BD93F9")
        bg_main = self.theme_colors.get("bg_main", "#13132A")
        self.add_btn = QPushButton("＋  Create Habit")
        self.add_btn.setFixedHeight(42)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {accent}, stop:1 {self.theme_colors.get('accent_hover', '#FF79C6')}
                );
                color: {bg_main};
                border: none;
                border-radius: 12px;
                font-weight: 800;
                font-size: 13px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                opacity: 0.88;
            }}
            QPushButton:pressed {{
                opacity: 0.75;
            }}
        """)
        self.add_btn.clicked.connect(self._on_add_clicked)
        card_lay.addWidget(self.add_btn)

        container.addWidget(self.card)

        # Fade in
        eff = QGraphicsOpacityEffect(self.card)
        self.card.setGraphicsEffect(eff)
        anim = QPropertyAnimation(eff, b"opacity", self.card)
        anim.setDuration(500)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self._fade_anim = anim

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "color: #9499C3; font-size: 10px; font-weight: 700; "
            "letter-spacing: 0.5px; background: transparent;"
        )
        return lbl

    def _on_type_changed(self, index: int):
        self.stacked.setCurrentIndex(index)

    def _on_add_clicked(self):
        name = self.input_name.text().strip()
        if not name:
            self.input_name.setFocus()
            return

        h_type = self.type_box.currentData()
        if h_type == "daily":
            daily_target = self.daily_spin.value()
            total_target = 0
        else:
            daily_target = self.pace_spin.value()
            total_target = self.total_spin.value()

        self.habit_added.emit(name, h_type, total_target, daily_target)
        self.input_name.clear()
        self.input_name.setFocus()
