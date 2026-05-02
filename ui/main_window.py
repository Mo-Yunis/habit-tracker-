from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from datetime import datetime

from core.database import add_habit
from ui.pages.dashboard import DashboardPage
from ui.pages.history import HistoryPage
from ui.pages.settings import SettingsPage
from ui.components.add_habit_form import AddHabitForm


class MainWindow(QWidget):
    def __init__(self, app, settings, theme_colors):
        super().__init__()
        self.app = app
        self.settings = settings
        self.theme_colors = theme_colors

        self.setWindowTitle("🔥Habit Tracker")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.resize(1200, 800)

        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        
        # --- LEFT SIDEBAR ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setMinimumWidth(250)
        self.sidebar.setMaximumWidth(350)
        self.update_sidebar_style()
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 30)
        sidebar_layout.setSpacing(15)
        
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet(f"color: {self.theme_colors.get('text_muted')}; font-weight: bold;")
        sidebar_layout.addWidget(nav_label)
        
        self.btn_dashboard = QPushButton("📊 Dashboard")
        self.btn_history = QPushButton("⏳ History")
        self.btn_settings = QPushButton("⚙️ Settings")
        
        self.update_nav_buttons_style()
            
        for btn in [self.btn_dashboard, self.btn_history, self.btn_settings]:
            sidebar_layout.addWidget(btn)
            
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.btn_history.clicked.connect(lambda: self.switch_page(1))
        self.btn_settings.clicked.connect(lambda: self.switch_page(2))

        sidebar_layout.addSpacing(30)

        # Form in sidebar
        self.add_habit_form = AddHabitForm(self.theme_colors)
        self.add_habit_form.habit_added.connect(self.on_habit_added)
        sidebar_layout.addWidget(self.add_habit_form)
        
        sidebar_layout.addStretch()

        footer_label = QLabel("تم التطوير بواسطه يونس\nلاتنسوا والدتي من دعائكم",)
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setStyleSheet(f"color: {self.theme_colors.get('text_muted')}; font-size: 14px;")
        sidebar_layout.addWidget(footer_label)

        self.splitter.addWidget(self.sidebar)

        # --- RIGHT MAIN AREA ---
        self.main_area = QFrame()
        main_area_layout = QVBoxLayout(self.main_area)
        main_area_layout.setContentsMargins(30, 30, 30, 30)

        # Top Bar for Toggle Sidebar
        top_bar = QHBoxLayout()
        self.btn_toggle_sidebar = QPushButton("☰")
        self.btn_toggle_sidebar.setObjectName("ToggleSidebar")
        self.btn_toggle_sidebar.setFixedSize(40, 40)
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        top_bar.addWidget(self.btn_toggle_sidebar)
        top_bar.addStretch()
        main_area_layout.addLayout(top_bar)

        self.stacked_widget = QStackedWidget()
        
        # Initialize Pages
        self.dashboard_page = DashboardPage(self.settings, self.theme_colors)
        self.dashboard_page.habit_deleted.connect(lambda: self.history_page.load_history())
        self.stacked_widget.addWidget(self.dashboard_page)
        
        self.history_page = HistoryPage()
        self.stacked_widget.addWidget(self.history_page)

        self.settings_page = SettingsPage(self.app, self.settings)
        self.settings_page.settings_changed.connect(self.on_settings_changed)
        self.stacked_widget.addWidget(self.settings_page)

        main_area_layout.addWidget(self.stacked_widget)
        self.splitter.addWidget(self.main_area)

        self.splitter.setSizes([300, 900])
        main_layout.addWidget(self.splitter)
        
        # Initial data load
        self.history_page.load_history()

    def update_sidebar_style(self):
        bg = self.theme_colors.get("bg_card", "#383a59")
        border = self.theme_colors.get("border", "#6272a4")
        self.sidebar.setStyleSheet(f"""
            QFrame#Sidebar {{
                background-color: {bg};
                border-right: 1px solid {border};
            }}
        """)
        
        if hasattr(self, 'btn_toggle_sidebar'):
            bg_input = self.theme_colors.get("bg_input", "#44475a")
            text_main = self.theme_colors.get("text_main", "#f8f8f2")
            self.btn_toggle_sidebar.setStyleSheet(f"""
                QPushButton#ToggleSidebar {{
                    background-color: transparent;
                    color: {text_main};
                    font-size: 20px;
                    border: none;
                    border-radius: 5px;
                }}
                QPushButton#ToggleSidebar:hover {{
                    background-color: {bg_input};
                }}
            """)

    def update_nav_buttons_style(self):
        for btn in [self.btn_dashboard, self.btn_history, self.btn_settings]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 10px;
                    background-color: transparent;
                    border: none;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: {self.theme_colors.get('bg_input')};
                }}
            """)

    def toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if index == 1:
            self.history_page.load_history()

    def on_settings_changed(self, settings, theme_colors):
        self.settings = settings
        self.theme_colors = theme_colors
        self.update_sidebar_style()
        self.update_nav_buttons_style()
        self.dashboard_page.update_theme(settings, theme_colors)

    def on_habit_added(self, name, h_type, total_target, daily_target):
        now = datetime.now()
        month = self.dashboard_page.month
        year = self.dashboard_page.year
        
        if month == now.month and year == now.year:
            created_day = now.day
        elif (year > now.year) or (year == now.year and month > now.month):
            created_day = 1
        else:
            created_day = 31
            
        add_habit(name, month, year, h_type, total_target, daily_target, created_day)
        self.dashboard_page.reload()
        self.history_page.load_history()