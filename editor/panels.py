import time
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QRect, QPoint
from PyQt5.QtGui import (
    QColor, QPixmap, QPainter, QIcon, QFont, QFontDatabase,
    QBrush, QPen, QLinearGradient,
)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QColorDialog, QListWidget,
    QListWidgetItem, QSpinBox, QGridLayout, QComboBox,
    QScrollArea, QFrame, QToolButton, QAbstractItemView,
    QGroupBox, QLineEdit, QSizePolicy, QCheckBox,
    QProgressBar, QMenu, QInputDialog, QApplication, QToolTip,
)

from .layers import BLEND_MODES, AdjustmentLayer, GroupLayer


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
        self.list_widget.setIconSize(QSize(24, 24))
        self.list_widget.setSpacing(1)
        layout.addWidget(self.list_widget)

    def _make_layer_item_widget(self, i, layer):
        widget = QWidget()
        h = QHBoxLayout(widget)
        h.setContentsMargins(2, 1, 2, 1)
        h.setSpacing(4)

        thumb = QLabel()
        thumb.setFixedSize(24, 24)
        thumb.setScaledContents(True)
        try:
            thumb_img = layer.image.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            thumb.setPixmap(QPixmap.fromImage(thumb_img))
        except Exception:
            pass
        h.addWidget(thumb)

        vis_btn = QToolButton()
        vis_btn.setFixedSize(18, 18)
        vis_btn.setText("👁" if layer.visible else " ")
        vis_btn.setToolTip("Toggle visibility")
        vis_btn.clicked.connect(lambda checked, idx=i: self._toggle_visibility(idx))
        h.addWidget(vis_btn)

        lock_btn = QToolButton()
        lock_btn.setFixedSize(18, 18)
        lock_btn.setText("🔒" if layer.locked else " ")
        lock_btn.setToolTip("Toggle lock")
        lock_btn.clicked.connect(lambda checked, idx=i: self._toggle_lock(idx))
        h.addWidget(lock_btn)

        name_label = QLabel(layer.name)
        name_label.setFixedHeight(20)
        if isinstance(layer, AdjustmentLayer):
            name_label.setText(f"⚡ {layer.name}")
        elif isinstance(layer, GroupLayer):
            name_label.setText(f"📁 {layer.name}")
        h.addWidget(name_label, 1)

        return widget

    def refresh(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for i, layer in enumerate(canvas.layer_stack.layers):
            item = QListWidgetItem()
            item.setData(Qt.UserRole, i)
            widget = self._make_layer_item_widget(i, layer)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
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

    def _toggle_visibility(self, idx):
        canvas = self.get_canvas()
        if canvas and 0 <= idx < len(canvas.layer_stack.layers):
            layer = canvas.layer_stack.layers[idx]
            layer.visible = not layer.visible
            canvas._refresh()
            self.refresh()

    def _toggle_lock(self, idx):
        canvas = self.get_canvas()
        if canvas and 0 <= idx < len(canvas.layer_stack.layers):
            layer = canvas.layer_stack.layers[idx]
            layer.locked = not layer.locked
            self.refresh()

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
            canvas._refresh()

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


class GradientPanel(QWidget):
    gradientChanged = pyqtSignal()

    def __init__(self, canvas_getter, parent=None):
        super().__init__(parent)
        self.get_canvas = canvas_getter
        from .gradient_editor import GradientEditorWidget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        self.editor = GradientEditorWidget()
        self.editor.gradientChanged.connect(self._on_gradient_changed)
        layout.addWidget(self.editor)

    def _on_gradient_changed(self):
        canvas = self.get_canvas()
        if canvas:
            canvas.gradient_obj = self.editor.get_gradient()
        self.gradientChanged.emit()

    def refresh(self):
        canvas = self.get_canvas()
        if canvas and hasattr(canvas, 'gradient_obj'):
            self.editor.set_gradient(canvas.gradient_obj)


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


class BrushPanel(QWidget):
    brushSettingsChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        tip_row = QHBoxLayout()
        tip_row.addWidget(QLabel("Tip:"))
        self.tip_combo = QComboBox()
        self.tip_combo.addItems(["Circle", "Square", "Texture"])
        self.tip_combo.currentTextChanged.connect(self._on_change)
        tip_row.addWidget(self.tip_combo)
        layout.addLayout(tip_row)

        hard_row = QHBoxLayout()
        hard_row.addWidget(QLabel("Hardness:"))
        self.hardness_slider = QSlider(Qt.Horizontal)
        self.hardness_slider.setRange(0, 100)
        self.hardness_slider.setValue(100)
        self.hardness_slider.valueChanged.connect(self._on_change)
        hard_row.addWidget(self.hardness_slider)
        self.hardness_label = QLabel("100%")
        self.hardness_label.setFixedWidth(32)
        hard_row.addWidget(self.hardness_label)
        layout.addLayout(hard_row)
        self.hardness_slider.valueChanged.connect(
            lambda v: self.hardness_label.setText(f"{v}%")
        )

        space_row = QHBoxLayout()
        space_row.addWidget(QLabel("Spacing:"))
        self.spacing_slider = QSlider(Qt.Horizontal)
        self.spacing_slider.setRange(1, 100)
        self.spacing_slider.setValue(25)
        self.spacing_slider.valueChanged.connect(self._on_change)
        space_row.addWidget(self.spacing_slider)
        self.spacing_label = QLabel("25%")
        self.spacing_label.setFixedWidth(32)
        space_row.addWidget(self.spacing_label)
        layout.addLayout(space_row)
        self.spacing_slider.valueChanged.connect(
            lambda v: self.spacing_label.setText(f"{v}%")
        )

        flow_row = QHBoxLayout()
        flow_row.addWidget(QLabel("Flow:"))
        self.flow_slider = QSlider(Qt.Horizontal)
        self.flow_slider.setRange(1, 100)
        self.flow_slider.setValue(100)
        self.flow_slider.valueChanged.connect(self._on_change)
        flow_row.addWidget(self.flow_slider)
        self.flow_label = QLabel("100%")
        self.flow_label.setFixedWidth(32)
        flow_row.addWidget(self.flow_label)
        layout.addLayout(flow_row)
        self.flow_slider.valueChanged.connect(
            lambda v: self.flow_label.setText(f"{v}%")
        )

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(80, 80)
        self.preview_label.setStyleSheet("border: 1px solid #555; border-radius: 4px;")
        layout.addWidget(self.preview_label)

        self._brush_engine = None

    def set_brush_engine(self, engine):
        self._brush_engine = engine
        self._sync_from_engine()

    def _sync_from_engine(self):
        if not self._brush_engine:
            return

    def _on_change(self):
        if self._brush_engine:
            tip_name = self.tip_combo.currentText()
            hardness = self.hardness_slider.value() / 100.0
            if tip_name == "Circle":
                self._brush_engine.set_circle_tip(hardness)
            elif tip_name == "Square":
                self._brush_engine.set_square_tip(hardness)
            self._brush_engine.spacing = self.spacing_slider.value() / 100.0
            self._brush_engine.flow = self.flow_slider.value() / 100.0
            self._update_preview()
        self.brushSettingsChanged.emit()

    def _update_preview(self):
        if not self._brush_engine:
            return
        pix = self._brush_engine.make_preview(60)
        self.preview_label.setPixmap(pix)


class PathPanel(QWidget):
    def __init__(self, canvas_getter, parent=None):
        super().__init__(parent)
        self.get_canvas = canvas_getter
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        layout.addWidget(QLabel("Paths:"))
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._row_changed)
        layout.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        self.del_btn = QPushButton("Delete")
        self.del_btn.clicked.connect(self._delete_path)
        btn_row.addWidget(self.del_btn)

        self.fill_cb = QCheckBox("Fill")
        self.fill_cb.setChecked(True)
        self.fill_cb.stateChanged.connect(self._toggle_fill)
        btn_row.addWidget(self.fill_cb)

        self.stroke_cb = QCheckBox("Stroke")
        self.stroke_cb.stateChanged.connect(self._toggle_stroke)
        btn_row.addWidget(self.stroke_cb)

        self.vis_btn = QPushButton("Hide")
        self.vis_btn.clicked.connect(self._toggle_visible)
        btn_row.addWidget(self.vis_btn)

        layout.addLayout(btn_row)

        action_row = QHBoxLayout()
        self.to_sel_btn = QPushButton("To Selection")
        self.to_sel_btn.clicked.connect(self._to_selection)
        action_row.addWidget(self.to_sel_btn)

        self.stroke_btn = QPushButton("Stroke Path")
        self.stroke_btn.clicked.connect(self._stroke_path)
        action_row.addWidget(self.stroke_btn)

        layout.addLayout(action_row)

    def refresh(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        paths = canvas.get_active_paths()
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for i, path in enumerate(paths):
            vis = "V" if path.visible else "H"
            fill = "F" if path.fill else "NF"
            stroke = "S" if path.stroke else "NS"
            item = QListWidgetItem(f"Path {i+1} [{vis}|{fill}|{stroke}]")
            item.setData(Qt.UserRole, i)
            self.list_widget.addItem(item)
        lid = id(canvas.layer_stack.active) if canvas.layer_stack.active else -1
        idx = canvas.active_path_index.get(lid, 0)
        if 0 <= idx < self.list_widget.count():
            self.list_widget.setCurrentRow(idx)
        self.list_widget.blockSignals(False)
        self._update_controls()

    def _update_controls(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        path = canvas.get_active_path()
        if path:
            self.fill_cb.blockSignals(True)
            self.fill_cb.setChecked(path.fill)
            self.fill_cb.blockSignals(False)
            self.stroke_cb.blockSignals(True)
            self.stroke_cb.setChecked(path.stroke)
            self.stroke_cb.blockSignals(False)
            self.vis_btn.setText("Hide" if path.visible else "Show")

    def _row_changed(self, row):
        canvas = self.get_canvas()
        if canvas and row >= 0:
            lid = id(canvas.layer_stack.active)
            canvas.active_path_index[lid] = row
            canvas.update()
            self._update_controls()

    def _delete_path(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        paths = canvas.get_active_paths()
        idx = self.list_widget.currentRow()
        if 0 <= idx < len(paths):
            del paths[idx]
            canvas.update()
            self.refresh()

    def _toggle_fill(self, state):
        canvas = self.get_canvas()
        if not canvas:
            return
        path = canvas.get_active_path()
        if path:
            path.fill = bool(state)
            canvas.update()
            self.refresh()

    def _toggle_stroke(self, state):
        canvas = self.get_canvas()
        if not canvas:
            return
        path = canvas.get_active_path()
        if path:
            path.stroke = bool(state)
            canvas.update()
            self.refresh()

    def _toggle_visible(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        path = canvas.get_active_path()
        if path:
            path.visible = not path.visible
            canvas.update()
            self.refresh()

    def _to_selection(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        path = canvas.get_active_path()
        if path:
            qp = path.to_qpainterpath()
            canvas.selection_path = qp
            canvas.selection_mask = canvas._selection_mask_from_path(qp)
            canvas.selection_phase = 0
            canvas.viewport().update()

    def _stroke_path(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        layer = canvas.layer_stack.active
        if not layer or layer.locked:
            return
        path = canvas.get_active_path()
        if not path:
            return
        qp = path.to_qpainterpath()
        p = QPainter(layer.image)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(canvas.tool_color)
        c.setAlpha(int(255 * canvas.tool_opacity))
        pen = QPen(c, canvas.tool_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.strokePath(qp, pen)
        p.end()
        canvas._refresh()


class NavigatorPanel(QWidget):
    def __init__(self, canvas_getter, parent=None):
        super().__init__(parent)
        self.get_canvas = canvas_getter
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(120, 90)
        self.preview_label.setStyleSheet("""
            QLabel {
                background: #0a0a0a;
                border: 1px solid #222;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.preview_label)

        zoom_row = QHBoxLayout()
        zoom_out_btn = QPushButton("\u2212")
        zoom_out_btn.setFixedSize(24, 24)
        zoom_out_btn.clicked.connect(self._zoom_out)
        zoom_row.addWidget(zoom_out_btn)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setAlignment(Qt.AlignCenter)
        zoom_row.addWidget(self.zoom_label)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(24, 24)
        zoom_in_btn.clicked.connect(self._zoom_in)
        zoom_row.addWidget(zoom_in_btn)

        fit_btn = QPushButton("Fit")
        fit_btn.setFixedSize(36, 24)
        fit_btn.clicked.connect(self._zoom_fit)
        zoom_row.addWidget(fit_btn)

        layout.addLayout(zoom_row)

    def refresh(self):
        canvas = self.get_canvas()
        if not canvas:
            return
        composite = canvas.layer_stack.composite()
        if composite and not composite.isNull():
            preview = composite.scaled(160, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(QPixmap.fromImage(preview))

    def _zoom_in(self):
        canvas = self.get_canvas()
        if canvas:
            canvas.zoom_in()

    def _zoom_out(self):
        canvas = self.get_canvas()
        if canvas:
            canvas.zoom_out()

    def _zoom_fit(self):
        canvas = self.get_canvas()
        if canvas:
            canvas.zoom_fit()
