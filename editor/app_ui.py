from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QKeySequence, QFont, QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QColorDialog,
    QToolBar, QToolButton, QSpinBox, QLabel, QComboBox,
    QSlider, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QInputDialog, QMenu, QStatusBar, QDockWidget,
    QButtonGroup, QFrame, QScroller, QScrollArea,
    QSplitter, QDialog, QGridLayout, QCheckBox, QGroupBox,
    QApplication,
)

from .canvas import CanvasView
from .panels import ColorPanel, LayerPanel, HistoryPanel, ToolOptionsPanel
from .tools import TOOL_LIST


class ToolPalette(QWidget):
    """Vertical tool palette on the left side (like Photoshop/Affinity)."""

    def __init__(self, canvas_getter, parent=None):
        super().__init__(parent)
        self.get_canvas = canvas_getter
        self.setFixedWidth(44)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(1)

        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)

        self.tool_buttons = {}

        for group_name, tools in TOOL_LIST:
            label = QLabel(group_name)
            label.setStyleSheet("color: #888; font-size: 9px; padding: 2px 0;")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

            for tool_cls in tools:
                btn = QToolButton()
                btn.setCheckable(True)
                btn.setToolTip(f"{tool_cls.name} ({tool_cls.shortcut})")
                btn.setText(tool_cls.shortcut)
                btn.setFixedSize(36, 28)
                btn.setStyleSheet("""
                    QToolButton { 
                        border: 1px solid #555; border-radius: 3px; 
                        font-weight: bold; font-size: 11px;
                        background: #3a3a3a; color: #ccc;
                    }
                    QToolButton:checked { 
                        background: #4a6a9a; color: #fff; border-color: #6a8aba;
                    }
                    QToolButton:hover { background: #4a4a4a; }
                """)
                btn.clicked.connect(lambda checked, t=tool_cls: self._select_tool(t))
                self.button_group.addButton(btn)
                layout.addWidget(btn)
                self.tool_buttons[tool_cls.name] = btn

        layout.addStretch()

        # Default: first tool selected
        if self.button_group.buttons():
            self.button_group.buttons()[0].setChecked(True)

    def _select_tool(self, tool_cls):
        canvas = self.get_canvas()
        if canvas:
            canvas.set_tool(tool_cls.name)


