from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from core.database import get_all_time_stats

class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        hist_layout = QVBoxLayout(self)
        hist_label = QLabel("All-Time History")
        hist_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        hist_layout.addWidget(hist_label)
        
        self.history_stats_lbl = QLabel("")
        self.history_stats_lbl.setStyleSheet("font-size: 18px;")
        hist_layout.addWidget(self.history_stats_lbl)
        hist_layout.addStretch()

    def load_history(self):
        stats = get_all_time_stats()
        text = f"Total Habits Tracked: {stats['total_habits']}\nTotal Completions Logged: {stats['total_completions']}"
        self.history_stats_lbl.setText(text)
