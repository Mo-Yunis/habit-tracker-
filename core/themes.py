def get_theme_stylesheet(theme_name):
    font_family = "'Outfit', 'Inter', 'Segoe UI', 'DejaVu Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', sans-serif"


    if theme_name == "Light":
        bg_main        = "#EEF1F7"
        bg_card        = "rgba(255,255,255,0.72)"
        bg_input       = "rgba(240,242,248,0.85)"
        glass_bg       = "rgba(255,255,255,0.55)"
        glass_border   = "rgba(200,210,230,0.70)"
        glow_color     = "rgba(0,100,255,0.18)"
        text_main      = "#111827"
        text_muted     = "#6B7280"
        accent         = "#4F6EF7"
        accent_hover   = "#3B56DA"
        border         = "rgba(200,210,230,0.60)"
        chart_bg       = "rgba(255,255,255,0.72)"
        chart_text     = "#111827"
        chart_grid     = "#D1D5DB"
        palette        = ['#4F6EF7','#06B6D4','#10B981','#F59E0B','#EF4444','#8B5CF6','#EC4899','#6366F1']
        scrollbar_h    = "rgba(100,120,180,0.25)"

    elif theme_name == "Dark":
        bg_main        = "#090B14"
        bg_card        = "rgba(20,24,42,0.82)"
        bg_input       = "rgba(30,35,60,0.90)"
        glass_bg       = "rgba(25,30,55,0.60)"
        glass_border   = "rgba(80,100,180,0.28)"
        glow_color     = "rgba(123,97,255,0.22)"
        text_main      = "#E8EAFF"
        text_muted     = "#6B7BB2"
        accent         = "#7B61FF"
        accent_hover   = "#A594FF"
        border         = "rgba(60,80,140,0.50)"
        chart_bg       = "rgba(20,24,42,0.82)"
        chart_text     = "#E8EAFF"
        chart_grid     = "#1E2A4A"
        palette        = ['#7B61FF','#FF6B8A','#20D9B1','#FFD166','#4ECDC4','#A8EDEA','#FF9F43','#6C5CE7']
        scrollbar_h    = "rgba(123,97,255,0.30)"

    else:  # Dracula (Default)
        bg_main        = "#13132A"
        bg_card        = "rgba(30,30,60,0.78)"
        bg_input       = "rgba(40,40,70,0.88)"
        glass_bg       = "rgba(35,35,68,0.62)"
        glass_border   = "rgba(148,153,195,0.22)"
        glow_color     = "rgba(189,147,249,0.20)"
        text_main      = "#F8F8F2"
        text_muted     = "#9499C3"
        accent         = "#BD93F9"
        accent_hover   = "#FF79C6"
        border         = "rgba(100,105,150,0.35)"
        chart_bg       = "rgba(30,30,60,0.78)"
        chart_text     = "#F8F8F2"
        chart_grid     = "#44475A"
        palette        = ['#BD93F9','#FF79C6','#8BE9FD','#50FA7B','#F1FA8C','#FFB86C','#FF5555','#6272A4']
        scrollbar_h    = "rgba(189,147,249,0.28)"

    stylesheet = f"""
    /* ── BASE ─────────────────────────────────────────────── */
    QWidget {{
        background-color: {bg_main};
        color: {text_main};
        font-family: {font_family};
        font-size: 14px;
    }}

    /* ── SCROLLBARS ───────────────────────────────────────── */
    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 4px 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {scrollbar_h};
        border-radius: 3px;
        min-height: 28px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {accent};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 6px;
    }}
    QScrollBar::handle:horizontal {{
        background: {scrollbar_h};
        border-radius: 3px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ── GLASS CARDS ──────────────────────────────────────── */
    QFrame#Card {{
        background-color: {bg_card};
        border-radius: 20px;
        border: 1px solid {glass_border};
    }}
    QFrame#GlassPanel {{
        background-color: {glass_bg};
        border-radius: 16px;
        border: 1px solid {glass_border};
    }}
    QFrame#StatCard {{
        background-color: {glass_bg};
        border-radius: 18px;
        border: 1px solid {glass_border};
    }}

    /* ── SIDEBAR ──────────────────────────────────────────── */
    QFrame#Sidebar {{
        background-color: {bg_card};
        border-radius: 20px;
        border: 1px solid {glass_border};
    }}

    /* ── INPUTS ───────────────────────────────────────────── */
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {bg_main};
        color: {text_main};
        padding: 10px 14px;
        border-radius: 12px;
        border: 1px solid {border};
        selection-background-color: {accent};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1.5px solid {accent};
        background-color: {bg_main};
    }}

    QLineEdit::placeholder {{
        color: {text_muted};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 28px;
    }}
    QComboBox::down-arrow {{
        width: 10px;
        height: 10px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {bg_main} !important;
        color: {text_main} !important;
        border: 1px solid {accent};
        selection-background-color: {accent};
        selection-color: {bg_main};
    }}
    /* The stubborn white box fix */
    QComboBox QListView, QComboBox QAbstractItemView, QComboBox QFrame {{
        background-color: {bg_main} !important;
        color: {text_main} !important;
        border: 1px solid {accent};
    }}
    QAbstractItemView {{
        background-color: {bg_main};
        color: {text_main};
        selection-background-color: {accent};
        selection-color: {bg_main};
        outline: none;
    }}
    QListView {{
        background-color: {bg_main} !important;
        color: {text_main} !important;
        border: 1px solid {accent};
        border-radius: 12px;
    }}

    QListView::item {{
        background-color: {bg_main};
        color: {text_main};
        padding: 10px;
        border-radius: 8px;
        margin: 2px;
    }}
    QListView::item:selected {{
        background-color: {accent};
        color: {bg_main};
    }}
    QListView::item:hover {{
        background-color: {glow_color};
        color: {accent};
    }}





    /* ── BUTTONS ──────────────────────────────────────────── */
    QPushButton {{
        background-color: {bg_input};
        color: {text_main};
        padding: 10px 20px;
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid {border};
    }}
    QPushButton:hover {{
        background-color: {accent};
        color: {bg_main};
        border: 1px solid {accent};
    }}
    QPushButton:pressed {{
        background-color: {accent_hover};
        border: 1px solid {accent_hover};
    }}
    QPushButton:disabled {{
        opacity: 0.4;
    }}

    /* ── PROGRESS BARS ────────────────────────────────────── */
    QProgressBar {{
        background-color: {bg_input};
        border-radius: 6px;
        border: none;
        height: 10px;
    }}
    QProgressBar::chunk {{
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {accent}, stop:1 {accent_hover}
        );
        border-radius: 6px;
    }}

    /* ── MISC ─────────────────────────────────────────────── */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    QSplitter::handle {{
        background-color: {border};
        width: 1px;
    }}
    QLabel {{
        background: transparent;
    }}
    QToolTip {{
        background-color: {bg_input};
        color: {text_main};
        border: 1px solid {border};
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 12px;
    }}
    """

    colors = {
        "bg_main":      bg_main,
        "bg_card":      bg_card,
        "bg_input":     bg_input,
        "glass_bg":     glass_bg,
        "glass_border": glass_border,
        "glow_color":   glow_color,
        "text_main":    text_main,
        "text_muted":   text_muted,
        "accent":       accent,
        "accent_hover": accent_hover,
        "border":       border,
        "chart_bg":     chart_bg,
        "chart_text":   chart_text,
        "chart_grid":   chart_grid,
        "palette":      palette,
    }

    return stylesheet, colors


def apply_theme(app, theme_name):
    stylesheet, colors = get_theme_stylesheet(theme_name)
    app.setStyleSheet(stylesheet)
    return colors
