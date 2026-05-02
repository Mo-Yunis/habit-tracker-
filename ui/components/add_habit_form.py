from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, 
    QStackedWidget, QSpinBox, QPushButton
)
from PyQt5.QtCore import pyqtSignal

class AddHabitForm(QWidget):
    habit_added = pyqtSignal(str, str, int, int) # name, habit_type, total_target, daily_target

    def __init__(self, theme_colors):
        super().__init__()
        self.theme_colors = theme_colors
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl_new = QLabel("NEW HABIT")
        lbl_new.setStyleSheet(f"color: {self.theme_colors.get('text_muted')}; font-weight: bold;")
        layout.addWidget(lbl_new)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Name...")
        layout.addWidget(self.input_name)
        
        self.type_box = QComboBox()
        self.type_box.addItem("Daily Repeating", "daily")
        self.type_box.addItem("Total Goal", "total")
        self.type_box.currentIndexChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_box)
        
        self.stacked_inputs = QStackedWidget()
        
        # Daily Page
        page_daily = QWidget()
        p0_layout = QVBoxLayout(page_daily)
        p0_layout.setContentsMargins(0,0,0,0)
        p0_layout.addWidget(QLabel("Times per day:"))
        self.daily_target_spin = QSpinBox()
        self.daily_target_spin.setRange(1, 1000)
        p0_layout.addWidget(self.daily_target_spin)
        
        # Total Page
        page_total = QWidget()
        p1_layout = QVBoxLayout(page_total)
        p1_layout.setContentsMargins(0,0,0,0)
        p1_layout.addWidget(QLabel("Total Target:"))
        self.total_target_spin = QSpinBox()
        self.total_target_spin.setRange(1, 10000)
        self.total_target_spin.setValue(30)
        p1_layout.addWidget(self.total_target_spin)
        
        p1_layout.addWidget(QLabel("Daily Pace:"))
        self.total_daily_spin = QSpinBox()
        self.total_daily_spin.setRange(1, 1000)
        p1_layout.addWidget(self.total_daily_spin)
        
        self.stacked_inputs.addWidget(page_daily)
        self.stacked_inputs.addWidget(page_total)
        layout.addWidget(self.stacked_inputs)
        
        self.add_btn = QPushButton("Add Habit")
        self.add_btn.clicked.connect(self.on_add_clicked)
        layout.addWidget(self.add_btn)

    def on_type_changed(self, index):
        self.stacked_inputs.setCurrentIndex(index)

    def on_add_clicked(self):
        name = self.input_name.text().strip()
        if not name:
            return
            
        h_type = self.type_box.currentData()
        
        if h_type == "daily":
            daily_target = self.daily_target_spin.value()
            total_target = 0
        else:
            daily_target = self.total_daily_spin.value()
            total_target = self.total_target_spin.value()
            
        self.habit_added.emit(name, h_type, total_target, daily_target)
        self.input_name.clear()
