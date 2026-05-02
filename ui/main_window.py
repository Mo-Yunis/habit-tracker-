from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QStackedWidget, QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPen, QColor
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from datetime import datetime

from core.database import add_habit
from ui.pages.dashboard import DashboardPage
from ui.pages.history import HistoryPage
from ui.pages.settings import SettingsPage
from ui.components.add_habit_form import AddHabitForm


# ── Icon factory ───────────────────────────────────────────────────────────

def create_icon(icon_type: str, color: str = "#9499C3") -> QIcon:
    pix = QPixmap(64, 64)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor(color))
    pen.setWidth(5)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)

    if icon_type == "menu":
        p.drawLine(12, 18, 52, 18)
        p.drawLine(12, 32, 52, 32)
        p.drawLine(12, 46, 52, 46)
    elif icon_type == "dashboard":
        p.drawRect(12, 35, 10, 15)
        p.drawRect(27, 20, 10, 30)
        p.drawRect(42, 30, 10, 20)
    elif icon_type == "history":
        p.drawEllipse(12, 12, 40, 40)
        p.drawLine(32, 32, 32, 22)
        p.drawLine(32, 32, 42, 32)
    elif icon_type == "settings":
        p.drawEllipse(22, 22, 20, 20)
        for i in range(8):
            p.save()
            p.translate(32, 32)
            p.rotate(i * 45)
            p.drawLine(0, -22, 0, -28)
            p.restore()
    elif icon_type == "plus":
        p.drawLine(32, 12, 32, 52)
        p.drawLine(12, 32, 52, 32)
    elif icon_type in ("delete", "close"):
        p.drawLine(16, 16, 48, 48)
        p.drawLine(48, 16, 16, 48)

    p.end()
    return QIcon(pix)


# ── NavButton ──────────────────────────────────────────────────────────────

class _NavButton(QPushButton):
    def __init__(self, label: str, icon_type: str, color: str):
        super().__init__(f"  {label}")
        self.icon_type = icon_type
        self.setIcon(create_icon(icon_type, color))
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setIconSize(QPixmap(22, 22).size())

    def set_active(self, active: bool, accent: str, text_main: str):
        if active:
            self.setIcon(create_icon(self.icon_type, accent))
            self.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(189,147,249,0.12);
                    color: {accent};
                    text-align: left;
                    padding-left: 14px;
                    border-left: 3px solid {accent};
                    border-radius: 0px 12px 12px 0px;
                    font-weight: 800;
                    font-size: 13px;
                    border-top: none; border-right: none; border-bottom: none;
                }}
            """)
        else:
            self.setIcon(create_icon(self.icon_type, text_main))
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {text_main};
                    text-align: left;
                    padding-left: 17px;
                    border: none;
                    border-radius: 12px;
                    font-weight: 500;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: rgba(148,153,195,0.10);
                    color: {accent};
                }}
            """)


# ── MainWindow ─────────────────────────────────────────────────────────────