class FilterGalleryDialog(QDialog):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setWindowTitle("Filter Gallery")
        self.resize(800, 500)

        layout = QHBoxLayout(self)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        categories = {
            "Adjustments": [
                ("Brightness / Contrast", self._bc),
                ("Hue / Saturation", self._hs),
                ("Levels", self._levels),
                ("Grayscale", lambda: self._apply_filter("grayscale")),
                ("Invert", lambda: self._apply_filter("invert")),
                ("Sepia", lambda: self._apply_filter("sepia")),
            ],
            "Blur": [
                ("Gaussian Blur", self._blur),
            ],
            "Sharpen": [
                ("Sharpen", self._sharpen),
                ("Edge Detect", lambda: self._apply_filter("edge_detect")),
            ],
            "Stylize": [
                ("Pixelate", self._pixelate),
                ("Posterize", self._posterize),
            ],
        }

        for cat_name, items in categories.items():
            grp = QGroupBox(cat_name)
            grp_layout = QVBoxLayout(grp)
            for btn_name, callback in items:
                btn = QPushButton(btn_name)
                btn.clicked.connect(callback)
                grp_layout.addWidget(btn)
            left_layout.addWidget(grp)

        left_layout.addStretch()

        self.preview_label = QLabel("Preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background: #222; border: 1px solid #555;")

        layout.addWidget(left_panel, 1)
        layout.addWidget(self.preview_label, 2)

    def _apply_filter(self, name):
        import editor.filters as f
        func = getattr(f, name, None)
        if func and self.canvas.layer_stack.active:
            self.canvas._save_state(name.replace("_", " ").title())
            self.canvas.layer_stack.active.image = func(self.canvas.layer_stack.active.image)
            self.canvas._refresh()

    def _bc(self):
        self._show_slider_dialog("Brightness / Contrast", [
            ("Brightness", -255, 255, 0),
            ("Contrast", 0, 300, 100),
        ], lambda vals: self._apply_multi([
            ("brightness", vals[0]),
            ("contrast", vals[1] / 100.0),
        ]))

    def _hs(self):
        self._show_slider_dialog("Hue / Saturation", [
            ("Hue", -180, 180, 0),
            ("Saturation", 0, 300, 100),
            ("Lightness", -100, 100, 0),
        ], lambda vals: self._apply_multi([
            ("hue_saturation", vals[0], vals[1] / 100.0, vals[2]),
        ]))

    def _levels(self):
        self._show_slider_dialog("Levels", [
            ("Shadow", 0, 255, 0),
            ("Mid (gamma)", 10, 990, 100),
            ("Highlight", 0, 255, 255),
        ], lambda vals: self._apply_multi([
            ("levels", vals[0], vals[1] / 100.0, vals[2]),
        ]))

    def _blur(self):
        r, ok = QInputDialog.getInt(self, "Gaussian Blur", "Radius:", 3, 1, 100)
        if ok:
            self._apply_filter_arg("gaussian_blur", r)

    def _sharpen(self):
        a, ok = QInputDialog.getDouble(self, "Sharpen", "Amount:", 1.0, 0.1, 10.0)
        if ok:
            self._apply_filter_arg("sharpen", a)

    def _pixelate(self):
        s, ok = QInputDialog.getInt(self, "Pixelate", "Block Size:", 8, 2, 200)
        if ok:
            self._apply_filter_arg("pixelate", s)

    def _posterize(self):
        l, ok = QInputDialog.getInt(self, "Posterize", "Levels:", 4, 2, 64)
        if ok:
            self._apply_filter_arg("posterize", l)

    def _apply_filter_arg(self, name, *args):
        import editor.filters as f
        func = getattr(f, name, None)
        if func and self.canvas.layer_stack.active:
            self.canvas._save_state(name.replace("_", " ").title())
            self.canvas.layer_stack.active.image = func(self.canvas.layer_stack.active.image, *args)
            self.canvas._refresh()

    def _apply_multi(self, steps):
        import editor.filters as f
        layer = self.canvas.layer_stack.active
        if not layer:
            return
        self.canvas._save_state("Filter")
        img = layer.image
        for name, *args in steps:
            func = getattr(f, name, None)
            if func:
                img = func(img, *args)
        layer.image = img
        self.canvas._refresh()

    def _show_slider_dialog(self, title, sliders, on_apply):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)

        spinboxes = []
        for label, lo, hi, default in sliders:
            row = QHBoxLayout()
            row.addWidget(QLabel(label + ":"))
            s = QSlider(Qt.Horizontal)
            s.setRange(lo, hi)
            s.setValue(default)
            row.addWidget(s)
            layout.addLayout(row)
            spinboxes.append(s)

        btn = QPushButton("Apply")
        btn.clicked.connect(lambda: (on_apply([s.value() for s in spinboxes]), dialog.close()))
        layout.addWidget(btn)
        dialog.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1400, 900)

        self.canvas = CanvasView(self)
        self.setCentralWidget(self.canvas)

        # Tool palette (left)
        self.tool_palette = ToolPalette(lambda: self.canvas)
        self.addToolBar(Qt.LeftToolBarArea, self._make_toolbar_wrapper(self.tool_palette))

        # Tool options bar (top)
        self.tool_options = QToolBar("Tool Options")
        self.tool_options.setMovable(False)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(1, 5000)
        self.size_spin.setValue(3)
        self.size_spin.setFixedWidth(60)
        self.size_spin.valueChanged.connect(self.canvas.set_tool_size)
        self.tool_options.addWidget(QLabel("  Size:"))
        self.tool_options.addWidget(self.size_spin)

        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(1, 100)
        self.opacity_spin.setValue(100)
        self.opacity_spin.setSuffix("%")
        self.opacity_spin.setFixedWidth(55)
        self.opacity_spin.valueChanged.connect(self.canvas.set_tool_opacity)
        self.tool_options.addWidget(QLabel("  Opacity:"))
        self.tool_options.addWidget(self.opacity_spin)

        self.tool_options.addSeparator()
        self.color_btn = QPushButton()
        self.color_btn.setFixedSize(28, 28)
        self.color_btn.setStyleSheet("background-color: #000; border: 1px solid #888; border-radius: 3px;")
        self.color_btn.clicked.connect(self._pick_color)
        self.tool_options.addWidget(QLabel("  Color:"))
        self.tool_options.addWidget(self.color_btn)

        self.addToolBar(self.tool_options)

        # Color panel (right dock)
        self.color_panel = ColorPanel()
        self.color_panel.colorChanged.connect(self.canvas.set_foreground_color)
        cdock = QDockWidget("Color", self)
        cdock.setWidget(self.color_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, cdock)

        # Layer panel (right dock)
        self.layer_panel = LayerPanel(lambda: self.canvas)
        ldock = QDockWidget("Layers", self)
        ldock.setWidget(self.layer_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, ldock)

        # Navigator (right dock, bottom)
        nav_label = QLabel("Navigator")
        nav_label.setAlignment(Qt.AlignCenter)
        nav_label.setStyleSheet("background: #333; min-height: 120px;")
        ndock = QDockWidget("Navigator", self)
        ndock.setWidget(nav_label)
        self.addDockWidget(Qt.RightDockWidgetArea, ndock)

        # History panel
        hp = HistoryPanel(lambda: self.canvas.history)
        hdock = QDockWidget("History", self)
        hdock.setWidget(hp)
        self.addDockWidget(Qt.RightDockWidgetArea, hdock)

        self.create_menus()
        self.create_statusbar()

        self.canvas.mouse_moved.connect(self._update_coords)
        self.canvas.status_changed.connect(self.statusBar().showMessage)
        self.canvas.color_picked.connect(self._sync_color_btn)
        self.canvas.layer_stack.layers = self.canvas.layer_stack.layers  # force ref

        self.current_path = None

    def _make_toolbar_wrapper(self, widget):
        tb = QToolBar("Tools")
        tb.setMovable(False)
        tb.addWidget(widget)
        return tb

    def _sync_color_btn(self, color):
        self.color_btn.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #888; border-radius: 3px;"
        )

    def _pick_color(self):
        color = QColorDialog.getColor(self.canvas.tool_color, self)
        if color.isValid():
            self.canvas.set_foreground_color(color)
            self._sync_color_btn(color)
            self.color_panel.set_color(color)

    def _update_coords(self, x, y):
        self.coord_label.setText(f"X: {int(x):4d}  Y: {int(y):4d}")
        try:
            c = self.canvas.get_pixel_color(self.canvas.last_point or self.canvas.mapToScene(self.canvas.rect().center()))
            if c:
                self.info_label.setText(f"R:{c.red():3d} G:{c.green():3d} B:{c.blue():3d}")
        except:
            pass

    def create_menus(self):
        mb = self.menuBar()

        file_m = mb.addMenu("&File")
        file_m.addAction("&New...", self._new_file, QKeySequence.New)
        file_m.addAction("&Open...", self._open_file, QKeySequence.Open)
        file_m.addSeparator()
        file_m.addAction("&Save", self._save_file, QKeySequence.Save)
        file_m.addAction("Save &As...", self._save_as_file, QKeySequence("Ctrl+Shift+S"))
        file_m.addSeparator()
        exp_m = file_m.addMenu("&Export")
        exp_m.addAction("Export as &PNG...", self._export_png)
        exp_m.addAction("Export as &JPEG...", self._export_jpg)
        file_m.addSeparator()
        file_m.addAction("&Close", self.close, QKeySequence("Ctrl+Q"))

        edit_m = mb.addMenu("&Edit")
        edit_m.addAction("&Undo", self._undo, QKeySequence.Undo)
        edit_m.addAction("&Redo", self._redo, QKeySequence("Ctrl+Shift+Z"))
        edit_m.addSeparator()
        edit_m.addAction("&Fill...", self._fill)
        edit_m.addAction("&Clear", self._clear)
        edit_m.addSeparator()
        edit_m.addAction("&Preferences...", lambda: None)

        img_m = mb.addMenu("&Image")
        img_m.addAction("&Resize...", self._resize)
        img_m.addAction("&Canvas Size...", self._canvas_size)
        img_m.addSeparator()
        img_m.addAction("&Flatten", self._flatten)

        layer_m = mb.addMenu("&Layer")
        layer_m.addAction("&New Layer", self._new_layer, QKeySequence("Ctrl+Shift+N"))
        layer_m.addAction("&Duplicate Layer", self._dup_layer)
        layer_m.addAction("&Delete Layer", self._del_layer)
        layer_m.addSeparator()
        layer_m.addAction("Merge &Visible", self._merge_visible)
        layer_m.addAction("&Flatten Image", self._flatten)

        filter_m = mb.addMenu("F&ilter")
        filter_m.addAction("&Filter Gallery...", self._show_filter_gallery)

        view_m = mb.addMenu("&View")
        view_m.addAction("Zoom &In", self.canvas.zoom_in, QKeySequence("Ctrl++"))
        view_m.addAction("Zoom &Out", self.canvas.zoom_out, QKeySequence("Ctrl+-"))
        view_m.addAction("Zoom to &100%", self.canvas.zoom_100, QKeySequence("Ctrl+1"))
        view_m.addAction("&Fit to Screen", self.canvas.zoom_fit, QKeySequence("Ctrl+0"))
        view_m.addSeparator()
        ga = view_m.addAction("Show &Grid")
        ga.setCheckable(True)
        ga.triggered.connect(lambda v: setattr(self.canvas, 'show_grid', v))
        view_m.addAction("&Snap to Grid")
        view_m.addSeparator()
        view_m.addAction("&Reset View", self.canvas.zoom_fit)

    def create_statusbar(self):
        sb = self.statusBar()
        sb.showMessage("Ready")
        self.coord_label = QLabel("X:    0  Y:    0")
        self.info_label = QLabel("")
        sb.addPermanentWidget(self.coord_label)
        sb.addPermanentWidget(self.info_label)

    def _new_file(self):
        w, ok = QInputDialog.getInt(self, "New Image", "Width:", 1920, 1, 20000)
        if not ok:
            return
        h, ok = QInputDialog.getInt(self, "New Image", "Height:", 1080, 1, 20000)
        if not ok:
            return
        self.canvas.new_image(w, h)
        self.current_path = None
        self.setWindowTitle(f"reverseaffinite Photo - [Untitled {w}x{h}]")
        self.layer_panel.refresh()

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.psd);;All Files (*)"
        )
        if path and self.canvas.open_image(path):
            self.current_path = path
            self.setWindowTitle(f"reverseaffinite Photo - [{path}]")
            self.statusBar().showMessage(f"Opened: {path}")
            self.layer_panel.refresh()

    def _save_file(self):
        if self.current_path:
            self.canvas.save_image(self.current_path)
            self.statusBar().showMessage(f"Saved: {self.current_path}")
        else:
            self._save_as_file()

    def _save_as_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;TIFF (*.tiff);;WebP (*.webp);;BMP (*.bmp)"
        )
        if path:
            self.canvas.save_image(path)
            self.current_path = path
            self.setWindowTitle(f"reverseaffinite Photo - [{path}]")
            self.statusBar().showMessage(f"Saved: {path}")

    def _export_png(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", "PNG (*.png)")
        if path:
            self.canvas.export_png(path)

    def _export_jpg(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export as JPEG", "", "JPEG (*.jpg *.jpeg)")
        if path:
            self.canvas.export_jpg(path)

    def _undo(self):
        if self.canvas.history.can_undo():
            self.canvas.history.undo(self.canvas.layer_stack)
            self.canvas._refresh()
            self.layer_panel.refresh()

    def _redo(self):
        if self.canvas.history.can_redo():
            self.canvas.history.redo(self.canvas.layer_stack)
            self.canvas._refresh()
            self.layer_panel.refresh()

    def _fill(self):
        layer = self.canvas.layer_stack.active
        if not layer or layer.locked:
            return
        color = QColorDialog.getColor(self.canvas.tool_color, self)
        if color.isValid():
            self.canvas._save_state("Fill")
            layer.image.fill(color)
            self.canvas._refresh()

    def _clear(self):
        layer = self.canvas.layer_stack.active
        if not layer or layer.locked:
            return
        self.canvas._save_state("Clear")
        layer.image.fill(Qt.transparent if layer.name != "Background" else Qt.white)
        self.canvas._refresh()

    def _resize(self):
        img = self.canvas.layer_stack.composite()
        w, ok1 = QInputDialog.getInt(self, "Resize", "Width:", img.width(), 1, 50000)
        if not ok1:
            return
        h, ok2 = QInputDialog.getInt(self, "Resize", "Height:", img.height(), 1, 50000)
        if not ok2:
            return
        self.canvas._save_state("Resize")
        for layer in self.canvas.layer_stack.layers:
            layer.image = layer.image.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.canvas._refresh()

    def _canvas_size(self):
        img = self.canvas.layer_stack.composite()
        w, ok1 = QInputDialog.getInt(self, "Canvas Size", "Width:", img.width(), 1, 50000)
        if not ok1:
            return
        h, ok2 = QInputDialog.getInt(self, "Canvas Size", "Height:", img.height(), 1, 50000)
        if not ok2:
            return
        self.canvas._save_state("Canvas Size")
        for layer in self.canvas.layer_stack.layers:
            new_img = QImage(w, h, QImage.Format_ARGB32)
            new_img.fill(Qt.transparent)
            p = __import__('PyQt5.QtGui', fromlist=['QPainter']).QPainter(new_img)
            p.drawImage(0, 0, layer.image)
            p.end()
            layer.image = new_img
        self.canvas._refresh()

    def _new_layer(self):
        self.canvas._save_state("New layer")
        self.canvas.layer_stack.add_layer()
        self.canvas._refresh()
        self.layer_panel.refresh()

    def _dup_layer(self):
        idx = self.canvas.layer_stack.active_index
        self.canvas._save_state("Duplicate layer")
        self.canvas.layer_stack.duplicate_layer(idx)
        self.canvas._refresh()
        self.layer_panel.refresh()

    def _del_layer(self):
        idx = self.canvas.layer_stack.active_index
        if idx >= 0:
            self.canvas._save_state("Delete layer")
            self.canvas.layer_stack.remove_layer(idx)
            self.canvas._refresh()
            self.layer_panel.refresh()

    def _merge_visible(self):
        self.canvas._save_state("Merge visible")
        self.canvas.layer_stack.merge_visible()
        self.canvas._refresh()
        self.layer_panel.refresh()

    def _flatten(self):
        self.canvas._save_state("Flatten")
        self.canvas.layer_stack.flatten()
        self.canvas._refresh()
        self.layer_panel.refresh()

    def _show_filter_gallery(self):
        dialog = FilterGalleryDialog(self.canvas, self)
        dialog.exec_()
        self.canvas._refresh()
