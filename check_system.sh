#!/bin/bash

echo "=========================================="
echo "   Checking System Compatibility (macOS)  "
echo "=========================================="
echo ""

# 1. Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "[ERROR] Incompatible operating system detected: $(uname)"
    echo "This project requires a macOS system with Apple Silicon."
    exit 1
fi

# 2. Check for Apple Silicon architecture (arm64)
ARCH=$(uname -m)
if [[ "$ARCH" != "arm64" ]]; then
    echo "[ERROR] Incompatible CPU architecture detected: $ARCH"
    echo "This project requires an Apple Silicon Mac (M1/M2/M3/M4 series)."
    echo "Intel Macs are not supported."
    exit 1
fi

echo "[SUCCESS] Apple Silicon Mac detected ($ARCH)."

# 3. Get total physical memory using sysctl and convert bytes to GB
HW_MEM_BYTES=$(sysctl -n hw.memsize)
MEM_GB=$((HW_MEM_BYTES / 1024 / 1024 / 1024))

echo ""
echo "Your machine has ${MEM_GB} GB of total memory."
echo ""