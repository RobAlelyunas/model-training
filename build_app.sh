#!/bin/bash
set -e

echo "Building application with PyInstaller..."
pyinstaller --noconfirm "Interactive Model Training.spec"

echo "Build complete! App ready at: dist/Interactive Model Training.app"