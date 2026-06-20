import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTabWidget, QDockWidget, QToolBar, QAction, QStatusBar, QMenuBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

from reverseaffinity.i18n import _
from reverseaffinity.shared.resources import apply_dark_theme
from editor.timeline_widget import TimelineWidget
from editor.transport_bar import TransportBar


class VideoMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen().availableSize()
        self.resize(int(screen.width() * 0.75), int(screen.height() * 0.8))
        apply_dark_theme(self)

        mbar = self.menuBar()
        file_m = mbar.addMenu(_("&File"))
        file_m.addAction(_("&New Project"), self.new_project, "Ctrl+N")
        file_m.addAction(_("&Open Project"), self.open_project, "Ctrl+O")
        file_m.addAction(_("&Save"), self.save_project, "Ctrl+S")
        file_m.addAction(_("Save &As..."), self.save_as, "Ctrl+Shift+S")
        file_m.addSeparator()
        file_m.addAction(_("E&xit"), self.close, "Ctrl+Q")

        edit_m = mbar.addMenu(_("&Edit"))
        edit_m.addAction(_("&Undo"), self.undo, "Ctrl+Z")
        edit_m.addAction(_("&Redo"), self.redo, "Ctrl+Shift+Z")

        timeline_m = mbar.addMenu(_("&Timeline"))
        timeline_m.addAction(_("Add &Track"), self.add_track)
        timeline_m.addAction(_("Split Clip"), self.split_clip, "Ctrl+K")
        timeline_m.addAction(_("Ripple Delete"), self.ripple_delete, "Shift+Del")

        view_m = mbar.addMenu(_("&View"))
        view_m.addAction(_("Toggle &Fullscreen"), self.toggle_fullscreen, "F11")

        # Toolbar
        tb = QToolBar(_("Transport"))
        self.addToolBar(tb)
        tb.addAction(_("Play"), self.toggle_play, "Space")

        # Central widget
        self.timeline = TimelineWidget()
        self.transport = TransportBar()
        transport_visible = True

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Preview area placeholder
        self.preview_label = QLabel(_("Video Preview"))
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        self.preview_label.setStyleSheet("background-color: #111; color: #555; font-size: 24px;")
        layout.addWidget(self.preview_label, 1)

        layout.addWidget(self.transport)
        layout.addWidget(self.timeline, 1)
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.statusBar().showMessage(_("Ready"))

    def new_project(self): pass
    def open_project(self): pass
    def save_project(self): pass
    def save_as(self): pass
    def undo(self): pass
    def redo(self): pass
    def add_track(self): pass
    def split_clip(self): pass
    def ripple_delete(self): pass
    def toggle_fullscreen(self): self.showFullScreen() if not self.isFullScreen() else self.showNormal()
    def toggle_play(self): pass


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("reverseaffinity Video")
    win = VideoMainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
