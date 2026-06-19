#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from editor.app_ui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("reverseaffinite")
    app.setOrganizationName("reverseaffinite")
    app.setApplicationDisplayName("reverseaffinite Photo")

    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.setWindowTitle("reverseaffinite Photo - [Untitled]")
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
