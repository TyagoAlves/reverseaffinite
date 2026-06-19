from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QColor, QPainter
import numpy as np
import copy


def _blend_normal(b, l):
    return l

def _blend_multiply(b, l):
    return b * l

def _blend_screen(b, l):
    return 1.0 - (1.0 - b) * (1.0 - l)

def _blend_overlay(b, l):
    mask = b < 0.5
    return np.where(mask, 2.0 * b * l, 1.0 - 2.0 * (1.0 - b) * (1.0 - l))

def _blend_darken(b, l):
    return np.minimum(b, l)

def _blend_lighten(b, l):
    return np.maximum(b, l)

def _blend_color_dodge(b, l):
    result = np.divide(b, 1.0 - l, out=np.ones_like(b), where=l < 0.999)
    return np.clip(result, 0.0, 1.0)

def _blend_color_burn(b, l):
    result = 1.0 - np.divide(1.0 - b, l, out=np.zeros_like(b), where=l > 0.001)
    return np.clip(result, 0.0, 1.0)

def _blend_hard_light(b, l):
    mask = l < 0.5
    return np.where(mask, 2.0 * b * l, 1.0 - 2.0 * (1.0 - b) * (1.0 - l))

def _blend_soft_light(b, l):
    mask = l < 0.5
    result = np.where(mask,
                      2.0 * b * l + b * b * (1.0 - 2.0 * l),
                      np.sqrt(b) * (2.0 * l - 1.0) + 2.0 * b * (1.0 - l))
    return np.clip(result, 0.0, 1.0)

def _blend_difference(b, l):
    return np.abs(b - l)

def _blend_exclusion(b, l):
    return b + l - 2.0 * b * l


BLEND_FUNCS = {
    "Normal": _blend_normal,
    "Multiply": _blend_multiply,
    "Screen": _blend_screen,
    "Overlay": _blend_overlay,
    "Darken": _blend_darken,
    "Lighten": _blend_lighten,
    "Color Dodge": _blend_color_dodge,
    "Color Burn": _blend_color_burn,
    "Hard Light": _blend_hard_light,
    "Soft Light": _blend_soft_light,
    "Difference": _blend_difference,
    "Exclusion": _blend_exclusion,
}

BLEND_MODES = list(BLEND_FUNCS.keys()) + ["Hue", "Saturation", "Color", "Luminosity"]


def _float_array_to_qimage(arr, w, h):
    u8 = np.clip(arr * 255.0, 0, 255).astype(np.uint8)
    u8 = np.ascontiguousarray(u8)
    qimg = QImage(u8.data, w, h, 4 * w, QImage.Format_RGBA8888)
    return qimg.copy()


def _qimage_to_float_array(img):
    w, h = img.width(), img.height()
    if img.format() != QImage.Format_RGBA8888:
        img = img.convertToFormat(QImage.Format_RGBA8888)
    ptr = img.constBits()
    ptr.setsize(img.sizeInBytes())
    arr = np.frombuffer(ptr, dtype=np.uint8).copy().reshape(h, w, 4)
    return arr.astype(np.float32) / 255.0


class Layer:
    def __init__(self, width, height, name="Background", fill=None):
        w = max(0, int(width))
        h = max(0, int(height))
        self.name = name
        self.image = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        self.image.fill(fill if fill is not None else (Qt.white if name == "Background" else Qt.transparent))
        self.visible = True
        self.locked = False
        self.opacity = 1.0
        self.blend_mode = "Normal"
        self.parent_group = None

    def copy(self):
        l = Layer(self.image.width(), self.image.height(), self.name + " (copy)")
        l.image = self.image.copy()
        l.visible = self.visible
        l.locked = self.locked
        l.opacity = self.opacity
        l.blend_mode = self.blend_mode
        l.parent_group = self.parent_group
        return l


class AdjustmentLayer(Layer):
    def __init__(self, width, height, name="Adjustment", filter_func=None, params=None):
        super().__init__(width, height, name, Qt.transparent)
        self.filter_func = filter_func
        self.params = params or {}
        self.image.fill(Qt.transparent)

    def copy(self):
        adj = AdjustmentLayer(self.image.width(), self.image.height(),
                              self.name + " (copy)", self.filter_func, self.params.copy())
        adj.image = self.image.copy()
        adj.visible = self.visible
        adj.locked = self.locked
        adj.opacity = self.opacity
        adj.blend_mode = self.blend_mode
        return adj


