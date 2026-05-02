from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QComboBox, QPushButton, QScrollArea, QSizePolicy,
    QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from core.settings import save_settings
from core.themes import apply_theme
from core.database import connect


# ── helpers ────────────────────────────────────────────────────────────────

def _section_card(title: str, icon: str) -> tuple:
    """Returns (card QFrame, inner_layout QVBoxLayout)."""
    card = QFrame()
    card.setObjectName("GlassPanel")

    inner = QVBoxLayout(card)
    inner.setContentsMargins(20, 16, 20, 16)
    inner.setSpacing(14)

    hdr = QHBoxLayout()
    icon_l = QLabel(icon)
    icon_l.setStyleSheet("font-size: 18px; background: transparent;")
    title_l = QLabel(title)
    title_l.setStyleSheet(
        "font-size: 13px; font-weight: 800; letter-spacing: 0.8px; background: transparent;"
    )
    hdr.addWidget(icon_l)
    hdr.addWidget(title_l)
    hdr.addStretch()
    inner.addLayout(hdr)

    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setStyleSheet("background: rgba(148,153,195,0.18); border: none; max-height: 1px;")
    inner.addWidget(sep)

    return card, inner


def _row_item(label_text: str, sub_text: str, widget: QWidget) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(12)

    col = QVBoxLayout()
    col.setSpacing(2)
    lbl = QLabel(label_text)
    lbl.setStyleSheet("font-size: 13px; font-weight: 700; background: transparent;")
    sub = QLabel(sub_text)
    sub.setStyleSheet("font-size: 11px; color: #9499C3; background: transparent;")
    col.addWidget(lbl)
    col.addWidget(sub)

    row.addLayout(col)
    row.addStretch()
    row.addWidget(widget)
    return row


def _styled_combo(options: list, current: str) -> QComboBox:
    from PyQt5.QtWidgets import QListView
    cb = QComboBox()
    cb.setView(QListView())
    cb.addItems(options)
    cb.setCurrentText(current)
    cb.setFixedWidth(180)
    cb.setFixedHeight(38)
    return cb


