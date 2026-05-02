import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont, QFontDatabase, QIcon
from core.database import init_db
from ui.main_window import MainWindow
from core.settings import load_settings
from core.themes import apply_theme

def main():
    init_db()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/icon.png"))
    
    settings = load_settings()
    theme_colors = apply_theme(app, settings.get("theme", "Dracula"))

    # Pass app to MainWindow so it can be re-styled later if theme changes
    win = MainWindow(app, settings, theme_colors)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()