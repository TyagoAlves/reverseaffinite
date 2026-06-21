import os
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QTimer
from PyQt5.QtGui import (
    QPainter, QPixmap, QColor, QImage, QBrush,
    QPolygonF, QBitmap, QRegion,
    QPainterPath, QCursor,
)
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

from .layers import LayerStack, Layer
from .history import HistoryManager
from .tools import PencilTool
from .guides import GuideManager
from .snapping import SnappingEngine
from .settings import SettingsManager
from .canvas_drawing import CanvasDrawingMixin
from .canvas_overlay import CanvasOverlayMixin
from .canvas_io import CanvasIOMixin


class CanvasView(CanvasDrawingMixin, CanvasOverlayMixin, CanvasIOMixin, QGraphicsView):
    mouse_moved = pyqtSignal(float, float)
    color_picked = pyqtSignal(QColor)
    bg_color_changed = pyqtSignal(QColor)
    status_changed = pyqtSignal(str)
    zoom_changed = pyqtSignal(float)
    history_changed = pyqtSignal()
    tool_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        self.layer_stack = LayerStack(800, 600)
        self.history = HistoryManager()
        self.history.history_changed.connect(self.history_changed.emit)
        self.history.push("New document", self.layer_stack.layers, self.layer_stack.active_index)

        self.zoom_level = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.tool = PencilTool()
        self.setCursor(getattr(self.tool, 'cursor', QCursor(Qt.ArrowCursor)))
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
        self.has_lasso = False
        self.gradient_start = None
        self.shape_start = None
        self.clone_source = None

        self.selection_mask = None
        self.selection_path = None
        self.selection_phase = 0
        self.selection_timer = QTimer()
        self.selection_timer.timeout.connect(self._march_selection)
        self.selection_timer.start(120)
        self.guide_mgr = GuideManager()
        self.snapping = SnappingEngine()
        self._settings = SettingsManager()

        self.pen_path = []
        self.pen_handle_offsets = []
        self.vector_paths = []
        self.selected_path_idx = -1
        self.edit_anchor_idx = -1
        self.edit_handle = None
        self.ruler_dragging_guide = False
        self.dragging_guide_index = -1
        self.ruler_drag_orientation = None
        self.ruler_drag_pos = None
        self.crop_active = False
        self.crop_start = None
        self.crop_end = None
        self.crop_drag_handle = None
        self._plugin_filters = {}

        self.show_grid = False
        self.show_rulers = True
        self.snap_indicator = None

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMouseTracking(True)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setAcceptDrops(True)

        self.tool_changed.emit(self.tool.name)
        self._refresh()

    def _refresh(self):
        composite = self.layer_stack.composite()
        self.pixmap_item.setPixmap(QPixmap.fromImage(composite))
        self.scene.setSceneRect(QRectF(composite.rect()))
        self.viewport().update()

    def temp_save_layer(self):
        layer = self.layer_stack.active
        if layer:
            self._temp_layer_image = layer.image.copy()

    def temp_restore_layer(self):
        if hasattr(self, '_temp_layer_image') and self._temp_layer_image:
            layer = self.layer_stack.active
            if layer:
                layer.image = self._temp_layer_image.copy()
                self._refresh()

    def _save_state(self, desc="Edit"):
        self.history.push(desc, self.layer_stack.layers, self.layer_stack.active_index)

    def set_tool(self, tool_name):
        from .tools import TOOLS_BY_NAME
        cls = TOOLS_BY_NAME.get(tool_name.lower())
        if cls:
            self.tool = cls()
            self.setCursor(getattr(self.tool, 'cursor', QCursor(Qt.ArrowCursor)))
            self.tool_changed.emit(self.tool.name)

    def set_tool_size(self, size):
        self.tool_size = max(1, size)

    def set_tool_opacity(self, val):
        self.tool_opacity = val / 100.0

    def set_tool_flow(self, val):
        self.tool_flow = val / 100.0

    def set_foreground_color(self, color):
        self.tool_color = color
        self.color_picked.emit(color)

    def set_background_color(self, color):
        self.bg_color = color
        self.bg_color_changed.emit(color)

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

    def zoom_to_selection(self):
        if not self.has_selection():
            return
        rect = self.selection_path.boundingRect()
        if rect.isEmpty():
            return
        margin = 20
        rect.adjust(-margin, -margin, margin, margin)
        self.fitInView(rect, Qt.KeepAspectRatio)
        self.zoom_level = self.transform().m11()
        self.zoom_changed.emit(self.zoom_level)

    def _apply_zoom(self):
        self.resetTransform()
        self.scale(self.zoom_level, self.zoom_level)
        self.zoom_changed.emit(self.zoom_level)

    def update_pixmap_position(self):
        pos = self.pixmap_item.pos()
        self.pixmap_item.setPos(pos.x() + self.pan_offset_x, pos.y() + self.pan_offset_y)

    def _march_selection(self):
        if self.selection_mask is not None:
            self.selection_phase = (self.selection_phase + 1) % 6
            self.viewport().update()

    def has_selection(self):
        return self.selection_mask is not None

    def clear_selection(self):
        self.selection_mask = None
        self.selection_path = None
        self.selection_phase = 0
        self.viewport().update()

    def _apply_selection_clip(self, painter):
        if self.selection_mask is None:
            return
        if self.selection_path is not None:
            painter.setClipPath(self.selection_path)
        else:
            mono = self.selection_mask.convertToFormat(QImage.Format_Mono,
                                                       Qt.ThresholdDither)
            bitmap = QBitmap.fromImage(mono)
            region = QRegion(bitmap)
            painter.setClipRegion(region)

    def _selection_mask_from_path(self, path):
        w = int(self.scene.sceneRect().width())
        h = int(self.scene.sceneRect().height())
        mask = QImage(w, h, QImage.Format_ARGB32)
        mask.fill(Qt.transparent)
        p = QPainter(mask)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(255, 255, 255)))
        p.drawPath(path)
        p.end()
        return mask

    def set_selection_rect(self, rect):
        from PyQt5.QtCore import QRect
        path = QPainterPath()
        path.addRect(QRectF(rect))
        self.selection_path = path
        self.selection_mask = self._selection_mask_from_path(path)
        self.selection_phase = 0
        self.viewport().update()

    def set_selection_ellipse(self, rect):
        from PyQt5.QtCore import QRect
        path = QPainterPath()
        path.addEllipse(QRectF(rect))
        self.selection_path = path
        self.selection_mask = self._selection_mask_from_path(path)
        self.selection_phase = 0
        self.viewport().update()

    def set_selection_lasso(self, points):
        path = QPainterPath()
        poly = QPolygonF(points)
        path.addPolygon(poly)
        path.closeSubpath()
        self.selection_path = path
        self.selection_mask = self._selection_mask_from_path(path)
        self.selection_phase = 0
        self.viewport().update()

    def set_selection_mask_image(self, mask_qimage):
        self.selection_mask = mask_qimage
        self.selection_path = None
        self.selection_phase = 0
        self.viewport().update()

    def move_layer_content(self, dx, dy):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return False
        w, h = layer.image.width(), layer.image.height()
        i_dx, i_dy = int(dx), int(dy)
        if i_dx == 0 and i_dy == 0:
            return False
        new_img = QImage(w, h, QImage.Format_ARGB32)
        new_img.fill(Qt.transparent)
        p = QPainter(new_img)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.drawImage(i_dx, i_dy, layer.image)
        p.end()
        layer.image = new_img
        self._refresh()
        return True

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.zoom_level *= factor
            self.scale(factor, factor)
            self.zoom_changed.emit(self.zoom_level)
            self.status_changed.emit(f"Zoom: {self.zoom_level * 100:.0f}%")
        else:
            super().wheelEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path and path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if not path:
                continue
            ext = os.path.splitext(path)[1].lower()
            if ext not in ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.psd'):
                continue
            layer = self.import_image_as_layer(path)
            if layer:
                main = self.window()
                if hasattr(main, 'statusBar'):
                    main.statusBar().showMessage(f"Placed: {os.path.basename(path)}")
                if hasattr(main, 'layer_panel'):
                    main.layer_panel.refresh()
                if hasattr(main, 'nav_panel'):
                    main.nav_panel.refresh()
                event.acceptProposedAction()
                return
        event.ignore()

    def paste_from_clipboard(self):
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        if mime.hasImage():
            img = clipboard.image()
            if img.isNull():
                return False
            if img.format() != QImage.Format_ARGB32:
                img = img.convertToFormat(QImage.Format_ARGB32)
            w, h = self.layer_stack.layers[0].image.width(), self.layer_stack.layers[0].image.height()
            if img.width() != w or img.height() != h:
                img = img.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            layer = Layer(w, h, "Pasted", Qt.transparent)
            layer.image = img.copy()
            self.layer_stack.layers.append(layer)
            self.layer_stack.active_index = len(self.layer_stack.layers) - 1
            self._save_state("Paste image")
            self._refresh()
            return True
        if mime.hasUrls():
            for url in mime.urls():
                path = url.toLocalFile()
                if path:
                    ext = os.path.splitext(path)[1].lower()
                    if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.psd'):
                        layer = self.import_image_as_layer(path)
                        if layer:
                            self._save_state(f"Paste {os.path.basename(path)}")
                            return True
        return False

    def _ruler_hit_test(self, view_pos):
        ruler_size = 20
        if view_pos.x() < ruler_size:
            return Qt.Vertical
        if view_pos.y() < ruler_size:
            return Qt.Horizontal
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            from .tools import PenTool
            if isinstance(self.tool, PenTool):
                self.tool.finalize(self)
            return
        if event.button() == Qt.LeftButton:
            view_pos = event.pos()
            ruler_orientation = self._ruler_hit_test(view_pos)
            if ruler_orientation is not None:
                pos = self.mapToScene(view_pos)
                if not self.guide_mgr.locked:
                    gi = self.guide_mgr.hit_test(pos, 8.0 / self.zoom_level)
                    if gi >= 0:
                        self.dragging_guide_index = gi
                        self.ruler_dragging_guide = True
                        self.ruler_drag_orientation = self.guide_mgr.guides[gi].orientation
                        self.ruler_drag_pos = pos.x() if self.ruler_drag_orientation == Qt.Vertical else pos.y()
                    else:
                        self.ruler_dragging_guide = True
                        self.ruler_drag_orientation = ruler_orientation
                        self.ruler_drag_pos = pos.x() if ruler_orientation == Qt.Vertical else pos.y()
                return
            self.drawing = True
            pos = self.mapToScene(view_pos)
            sn_pos, snap_info = self._snap_point(pos)
            self.last_point = sn_pos
            mods = int(event.modifiers())
            self._save_state(f"{self.tool.name if hasattr(self.tool, 'name') else 'Tool'}")
            self.tool.press(self, sn_pos, mods)
            if snap_info:
                self._show_snap_indicator(snap_info[0], snap_info[1])
                self.status_changed.emit(f"Snap to {snap_info[1]}")
        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = self.mapToScene(event.pos())
        self.mouse_moved.emit(pos.x(), pos.y())
        if self.ruler_dragging_guide:
            self.ruler_drag_pos = pos.x() if self.ruler_drag_orientation == Qt.Vertical else pos.y()
            self.viewport().update()
            return
        if self.drawing and self.last_point:
            mods = int(event.modifiers())
            sn_pos, snap_info = self._snap_point(pos)
            self.tool.move(self, self.last_point, sn_pos, mods)
            self.last_point = sn_pos
            if snap_info:
                self._show_snap_indicator(snap_info[0], snap_info[1])
                self.status_changed.emit(f"Snap to {snap_info[1]}")
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.ruler_dragging_guide:
                pos = self.mapToScene(event.pos())
                if self.dragging_guide_index >= 0:
                    if not self.guide_mgr.locked:
                        view_pos = event.pos()
                        ruler_orientation = self._ruler_hit_test(view_pos)
                        if ruler_orientation is not None:
                            self.guide_mgr.remove_guide(self.dragging_guide_index)
                        else:
                            g = self.guide_mgr.guides[self.dragging_guide_index]
                            g.position = pos.x() if g.orientation == Qt.Vertical else pos.y()
                    self.dragging_guide_index = -1
                else:
                    pv = pos.x() if self.ruler_drag_orientation == Qt.Vertical else pos.y()
                    if pv >= 0:
                        self.guide_mgr.add_guide(self.ruler_drag_orientation, pv)
                self.ruler_dragging_guide = False
                self.ruler_drag_orientation = None
                self.ruler_drag_pos = None
                self.viewport().update()
                return
            if self.drawing:
                self.drawing = False
                mods = int(event.modifiers())
                pos = self.mapToScene(event.pos())
                sn_pos, snap_info = self._snap_point(pos)
                self.tool.release(self, sn_pos, mods)
                if snap_info:
                    self._show_snap_indicator(snap_info[0], snap_info[1])
                    self.status_changed.emit(f"Snap to {snap_info[1]}")
        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
            event.ignore()

    def keyPressEvent(self, event):
        key = event.key()
        mods = event.modifiers()

        # Tool shortcuts (Photoshop-style)
        if key == Qt.Key_V and not mods: self.set_tool("Move Tool")
        elif key == Qt.Key_M and not mods: self.set_tool("Rectangular Marquee Tool")
        elif key == Qt.Key_L and not mods: self.set_tool("Lasso Tool")
        elif key == Qt.Key_W and not mods: self.set_tool("Magic Wand Tool")
        elif key == Qt.Key_B and not mods: self.set_tool("Brush Tool")
        elif key == Qt.Key_P and not mods: self.set_tool("Pen Tool")
        elif key == Qt.Key_N and not mods: self.set_tool("Pencil Tool")
        elif key == Qt.Key_E and not mods: self.set_tool("Eraser Tool")
        elif key == Qt.Key_G and not mods: self.set_tool("Gradient Tool")
        elif key == Qt.Key_U and not mods: self.set_tool("Rectangle Tool")
        elif key == Qt.Key_S and not mods: self.set_tool("Clone Stamp Tool")
        elif key == Qt.Key_J and not mods: self.set_tool("Spot Healing Brush Tool")
        elif key == Qt.Key_C and not mods: self.set_tool("Crop Tool")
        elif key == Qt.Key_T and not mods: self.set_tool("Horizontal Type Tool")
        elif key == Qt.Key_H and not mods: self.set_tool("Hand Tool")
        elif key == Qt.Key_Z and not mods: self.set_tool("Zoom Tool")
        elif key == Qt.Key_I and not mods: self.set_tool("Eyedropper Tool")
        elif key == Qt.Key_K and not mods: self.set_tool("Paint Bucket Tool")

        elif key == Qt.Key_BracketRight and not mods: self.set_tool_size(self.tool_size + 1)
        elif key == Qt.Key_BracketLeft and not mods: self.set_tool_size(max(1, self.tool_size - 1))

        # Enter / Return to finalize pen or apply crop
        elif key in (Qt.Key_Return, Qt.Key_Enter) and not mods:
            from .tools import PenTool, CropTool
            if isinstance(self.tool, PenTool):
                self.tool.finalize(self)
            elif isinstance(self.tool, CropTool):
                self.tool.apply(self)

        # Backspace to delete selected anchor in pen tool
        elif key == Qt.Key_Backspace and not mods:
            from .tools import PenTool
            if isinstance(self.tool, PenTool):
                self.tool.key_press(self, key)

        # Escape to cancel pen or crop
        elif key == Qt.Key_Escape and not mods:
            from .tools import PenTool, CropTool
            if isinstance(self.tool, PenTool):
                self.tool.cancel(self)
            elif isinstance(self.tool, CropTool):
                self.tool.cancel(self)

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
            elif key == Qt.Key_V:
                if self.paste_from_clipboard():
                    self.status_changed.emit("Pasted image from clipboard")
                    main = self.window()
                    if hasattr(main, 'layer_panel'):
                        main.layer_panel.refresh()
                    if hasattr(main, 'nav_panel'):
                        main.nav_panel.refresh()
            elif key == Qt.Key_Plus: self.zoom_in()
            elif key == Qt.Key_Minus: self.zoom_out()
            elif key == Qt.Key_0: self.zoom_fit()
            elif key == Qt.Key_1: self.zoom_100()
            elif key == Qt.Key_2: self.zoom_to_selection()

        super().keyPressEvent(event)
