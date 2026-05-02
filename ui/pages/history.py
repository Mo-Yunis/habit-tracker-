from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFrame, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from PyQt5.QtGui import QColor

from core.database import get_full_history
from datetime import datetime, timedelta


# ── helpers ────────────────────────────────────────────────────────────────

def _glass_frame(object_name="GlassPanel", radius=16):
    f = QFrame()
    f.setObjectName(object_name)
    return f


def _label(text, size=13, weight=600, color="#F8F8F2", align=Qt.AlignLeft):
    lbl = QLabel(text)
    lbl.setAlignment(align)
    lbl.setStyleSheet(
        f"color: {color}; font-size: {size}px; font-weight: {weight}; background: transparent;"
    )
    return lbl


def _fade_in(widget, duration=350):
    eff = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(eff)
    anim = QPropertyAnimation(eff, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start()
    widget._fade_anim = anim          # keep ref alive


# ── Stat Card ──────────────────────────────────────────────────────────────

class _StatCard(QFrame):
    def __init__(self, icon, value, label, accent="#BD93F9"):
        super().__init__()
        self.setObjectName("StatCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(110)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(8)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(
            f"font-size: 22px; background: transparent; color: {accent};"
        )
        top.addWidget(icon_lbl)
        top.addStretch()
        lay.addLayout(top)

        self.val_lbl = QLabel(str(value))
        self.val_lbl.setStyleSheet(
            f"font-size: 28px; font-weight: 800; color: {accent}; background: transparent;"
        )
        lay.addWidget(self.val_lbl)

        sub = QLabel(label)
        sub.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #9499C3; background: transparent; letter-spacing: 0.5px;"
        )
        lay.addWidget(sub)

    def set_value(self, v):
        self.val_lbl.setText(str(v))


# ── 30-day heatmap strip ───────────────────────────────────────────────────

class _HeatmapStrip(QWidget):
    def __init__(self, heatmap: dict, daily_target: int, accent="#BD93F9"):
        super().__init__()
        self.setFixedHeight(22)

        today = datetime.now().date()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            ds = d.strftime("%Y-%m-%d")
            val = heatmap.get(ds, -1)   # -1 = no log entry

            cell = QFrame()
            cell.setFixedSize(14, 14)
            cell.setToolTip(ds)

            if val == -1:
                bg = "rgba(100,100,140,0.18)"
            elif val == 0:
                bg = "rgba(255,85,85,0.40)"
            elif val >= daily_target:
                bg = accent
            else:
                ratio = val / daily_target
                a = int(60 + ratio * 130)
                bg = f"rgba(189,147,249,{a/255:.2f})" if accent == "#BD93F9" else accent

            cell.setStyleSheet(
                f"background: {bg}; border-radius: 3px;"
            )
            layout.addWidget(cell)

        layout.addStretch()


# ── Per-habit history row ──────────────────────────────────────────────────

class _HabitHistoryRow(QFrame):
    def __init__(self, data: dict, palette: list, index: int):
        super().__init__()
        self.setObjectName("GlassPanel")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        accent = palette[index % len(palette)]

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 14, 20, 14)
        outer.setSpacing(8)

        # ── Row 1: name + type badge + percent ────────────────────────────
        r1 = QHBoxLayout()
        r1.setSpacing(10)

        name_lbl = QLabel(data["name"])
        name_lbl.setStyleSheet(
            f"font-size: 15px; font-weight: 800; color: {accent}; background: transparent;"
        )
        r1.addWidget(name_lbl)

        type_badge = QLabel("📅 Daily" if data["type"] == "daily" else "🎯 Goal")
        type_badge.setStyleSheet(
            f"font-size: 11px; font-weight: 700; "
            f"color: {accent}; background: rgba(189,147,249,0.12); "
            f"border: 1px solid {accent}; border-radius: 8px; "
            f"padding: 2px 8px;"
        )
        r1.addWidget(type_badge)

        if data["status"] != "active":
            status_b = QLabel("✓ Done")
            status_b.setStyleSheet(
                "font-size: 11px; font-weight: 700; color: #50FA7B; "
                "background: rgba(80,250,123,0.12); border: 1px solid #50FA7B; "
                "border-radius: 8px; padding: 2px 8px;"
            )
            r1.addWidget(status_b)

        r1.addStretch()

        pct = data["percent"]
        pct_color = "#50FA7B" if pct >= 100 else accent
        pct_lbl = QLabel(f"{pct}%")
        pct_lbl.setStyleSheet(
            f"font-size: 18px; font-weight: 800; color: {pct_color}; background: transparent;"
        )
        r1.addWidget(pct_lbl)
        outer.addLayout(r1)

        # ── Progress bar ──────────────────────────────────────────────────
        bar_bg = QFrame()
        bar_bg.setFixedHeight(6)
        bar_bg.setStyleSheet(
            "background: rgba(100,100,140,0.25); border-radius: 3px;"
        )
        bar_fill = QFrame(bar_bg)
        bar_fill.setFixedHeight(6)
        bar_fill.setStyleSheet(
            f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {accent}, stop:1 {pct_color}); border-radius: 3px;"
        )
        # width set after show via timer
        self._bar_fill = bar_fill
        self._bar_bg   = bar_bg
        self._pct      = pct
        outer.addWidget(bar_bg)

        # ── Row 2: mini stats ─────────────────────────────────────────────
        r2 = QHBoxLayout()
        r2.setSpacing(20)
        stats = [
            ("📅 Started",      data["start_date"]),
            ("🔥 Best streak",  f"{data['best_streak']} days"),
            ("✅ Completions",  str(data["total_completions"])),
        ]
        if data["type"] == "daily":
            stats.append(("🎯 Daily target", str(data["daily_target"])))
        else:
            stats.append(("🏆 Total target", str(data["total_target"])))

        for icon_label, value in stats:
            col = QVBoxLayout()
            col.setSpacing(2)
            k = QLabel(icon_label)
            k.setStyleSheet("font-size: 10px; color: #9499C3; font-weight: 600; background: transparent;")
            v = QLabel(value)
            v.setStyleSheet(f"font-size: 13px; color: {accent}; font-weight: 700; background: transparent;")
            col.addWidget(k)
            col.addWidget(v)
            r2.addLayout(col)

        r2.addStretch()
        outer.addLayout(r2)

        # ── Heatmap ───────────────────────────────────────────────────────
        heat_label = QLabel("LAST 30 DAYS")
        heat_label.setStyleSheet(
            "font-size: 9px; font-weight: 800; color: #9499C3; letter-spacing: 1px; background: transparent;"
        )
        outer.addWidget(heat_label)

        strip = _HeatmapStrip(data["heatmap"], data["daily_target"], accent=accent)
        outer.addWidget(strip)

        # Animate bar fill after layout
        QTimer.singleShot(100, self._animate_bar)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_bar()

    def _sync_bar(self):
        w = self._bar_bg.width()
        fill_w = max(6, int(w * self._pct / 100))
        self._bar_fill.setFixedWidth(fill_w)

    def _animate_bar(self):
        self._sync_bar()


