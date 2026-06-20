from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QSpinBox, QComboBox, QCheckBox, QPushButton,
    QGroupBox, QGridLayout, QColorDialog, QLineEdit,
    QFormLayout,
)


class ColorButton(QPushButton):
    def __init__(self, color='#000000', parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedSize(36, 24)
        self._update_style()
        self.clicked.connect(self._pick)

    def _update_style(self):
        self.setStyleSheet(
            f"background-color: {self._color.name()}; border: 1px solid #888; border-radius: 3px;"
        )

    def _pick(self):
        c = QColorDialog.getColor(self._color, self)
        if c.isValid():
            self._color = c
            self._update_style()

    def color(self):
        return self._color

    def set_color(self, color):
        if isinstance(color, str):
            self._color = QColor(color)
        else:
            self._color = color
        self._update_style()

    def color_name(self):
        return self._color.name()


class PreferencesDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self._original = settings.all_settings()
        self.setWindowTitle("Preferences")
        self.resize(520, 440)

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_general_tab(), "General")
        self.tabs.addTab(self._build_grid_tab(), "Grid && Guides")
        self.tabs.addTab(self._build_performance_tab(), "Performance")
        self.tabs.addTab(self._build_appearance_tab(), "Appearance")
        self.tabs.addTab(self._build_file_tab(), "File Handling")
        layout.addWidget(self.tabs)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._on_ok)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self._on_cancel)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._on_apply)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

    def _build_general_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.gen_width = QSpinBox()
        self.gen_width.setRange(1, 20000)
        self.gen_width.setValue(self._original.get('default_width', 800))
        form.addRow("Default width:", self.gen_width)
        self.gen_height = QSpinBox()
        self.gen_height.setRange(1, 20000)
        self.gen_height.setValue(self._original.get('default_height', 600))
        form.addRow("Default height:", self.gen_height)
        self.gen_bg_color = ColorButton(self._original.get('default_bg_color', '#ffffff'))
        form.addRow("Background color:", self.gen_bg_color)
        self.gen_units = QComboBox()
        self.gen_units.addItems(['px', 'in', 'cm', 'mm', 'pt'])
        self.gen_units.setCurrentText(self._original.get('units', 'px'))
        form.addRow("Units:", self.gen_units)
        self.gen_language = QComboBox()
        self.gen_language.addItems(['system', 'en', 'pt-BR', 'es', 'fr', 'de', 'ja', 'zh'])
        self.gen_language.setCurrentText(self._original.get('language', 'system'))
        form.addRow("Language:", self.gen_language)
        self.gen_auto_save = QSpinBox()
        self.gen_auto_save.setRange(0, 60)
        self.gen_auto_save.setValue(self._original.get('auto_save_interval', 0))
        self.gen_auto_save.setSuffix(" min (0=disabled)")
        form.addRow("Auto-save:", self.gen_auto_save)
        return w

    def _build_grid_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.grid_color_btn = ColorButton(self._original.get('grid_color', '#808080'))
        form.addRow("Grid color:", self.grid_color_btn)
        self.grid_spacing = QSpinBox()
        self.grid_spacing.setRange(1, 500)
        self.grid_spacing.setValue(self._original.get('grid_spacing', 50))
        form.addRow("Grid spacing:", self.grid_spacing)
        self.grid_style = QComboBox()
        self.grid_style.addItems(['Lines', 'Dots', 'Crosses'])
        self.grid_style.setCurrentText(self._original.get('grid_style', 'Lines'))
        form.addRow("Grid style:", self.grid_style)
        self.guide_color_btn = ColorButton(self._original.get('guide_color', '#4a8ac4'))
        form.addRow("Guide color:", self.guide_color_btn)
        self.snap_threshold = QSpinBox()
        self.snap_threshold.setRange(1, 50)
        self.snap_threshold.setValue(self._original.get('snap_threshold', 5))
        form.addRow("Snap threshold:", self.snap_threshold)
        return w

    def _build_performance_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.perf_undo = QSpinBox()
        self.perf_undo.setRange(10, 500)
        self.perf_undo.setValue(self._original.get('undo_levels', 100))
        form.addRow("Undo levels:", self.perf_undo)
        self.perf_cache = QSpinBox()
        self.perf_cache.setRange(64, 4096)
        self.perf_cache.setValue(self._original.get('cache_size_mb', 512))
        self.perf_cache.setSuffix(" MB")
        form.addRow("Cache size:", self.perf_cache)
        self.perf_opengl = QCheckBox()
        self.perf_opengl.setChecked(self._original.get('use_opengl', False))
        form.addRow("Use OpenGL:", self.perf_opengl)
        self.perf_live = QCheckBox()
        self.perf_live.setChecked(self._original.get('live_preview', True))
        form.addRow("Live preview:", self.perf_live)
        return w

    def _build_appearance_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.app_theme = QComboBox()
        self.app_theme.addItems(['Dark', 'Light', 'System'])
        self.app_theme.setCurrentText(self._original.get('theme', 'Dark'))
        form.addRow("Theme:", self.app_theme)
        self.app_font_size = QSpinBox()
        self.app_font_size.setRange(8, 24)
        self.app_font_size.setValue(self._original.get('font_size', 12))
        form.addRow("Font size:", self.app_font_size)
        self.app_canvas_bg = QComboBox()
        self.app_canvas_bg.addItems(['Checkered', 'Solid', 'Custom'])
        self.app_canvas_bg.setCurrentText(self._original.get('canvas_bg', 'Checkered'))
        form.addRow("Canvas background:", self.app_canvas_bg)
        self.app_checkered = QComboBox()
        self.app_checkered.addItems(['Small', 'Medium', 'Large'])
        self.app_checkered.setCurrentText(self._original.get('checkered_size', 'Medium'))
        form.addRow("Checkered size:", self.app_checkered)
        return w

    def _build_file_tab(self):
        w = QWidget()
        form = QFormLayout(w)
        self.file_format = QComboBox()
        self.file_format.addItems(['png', 'jpg', 'tiff', 'webp', 'bmp'])
        self.file_format.setCurrentText(self._original.get('default_save_format', 'png'))
        form.addRow("Default format:", self.file_format)
        self.file_jpeg_q = QSpinBox()
        self.file_jpeg_q.setRange(1, 100)
        self.file_jpeg_q.setValue(self._original.get('jpeg_quality', 95))
        form.addRow("JPEG quality:", self.file_jpeg_q)
        self.file_png_comp = QSpinBox()
        self.file_png_comp.setRange(0, 9)
        self.file_png_comp.setValue(self._original.get('png_compression', 6))
        form.addRow("PNG compression:", self.file_png_comp)
        self.file_layers = QCheckBox()
        self.file_layers.setChecked(self._original.get('include_layers', False))
        form.addRow("Include layers:", self.file_layers)
        return w

    def _collect(self):
        return {
            'default_width': self.gen_width.value(),
            'default_height': self.gen_height.value(),
            'default_bg_color': self.gen_bg_color.color_name(),
            'units': self.gen_units.currentText(),
            'language': self.gen_language.currentText(),
            'auto_save_interval': self.gen_auto_save.value(),
            'grid_color': self.grid_color_btn.color_name(),
            'grid_spacing': self.grid_spacing.value(),
            'grid_style': self.grid_style.currentText(),
            'guide_color': self.guide_color_btn.color_name(),
            'snap_threshold': self.snap_threshold.value(),
            'undo_levels': self.perf_undo.value(),
            'cache_size_mb': self.perf_cache.value(),
            'use_opengl': self.perf_opengl.isChecked(),
            'live_preview': self.perf_live.isChecked(),
            'theme': self.app_theme.currentText(),
            'font_size': self.app_font_size.value(),
            'canvas_bg': self.app_canvas_bg.currentText(),
            'checkered_size': self.app_checkered.currentText(),
            'default_save_format': self.file_format.currentText(),
            'jpeg_quality': self.file_jpeg_q.value(),
            'png_compression': self.file_png_comp.value(),
            'include_layers': self.file_layers.isChecked(),
        }

    def _apply(self):
        vals = self._collect()
        for k, v in vals.items():
            self._settings.set(k, v)
        self._settings.save()

    def _on_apply(self):
        self._apply()

    def _on_ok(self):
        self._apply()
        self.accept()

    def _on_cancel(self):
        for k, v in self._original.items():
            if k in ('recent_files',):
                continue
            self._settings.set(k, v)
        self.reject()
