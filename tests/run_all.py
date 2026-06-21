#!/usr/bin/env python3
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_layers import TestBlendFunctions, TestLayer, TestAdjustmentLayer, \
    TestGroupLayer, TestLayerStack, TestFloatArrayConversion
from tests.test_filters import TestArrayConversion, TestFilters, TestFilterEdgeCases
from tests.test_tools import TestToolRegistration, TestToolShortcutsInCanvas
from tests.test_history import TestHistoryEntry, TestHistoryManager
from tests.test_canvas import TestCanvasComposite, TestCanvasSelection, \
    TestCanvasFileIO, TestCanvasZoomPan, TestCanvasDrawing, TestCanvasMoveLayer

from tests.test_regressions import (
    TestColorDodgeNoNan, TestColorBurnNoInf,
    TestFilterPreservesAlpha, TestBrightnessClipping, TestCanvasMemory,
)
from tests.test_integration import (
    TestCreateDrawFilterSaveReopen, TestLayerAddPaintFlatten,
    TestUndoRedoSequence, TestSelectionFillVerify,
    TestLayerBlendModes, TestLayerOpacity,
)


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for tc in [
        TestBlendFunctions, TestLayer, TestAdjustmentLayer, TestGroupLayer,
        TestLayerStack, TestFloatArrayConversion,
        TestArrayConversion, TestFilters, TestFilterEdgeCases,
        TestToolRegistration, TestToolShortcutsInCanvas,
        TestHistoryEntry, TestHistoryManager,
        TestCanvasComposite, TestCanvasSelection, TestCanvasFileIO,
        TestCanvasZoomPan, TestCanvasDrawing, TestCanvasMoveLayer,
        TestColorDodgeNoNan, TestColorBurnNoInf,
        TestFilterPreservesAlpha, TestBrightnessClipping, TestCanvasMemory,
        TestCreateDrawFilterSaveReopen, TestLayerAddPaintFlatten,
        TestUndoRedoSequence, TestSelectionFillVerify,
        TestLayerBlendModes, TestLayerOpacity,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(tc))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
