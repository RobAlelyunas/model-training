#!/bin/bash
set -e

echo "Building application with PyInstaller..."
pyinstaller --noconfirm "Interactive Model Training.spec"

echo "Preparing DMG staging directory..."
rm -rf build/dmg
mkdir -p build/dmg
cp -r "dist/Interactive Model Training.app" build/dmg/
ln -s /Applications build/dmg/Applications

echo "Creating DMG package..."
DMG_NAME="dist/Interactive Model Training.dmg"
rm -f "$DMG_NAME"
hdiutil create -volname "Interactive Model Training" -srcfolder build/dmg -ov -format UDZO "$DMG_NAME"

echo "Build complete! Package ready: $DMG_NAME"