from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QRect
from PyQt5.QtGui import (
    QPainter, QPixmap, QPen, QColor, QImage, QBrush,
    QTransform, QPolygonF, QFont, QFontMetrics,
)
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
import math
from collections import deque

from .layers import LayerStack
from .history import HistoryManager
from .tools import SHORTCUT_MAP, PencilTool


class CanvasView(QGraphicsView):
    mouse_moved = pyqtSignal(float, float)
    color_picked = pyqtSignal(QColor)
    status_changed = pyqtSignal(str)
    zoom_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.layer_stack = LayerStack(800, 600)
        self.history = HistoryManager()
        self.history.push("New document", self.layer_stack.layers, self.layer_stack.active_index)

        self.zoom_level = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.tool = PencilTool()
        self.tool_size = 3
        self.tool_color = QColor(0, 0, 0)
        self.tool_opacity = 1.0
        self.tool_flow = 1.0
        self.bg_color = QColor(255, 255, 255)
        self.drawing = False
        self.dragging_layer = False
        self.last_point = None
        self.selection_start = None
        self.selection = None
        self.rubber_band_start = None
        self.rubber_band_end = None
        self.has_rubber_band = False
        self.lasso_points = []
        self.gradient_start = None
        self.shape_start = None
        self.clone_source = None

        self.show_grid = False
        self.show_rulers = True
        self.snap_to_grid = False

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self._refresh()

    def _refresh(self):
        composite = self.layer_stack.composite()
        self.pixmap_item.setPixmap(QPixmap.fromImage(composite))
        self.scene.setSceneRect(QRectF(composite.rect()))

    def _save_state(self, desc="Edit"):
        self.history.push(desc, self.layer_stack.layers, self.layer_stack.active_index)

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

    def save_image(self, path):
        return self.layer_stack.composite().save(path)

    def export_png(self, path):
        return self.layer_stack.composite().save(path, "PNG")

    def export_jpg(self, path, quality=95):
        return self.layer_stack.composite().save(path, "JPEG", quality)

    def set_tool(self, tool_name):
        from .tools import TOOLS_BY_NAME
        cls = TOOLS_BY_NAME.get(tool_name.lower())
        if cls:
            self.tool = cls()

    def set_tool_size(self, size):
        self.tool_size = max(1, size)

    def set_tool_opacity(self, val):
        self.tool_opacity = val / 100.0

    def set_foreground_color(self, color):
        self.tool_color = color
        self.color_picked.emit(color)

    def set_background_color(self, color):
        self.bg_color = color

    def set_drag_mode(self, mode):
        """0=NoDrag, 1=ScrollHandDrag"""
        self.setDragMode(
            QGraphicsView.ScrollHandDrag if mode == 1 else QGraphicsView.NoDrag
        )
        self.dragging_layer = False

    def zoom_in(self):
        self.zoom_level *= 1.25
        self._apply_zoom()

    def zoom_out(self):
        self.zoom_level /= 1.25
        self._apply_zoom()

    def zoom_fit(self):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.zoom_level = self.transform().m11()
        self.zoom_changed.emit(self.zoom_level)

    def zoom_100(self):
        self.zoom_level = 1.0
        self._apply_zoom()

    def _apply_zoom(self):
        self.resetTransform()
        self.scale(self.zoom_level, self.zoom_level)
        self.zoom_changed.emit(self.zoom_level)

    def update_pixmap_position(self):
        pos = self.pixmap_item.pos()
        self.pixmap_item.setPos(pos.x() + self.pan_offset_x, pos.y() + self.pan_offset_y)

    def draw_point(self, pos):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return
        p = QPainter(layer.image)
        p.setRenderHint(QPainter.Antialiasing)
        c = self.tool_color
        c.setAlpha(int(255 * self.tool_opacity))
        pen = QPen(c, self.tool_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.drawPoint(pos)
        p.end()
        self._refresh()

    def draw_line(self, p1, p2):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return
        p = QPainter(layer.image)
        p.setRenderHint(QPainter.Antialiasing)
        c = self.tool_color
        c.setAlpha(int(255 * self.tool_opacity))
        pen = QPen(c, self.tool_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.drawLine(p1, p2)
        p.end()
        self._refresh()

    def erase_point(self, pos):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return
        p = QPainter(layer.image)
        p.setRenderHint(QPainter.Antialiasing)
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        pen = QPen(QColor(0, 0, 0, 0), self.tool_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.drawPoint(pos)
        p.end()
        self._refresh()

    def erase_line(self, p1, p2):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return
        p = QPainter(layer.image)
        p.setRenderHint(QPainter.Antialiasing)
        p.setCompositionMode(QPainter.CompositionMode_Clear)
        pen = QPen(QColor(0, 0, 0, 0), self.tool_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.drawLine(p1, p2)
        p.end()
        self._refresh()

    def get_pixel_color(self, pos):
        layer = self.layer_stack.active
        if not layer:
            return None
        x = max(0, min(int(pos.x()), layer.image.width() - 1))
        y = max(0, min(int(pos.y()), layer.image.height() - 1))
        return layer.image.pixelColor(x, y)

    def flood_fill(self, pos):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return
        x, y = int(pos.x()), int(pos.y())
        w, h = layer.image.width(), layer.image.height()
        if x < 0 or x >= w or y < 0 or y >= h:
            return

        target = layer.image.pixelColor(x, y)
        if target == self.tool_color:
            return

        q = deque()
        q.append((x, y))
        visited = {(x, y)}

        p = QPainter(layer.image)
        p.setPen(QPen(self.tool_color, 1))

        while q:
            cx, cy = q.popleft()
            if layer.image.pixelColor(cx, cy) == target:
                p.drawPoint(cx, cy)
                for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        q.append((nx, ny))
        p.end()
        self._refresh()

    def flood_fill_select(self, pos):
        pass

    def draw_gradient(self, start, end):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return
        from PyQt5.QtGui import QLinearGradient
        w, h = layer.image.width(), layer.image.height()
        grad = QLinearGradient(start, end)
        grad.setColorAt(0.0, self.tool_color)
        grad.setColorAt(1.0, self.bg_color)
        p = QPainter(layer.image)
        p.fillRect(0, 0, w, h, grad)
        p.end()
        self._refresh()

    def draw_rect_shape(self, start, end):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return
        p = QPainter(layer.image)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.tool_color, self.tool_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        rect = QRectF(start, end)
        p.drawRect(rect.normalized())
        p.end()
        self._refresh()

    def clone_stamp(self, src, dst):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return
        sx, sy = int(src.x()), int(src.y())
        dx, dy = int(dst.x()), int(dst.y())
        w, h = layer.image.width(), layer.image.height()
        if not (0 <= sx < w and 0 <= sy < h and 0 <= dx < w and 0 <= dy < h):
            return
        color = layer.image.pixelColor(sx, sy)
        p = QPainter(layer.image)
        pen = QPen(color, self.tool_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(pen)
        p.drawPoint(dx, dy)
        p.end()
        self._refresh()

    def draw_rubber_band(self, painter):
        if not self.has_rubber_band or not self.rubber_band_start or not self.rubber_band_end:
            return
        painter.save()
        painter.setPen(QPen(QColor(100, 150, 255, 200), 1, Qt.DashLine))
        painter.setBrush(QBrush(QColor(100, 150, 255, 30)))
        rect = QRectF(self.rubber_band_start, self.rubber_band_end)
        painter.drawRect(rect.normalized())
        painter.restore()

    def draw_lasso(self, painter):
        if len(self.lasso_points) < 2:
            return
        painter.save()
        painter.setPen(QPen(QColor(100, 150, 255, 200), 1, Qt.DashLine))
        poly = QPolygonF([pt for pt in self.lasso_points])
        painter.drawPolygon(poly)
        painter.restore()

    def draw_grid(self, painter):
        if not self.show_grid:
            return
        w = int(self.scene.sceneRect().width())
        h = int(self.scene.sceneRect().height())
        spacing = 50
        painter.save()
        painter.setPen(QPen(QColor(128, 128, 128, 60), 1 / self.zoom_level))
        for x in range(spacing, w, spacing):
            painter.drawLine(x, 0, x, h)
        for y in range(spacing, h, spacing):
            painter.drawLine(0, y, w, y)
        painter.restore()

    def draw_rulers(self, painter):
        if not self.show_rulers:
            return
        ruler_size = 20
        w = int(self.pixmap_item.pixmap().width())
        h = int(self.pixmap_item.pixmap().height())
        painter.save()
        painter.setPen(QPen(QColor(80, 80, 80), 1))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawRect(0, 0, w, ruler_size)
        painter.drawRect(0, 0, ruler_size, h)

        painter.setPen(QColor(180, 180, 180))
        font = QFont("monospace", 7)
        painter.setFont(font)
        spacing = 50
        for x in range(spacing, w, spacing):
            painter.drawLine(x, ruler_size - 4, x, ruler_size)
            painter.drawText(x + 2, ruler_size - 2, str(x))
        for y in range(spacing, h, spacing):
            painter.drawLine(ruler_size - 4, y, ruler_size, y)
            painter.drawText(2, y + 10, str(y))
        painter.restore()

    def draw_overlay(self, painter):
        self.draw_grid(painter)
        self.draw_rubber_band(painter)
        self.draw_lasso(painter)

    def drawForeground(self, painter, rect):
        self.draw_overlay(painter)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.zoom_level *= factor
            self.scale(factor, factor)
            self.zoom_changed.emit(self.zoom_level)
            self.status_changed.emit(f"Zoom: {self.zoom_level * 100:.0f}%")
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            pos = self.mapToScene(event.pos())
            self.last_point = pos
            mods = int(event.modifiers())
            self._save_state(f"{self.tool.name if hasattr(self.tool, 'name') else 'Tool'}")
            self.tool.press(self, pos, mods)
        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        self.mouse_moved.emit(pos.x(), pos.y())
        if self.drawing and self.last_point:
            mods = int(event.modifiers())
            self.tool.move(self, self.last_point, pos, mods)
            self.last_point = pos
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawing = False
            mods = int(event.modifiers())
            self.tool.release(self, self.mapToScene(event.pos()), mods)
        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
            event.ignore()

    def keyPressEvent(self, event):
        key = event.key()
        mods = event.modifiers()

        # Tool shortcuts
        if key == Qt.Key_V and not mods: self.set_tool("Move")
        elif key == Qt.Key_M and not mods: self.set_tool("Rectangular Select")
        elif key == Qt.Key_L and not mods: self.set_tool("Lasso")
        elif key == Qt.Key_W and not mods: self.set_tool("Magic Wand")
        elif key == Qt.Key_B and not mods: self.set_tool("Brush")
        elif key == Qt.Key_P and not mods: self.set_tool("Pencil")
        elif key == Qt.Key_E and not mods: self.set_tool("Eraser")
        elif key == Qt.Key_G and not mods: self.set_tool("Gradient")
        elif key == Qt.Key_U and not mods: self.set_tool("Shape")
        elif key == Qt.Key_S and not mods: self.set_tool("Clone Stamp")
        elif key == Qt.Key_H and not mods: self.set_tool("Hand")
        elif key == Qt.Key_Z and not mods: self.set_tool("Zoom")
        elif key == Qt.Key_I and not mods: self.set_tool("Color Picker")
        elif key == Qt.Key_K and not mods: self.set_tool("Flood Fill")

        elif key == Qt.Key_BracketRight and not mods: self.set_tool_size(self.tool_size + 1)
        elif key == Qt.Key_BracketLeft and not mods: self.set_tool_size(max(1, self.tool_size - 1))

        # Ctrl+
        elif mods & Qt.ControlModifier:
            if key == Qt.Key_Z:
                if mods & Qt.ShiftModifier:
                    if self.history.can_redo():
                        self.history.redo(self.layer_stack)
                        self._refresh()
                else:
                    if self.history.can_undo():
                        self.history.undo(self.layer_stack)
                        self._refresh()
            elif key == Qt.Key_Plus: self.zoom_in()
            elif key == Qt.Key_Minus: self.zoom_out()
            elif key == Qt.Key_0: self.zoom_fit()
            elif key == Qt.Key_1: self.zoom_100()

        super().keyPressEvent(event)
