import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase

from gui.main_window import MainWindow


def load_fonts():
    QFontDatabase.addApplicationFont("assets/fonts/Orbitron-Regular.ttf")
    QFontDatabase.addApplicationFont("assets/fonts/Orbitron-Bold.ttf")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HTTP Debugger Lite - Yashvir Gaming")

    load_fonts()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()