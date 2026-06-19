#!/usr/bin/env python3
"""
Demonstration script for reverseaffinite.
Creates an image, applies tools and filters, tests undo/redo,
and saves the result as demo_output.png.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
app = QApplication(sys.argv)

from PyQt5.QtCore import Qt, QPointF, QRect
from PyQt5.QtGui import QColor

from editor.canvas import CanvasView


def demo():
    canvas = CanvasView()
    canvas.new_image(400, 300, QColor(255, 255, 255))

    # Draw with brush
    canvas._save_state("Brush rectangle")
    canvas.set_tool("Brush")
    canvas.tool_color = QColor(220, 50, 50)
    canvas.tool_size = 8
    canvas.draw_point(QPointF(100, 80))
    canvas.draw_line(QPointF(100, 80), QPointF(300, 80))
    canvas.draw_line(QPointF(300, 80), QPointF(300, 220))
    canvas.draw_line(QPointF(300, 220), QPointF(100, 220))
    canvas.draw_line(QPointF(100, 220), QPointF(100, 80))

    # Draw with pencil
    canvas._save_state("Pencil star")
    canvas.set_tool("Pencil")
    canvas.tool_color = QColor(50, 120, 220)
    canvas.tool_size = 3
    canvas.draw_point(QPointF(200, 50))
    canvas.draw_line(QPointF(200, 50), QPointF(350, 150))
    canvas.draw_line(QPointF(350, 150), QPointF(200, 250))
    canvas.draw_line(QPointF(200, 250), QPointF(50, 150))
    canvas.draw_line(QPointF(50, 150), QPointF(200, 50))

    # Draw a shape
    canvas._save_state("Shape rectangle")
    canvas.set_tool("Shape")
    canvas.tool_color = QColor(50, 200, 80)
    canvas.tool_size = 3
    canvas.draw_rect_shape(QPointF(130, 110), QPointF(270, 190))

    # Test undo
    print("Testing undo...")
    assert canvas.history.can_undo(), "Should be able to undo"
    canvas.history.undo(canvas.layer_stack)
    canvas._refresh()
    print("  Undo: OK")

    # Test redo
    print("Testing redo...")
    assert canvas.history.can_redo(), "Should be able to redo"
    canvas.history.redo(canvas.layer_stack)
    canvas._refresh()
    print("  Redo: OK")

    # Apply filters
    print("Applying filters...")

    from editor.filters import grayscale, posterize

    # Add a new layer for filter demo
    canvas._save_state("Add layer")
    canvas.layer_stack.add_layer("Filter Demo")
    canvas._refresh()

    # Draw on new layer
    canvas.tool_color = QColor(255, 200, 50)
    canvas.set_tool("Brush")
    canvas.draw_point(QPointF(200, 150))

    # Apply grayscale to first layer
    canvas.layer_stack.active_index = 0
    canvas.layer_stack.active.image = grayscale(canvas.layer_stack.active.image)
    canvas._refresh()

    # Apply posterize to second layer
    canvas.layer_stack.active_index = 1
    canvas.layer_stack.active.image = posterize(canvas.layer_stack.active.image, 6)
    canvas._refresh()

    print("  Filters: OK")

    # Test file save
    from tempfile import mkstemp
    fd, path = mkstemp(suffix=".png")
    os.close(fd)
    result = canvas.save_image(path)
    assert result, "Save should succeed"
    print(f"  Saved to {path}: OK")

    # Reload
    result = canvas.open_image(path)
    assert result, "Open should succeed"
    print("  Reload: OK")

    os.unlink(path)

    # Test selection
    print("Testing selections...")
    canvas.set_selection_rect(QRect(50, 50, 100, 100))
    assert canvas.has_selection(), "Selection should exist"
    canvas.clear_selection()
    assert not canvas.has_selection(), "Selection should be cleared"
    print("  Selections: OK")

    # Test layer operations
    print("Testing layer operations...")
    canvas._save_state("Add layer 1")
    canvas.layer_stack.add_layer("Test Layer")
    assert len(canvas.layer_stack.layers) == 2, "Should have 2 layers"

    canvas._save_state("Duplicate layer")
    canvas.layer_stack.duplicate_layer(0)
    assert len(canvas.layer_stack.layers) == 3, "Should have 3 layers after duplicate"

    canvas._save_state("Flatten")
    canvas.layer_stack.flatten()
    assert len(canvas.layer_stack.layers) == 1, "Should have 1 layer after flatten"
    print("  Layer operations: OK")

    # Final save
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_output.png")
    canvas.save_image(output_path)
    print(f"\nDemo output saved to: {output_path}")
    print("All demo operations completed successfully!")

    return 0


if __name__ == "__main__":
    sys.exit(demo())
