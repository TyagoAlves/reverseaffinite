#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "=== reverseaffinity Sync Script ==="
echo "1) Pull latest from GitHub"
git -C "$REPO_DIR" pull origin main 2>&1
echo "2) Build C++ engine"
bash "$REPO_DIR/cpp_editor/build.sh" 2>&1
echo "3) Build AppImage"
bash "$REPO_DIR/build-appimage.sh" 2>&1
echo "4) Upload AppImage to S3"
aws s3 cp "$REPO_DIR/reverseaffinity-x86_64.AppImage" \
    s3://reverseaffinity-releases/reverseaffinity-x86_64.AppImage 2>&1
echo "5) Push changes to GitHub"
git -C "$REPO_DIR" push origin main 2>&1
echo "=== Sync Complete ==="
