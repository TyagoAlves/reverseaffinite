from PyQt5.QtGui import QPalette, QColor


DARK_THEME = """
/* ===== Global ===== */
QMainWindow, QDialog {
    background-color: #1e1e1e;
    color: #d4d4d4;
}
QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-size: 12px;
}

/* ===== Menu Bar ===== */
QMenuBar {
    background-color: #2a2a2a;
    color: #d4d4d4;
    border-bottom: 1px solid #3a3a3a;
    padding: 2px 0;
}
QMenuBar::item {
    padding: 4px 12px;
    background: transparent;
    border-radius: 3px;
}
QMenuBar::item:selected {
    background: #4a8ac4;
    color: #fff;
}
QMenu {
    background-color: #2a2a2a;
    border: 1px solid #444;
    padding: 4px;
    border-radius: 4px;
}
QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 3px;
}
QMenu::item:selected {
    background: #4a8ac4;
    color: #fff;
}
QMenu::separator {
    height: 1px;
    background: #444;
    margin: 4px 8px;
}

/* ===== Tool Bar ===== */
QToolBar {
    background-color: #2a2a2a;
    border: none;
    border-bottom: 1px solid #3a3a3a;
    spacing: 4px;
    padding: 2px;
}
QToolBar::separator {
    width: 1px;
    background: #444;
    margin: 3px 4px;
}

/* ===== Dock Widget ===== */
QDockWidget {
    background-color: #252525;
    border: 1px solid #3a3a3a;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}
QDockWidget::title {
    background-color: #2a2a2a;
    padding: 6px 8px;
    border-bottom: 1px solid #3a3a3a;
    color: #d4d4d4;
    font-weight: bold;
    font-size: 11px;
}
QDockWidget::close-button, QDockWidget::float-button {
    padding: 0px;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #3a3a3a;
    color: #d4d4d4;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 5px 14px;
    min-height: 22px;
}
QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #6a8aba;
}
QPushButton:pressed {
    background-color: #4a8ac4;
    color: #fff;
}
QPushButton:disabled {
    background-color: #2a2a2a;
    color: #666;
    border-color: #3a3a3a;
}

QToolButton {
    background-color: #3a3a3a;
    color: #d4d4d4;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 2px 6px;
}
QToolButton:hover {
    background-color: #4a4a4a;
    border-color: #6a8aba;
}
QToolButton:checked {
    background-color: #4a8ac4;
    color: #fff;
    border-color: #6aaa4a;
}
QToolButton:disabled {
    background-color: #2a2a2a;
    color: #666;
}

/* ===== Combo Box ===== */
QComboBox {
    background-color: #333;
    color: #d4d4d4;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 3px 8px;
    min-height: 22px;
}
QComboBox:hover {
    border-color: #6a8aba;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox::down-arrow {
    image: none;
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #2a2a2a;
    border: 1px solid #444;
    selection-background-color: #4a8ac4;
    selection-color: #fff;
    outline: none;
}

/* ===== Spin Box ===== */
QSpinBox {
    background-color: #333;
    color: #d4d4d4;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 2px 6px;
    min-height: 20px;
}
QSpinBox:hover {
    border-color: #6a8aba;
}
QSpinBox::up-button, QSpinBox::down-button {
    border: none;
    background: transparent;
    width: 16px;
}

/* ===== Slider ===== */
QSlider::groove:horizontal {
    background: #3a3a3a;
    height: 6px;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #4a8ac4;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::handle:horizontal:hover {
    background: #5a9ad4;
}
QSlider::sub-page:horizontal {
    background: #4a8ac4;
    border-radius: 3px;
}

/* ===== Scroll Bar ===== */
QScrollBar:vertical {
    background: #2a2a2a;
    width: 10px;
    border: none;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #555;
    min-height: 30px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #6a8aba;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    border: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background: #2a2a2a;
    height: 10px;
    border: none;
    border-radius: 5px;
}
QScrollBar::handle:horizontal {
    background: #555;
    min-width: 30px;
    border-radius: 5px;
}
QScrollBar::handle:horizontal:hover {
    background: #6a8aba;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
    border: none;
}

/* ===== List Widget ===== */
QListWidget {
    background-color: #252525;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    outline: none;
}
QListWidget::item {
    padding: 4px 8px;
    border-radius: 3px;
    color: #d4d4d4;
}
QListWidget::item:selected {
    background-color: #4a8ac4;
    color: #fff;
}
QListWidget::item:hover:!selected {
    background-color: #3a3a3a;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #2a2a2a;
    border-top: 1px solid #3a3a3a;
    color: #aaa;
    font-size: 11px;
}
QStatusBar::item {
    border: none;
}

/* ===== Labels ===== */
QLabel {
    color: #d4d4d4;
    background: transparent;
}
QLabel:disabled {
    color: #666;
}

/* ===== Group Box ===== */
QGroupBox {
    background-color: #252525;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    margin-top: 14px;
    font-weight: bold;
    padding: 12px 8px 8px 8px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
    color: #d4d4d4;
}

/* ===== Line Edit ===== */
QLineEdit {
    background-color: #333;
    color: #d4d4d4;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 3px 6px;
    min-height: 20px;
}
QLineEdit:hover {
    border-color: #6a8aba;
}
QLineEdit:focus {
    border-color: #4a8ac4;
}

/* ===== Check Box ===== */
QCheckBox {
    color: #d4d4d4;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #555;
    border-radius: 3px;
    background: #333;
}
QCheckBox::indicator:checked {
    background: #4a8ac4;
    border-color: #4a8ac4;
}

/* ===== Splitter ===== */
QSplitter::handle {
    background: #3a3a3a;
    width: 2px;
}

/* ===== Message Box ===== */
QMessageBox {
    background-color: #1e1e1e;
}
QMessageBox QLabel {
    color: #d4d4d4;
}
QMessageBox QPushButton {
    min-width: 80px;
}

/* ===== Tab Widget/Bar ===== */
QTabWidget::pane {
    background-color: #252525;
    border: 1px solid #3a3a3a;
}
QTabBar::tab {
    background-color: #2a2a2a;
    color: #aaa;
    border: 1px solid #3a3a3a;
    border-bottom: none;
    padding: 6px 14px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}
QTabBar::tab:selected {
    background-color: #333;
    color: #fff;
}
QTabBar::tab:hover:!selected {
    background-color: #3a3a3a;
}

/* ===== Progress Bar ===== */
QProgressBar {
    background-color: #333;
    border: 1px solid #555;
    border-radius: 4px;
    text-align: center;
    color: #d4d4d4;
    height: 16px;
}
QProgressBar::chunk {
    background-color: #4a8ac4;
    border-radius: 3px;
}
"""


def apply_dark_theme(app):
    app.setStyleSheet(DARK_THEME)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, QColor(212, 212, 212))
    palette.setColor(QPalette.Base, QColor(37, 37, 37))
    palette.setColor(QPalette.AlternateBase, QColor(42, 42, 42))
    palette.setColor(QPalette.ToolTipBase, QColor(42, 42, 42))
    palette.setColor(QPalette.ToolTipText, QColor(212, 212, 212))
    palette.setColor(QPalette.Text, QColor(212, 212, 212))
    palette.setColor(QPalette.Button, QColor(58, 58, 58))
    palette.setColor(QPalette.ButtonText, QColor(212, 212, 212))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(74, 138, 196))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
