"""
Professional tools inspired by industry standards.
Hotkeys:
  V - Move          M - Rect Select   L - Lasso
  W - Magic Wand    B - Brush         P - Pencil
  E - Eraser        G - Gradient      U - Shape
  S - Clone Stamp   Y - History Brush H - Hand
  Z - Zoom          I - Color Picker  K - Fill
"""

SHORTCUT_MAP = {}


def register(name, shortcut, cls):
    SHORTCUT_MAP[shortcut.lower()] = cls


class Tool:
    name = "tool"
    shortcut = ""
    cursor_shape = None

    def __init__(self):
        self.pressure = 1.0

    def press(self, canvas, pos, modifiers): pass
    def move(self, canvas, last, pos, modifiers): pass
    def release(self, canvas, pos, modifiers): pass
    def double_click(self, canvas, pos, modifiers): pass


class MoveTool(Tool):
    name = "Move"
    shortcut = "V"

    def press(self, canvas, pos, mods):
        canvas.drag_start = pos
        canvas.dragging_layer = True

    def move(self, canvas, last, pos, mods):
        if canvas.dragging_layer:
            dx = pos.x() - last.x()
            dy = pos.y() - last.y()
            canvas.pan_offset_x += dx
            canvas.pan_offset_y += dy
            canvas.update_pixmap_position()

    def release(self, canvas, pos, mods):
        canvas.dragging_layer = False


class RectSelectTool(Tool):
    name = "Rectangular Select"
    shortcut = "M"

    def press(self, canvas, pos, mods):
        canvas.selection_start = pos
        canvas.rubber_band_start = pos
        canvas.rubber_band_end = pos
        canvas.has_rubber_band = True

    def move(self, canvas, last, pos, mods):
        canvas.rubber_band_end = pos
        canvas.update()

    def release(self, canvas, pos, mods):
        canvas.has_rubber_band = False
        canvas.selection = self._rect(canvas.selection_start, pos)
        canvas.update()

    def _rect(self, p1, p2):
        from PyQt5.QtCore import QRect, QPoint
        x1, y1 = int(p1.x()), int(p1.y())
        x2, y2 = int(p2.x()), int(p2.y())
        return QRect(QPoint(min(x1, x2), min(y1, y2)), QPoint(max(x1, x2), max(y1, y2)))


class EllipseSelectTool(Tool):
    name = "Elliptical Select"
    shortcut = "M"

    def press(self, canvas, pos, mods):
        canvas.selection_start = pos

    def release(self, canvas, pos, mods):
        canvas.update()


class LassoTool(Tool):
    name = "Lasso"
    shortcut = "L"

    def press(self, canvas, pos, mods):
        canvas.lasso_points = [pos]

    def move(self, canvas, last, pos, mods):
        canvas.lasso_points.append(pos)
        canvas.update()

    def release(self, canvas, pos, mods):
        if canvas.lasso_points:
            canvas.lasso_points.append(pos)
        canvas.update()


class MagicWandTool(Tool):
    name = "Magic Wand"
    shortcut = "W"

    def press(self, canvas, pos, mods):
        canvas.flood_fill_select(pos)


class PencilTool(Tool):
    name = "Pencil"
    shortcut = "P"

    def press(self, canvas, pos, mods):
        canvas.draw_point(pos)

    def move(self, canvas, last, pos, mods):
        canvas.draw_line(last, pos)


class BrushTool(Tool):
    name = "Brush"
    shortcut = "B"

    def press(self, canvas, pos, mods):
        canvas.draw_point(pos)

    def move(self, canvas, last, pos, mods):
        canvas.draw_line(last, pos)


class EraserTool(Tool):
    name = "Eraser"
    shortcut = "E"

    def press(self, canvas, pos, mods):
        canvas.erase_point(pos)

    def move(self, canvas, last, pos, mods):
        canvas.erase_line(last, pos)


class GradientTool(Tool):
    name = "Gradient"
    shortcut = "G"

    def press(self, canvas, pos, mods):
        canvas.gradient_start = pos

    def release(self, canvas, pos, mods):
        canvas.draw_gradient(canvas.gradient_start, pos)


class ShapeTool(Tool):
    name = "Shape"
    shortcut = "U"

    def press(self, canvas, pos, mods):
        canvas.shape_start = pos

    def release(self, canvas, pos, mods):
        canvas.draw_rect_shape(canvas.shape_start, pos)


class CloneStampTool(Tool):
    name = "Clone Stamp"
    shortcut = "S"
    clone_source = None

    def press(self, canvas, pos, mods):
        if mods & 0x04000000:  # Alt
            self.clone_source = pos
        elif self.clone_source:
            canvas.clone_stamp(self.clone_source, pos)

    def move(self, canvas, last, pos, mods):
        if self.clone_source and not (mods & 0x04000000):
            dx = pos.x() - last.x()
            dy = pos.y() - last.y()
            src = canvas.clone_source
            canvas.clone_stamp(src, pos)
            canvas.clone_source = src + dx


class ColorPickerTool(Tool):
    name = "Color Picker"
    shortcut = "I"

    def press(self, canvas, pos, mods):
        color = canvas.get_pixel_color(pos)
        if color:
            canvas.set_foreground_color(color)


class FloodFillTool(Tool):
    name = "Flood Fill"
    shortcut = "K"

    def press(self, canvas, pos, mods):
        canvas.flood_fill(pos)


class HandTool(Tool):
    name = "Hand"
    shortcut = "H"

    def press(self, canvas, pos, mods):
        canvas.setDragMode(1)
        super().press(canvas, pos, mods)

    def release(self, canvas, pos, mods):
        canvas.setDragMode(0)
        super().release(canvas, pos, mods)


class ZoomTool(Tool):
    name = "Zoom"
    shortcut = "Z"

    def press(self, canvas, pos, mods):
        if mods & 0x04000000:  # Alt
            canvas.zoom_out()
        else:
            canvas.zoom_in()


# Register all tools
for _cls in [MoveTool, RectSelectTool, EllipseSelectTool, LassoTool,
             MagicWandTool, PencilTool, BrushTool, EraserTool,
             GradientTool, ShapeTool, CloneStampTool,
             ColorPickerTool, FloodFillTool, HandTool, ZoomTool]:
    SHORTCUT_MAP[_cls.shortcut.lower()] = _cls

TOOLS_BY_NAME = {}
for _cls in [MoveTool, RectSelectTool, EllipseSelectTool, LassoTool,
             MagicWandTool, PencilTool, BrushTool, EraserTool,
             GradientTool, ShapeTool, CloneStampTool,
             ColorPickerTool, FloodFillTool, HandTool, ZoomTool]:
    TOOLS_BY_NAME[_cls.name.lower()] = _cls

TOOL_LIST = [
    ("Select", [MoveTool, RectSelectTool, EllipseSelectTool, LassoTool, MagicWandTool]),
    ("Draw", [PencilTool, BrushTool, EraserTool, GradientTool, ShapeTool]),
    ("Retouch", [CloneStampTool]),
    ("Color", [ColorPickerTool, FloodFillTool]),
    ("View", [HandTool, ZoomTool]),
]
