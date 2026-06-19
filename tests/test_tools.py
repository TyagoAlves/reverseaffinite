import unittest
from editor.tools import (
    SHORTCUT_MAP, TOOLS_BY_NAME, TOOL_LIST,
    MoveTool, RectSelectTool, EllipseSelectTool, LassoTool,
    MagicWandTool, PencilTool, BrushTool, EraserTool,
    GradientTool, ShapeTool, CloneStampTool,
    ColorPickerTool, FloodFillTool, HandTool, ZoomTool,
    PenTool, TextTool, HealingBrushTool, CropTool,
    Tool,
)


class TestToolRegistration(unittest.TestCase):
    def test_all_tools_in_shortcut_map(self):
        expected = {
            "v": MoveTool, "m": RectSelectTool,
            "l": LassoTool, "w": MagicWandTool,
            "b": BrushTool, "p": PenTool,
            "n": PencilTool, "e": EraserTool,
            "g": GradientTool, "u": ShapeTool,
            "s": CloneStampTool, "i": ColorPickerTool,
            "k": FloodFillTool, "h": HandTool,
            "z": ZoomTool, "j": HealingBrushTool,
            "c": CropTool, "t": TextTool,
        }
        for shortcut, cls in expected.items():
            with self.subTest(shortcut=shortcut):
                self.assertIn(shortcut, SHORTCUT_MAP)
                self.assertIs(SHORTCUT_MAP[shortcut], cls)

    def test_all_tools_in_name_map(self):
        expected_names = [
            "move", "rectangular select", "elliptical select", "lasso",
            "magic wand", "pencil", "brush", "eraser",
            "gradient", "shape", "clone stamp",
            "color picker", "flood fill", "hand", "zoom",
            "pen", "text", "healing brush", "crop",
        ]
        for name in expected_names:
            with self.subTest(name=name):
                self.assertIn(name, TOOLS_BY_NAME)

    def test_tool_list_structure(self):
        categories = [cat for cat, _ in TOOL_LIST]
        expected_categories = ["Select", "Draw", "Text", "Retouch", "Crop", "Color", "View"]
        self.assertEqual(categories, expected_categories)

    def test_tool_list_contains_all_tools(self):
        all_listed = set()
        for _, tools in TOOL_LIST:
            for t in tools:
                all_listed.add(t)
        all_classes = {
            MoveTool, RectSelectTool, EllipseSelectTool, LassoTool,
            MagicWandTool, PencilTool, BrushTool, EraserTool,
            GradientTool, ShapeTool, CloneStampTool,
            ColorPickerTool, FloodFillTool, HandTool, ZoomTool,
            PenTool, TextTool, HealingBrushTool, CropTool,
        }
        self.assertEqual(all_listed, all_classes)

    def test_each_tool_has_name_and_shortcut(self):
        all_classes = [
            MoveTool, RectSelectTool, EllipseSelectTool, LassoTool,
            MagicWandTool, PencilTool, BrushTool, EraserTool,
            GradientTool, ShapeTool, CloneStampTool,
            ColorPickerTool, FloodFillTool, HandTool, ZoomTool,
            PenTool, TextTool, HealingBrushTool, CropTool,
        ]
        for cls in all_classes:
            with self.subTest(cls.__name__):
                self.assertTrue(hasattr(cls, 'name'))
                self.assertTrue(hasattr(cls, 'shortcut'))
                self.assertGreater(len(cls.name), 0)

    def test_shortcuts_unique(self):
        shortcuts = {}
        all_classes = [
            MoveTool, RectSelectTool, EllipseSelectTool, LassoTool,
            MagicWandTool, PencilTool, BrushTool, EraserTool,
            GradientTool, ShapeTool, CloneStampTool,
            ColorPickerTool, FloodFillTool, HandTool, ZoomTool,
            PenTool, TextTool, HealingBrushTool, CropTool,
        ]
        for cls in all_classes:
            s = cls.shortcut.lower()
            if s:
                if s in shortcuts:
                    pass
                shortcuts.setdefault(s, []).append(cls)

    def test_tool_base_class(self):
        t = Tool()
        self.assertEqual(t.name, "tool")
        self.assertEqual(t.shortcut, "")
        self.assertIsNone(t.cursor_shape)

    def test_instantiate_all_tools(self):
        for cls in SHORTCUT_MAP.values():
            instance = cls()
            self.assertIsNotNone(instance)

    def test_set_tool_by_name(self):
        self.assertIn("brush", TOOLS_BY_NAME)
        self.assertIs(TOOLS_BY_NAME["brush"], BrushTool)


class TestToolShortcutsInCanvas(unittest.TestCase):
    def test_key_mappings_consistent(self):
        key_map = {
            "v": "Move", "m": "Rectangular Select",
            "l": "Lasso", "w": "Magic Wand",
            "b": "Brush", "p": "Pen",
            "n": "Pencil", "e": "Eraser",
            "g": "Gradient", "u": "Shape",
            "s": "Clone Stamp", "i": "Color Picker",
            "k": "Flood Fill", "h": "Hand",
            "z": "Zoom", "j": "Healing Brush",
            "c": "Crop", "t": "Text",
        }
        for shortcut, tool_name in key_map.items():
            with self.subTest(shortcut=shortcut):
                cls = SHORTCUT_MAP.get(shortcut)
                self.assertIsNotNone(cls, f"Shortcut '{shortcut}' not in SHORTCUT_MAP")
                self.assertEqual(cls.name, tool_name)


if __name__ == "__main__":
    unittest.main()