class GroupLayer:
    def __init__(self, name="Group"):
        self.name = name
        self.visible = True
        self.locked = False
        self.opacity = 1.0
        self.blend_mode = "Normal"
        self.children = []


class LayerStack:
    def __init__(self, width=800, height=600):
        self.layers = [Layer(width, height, "Background")]
        self.active_index = 0

    @property
    def active(self):
        return self._get(self.active_index)

    def _get(self, idx):
        if 0 <= idx < len(self.layers):
            return self.layers[idx]
        return None

    def add_layer(self, name=None):
        if not self.layers:
            return None
        w, h = self.layers[0].image.width(), self.layers[0].image.height()
        idx = len(self.layers)
        layer = Layer(w, h, name or f"Layer {idx}", Qt.transparent)
        self.layers.append(layer)
        self.active_index = idx
        return layer

    def add_background(self, color=QColor(Qt.white)):
        if not self.layers:
            return
        w, h = self.layers[0].image.width(), self.layers[0].image.height()
        idx = len(self.layers)
        layer = Layer(w, h, f"Background", color)
        self.layers.insert(0, layer)
        self.active_index = idx + 1

    def remove_layer(self, index):
        if len(self.layers) <= 1:
            return
        if 0 <= index < len(self.layers):
            self.layers.pop(index)
            if self.active_index >= len(self.layers):
                self.active_index = len(self.layers) - 1

    def move_layer(self, from_idx, to_idx):
        if 0 <= from_idx < len(self.layers) and 0 <= to_idx < len(self.layers):
            layer = self.layers.pop(from_idx)
            self.layers.insert(to_idx, layer)
            self.active_index = to_idx

    def duplicate_layer(self, index):
        if 0 <= index < len(self.layers):
            layer = self.layers[index].copy()
            layer.name = f"{layer.name} (copy)"
            self.layers.insert(index + 1, layer)
            self.active_index = index + 1

    def flatten(self):
        if len(self.layers) == 1:
            return
        composite = self.composite()
        self.layers = [Layer(composite.width(), composite.height(), "Flattened")]
        self.layers[0].image = composite
        self.active_index = 0

    def merge_visible(self):
        visible = [(i, l) for i, l in enumerate(self.layers) if l.visible]
        if len(visible) <= 1:
            return
        target_idx = visible[0][0]
        base = visible[0][1].image.copy()
        for i, layer in visible[1:]:
            p = QPainter(base)
            p.setOpacity(layer.opacity)
            p.drawImage(0, 0, layer.image)
            p.end()
        to_remove = [i for i, _ in visible[1:]]
        for i in sorted(to_remove, reverse=True):
            self.layers.pop(i)
        self.layers[target_idx].image = base
        self.layers[target_idx].name = "Merged"
        self.active_index = target_idx

    def composite(self):
        if not self.layers:
            return QImage()
        visible = [l for l in self.layers if l.visible]
        if not visible:
            w = self.layers[0].image.width()
            h = self.layers[0].image.height()
            return QImage(w, h, QImage.Format_ARGB32_Premultiplied)
        w = visible[0].image.width()
        h = visible[0].image.height()
        result = np.zeros((h, w, 4), dtype=np.float32)
        for layer in visible:
            if isinstance(layer, GroupLayer):
                continue
            if isinstance(layer, AdjustmentLayer):
                if layer.filter_func:
                    qimg = _float_array_to_qimage(result, w, h)
                    result_qimg = layer.filter_func(qimg, layer.params)
                    result = _qimage_to_float_array(result_qimg)
                continue
            img = layer.image
            iw, ih = img.width(), img.height()
            if iw != w or ih != h:
                img = img.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            ptr = img.constBits()
            ptr.setsize(img.sizeInBytes())
            arr = np.frombuffer(ptr, dtype=np.uint8).copy().reshape(ih, iw, 4)
            layer_arr = arr.astype(np.float32) / 255.0
            blend_func = BLEND_FUNCS.get(layer.blend_mode, _blend_normal)
            blend_rgb = blend_func(result[:, :, :3], layer_arr[:, :, :3])
            alpha = layer_arr[:, :, 3] * layer.opacity
            a = alpha[:, :, np.newaxis]
            result[:, :, :3] = blend_rgb * a + result[:, :, :3] * (1.0 - a)
            result[:, :, 3] = alpha + result[:, :, 3] * (1.0 - alpha)
        return _float_array_to_qimage(result, w, h)
