from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QToolButton, QButtonGroup, QColorDialog,
)

from .tools import TOOL_LIST
from .tool_icons import get_tool_icon
from .i18n import _


class ToolPalette(QWidget):
    def __init__(self, canvas_getter, parent=None):
        super().__init__(parent)
        self.get_canvas = canvas_getter
        self.setFixedWidth(42)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(1)

        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)

        self.tool_buttons = {}

        for group_name, tools in TOOL_LIST:
            for i, tool_cls in enumerate(tools):
                btn = QToolButton()
                btn.setCheckable(True)
                btn.setToolTip(f"{tool_cls.name} ({tool_cls.shortcut})")
                icon = get_tool_icon(tool_cls.name)
                if not icon.isNull():
                    btn.setIcon(icon)
                    btn.setIconSize(QSize(20, 20))
                else:
                    btn.setText(tool_cls.shortcut)
                btn.setFixedSize(36, 26)
                btn.setStyleSheet("""
                    QToolButton {
                        border: 1px solid #2a2a2a; border-radius: 3px;
                        background: #1a1a1a;
                    }
                    QToolButton:checked {
                        background: #3a8ac4; border-color: #5a9ad4;
                    }
                    QToolButton:hover:!checked {
                        background: #2a2a2a; border-color: #555;
                    }
                """)
                btn.clicked.connect(lambda checked, t=tool_cls: self._select_tool(t))
                self.button_group.addButton(btn)
                layout.addWidget(btn)
                self.tool_buttons[tool_cls.name] = btn

            if group_name != TOOL_LIST[-1][0]:
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("color: #333; max-height: 1px; margin: 2px 6px;")
                layout.addWidget(sep)

        layout.addStretch()

        color_frame = QFrame()
        color_frame.setFixedSize(42, 66)
        color_layout = QVBoxLayout(color_frame)
        color_layout.setContentsMargins(4, 4, 4, 4)
        color_layout.setSpacing(1)
        color_layout.setAlignment(Qt.AlignCenter)

        self.fg_btn = QPushButton()
        self.fg_btn.setFixedSize(28, 28)
        self.fg_btn.setToolTip(_("Foreground Color"))
        self.fg_btn.setCursor(Qt.PointingHandCursor)
        self.bg_btn = QPushButton()
        self.bg_btn.setFixedSize(28, 28)
        self.bg_btn.setToolTip(_("Background Color"))
        self.bg_btn.setCursor(Qt.PointingHandCursor)

        self.fg_btn.clicked.connect(lambda: self._pick_color(True))
        self.bg_btn.clicked.connect(lambda: self._pick_color(False))

        self.fg_color = QColor(0, 0, 0)
        self.bg_color = QColor(255, 255, 255)
        self._update_swatches()

        fg_container = QWidget()
        fg_l = QHBoxLayout(fg_container)
        fg_l.setContentsMargins(0, 0, 0, 0)
        fg_l.setAlignment(Qt.AlignCenter)
        fg_l.addWidget(self.fg_btn)

        bg_container = QWidget()
        bg_l = QHBoxLayout(bg_container)
        bg_l.setContentsMargins(0, 0, 0, 0)
        bg_l.setAlignment(Qt.AlignCenter)
        bg_l.addWidget(self.bg_btn)

        color_layout.addWidget(fg_container)
        color_layout.addWidget(bg_container)

        self.swap_btn = QPushButton("\u2195")
        self.swap_btn.setFixedSize(16, 14)
        self.swap_btn.setToolTip(_("Swap colors"))
        self.swap_btn.setCursor(Qt.PointingHandCursor)
        self.swap_btn.setStyleSheet(
            "QPushButton { background: #333; border: 1px solid #555; border-radius: 2px; "
            "font-size: 9px; padding: 0px; }"
            "QPushButton:hover { background: #555; }"
        )
        self.swap_btn.clicked.connect(self._swap_colors)

        swap_container = QWidget()
        swap_l = QHBoxLayout(swap_container)
        swap_l.setContentsMargins(0, 0, 0, 0)
        swap_l.setAlignment(Qt.AlignCenter)
        swap_l.addWidget(self.swap_btn)

        color_layout.addWidget(swap_container)

        layout.addWidget(color_frame, 0, Qt.AlignCenter)

        if self.button_group.buttons():
            self.button_group.buttons()[0].setChecked(True)

    def _update_swatches(self):
        fg_border = "#888"
        bg_border = "#888"
        self.fg_btn.setStyleSheet(
            f"background-color: {self.fg_color.name()}; "
            f"border: 2px solid {fg_border}; border-radius: 3px;"
        )
        self.bg_btn.setStyleSheet(
            f"background-color: {self.bg_color.name()}; "
            f"border: 2px solid {bg_border}; border-radius: 3px;"
        )

    def _pick_color(self, fg):
        d = QColorDialog(self.fg_color if fg else self.bg_color, self)
        d.setWindowTitle(_("Select Color"))
        d.setOptions(QColorDialog.DontUseNativeDialog)
        d.setStyleSheet("""
            QColorDialog { background-color: #1a1a1a; color: #e0e0e0; }
            QColorDialog QLabel { color: #c0c0c0; }
            QColorDialog QSpinBox { background: #222; color: #d0d0d0; border: 1px solid #444; }
            QColorDialog QLineEdit { background: #222; color: #d0d0d0; border: 1px solid #444; }
            QColorDialog QPushButton { background: #333; color: #d0d0d0; border: 1px solid #555; padding: 4px 12px; border-radius: 3px; }
            QColorDialog QPushButton:hover { background: #444; }
            QColorDialog QComboBox { background: #222; color: #d0d0d0; border: 1px solid #444; }
            QColorDialog QComboBox QAbstractItemView { background: #222; color: #d0d0d0; selection-background-color: #3a8ac4; }
        """)
        if d.exec_() == QColorDialog.Accepted:
            c = d.selectedColor()
            if fg:
                self.fg_color = c
            else:
                self.bg_color = c
            self._update_swatches()
            canvas = self.get_canvas()
            if canvas:
                if fg:
                    canvas.set_foreground_color(c)
                else:
                    canvas.set_background_color(c)

    def _swap_colors(self):
        self.fg_color, self.bg_color = self.bg_color, self.fg_color
        self._update_swatches()
        canvas = self.get_canvas()
        if canvas:
            canvas.tool_color = self.fg_color
            canvas.bg_color = self.bg_color
            canvas.color_picked.emit(self.fg_color)

    def set_colors(self, fg, bg):
        self.fg_color = fg
        self.bg_color = bg
        self._update_swatches()

    def select_tool_by_name(self, tool_name):
        btn = self.tool_buttons.get(tool_name)
        if btn:
            btn.setChecked(True)

    def _select_tool(self, tool_cls):
        canvas = self.get_canvas()
        if canvas:
            canvas.set_tool(tool_cls.name)
