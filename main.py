#!/usr/bin/env python3
"""Reverseaffinity - Photo Editor / Launcher"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon


def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "home"

    if mode in ("photo", "editor", "p"):
        from editor.app_ui import MainWindow
        from editor.resources import apply_dark_theme
        from editor.i18n import _

        app = QApplication(sys.argv)
        app.setApplicationName("reverseaffinity")
        app.setOrganizationName("reverseaffinity")
        app.setApplicationDisplayName("reverseaffinity Photo")

        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.svg")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        apply_dark_theme(app)

        window = MainWindow()
        window.setWindowTitle(_("reverseaffinity Photo - [Untitled]"))
        window.show()
        sys.exit(app.exec_())

    elif mode in ("video", "v"):
        from reverseaffinity.video import run_video
        run_video()

    elif mode in ("effects", "e"):
        from reverseaffinity.effects import run_effects
        run_effects()

    else:
        from reverseaffinity.home import main as home_main
        home_main()


if __name__ == "__main__":
    main()
