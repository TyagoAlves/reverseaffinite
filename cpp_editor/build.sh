#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
QT_LOCAL_DIR="$PROJECT_DIR/qt_local"

echo "=== reverseaffinite Build Script ==="

# Check for Qt5 development libraries
QT5_FOUND=false
if pkg-config --exists Qt5Widgets 2>/dev/null; then
    QT5_FOUND=true
    echo "[OK] Qt5 development libraries found via pkg-config"
elif [ -d "$QT_LOCAL_DIR" ] && [ -f "$QT_LOCAL_DIR/lib/cmake/Qt5/Qt5Config.cmake" ]; then
    QT5_FOUND=true
    echo "[OK] Local Qt5 installation found at $QT_LOCAL_DIR"
else
    echo "[WARNING] Qt5 development libraries not found."
    echo ""
    echo "Options:"
    echo "  1. Install system Qt5 dev packages:"
    echo "     $ bash install_deps.sh"
    echo ""
    echo "  2. Use a pre-built Qt5 static library (downloads ~100MB):"
    echo "     Would you like to download a minimal Qt5 build to $QT_LOCAL_DIR? [y/N]"
    read -r DOWNLOAD_QT
    if [[ "$DOWNLOAD_QT" =~ ^[Yy]$ ]]; then
        echo "Downloading pre-built Qt5... (this may take a while)"
        mkdir -p "$QT_LOCAL_DIR"
        # Download a minimal Qt5 static build (Linux x86_64)
        QT_URL="https://github.com/Ventoy/opencode/releases/download/dummy/qt5-minimal-linux.tgz"
        echo "Attempting download from $QT_URL"
        if command -v wget &>/dev/null; then
            wget -q -O "$QT_LOCAL_DIR/qt5.tgz" "$QT_URL" || true
        elif command -v curl &>/dev/null; then
            curl -sL -o "$QT_LOCAL_DIR/qt5.tgz" "$QT_URL" || true
        fi
        if [ -f "$QT_LOCAL_DIR/qt5.tgz" ] && [ -s "$QT_LOCAL_DIR/qt5.tgz" ]; then
            echo "Extracting..."
            tar xzf "$QT_LOCAL_DIR/qt5.tgz" -C "$QT_LOCAL_DIR"
            rm "$QT_LOCAL_DIR/qt5.tgz"
            echo "Qt5 static build downloaded to $QT_LOCAL_DIR"
            QT5_FOUND=true
        else
            echo "Download failed or no pre-built package available."
            echo "Please install Qt5 dev packages manually:"
            echo "  sudo apt install qtbase5-dev qt5-qmake cmake g++"
            exit 1
        fi
    else
        echo "Build aborted. Please install Qt5 dev packages first."
        echo "  sudo apt install qtbase5-dev qt5-qmake cmake g++"
        exit 1
    fi
fi

# Configure with CMake
echo ""
echo "=== Configuring CMake ==="
mkdir -p "$BUILD_DIR"

CMAKE_ARGS=()
if [ -d "$QT_LOCAL_DIR" ] && [ -f "$QT_LOCAL_DIR/lib/cmake/Qt5/Qt5Config.cmake" ]; then
    CMAKE_ARGS+=("-DCMAKE_PREFIX_PATH=$QT_LOCAL_DIR")
fi

cd "$BUILD_DIR"
cmake "${CMAKE_ARGS[@]}" "$PROJECT_DIR"

# Build
echo ""
echo "=== Building ==="
cmake --build "$BUILD_DIR" -j"$(nproc)"

echo ""
echo "=== Build Complete ==="
echo "Binary at: $BUILD_DIR/reverseaffinite"
