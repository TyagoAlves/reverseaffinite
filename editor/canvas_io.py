import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QImage
from .file_formats import FORMAT_REGISTRY, get_format_for_filename
from .layers import Layer, LayerStack


class CanvasIOMixin:
    def new_image(self, width, height, bg=None):
        if bg is None:
            bg = QColor(Qt.white)
        self.layer_stack = LayerStack(width, height)
        if bg != Qt.white:
            self.layer_stack.layers[0].image.fill(bg)
        self.history.clear()
        self.history.push("New document", self.layer_stack.layers, self.layer_stack.active_index)
        self._refresh()
        self.zoom_fit()

    def open_image(self, path):
        if not path:
            return False
        try:
            ext = get_format_for_filename(path)
            fmt = FORMAT_REGISTRY.get(ext)
            if fmt and fmt.get('importer'):
                layer_stack = fmt['importer'](path)
                if layer_stack and layer_stack.layers:
                    self.layer_stack = layer_stack
                    w = self.layer_stack.layers[0].image.width()
                    h = self.layer_stack.layers[0].image.height()
                    self.history.clear()
                    self.history.push(f"Open {path}", self.layer_stack.layers, self.layer_stack.active_index)
                    self._refresh()
                    self.zoom_fit()
                    return True
            img = QImage(path)
            if img.isNull():
                return False
            if img.format() != QImage.Format_ARGB32:
                img = img.convertToFormat(QImage.Format_ARGB32)
            w, h = img.width(), img.height()
            self.layer_stack = LayerStack(w, h)
            self.layer_stack.layers[0].image = img.copy()
            self.history.clear()
            self.history.push(f"Open {path}", self.layer_stack.layers, self.layer_stack.active_index)
            self._refresh()
            self.zoom_fit()
            return True
        except Exception:
            return False

    def save_image(self, path, opts=None):
        if not path:
            return False
        try:
            ext = get_format_for_filename(path)
            fmt = FORMAT_REGISTRY.get(ext)
            if fmt and fmt.get('exporter'):
                return fmt['exporter'](self.layer_stack, path, opts)
            composite = self.layer_stack.composite()
            return composite.save(path)
        except Exception:
            return False

    def import_image_as_layer(self, path):
        if not path:
            return None
        try:
            img = QImage(path)
            if img.isNull():
                return None
            if img.format() != QImage.Format_ARGB32:
                img = img.convertToFormat(QImage.Format_ARGB32)
            name = os.path.splitext(os.path.basename(path))[0]
            w, h = self.layer_stack.layers[0].image.width(), self.layer_stack.layers[0].image.height()
            if img.width() != w or img.height() != h:
                img = img.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            layer = Layer(w, h, name, Qt.transparent)
            layer.image = img.copy()
            self.layer_stack.layers.append(layer)
            self.layer_stack.active_index = len(self.layer_stack.layers) - 1
            self._save_state(f"Place {name}")
            self._refresh()
            return layer
        except Exception:
            return None

    def export_png(self, path):
        if not path:
            return False
        try:
            return self.layer_stack.composite().save(path, "PNG")
        except Exception:
            return False

    def export_jpg(self, path, quality=95):
        if not path:
            return False
        try:
            return self.layer_stack.composite().save(path, "JPEG", quality)
        except Exception:
            return False
