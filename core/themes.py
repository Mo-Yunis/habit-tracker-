def get_theme_stylesheet(theme_name):
    # Common variables
    font_family = "'Segoe UI', 'Inter', 'Roboto', Arial"
    
    if theme_name == "Light":
        bg_main = "#f4f5f7"
        bg_card = "#ffffff"
        bg_input = "#ffffff"
        text_main = "#172b4d"
        text_muted = "#5e6c84"
        accent = "#0052cc"
        accent_hover = "#0065ff"
        border = "#dfe1e6"
        chart_bg = "#ffffff"
        chart_text = "#172b4d"
        chart_grid = "#ebecf0"
        palette = ['#0052cc', '#00875a', '#ff991f', '#de350b', '#6554c0', '#00b8d9', '#ff5630', '#36b37e']
    elif theme_name == "Dark":
        bg_main = "#121212"
        bg_card = "#1e1e1e"
        bg_input = "#2d2d2d"
        text_main = "#ffffff"
        text_muted = "#aaaaaa"
        accent = "#bb86fc"
        accent_hover = "#ce93d8"
        border = "#333333"
        chart_bg = "#1e1e1e"
        chart_text = "#ffffff"
        chart_grid = "#333333"
        palette = ['#bb86fc', '#cf6679', '#03dac6', '#ffb300', '#2196f3', '#4caf50', '#e91e63', '#9c27b0']
    else: # Dracula (default)
        bg_main = "#282a36"
        bg_card = "#383a59"
        bg_input = "#44475a"
        text_main = "#f8f8f2"
        text_muted = "#6272a4"
        accent = "#bd93f9"
        accent_hover = "#ff79c6"
        border = "#6272a4"
        chart_bg = "#282a36"
        chart_text = "#f8f8f2"
        chart_grid = "#44475a"
        palette = ['#bd93f9', '#ff79c6', '#8be9fd', '#50fa7b', '#f1fa8c', '#ffb86c', '#ff5555', '#6272a4']

    # Define the stylesheet
    stylesheet = f"""
    QWidget {{
        background-color: {bg_main};
        color: {text_main};
        font-family: {font_family};
        font-size: 14px;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background-color: {bg_main};
        width: 12px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {bg_input};
        min-height: 20px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {text_muted};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QPushButton {{
        background-color: {bg_input};
        color: {text_main};
        padding: 8px 16px;
        border-radius: 8px;
        font-weight: bold;
        border: 1px solid {border};
    }}

    QPushButton:hover {{
        background-color: {text_muted};
        border: 1px solid {accent};
    }}

    QPushButton:pressed {{
        background-color: {accent};
        color: {bg_main};
    }}

    QLineEdit, QComboBox, QSpinBox {{
        background-color: {bg_input};
        color: {text_main};
        padding: 8px;
        border-radius: 8px;
        border: 1px solid {border};
    }}

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {accent};
    }}

    QComboBox::drop-down {{
        border: none;
    }}

    QProgressBar {{
        background-color: {bg_input};
        border-radius: 6px;
        text-align: center;
        color: transparent;
    }}

    QProgressBar::chunk {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {accent}, stop:1 {accent_hover});
        border-radius: 6px;
    }}

    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    
    QSplitter::handle {{
        background-color: {border};
    }}
    """
    
    colors = {
        "bg_main": bg_main,
        "bg_card": bg_card,
        "bg_input": bg_input,
        "text_main": text_main,
        "text_muted": text_muted,
        "accent": accent,
        "accent_hover": accent_hover,
        "border": border,
        "chart_bg": chart_bg,
        "chart_text": chart_text,
        "chart_grid": chart_grid,
        "palette": palette
    }
    
    return stylesheet, colors

def apply_theme(app, theme_name):
    stylesheet, colors = get_theme_stylesheet(theme_name)
    app.setStyleSheet(stylesheet)
    return colors