def _danger_btn(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(38)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet("""
        QPushButton {
            background: rgba(255,85,85,0.12);
            color: #FF5555;
            border: 1px solid rgba(255,85,85,0.35);
            border-radius: 10px;
            font-weight: 700;
            padding: 0 16px;
        }
        QPushButton:hover {
            background: #FF5555;
            color: white;
            border: 1px solid #FF5555;
        }
    """)
    return btn


def _accent_btn(text: str, accent: str = "#BD93F9") -> QPushButton:
    btn = QPushButton(text)
    btn.setFixedHeight(38)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: rgba(189,147,249,0.14);
            color: {accent};
            border: 1px solid {accent};
            border-radius: 10px;
            font-weight: 700;
            padding: 0 16px;
        }}
        QPushButton:hover {{
            background: {accent};
            color: #13132A;
        }}
    """)
    return btn


# ── Theme swatch ───────────────────────────────────────────────────────────

class _ThemeSwatch(QFrame):
    selected = pyqtSignal(str)

    PREVIEWS = {
        "Dracula": ("#13132A", "#BD93F9", "#FF79C6"),
        "Dark":    ("#090B14", "#7B61FF", "#A594FF"),
        "Light":   ("#EEF1F7", "#4F6EF7", "#3B56DA"),
    }

    def __init__(self, name: str, active: bool = False):
        super().__init__()
        self.name = name
        self.setFixedSize(90, 72)
        self.setCursor(Qt.PointingHandCursor)
        self._active = active
        self._build()

    def _build(self):
        bg, a1, a2 = self.PREVIEWS.get(self.name, ("#1E1E2E", "#BD93F9", "#FF79C6"))
        border = "#BD93F9" if self._active else "rgba(148,153,195,0.25)"
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border-radius: 12px;
                border: 2px solid {border};
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(4)

        bar1 = QFrame()
        bar1.setFixedHeight(8)
        bar1.setStyleSheet(f"background: {a1}; border-radius: 4px;")
        bar2 = QFrame()
        bar2.setFixedHeight(8)
        bar2.setStyleSheet(f"background: {a2}; border-radius: 4px;")
        lay.addWidget(bar1)
        lay.addWidget(bar2)
        lay.addStretch()

        lbl = QLabel(self.name)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {a1}; background: transparent;")
        lay.addWidget(lbl)

    def set_active(self, v: bool):
        self._active = v
        self._build()

    def mousePressEvent(self, _):
        self.selected.emit(self.name)


# ── Settings Page ──────────────────────────────────────────────────────────

class SettingsPage(QWidget):
    settings_changed = pyqtSignal(object, object)

    def __init__(self, app, settings):
        super().__init__()
        self.app = app
        self.settings = settings
        self._swatches = {}
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QVBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 18)
        hdr.addWidget(_lbl("Settings", 28, 800))
        hdr.addWidget(_lbl("Customise your experience", 13, 500, "#9499C3"))
        root.addLayout(hdr)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(scroll)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(container)
        vbox.setSpacing(16)
        vbox.setAlignment(Qt.AlignTop)
        scroll.setWidget(container)

        # ── 🎨 Appearance ─────────────────────────────────────────────────
        card_app, lay_app = _section_card("APPEARANCE", "🎨")

        # Theme swatches
        swatches_row = QHBoxLayout()
        swatches_row.setSpacing(12)
        current_theme = self.settings.get("theme", "Dracula")
        for name in ["Dracula", "Dark", "Light"]:
            sw = _ThemeSwatch(name, active=(name == current_theme))
            sw.selected.connect(self._on_theme_selected)
            self._swatches[name] = sw
            swatches_row.addWidget(sw)
        swatches_row.addStretch()
        lay_app.addLayout(swatches_row)

        # Graph type
        self._graph_combo = _styled_combo(
            ["Horizontal Bar", "Vertical Bar", "Pie Chart"],
            self.settings.get("graph_type", "Horizontal Bar")
        )
        self._graph_combo.currentTextChanged.connect(self._auto_save)
        lay_app.addLayout(_row_item(
            "Chart Type", "Dashboard graph style",
            self._graph_combo
        ))
        vbox.addWidget(card_app)

        # ── ⚙️ Behaviour ──────────────────────────────────────────────────
        card_beh, lay_beh = _section_card("BEHAVIOUR", "⚙️")

        self._week_combo = _styled_combo(
            ["Monday", "Saturday", "Sunday"],
            self.settings.get("start_of_week", "Monday")
        )
        self._week_combo.currentTextChanged.connect(self._auto_save)
        lay_beh.addLayout(_row_item(
            "Start of Week", "Which day begins your week",
            self._week_combo
        ))

        self._streak_chk = _toggle_check(
            self.settings.get("show_streaks", True)
        )
        self._streak_chk.stateChanged.connect(self._auto_save)
        lay_beh.addLayout(_row_item(
            "Show Streaks", "Display streak counters on habit cards",
            self._streak_chk
        ))

        self._compact_chk = _toggle_check(
            self.settings.get("compact_mode", False)
        )
        self._compact_chk.stateChanged.connect(self._auto_save)
        lay_beh.addLayout(_row_item(
            "Compact Mode", "Denser layout for smaller screens",
            self._compact_chk
        ))
        vbox.addWidget(card_beh)

        # ── 🗄️ Data ───────────────────────────────────────────────────────
        card_dat, lay_dat = _section_card("DATA", "🗄️")

        export_btn = _accent_btn("Export CSV")
        export_btn.clicked.connect(self._export_csv)
        lay_dat.addLayout(_row_item(
            "Export Habits", "Download all logs as a CSV file",
            export_btn
        ))

        reset_btn = _danger_btn("Reset All Data")
        reset_btn.clicked.connect(self._reset_data)
        lay_dat.addLayout(_row_item(
            "Reset Database", "Permanently delete all habits & logs",
            reset_btn
        ))
        vbox.addWidget(card_dat)

        # ── ℹ️ About ──────────────────────────────────────────────────────
        card_about, lay_about = _section_card("ABOUT", "ℹ️")

        for key, val in [
            ("Version",   "2.0.0 — Liquid Glass Edition"),
            ("Developer", "Yunis"),
            ("Note",      "لا تنسوا والدتي من دعائكم 🤍"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(12)
            k = QLabel(key)
            k.setStyleSheet("font-size: 12px; color: #9499C3; font-weight: 600; background: transparent;")
            v = QLabel(val)
            v.setStyleSheet("font-size: 13px; font-weight: 700; background: transparent;")
            row.addWidget(k, 1)
            row.addWidget(v, 3)
            lay_about.addLayout(row)

        vbox.addWidget(card_about)
        vbox.addStretch()

    # ── slots ──────────────────────────────────────────────────────────────

    def _on_theme_selected(self, name: str):
        for n, sw in self._swatches.items():
            sw.set_active(n == name)
        self.settings["theme"] = name
        self._auto_save()
        theme_colors = apply_theme(self.app, name)
        self.settings_changed.emit(self.settings, theme_colors)

    def _auto_save(self, *_):
        self.settings["graph_type"]    = self._graph_combo.currentText()
        self.settings["start_of_week"] = self._week_combo.currentText()
        self.settings["show_streaks"]  = self._streak_chk.isChecked()
        self.settings["compact_mode"]  = self._compact_chk.isChecked()
        save_settings(self.settings)
        # Emit without re-applying theme (already done in _on_theme_selected)
        theme_colors = apply_theme(self.app, self.settings.get("theme", "Dracula"))
        self.settings_changed.emit(self.settings, theme_colors)

    def _export_csv(self):
        import csv, os
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", "habits_export.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        conn = connect()
        c = conn.cursor()
        c.execute("""
            SELECT h.name, h.habit_type, h.start_date, l.log_date, l.completed
            FROM habits h
            JOIN habit_logs l ON h.id = l.habit_id
            ORDER BY h.name, l.log_date
        """)
        rows = c.fetchall()
        conn.close()
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["Habit", "Type", "Start Date", "Log Date", "Completed"])
            w.writerows(rows)
        QMessageBox.information(self, "Export Complete", f"Saved to:\n{path}")

    def _reset_data(self):
        reply = QMessageBox.question(
            self, "⚠️  Reset All Data",
            "This will permanently delete ALL habits and logs, and reset all settings to defaults.\nThis action cannot be undone.\n\nAre you sure?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # 1. Reset Database
            from core.database import init_db
            init_db()
            
            # 2. Reset Settings
            from core.settings import DEFAULT_SETTINGS, save_settings
            self.settings.clear()
            self.settings.update(DEFAULT_SETTINGS.copy())
            save_settings(self.settings)
            
            QMessageBox.information(self, "Done", "App has been reset to its original state.")
            
            # 3. Notify app
            theme_colors = apply_theme(self.app, self.settings.get("theme", "Dracula"))
            self.refresh()
            self.settings_changed.emit(self.settings, theme_colors)



    def refresh(self):
        # Update theme swatches
        theme = self.settings.get("theme", "Dracula")
        for n, sw in self._swatches.items():
            sw.set_active(n == theme)
        
        # Update combos/checks
        self._graph_combo.setCurrentText(self.settings.get("graph_type", "Horizontal Bar"))
        self._week_combo.setCurrentText(self.settings.get("start_of_week", "Monday"))
        self._streak_chk.setChecked(self.settings.get("show_streaks", True))
        self._compact_chk.setChecked(self.settings.get("compact_mode", False))


# ── tiny helpers (module-level) ────────────────────────────────────────────

def _lbl(text, size=14, weight=600, color=None):
    l = QLabel(text)
    style = f"font-size: {size}px; font-weight: {weight}; background: transparent;"
    if color:
        style += f" color: {color};"
    l.setStyleSheet(style)
    return l


def _toggle_check(checked: bool) -> QCheckBox:
    cb = QCheckBox()
    cb.setChecked(checked)
    cb.setStyleSheet("""
        QCheckBox::indicator {
            width: 38px; height: 20px;
            border-radius: 10px;
        }
        QCheckBox::indicator:unchecked {
            background: rgba(100,100,140,0.30);
            border: 1px solid rgba(148,153,195,0.30);
            border-radius: 10px;
        }
        QCheckBox::indicator:checked {
            background: #BD93F9;
            border: 1px solid #BD93F9;
            border-radius: 10px;
        }
    """)
    return cb
