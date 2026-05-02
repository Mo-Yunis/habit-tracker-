from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QComboBox, QPushButton
from PyQt5.QtCore import pyqtSignal
from core.settings import save_settings
from core.themes import apply_theme

class SettingsPage(QWidget):
    settings_changed = pyqtSignal(object, object) # settings, theme_colors

    def __init__(self, app, settings):
        super().__init__()
        self.app = app
        self.settings = settings
        self.init_ui()

    def init_ui(self):
        set_layout = QVBoxLayout(self)
        set_label = QLabel("Settings")
        set_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        set_layout.addWidget(set_label)
        
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dracula", "Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings.get("theme", "Dracula"))
        form_layout.addWidget(self.theme_combo, 0, 1)
        
        form_layout.addWidget(QLabel("Graph Type:"), 1, 0)
        self.graph_combo = QComboBox()
        self.graph_combo.addItems(["Horizontal Bar", "Vertical Bar", "Pie Chart"])
        self.graph_combo.setCurrentText(self.settings.get("graph_type", "Horizontal Bar"))
        form_layout.addWidget(self.graph_combo, 1, 1)
        
        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_and_apply_settings)
        form_layout.addWidget(btn_save, 2, 0, 1, 2)
        
        set_layout.addLayout(form_layout)
        set_layout.addStretch()

    def save_and_apply_settings(self):
        self.settings["theme"] = self.theme_combo.currentText()
        self.settings["graph_type"] = self.graph_combo.currentText()
        save_settings(self.settings)
        
        theme_colors = apply_theme(self.app, self.settings["theme"])
        self.settings_changed.emit(self.settings, theme_colors)