# ── Main History Page ──────────────────────────────────────────────────────

class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QHBoxLayout()
        hdr.setContentsMargins(0, 0, 0, 16)
        hdr.setSpacing(8)
        title = _label("History", size=28, weight=800)
        subtitle = _label("All-time progress & insights", size=13, weight=500, color="#9499C3")
        hdr_col = QVBoxLayout()
        hdr_col.setSpacing(2)
        hdr_col.addWidget(title)
        hdr_col.addWidget(subtitle)
        hdr.addLayout(hdr_col)
        hdr.addStretch()
        root.addLayout(hdr)

        # Stat cards row
        self._cards_row = QHBoxLayout()
        self._cards_row.setSpacing(14)

        self._card_habits      = _StatCard("📋", "—", "TOTAL HABITS",      "#BD93F9")
        self._card_completions = _StatCard("✅", "—", "TOTAL COMPLETIONS", "#50FA7B")
        self._card_streak      = _StatCard("🔥", "—", "BEST STREAK",       "#FFB86C")
        self._card_rate        = _StatCard("📈", "—", "AVG SUCCESS RATE",  "#8BE9FD")

        for card in [self._card_habits, self._card_completions, self._card_streak, self._card_rate]:
            self._cards_row.addWidget(card)

        root.addLayout(self._cards_row)
        root.addSpacing(18)

        # Habit list
        list_title = _label("PER-HABIT BREAKDOWN", size=10, weight=800, color="#9499C3")
        list_title.setContentsMargins(0, 0, 0, 6)
        root.addWidget(list_title)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        root.addWidget(self._scroll)

        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._vbox = QVBoxLayout(self._container)
        self._vbox.setSpacing(12)
        self._vbox.setAlignment(Qt.AlignTop)
        self._scroll.setWidget(self._container)

    def load_history(self):
        # Clear list
        while self._vbox.count():
            item = self._vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        history = get_full_history()

        if not history:
            empty = _label(
                "No habits yet — create your first habit to see history here! 🚀",
                size=14, weight=600, color="#9499C3", align=Qt.AlignCenter
            )
            empty.setContentsMargins(40, 60, 40, 60)
            self._vbox.addWidget(empty)
            return

        # Aggregate global stats
        total_habits      = len(history)
        total_completions = sum(h["total_completions"] for h in history)
        best_streak       = max((h["best_streak"] for h in history), default=0)
        avg_rate          = int(sum(h["percent"] for h in history) / total_habits) if total_habits else 0

        self._card_habits.set_value(total_habits)
        self._card_completions.set_value(total_completions)
        self._card_streak.set_value(f"{best_streak}d")
        self._card_rate.set_value(f"{avg_rate}%")

        # Default palette
        palette = [
            "#BD93F9", "#FF79C6", "#8BE9FD", "#50FA7B",
            "#F1FA8C", "#FFB86C", "#FF5555", "#6272A4",
        ]

        for i, h in enumerate(history):
            row = _HabitHistoryRow(h, palette, i)
            _fade_in(row, duration=300 + i * 40)
            self._vbox.addWidget(row)

        self._vbox.addStretch()
