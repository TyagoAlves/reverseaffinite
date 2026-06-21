from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPixmap, QPainterPath, QPolygonF, QFont


class CanvasOverlayMixin:
    def draw_rubber_band(self, painter):
        if not self.has_rubber_band or not self.rubber_band_start or not self.rubber_band_end:
            return
        painter.save()
        painter.setPen(QPen(QColor(100, 150, 255, 200), 1, Qt.DashLine))
        painter.setBrush(QBrush(QColor(100, 150, 255, 30)))
        rect = QRectF(self.rubber_band_start, self.rubber_band_end)
        painter.drawRect(rect.normalized())
        painter.restore()

    def draw_selection_overlay(self, painter):
        if self.selection_mask is None:
            return
        w = self.selection_mask.width()
        h = self.selection_mask.height()
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        sel_pix = QPixmap.fromImage(self.selection_mask)
        tinted = QPixmap(w, h)
        tinted.fill(QColor(60, 120, 255, 40))
        tinted.setMask(sel_pix.createHeuristicMask())
        painter.drawPixmap(0, 0, tinted)
        if self.selection_path is not None:
            pen = QPen(QColor(60, 120, 255), 1, Qt.CustomDashLine)
            pen.setDashPattern([6, 4])
            pen.setDashOffset(self.selection_phase)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.selection_path)
        painter.restore()

    def draw_lasso(self, painter):
        if not self.has_lasso or len(self.lasso_points) < 2:
            return
        painter.save()
        painter.setPen(QPen(QColor(100, 150, 255, 200), 1, Qt.DashLine))
        painter.setBrush(QBrush(QColor(100, 150, 255, 20)))
        poly = QPolygonF([pt for pt in self.lasso_points])
        painter.drawPolygon(poly)
        painter.restore()

    def draw_grid(self, painter):
        if not self.show_grid:
            return
        w = int(self.scene.sceneRect().width())
        h = int(self.scene.sceneRect().height())
        if self._settings:
            spacing = self._settings.get('grid_spacing', 50)
            color = QColor(self._settings.get('grid_color', '#808080'))
            style = self._settings.get('grid_style', 'Lines')
        else:
            spacing = 50
            color = QColor(128, 128, 128)
            style = 'Lines'
        painter.save()
        painter.setPen(QPen(color, 1 / self.zoom_level))
        if style == 'Lines':
            for x in range(spacing, w, spacing):
                painter.drawLine(x, 0, x, h)
            for y in range(spacing, h, spacing):
                painter.drawLine(0, y, w, y)
        elif style == 'Dots':
            for x in range(spacing, w, spacing):
                for y in range(spacing, h, spacing):
                    painter.drawPoint(x, y)
        elif style == 'Crosses':
            s = 4 / self.zoom_level
            for x in range(spacing, w, spacing):
                for y in range(spacing, h, spacing):
                    painter.drawLine(x - s, y, x + s, y)
                    painter.drawLine(x, y - s, x, y + s)
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
        spacing = self._settings.get('grid_spacing', 50) if self._settings else 50
        for x in range(spacing, w, spacing):
            painter.drawLine(x, ruler_size - 4, x, ruler_size)
            painter.drawText(x + 2, ruler_size - 2, str(x))
        for y in range(spacing, h, spacing):
            painter.drawLine(ruler_size - 4, y, ruler_size, y)
            painter.drawText(2, y + 10, str(y))
        painter.restore()

    def draw_pen_path(self, painter):
        painter.save()
        z = self.zoom_level
        if self.pen_path and len(self.pen_path) >= 2:
            path = QPainterPath()
            path.moveTo(self.pen_path[0])
            for i in range(1, len(self.pen_path)):
                prev = self.pen_path[i - 1]
                curr = self.pen_path[i]
                h_out = self.pen_handle_offsets[i - 1] if i - 1 < len(self.pen_handle_offsets) else None
                h_in = self.pen_handle_offsets[i] if i < len(self.pen_handle_offsets) else None
                if h_out is not None and h_in is not None:
                    path.cubicTo(prev + h_out, curr - h_in, curr)
                elif h_out is not None:
                    path.cubicTo(prev + h_out, curr, curr)
                elif h_in is not None:
                    path.cubicTo(prev, curr - h_in, curr)
                else:
                    path.lineTo(curr)
            painter.setPen(QPen(QColor(self.tool_color), 1.5 / z))
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)
            for pt in self.pen_path:
                painter.setBrush(QBrush(self.tool_color))
                painter.setPen(QPen(Qt.white, 1))
                r = 3.0 / z
                painter.drawEllipse(pt, r, r)
        self.draw_path_edit_overlay(painter)
        painter.restore()

    def draw_path_edit_overlay(self, painter):
        if self.selected_path_idx < 0 or self.selected_path_idx >= len(self.vector_paths):
            return
        pobj = self.vector_paths[self.selected_path_idx]
        if not pobj.anchors:
            return
        z = self.zoom_level
        painter.save()
        track_anchor_r = 4.0 / z
        track_handle_r = 3.0 / z
        for i, anchor in enumerate(pobj.anchors):
            pos = anchor.position
            is_selected = (i == self.edit_anchor_idx)
            painter.setBrush(QBrush(QColor(100, 150, 255, 180)))
            painter.setPen(QPen(Qt.white if is_selected else Qt.black, 1.0 / z))
            painter.drawEllipse(pos, track_anchor_r, track_anchor_r)
            for htype in ('handle_in', 'handle_out'):
                hpos = anchor.handle_in if htype == 'handle_in' else anchor.handle_out
                if (hpos - pos).manhattanLength() > 0.5:
                    painter.setPen(QPen(QColor(100, 150, 255), 1.0 / z, Qt.DashLine))
                    painter.drawLine(pos, hpos)
                    is_hover = (self.edit_handle == htype and i == self.edit_anchor_idx)
                    painter.setBrush(QBrush(QColor(255, 200, 100)))
                    painter.setPen(QPen(Qt.white if is_hover else Qt.black, 1.0 / z))
                    painter.drawEllipse(hpos, track_handle_r, track_handle_r)
        painter.restore()

    def _rasterize_vector_paths(self):
        layer = self.layer_stack.active
        if not layer or layer.locked:
            return
        layer.image.fill(Qt.transparent)
        for pobj in self.vector_paths:
            if pobj.visible:
                pobj.rasterize_to(layer.image, fill_color=self.tool_color, stroke_color=self.tool_color)
        self._refresh()

    def draw_crop_overlay(self, painter):
        if not self.crop_active or self.crop_start is None or self.crop_end is None:
            return
        rect = QRectF(self.crop_start, self.crop_end).normalized()
        painter.save()
        overlay_color = QColor(0, 0, 0, 128)
        painter.setBrush(overlay_color)
        painter.setPen(Qt.NoPen)
        sr = self.scene.sceneRect()
        painter.drawRect(0, 0, sr.width(), rect.top())
        painter.drawRect(0, rect.bottom(), sr.width(), sr.height() - rect.bottom())
        painter.drawRect(0, rect.top(), rect.left(), rect.height())
        painter.drawRect(rect.right(), rect.top(), sr.width() - rect.right(), rect.height())
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(100, 150, 255), 1.5 / self.zoom_level))
        painter.drawRect(rect)
        hs = 6.0 / self.zoom_level
        painter.setBrush(QColor(100, 150, 255))
        painter.setPen(Qt.NoPen)
        for pt in [rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight()]:
            painter.drawRect(QRectF(pt.x() - hs / 2, pt.y() - hs / 2, hs, hs))
        for pt in [QPointF(rect.center().x(), rect.top()),
                   QPointF(rect.center().x(), rect.bottom()),
                   QPointF(rect.left(), rect.center().y()),
                   QPointF(rect.right(), rect.center().y())]:
            painter.drawRect(QRectF(pt.x() - hs / 2, pt.y() - hs / 2, hs, hs))
        painter.restore()

    def _snap_point(self, pos):
        if not hasattr(self, 'snapping'):
            return pos, None
        grid_spacing = self._settings.get('grid_spacing', 50) if self._settings else 50
        guides = self.guide_mgr.guides if self.guide_mgr else []
        return self.snapping.snap_point(pos, guides=guides, grid_spacing=grid_spacing)

    def _show_snap_indicator(self, pos, text):
        self.snap_indicator = (pos, text)

    def draw_snap_indicator(self, painter):
        if self.snap_indicator is None:
            return
        pos, text = self.snap_indicator
        painter.save()
        painter.setPen(QPen(QColor(255, 255, 0, 200), 1, Qt.DashLine))
        painter.setBrush(QBrush(QColor(255, 255, 0, 30)))
        hs = 4.0 / self.zoom_level
        painter.drawRect(QRectF(pos.x() - hs, pos.y() - hs, hs * 2, hs * 2))
        painter.setPen(QColor(255, 255, 0, 200))
        font = QFont("monospace", 8)
        painter.setFont(font)
        painter.drawText(QPointF(pos.x() + hs + 2, pos.y() - hs - 2), text)
        painter.restore()

    def draw_overlay(self, painter):
        self.draw_grid(painter)
        self.draw_selection_overlay(painter)
        self.draw_rubber_band(painter)
        self.draw_lasso(painter)
        self.draw_pen_path(painter)
        self.draw_crop_overlay(painter)
        self.guide_mgr.draw(painter, self.pixmap_item.pixmap().size())
        self.draw_snap_indicator(painter)

    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QColor(30, 30, 30))
        scene_rect = self.scene.sceneRect()
        if scene_rect.isEmpty():
            return
        shadow_rect = scene_rect.translated(3, 3)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 80))
        painter.save()
        painter.setClipRect(scene_rect)
        light = QColor(0x1a, 0x1a, 0x1a)
        dark = QColor(0x0d, 0x0d, 0x0d)
        s = 16
        for x in range(int(scene_rect.left()), int(scene_rect.right()), s):
            for y in range(int(scene_rect.top()), int(scene_rect.bottom()), s):
                col = light if ((x // s) + (y // s)) % 2 == 0 else dark
                painter.fillRect(x, y, s, s, col)
        painter.restore()
        painter.setPen(QPen(QColor(10, 10, 10), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(scene_rect)

    def drawForeground(self, painter, rect):
        self.draw_overlay(painter)
