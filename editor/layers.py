from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QColor, QPainter

BLEND_MODES = [
    "Normal", "Multiply", "Screen", "Overlay",
    "Darken", "Lighten", "Color Dodge", "Color Burn",
    "Hard Light", "Soft Light", "Difference", "Exclusion",
    "Hue", "Saturation", "Color", "Luminosity",
]


class Layer:
    def __init__(self, width, height, name="Background", fill=None):
        self.name = name
        self.image = QImage(width, height, QImage.Format_ARGB32)
        self.image.fill(fill if fill is not None else (Qt.white if name == "Background" else Qt.transparent))
        self.visible = True
        self.locked = False
        self.opacity = 1.0
        self.blend_mode = "Normal"
        self.parent_group = None

    def copy(self):
        import copy
        return copy.deepcopy(self)


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
        w, h = self.layers[0].image.width(), self.layers[0].image.height()
        idx = len(self.layers)
        layer = Layer(w, h, name or f"Layer {idx}", Qt.transparent)
        self.layers.append(layer)
        self.active_index = idx
        return layer

    def add_background(self, color=QColor(Qt.white)):
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
        result = QImage(self.layers[0].image.size(), QImage.Format_ARGB32)
        result.fill(Qt.transparent)
        for layer in self.layers:
            if not layer.visible:
                continue
            p = QPainter(result)
            p.setOpacity(layer.opacity)
            p.drawImage(0, 0, layer.image)
            p.end()
            if layer.blend_mode != "Normal":
                pass
        return result