class MainWindow(QWidget):
    def __init__(self, app, settings, theme_colors):
        super().__init__()
        self.app          = app
        self.settings     = settings
        self.theme_colors = theme_colors

        self.setWindowTitle("🔥 Habit Tracker")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.resize(1280, 820)

        self._init_ui()

    # ── build UI ───────────────────────────────────────────────────────────

    def _init_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)

        # ── SIDEBAR ────────────────────────────────────────────────────────
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(272)

        sb_lay = QVBoxLayout(self.sidebar)
        sb_lay.setContentsMargins(14, 18, 14, 18)
        sb_lay.setSpacing(8)

        # Logo row
        logo_row = QHBoxLayout()
        logo = QLabel("🔥 HABIT")
        logo.setStyleSheet(
            f"color: {self.theme_colors.get('accent','#BD93F9')}; "
            "font-size: 22px; font-weight: 900; letter-spacing: 2px;"
        )
        self._btn_toggle = QPushButton()
        self._btn_toggle.setIcon(create_icon("menu", self.theme_colors.get("text_muted", "#9499C3")))
        self._btn_toggle.setFixedSize(32, 32)
        self._btn_toggle.setCursor(Qt.PointingHandCursor)
        self._btn_toggle.setStyleSheet("background: transparent; border: none;")
        self._btn_toggle.clicked.connect(self._toggle_sidebar)
        logo_row.addWidget(logo)
        logo_row.addStretch()
        logo_row.addWidget(self._btn_toggle)
        sb_lay.addLayout(logo_row)
        sb_lay.addSpacing(16)

        # Nav section label
        nav_lbl = QLabel("NAVIGATION")
        nav_lbl.setStyleSheet(
            "color: #9499C3; font-size: 9px; font-weight: 800; "
            "letter-spacing: 1.8px; background: transparent;"
        )
        sb_lay.addWidget(nav_lbl)
        sb_lay.addSpacing(4)

        # Nav buttons
        self._nav_btns = [
            _NavButton("Dashboard", "dashboard", self.theme_colors.get("text_main", "#F8F8F2")),
            _NavButton("History",   "history",   self.theme_colors.get("text_main", "#F8F8F2")),
            _NavButton("Settings",  "settings",  self.theme_colors.get("text_main", "#F8F8F2")),
        ]
        for i, btn in enumerate(self._nav_btns):
            btn.clicked.connect(lambda _, idx=i: self._switch_page(idx))
            sb_lay.addWidget(btn)

        sb_lay.addSpacing(24)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet(
            "background: rgba(148,153,195,0.18); border: none; max-height: 1px;"
        )
        sb_lay.addWidget(div)
        sb_lay.addSpacing(8)

        # Create new label
        create_lbl = QLabel("CREATE NEW")
        create_lbl.setStyleSheet(
            "color: #9499C3; font-size: 9px; font-weight: 800; "
            "letter-spacing: 1.8px; background: transparent;"
        )
        sb_lay.addWidget(create_lbl)

        self.add_form = AddHabitForm(self.theme_colors)
        self.add_form.habit_added.connect(self._on_habit_added)
        sb_lay.addWidget(self.add_form)

        sb_lay.addStretch()

        # Footer
        footer = QLabel("Built by Yunis  •  لا تنسوا والدتي من دعائكم 🤍")
        footer.setAlignment(Qt.AlignCenter)
        footer.setWordWrap(True)
        footer.setStyleSheet(
            "color: #9499C3; font-size: 10px; font-weight: 500; background: transparent;"
        )
        sb_lay.addWidget(footer)

        self.splitter.addWidget(self.sidebar)

        # ── MAIN AREA ──────────────────────────────────────────────────────
        self.main_area = QFrame()
        self.main_area.setStyleSheet("background: transparent;")
        ma_lay = QVBoxLayout(self.main_area)
        ma_lay.setContentsMargins(16, 8, 16, 16)
        ma_lay.setSpacing(16)

        # Top bar
        top_bar = QHBoxLayout()
        self._btn_open_sidebar = QPushButton()
        self._btn_open_sidebar.setIcon(
            create_icon("menu", self.theme_colors.get("accent", "#BD93F9"))
        )
        self._btn_open_sidebar.setFixedSize(38, 38)
        self._btn_open_sidebar.setCursor(Qt.PointingHandCursor)
        self._btn_open_sidebar.setStyleSheet("background: transparent; border: none;")
        self._btn_open_sidebar.clicked.connect(self._toggle_sidebar)
        self._btn_open_sidebar.hide()

        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet(
            "font-size: 24px; font-weight: 800; margin-left: 6px; background: transparent;"
        )

        # Date badge
        date_badge = QLabel(datetime.now().strftime("  %A, %d %B %Y  "))
        date_badge.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #9499C3; "
            "background: rgba(148,153,195,0.10); "
            "border: 1px solid rgba(148,153,195,0.20); "
            "border-radius: 10px; padding: 4px 10px;"
        )

        top_bar.addWidget(self._btn_open_sidebar)
        top_bar.addWidget(self.page_title)
        top_bar.addStretch()
        top_bar.addWidget(date_badge)
        ma_lay.addLayout(top_bar)

        # Pages
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("background: transparent;")

        self.dashboard_page = DashboardPage(self.settings, self.theme_colors)
        self.dashboard_page.habit_deleted.connect(lambda: self.history_page.load_history())
        self.pages.addWidget(self.dashboard_page)

        self.history_page = HistoryPage()
        self.pages.addWidget(self.history_page)

        self.settings_page = SettingsPage(self.app, self.settings)
        self.settings_page.settings_changed.connect(self._on_settings_changed)
        self.pages.addWidget(self.settings_page)

        ma_lay.addWidget(self.pages)
        self.splitter.addWidget(self.main_area)
        self.splitter.setSizes([272, 1008])
        root.addWidget(self.splitter)

        # Init state
        self._update_nav(0)
        self.history_page.load_history()

    # ── helpers ────────────────────────────────────────────────────────────

    def _update_nav(self, active_idx: int):
        accent    = self.theme_colors.get("accent",    "#BD93F9")
        text_main = self.theme_colors.get("text_main", "#F8F8F2")
        for i, btn in enumerate(self._nav_btns):
            btn.set_active(i == active_idx, accent, text_main)

    def _toggle_sidebar(self):
        if self.sidebar.isVisible():
            self.sidebar.hide()
            self._btn_open_sidebar.show()
        else:
            self.sidebar.show()
            self._btn_open_sidebar.hide()

    def _switch_page(self, idx: int):
        self.pages.setCurrentIndex(idx)
        self.page_title.setText(["Dashboard", "History", "Settings"][idx])
        self._update_nav(idx)
        if idx == 1:
            self.history_page.load_history()

    def _on_settings_changed(self, settings, theme_colors):
        self.settings     = settings
        self.theme_colors = theme_colors
        self._update_nav(self.pages.currentIndex())
        
        # Trigger full reload of dashboard habits
        self.dashboard_page.update_theme(settings, theme_colors)
        self.dashboard_page.reload()
        
        # Trigger reload of history
        self.history_page.load_history()


    def _on_habit_added(self, name: str, h_type: str, total_target: int, daily_target: int):
        add_habit(name, h_type, total_target, daily_target)
        self.dashboard_page.reload()
        self.history_page.load_history()
