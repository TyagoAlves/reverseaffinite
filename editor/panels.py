from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QPixmap, QPainter, QIcon, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QColorDialog, QListWidget,
    QListWidgetItem, QSpinBox, QGridLayout, QComboBox,
    QScrollArea, QFrame, QToolButton, QAbstractItemView,
    QGroupBox, QLineEdit, QSizePolicy, QCheckBox,
)

from .layers import BLEND_MODES


class ColorSwatch(QPushButton):
    colorPicked = pyqtSignal(QColor)

    def __init__(self, color=QColor(0, 0, 0), parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(28, 28)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()
        self.clicked.connect(self._pick)

    def _update_style(self):
        r, g, b = self._color.red(), self._color.green(), self._color.blue()
        lum = (r * 299 + g * 587 + b * 114) / 1000
        border = "#333" if lum > 128 else "#999"
        self.setStyleSheet(
            f"background-color: {self._color.name()}; "
            f"border: 2px solid {border}; border-radius: 4px;"
        )

    def set_color(self, c):
        self._color = c
        self._update_style()

    def color(self):
        return self._color

    def _pick(self):
        c = QColorDialog.getColor(self._color, self)
        if c.isValid():
            self._color = c
            self._update_style()
            self.colorPicked.emit(c)


class ColorPanel(QWidget):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        swatch_row = QHBoxLayout()
        swatch_row.addWidget(QLabel("FG:"))
        self.fg = ColorSwatch(QColor(0, 0, 0))
        swatch_row.addWidget(self.fg)
        swatch_row.addWidget(QLabel("BG:"))
        self.bg = ColorSwatch(QColor(255, 255, 255))
        swatch_row.addWidget(self.bg)
        swap_btn = QPushButton("↔")
        swap_btn.setFixedSize(24, 24)
        swap_btn.clicked.connect(self._swap)
        swatch_row.addWidget(swap_btn)
        layout.addLayout(swatch_row)

        self.fg.colorPicked.connect(lambda c: self.colorChanged.emit(c))

        grid = QGridLayout()
        grid.setSpacing(2)

        self.r_spin = self._spin(0, 255)
        self.g_spin = self._spin(0, 255)
        self.b_spin = self._spin(0, 255)
        self.h_spin = self._spin(0, 360)
        self.s_spin = self._spin(0, 100)
        self.l_spin = self._spin(0, 100)
        self.hex_edit = QLineEdit("000000")
        self.hex_edit.setMaxLength(6)
        self.hex_edit.textChanged.connect(self._hex_changed)

        grid.addWidget(QLabel("R:"), 0, 0); grid.addWidget(self.r_spin, 0, 1)
        grid.addWidget(QLabel("G:"), 1, 0); grid.addWidget(self.g_spin, 1, 1)
        grid.addWidget(QLabel("B:"), 2, 0); grid.addWidget(self.b_spin, 2, 1)
        grid.addWidget(QLabel("H:"), 3, 0); grid.addWidget(self.h_spin, 3, 1)
        grid.addWidget(QLabel("S:"), 4, 0); grid.addWidget(self.s_spin, 4, 1)
        grid.addWidget(QLabel("L:"), 5, 0); grid.addWidget(self.l_spin, 5, 1)
        grid.addWidget(QLabel("#"), 6, 0); grid.addWidget(self.hex_edit, 6, 1)

        layout.addLayout(grid)

        for s in [self.r_spin, self.g_spin, self.b_spin]:
            s.valueChanged.connect(self._rgb_changed)
        for s in [self.h_spin, self.s_spin, self.l_spin]:
            s.valueChanged.connect(self._hsl_changed)

        self._updating = False

    def _spin(self, lo, hi):
        s = QSpinBox()
        s.setRange(lo, hi)
        s.setFixedHeight(20)
        return s

    def _swap(self):
        fg, bg = self.fg.color(), self.bg.color()
        self.fg.set_color(bg)
        self.bg.set_color(fg)
        self.colorChanged.emit(self.fg.color())

    def _rgb_changed(self):
        if self._updating:
            return
        c = QColor(self.r_spin.value(), self.g_spin.value(), self.b_spin.value())
        self._sync(c)

    def _hsl_changed(self):
        if self._updating:
            return
        c = QColor()
        c.setHsl(self.h_spin.value(), self.s_spin.value(), self.l_spin.value())
        self._sync(c)

    def _hex_changed(self, text):
        if self._updating:
            return
        if len(text) == 6:
            try:
                c = QColor(f"#{text}")
                if c.isValid():
                    self._sync(c)
            except Exception:
                pass

    def _sync(self, c):
        self._updating = True
        self.r_spin.setValue(c.red())
        self.g_spin.setValue(c.green())
        self.b_spin.setValue(c.blue())
        self.h_spin.setValue(max(0, c.hue()))
        self.s_spin.setValue(c.saturation())
        self.l_spin.setValue(c.lightness())
        self.hex_edit.setText(c.name().lstrip("#"))
        self._updating = False
        self.fg.set_color(c)
        self.colorChanged.emit(c)

    def set_color(self, c):
        self._sync(c)


class LayerPanel(QWidget):
    layerChanged = pyqtSignal(int)

    def __init__(self, canvas_getter, parent=None):
        super().__init__(parent)
        self.get_canvas = canvas_getter
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self.blend_combo = QComboBox()
        self.blend_combo.addItems(BLEND_MODES)
        self.blend_combo.currentTextChanged.connect(self._blend_changed)
        mode_row.addWidget(self.blend_combo)
        layout.addLayout(mode_row)

        opacity_row = QHBoxLayout()
        opacity_row.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self._opacity_changed)
        opacity_row.addWidget(self.opacity_slider)
        self.opacity_label = QLabel("100%")
        self.opacity_label.setFixedWidth(32)
        opacity_row.addWidget(self.opacity_label)
        layout.addLayout(opacity_row)

        btn_row = QHBoxLayout()
        self.add_btn = QToolButton(); self.add_btn.setText("+")
        self.add_btn.clicked.connect(self._add_layer)
        self.del_btn = QToolButton(); self.del_btn.setText("−")
        self.del_btn.clicked.connect(self._del_layer)
        self.dup_btn = QToolButton(); self.dup_btn.setText("⧉")
        self.dup_btn.clicked.connect(self._dup_layer)
        self.up_btn = QToolButton(); self.up_btn.setText("↑")
        self.up_btn.clicked.connect(self._move_up)
        self.down_btn = QToolButton(); self.down_btn.setText("↓")
        self.down_btn.clicked.connect(self._move_down)

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.del_btn)
        btn_row.addWidget(self.dup_btn)
        btn_row.addWidget(self.up_btn)
        btn_row.addWidget(self.down_btn)
        layout.addLayout(btn_row)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.currentRowChanged.connect(self._row_changed)
        layout.addWidget(self.list_widget)

    def refresh(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for i, layer in enumerate(canvas.layer_stack.layers):
            vis = "[V]" if layer.visible else "[ ]"
            lock = "[L]" if layer.locked else ""
            prefix = "[F] " if hasattr(layer, 'filter_func') and layer.filter_func else ""
            item = QListWidgetItem(f"{prefix}{vis}{lock} {layer.name}")
            item.setData(Qt.UserRole, i)
            self.list_widget.addItem(item)
        if 0 <= canvas.layer_stack.active_index < self.list_widget.count():
            self.list_widget.setCurrentRow(canvas.layer_stack.active_index)
        self.list_widget.blockSignals(False)

        active = canvas.layer_stack.active
        if active:
            self.blend_combo.blockSignals(True)
            idx = self.blend_combo.findText(active.blend_mode)
            if idx >= 0:
                self.blend_combo.setCurrentIndex(idx)
            self.blend_combo.blockSignals(False)
            self.opacity_slider.blockSignals(True)
            self.opacity_slider.setValue(int(active.opacity * 100))
            self.opacity_label.setText(f"{int(active.opacity * 100)}%")
            self.opacity_slider.blockSignals(False)

    def _row_changed(self, row):
        canvas = self.get_canvas()
        if canvas and row >= 0:
            canvas.layer_stack.active_index = row
            canvas._refresh()
            self.refresh()

    def _blend_changed(self, mode):
        canvas = self.get_canvas()
        if canvas and canvas.layer_stack.active:
            canvas.layer_stack.active.blend_mode = mode

    def _opacity_changed(self, val):
        canvas = self.get_canvas()
        if canvas and canvas.layer_stack.active:
            canvas.layer_stack.active.opacity = val / 100.0
            self.opacity_label.setText(f"{val}%")
            canvas._refresh()

    def _add_layer(self):
        canvas = self.get_canvas()
        if canvas:
            canvas._save_state("New layer")
            canvas.layer_stack.add_layer()
            canvas._refresh()
            self.refresh()

    def _del_layer(self):
        canvas = self.get_canvas()
        if canvas:
            idx = self.list_widget.currentRow()
            if idx >= 0:
                canvas._save_state("Delete layer")
                canvas.layer_stack.remove_layer(idx)
                canvas._refresh()
                self.refresh()

    def _dup_layer(self):
        canvas = self.get_canvas()
        if canvas:
            idx = self.list_widget.currentRow()
            if idx >= 0:
                canvas._save_state("Duplicate layer")
                canvas.layer_stack.duplicate_layer(idx)
                canvas._refresh()
                self.refresh()

    def _move_up(self):
        canvas = self.get_canvas()
        if canvas:
            idx = self.list_widget.currentRow()
            if idx > 0:
                canvas._save_state("Reorder layer")
                canvas.layer_stack.move_layer(idx, idx - 1)
                canvas._refresh()
                self.refresh()

    def _move_down(self):
        canvas = self.get_canvas()
        if canvas:
            idx = self.list_widget.currentRow()
            if 0 <= idx < len(canvas.layer_stack.layers) - 1:
                canvas._save_state("Reorder layer")
                canvas.layer_stack.move_layer(idx, idx + 1)
                canvas._refresh()
                self.refresh()


class HistoryPanel(QWidget):
    def __init__(self, canvas_getter, parent=None):
        super().__init__(parent)
        self.get_canvas = canvas_getter
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.count_label = QLabel("History: 0 entries")
        layout.addWidget(self.count_label)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._row_changed)
        layout.addWidget(self.list_widget)

    def refresh(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        history = canvas.history
        self.list_widget.blockSignals(True)
        cur_row = self.list_widget.currentRow()
        self.list_widget.clear()
        for i, entry in enumerate(history.stack):
            item = QListWidgetItem(entry.description)
            item.setData(Qt.UserRole, i)
            self.list_widget.addItem(item)
        if 0 <= history.index < self.list_widget.count():
            self.list_widget.setCurrentRow(history.index)
        self.list_widget.blockSignals(False)
        self.count_label.setText(f"History: {len(history.stack)} entries")

    def _row_changed(self, row):
        if row < 0:
            return
        canvas = self.get_canvas()
        if not canvas:
            return
        history = canvas.history
        if row != history.index:
            history.jump_to(canvas.layer_stack, row)
            canvas._refresh()

    def set_canvas(self, canvas_getter):
        self.get_canvas = canvas_getter


class ToolOptionsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        layout.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 5000)
        self.size_spin.setValue(3)
        self.size_spin.setFixedWidth(60)
        layout.addWidget(self.size_spin)

        layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(1, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setFixedWidth(80)
        layout.addWidget(self.opacity_slider)

        layout.addWidget(QLabel("Flow:"))
        self.flow_slider = QSlider(Qt.Horizontal)
        self.flow_slider.setRange(1, 100)
        self.flow_slider.setValue(100)
        self.flow_slider.setFixedWidth(80)
        layout.addWidget(self.flow_slider)

        layout.addWidget(QLabel("Font:"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(QFontDatabase().families())
        self.font_combo.setCurrentText("Arial")
        self.font_combo.setFixedWidth(120)
        layout.addWidget(self.font_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(1, 999)
        self.font_size_spin.setValue(32)
        self.font_size_spin.setFixedWidth(50)
        layout.addWidget(self.font_size_spin)

        self.bold_btn = QToolButton()
        self.bold_btn.setText("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setFixedSize(24, 24)
        layout.addWidget(self.bold_btn)

        self.italic_btn = QToolButton()
        self.italic_btn.setText("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setFixedSize(24, 24)
        layout.addWidget(self.italic_btn)

        self.underline_btn = QToolButton()
        self.underline_btn.setText("U")
        self.underline_btn.setCheckable(True)
        self.underline_btn.setFixedSize(24, 24)
        layout.addWidget(self.underline_btn)

        layout.addStretch()
