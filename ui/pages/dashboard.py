from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QScrollArea, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime

from core.database import get_habits
from ui.components.chart import DashboardChart
from ui.components.habit_row import HabitRow

class DashboardPage(QWidget):
    habit_deleted = pyqtSignal()
    
    def __init__(self, settings, theme_colors):
        super().__init__()
        self.settings = settings
        self.theme_colors = theme_colors
        self.current_habits = []
        
        now = datetime.now()
        self.month = now.month
        self.year = now.year
        
        self.init_ui()
        self.load()

    def init_ui(self):
        dash_layout = QVBoxLayout(self)
        dash_layout.setContentsMargins(0,0,0,0)
        
        header = QHBoxLayout()
        self.title = QLabel("Dashboard overview")
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; letter-spacing: 1px;")
        header.addWidget(self.title)
        header.addStretch()

        self.view_mode_combo = QComboBox()
        self.month_box = QComboBox()
        self.year_box = QComboBox()

        from PyQt5.QtWidgets import QListView
        for cb in [self.view_mode_combo, self.month_box, self.year_box]:
            cb.setView(QListView())

        self.view_mode_combo.addItems(["Today", "Entire Month"])
        self.view_mode_combo.currentTextChanged.connect(self.reload)
        self.view_mode_combo.setFixedHeight(38)

        for i in range(1, 13):
            self.month_box.addItem(datetime(2000, i, 1).strftime('%B'), str(i))
        for y in range(2020, 2035):
            self.year_box.addItem(str(y))

        self.month_box.setCurrentIndex(self.month - 1)
        self.year_box.setCurrentText(str(self.year))
        self.month_box.currentIndexChanged.connect(self.reload)
        self.year_box.currentTextChanged.connect(self.reload)

        header.addWidget(self.view_mode_combo)
        header.addWidget(self.month_box)
        header.addWidget(self.year_box)
        dash_layout.addLayout(header)

        self.chart = DashboardChart(self, width=10, height=2.5, theme_colors=self.theme_colors)
        dash_layout.addWidget(self.chart)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        dash_layout.addWidget(self.scroll)

    def load(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        v = QVBoxLayout(container)
        v.setSpacing(20)
        v.setAlignment(Qt.AlignTop)

        self.current_habits = get_habits(self.month, self.year)
        view_mode = self.view_mode_combo.currentText()

        for h in self.current_habits:
            row = HabitRow(h, view_mode=view_mode)
            row.data_changed.connect(self.update_chart_only)
            row.habit_deleted.connect(self.on_habit_deleted)
            v.addWidget(row)

        self.scroll.setWidget(container)
        self.update_chart_only()

    def update_chart_only(self):
        self.current_habits = get_habits(self.month, self.year)
        view_mode = self.view_mode_combo.currentText()
        self.chart.plot(self.current_habits, self.settings.get("graph_type", "Horizontal Bar"), view_mode=view_mode)

    def reload(self):
        self.month = int(self.month_box.currentData())
        self.year = int(self.year_box.currentText())
        
        now = datetime.now()
        if self.month != now.month or self.year != now.year:
            self.view_mode_combo.setCurrentText("Entire Month")
            self.view_mode_combo.setEnabled(False)
        else:
            self.view_mode_combo.setEnabled(True)
            
        self.load()

    def on_habit_deleted(self):
        self.reload()
        self.habit_deleted.emit()
        
    def update_theme(self, settings, theme_colors):
        self.settings = settings
        self.theme_colors = theme_colors
        self.chart.update_theme(theme_colors)
        self.update_chart_only()
