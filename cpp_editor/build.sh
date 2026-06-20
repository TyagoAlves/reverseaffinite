#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="/tmp/reverseaffinite_build"
QT_LOCAL_DIR="$PROJECT_DIR/qt_local/gcc_64"

echo "=== reverseaffinite Build Script ==="

# Check for Qt5 headers
if [ ! -d "$QT_LOCAL_DIR/include/QtCore" ]; then
    echo ""
    echo "[INFO] Qt5 headers not found locally."
    echo "Attempting to download Qt5 SDK using aqtinstall..."
    echo ""

    # Ensure aqtinstall is available
    if python3 -c "import aqt" 2>/dev/null; then
        AQT_CMD="python3 -m aqt"
    elif [ -f /tmp/qt_venv/bin/python ]; then
        AQT_CMD="/tmp/qt_venv/bin/python -m aqt"
    else
        echo "[INFO] Installing aqtinstall..."
        pip install aqtinstall -q 2>&1 && AQT_CMD="python3 -m aqt" || true
    fi

    if [ -n "$AQT_CMD" ]; then
        echo "Downloading Qt5 5.15.2..."
        QT_TMP=$(mktemp -d)
        $AQT_CMD install-qt linux desktop 5.15.2 gcc_64 -O "$QT_TMP" 2>&1
        echo "Copying to $QT_LOCAL_DIR..."
        rm -rf "$QT_LOCAL_DIR"
        mkdir -p "$PROJECT_DIR/qt_local"
        (cd "$QT_TMP/5.15.2" && tar cf - gcc_64 --dereference) | (cd "$PROJECT_DIR/qt_local" && tar xf - 2>/dev/null || true)
        rm -rf "$QT_TMP"
        find "$QT_LOCAL_DIR/lib/cmake" -name "*.cmake" -exec sed -i 's/\(libQt5[^.]*\)\.so\.5\.15\.2/\1.so/g' {} \; 2>/dev/null || true
    else
        echo "[WARNING] aqtinstall not available. Try: pip install aqtinstall"
        echo "Qt5 headers will not be available - build may fail."
    fi
fi

if [ -d "$QT_LOCAL_DIR/include/QtCore" ]; then
    echo "[OK] Qt5 headers found at $QT_LOCAL_DIR"
else
    echo "[ERROR] Qt5 headers not found! Please run 'pip install aqtinstall' first, then this script."
    exit 1
fi

# Configure with CMake
echo ""
echo "=== Configuring CMake ==="
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cmake -S "$PROJECT_DIR" -B "$BUILD_DIR" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

# Build
echo ""
echo "=== Building ==="
cmake --build "$BUILD_DIR" -j"$(nproc)" 2>&1

echo ""
echo "=== Build Complete ==="
echo "Binary at: $BUILD_DIR/reverseaffinite"
echo ""
echo "To run: $BUILD_DIR/reverseaffinite"
