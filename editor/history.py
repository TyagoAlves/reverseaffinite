from collections import deque
import copy
from PyQt5.QtCore import QObject, pyqtSignal
from .layers import Layer


class HistoryEntry:
    def __init__(self, description, snapshot, active_index):
        self.description = description
        self.snapshot = snapshot
        self.active_index = active_index


class HistoryManager(QObject):
    history_changed = pyqtSignal()

    def __init__(self, max_states=100):
        super().__init__()
        self.stack = deque(maxlen=max_states)
        self.index = -1

    def push(self, description, layers, active_index):
        snap = [(l.name, l.image.copy(), l.visible, l.locked, l.opacity, l.blend_mode)
                for l in layers]
        entry = HistoryEntry(description, snap, active_index)
        while self.index < len(self.stack) - 1:
            self.stack.pop()
        self.stack.append(entry)
        self.index = len(self.stack) - 1
        self.history_changed.emit()

    def undo(self, layer_stack):
        if self.index <= 0:
            return False
        self.index -= 1
        self._restore(layer_stack)
        self.history_changed.emit()
        return True

    def redo(self, layer_stack):
        if self.index >= len(self.stack) - 1:
            return False
        self.index += 1
        self._restore(layer_stack)
        self.history_changed.emit()
        return True

    def jump_to(self, layer_stack, index):
        if 0 <= index < len(self.stack):
            self.index = index
            self._restore(layer_stack)
            self.history_changed.emit()
            return True
        return False

    def _restore(self, layer_stack):
        entry = self.stack[self.index]
        layer_stack.layers.clear()
        for name, img, vis, locked, opacity, blend in entry.snapshot:
            l = Layer(img.width(), img.height(), name)
            l.image = img
            l.visible = vis
            l.locked = locked
            l.opacity = opacity
            l.blend_mode = blend
            layer_stack.layers.append(l)
        layer_stack.active_index = entry.active_index

    def can_undo(self):
        return self.index > 0

    def can_redo(self):
        return self.index < len(self.stack) - 1

    def clear(self):
        self.stack.clear()
        self.index = -1
        self.history_changed.emit()
