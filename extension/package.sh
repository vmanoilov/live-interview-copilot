#!/bin/bash

# Package Chrome Extension for Distribution
# Creates a distributable ZIP file of the Live Interview Copilot extension

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Extension name and version from manifest.json
EXTENSION_NAME="live-interview-copilot"
VERSION=$(grep -oP '"version":\s*"\K[^"]+' manifest.json)

# Output directory and filename
OUTPUT_DIR="$SCRIPT_DIR/dist"
OUTPUT_FILE="${EXTENSION_NAME}-v${VERSION}.zip"

echo "===================================="
echo "Packaging Chrome Extension"
echo "===================================="
echo "Extension: $EXTENSION_NAME"
echo "Version: $VERSION"
echo "Output: $OUTPUT_DIR/$OUTPUT_FILE"
echo

# Create dist directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Remove old package if it exists
if [ -f "$OUTPUT_DIR/$OUTPUT_FILE" ]; then
    echo "Removing old package..."
    rm "$OUTPUT_DIR/$OUTPUT_FILE"
fi

# Files and directories to include in the package
INCLUDE_FILES=(
    "manifest.json"
    "background.js"
    "content_script.js"
    "offscreen.html"
    "offscreen.js"
    "popup.html"
    "icons/"
)

echo "Creating package..."

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy files to temporary directory
for item in "${INCLUDE_FILES[@]}"; do
    if [ -d "$item" ]; then
        cp -r "$item" "$TEMP_DIR/"
    elif [ -f "$item" ]; then
        cp "$item" "$TEMP_DIR/"
    else
        echo "Warning: $item not found, skipping..."
    fi
done

# Create ZIP package
cd "$TEMP_DIR"
zip -r "$OUTPUT_DIR/$OUTPUT_FILE" . > /dev/null

echo
echo "✓ Package created successfully!"
echo "  Location: $OUTPUT_DIR/$OUTPUT_FILE"
echo "  Size: $(du -h "$OUTPUT_DIR/$OUTPUT_FILE" | cut -f1)"
echo
echo "Installation Instructions:"
echo "1. Open Chrome and go to chrome://extensions/"
echo "2. Enable 'Developer mode'"
echo "3. Drag and drop the ZIP file or:"
echo "   - Extract the ZIP file"
echo "   - Click 'Load unpacked' and select the extracted folder"
echo
echo "Note: For production distribution, the extension should be published"
echo "      to the Chrome Web Store for automatic updates and user trust."
echo
