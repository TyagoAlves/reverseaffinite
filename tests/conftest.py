import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication


def pytest_configure():
    if QApplication.instance() is None:
        QApplication(sys.argv)
