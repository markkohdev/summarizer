#!/usr/bin/env zsh

# Paths to your source and destination directories (passed as arguments)
SOURCE_DIR="$1"
DEST_DIR="$2"

# Validate arguments
if [[ -z "$SOURCE_DIR" ]] || [[ -z "$DEST_DIR" ]]; then
    echo "Error: Source and destination directories are required"
    echo "Usage: $0 <source_dir> <dest_dir>"
    exit 1
fi

# Find the newest file in the source directory
LATEST_FILE=$(find "$SOURCE_DIR" -type f -mtime -1m -print0 | xargs -0 ls -t | head -n 1)

# If no recent file is found, exit
if [[ -z "$LATEST_FILE" ]]; then
    exit 0
fi

echo "New file detected: $LATEST_FILE"

# Wait until the file size has not changed for 5 seconds
LAST_SIZE=-1
CURRENT_SIZE=$(stat -f%z "$LATEST_FILE")

while [ "$LAST_SIZE" != "$CURRENT_SIZE" ]; do
    LAST_SIZE=$CURRENT_SIZE
    sleep 10
    CURRENT_SIZE=$(stat -f%z "$LATEST_FILE")
    echo "Checking file size... Last: $LAST_SIZE, Current: $CURRENT_SIZE"
done

echo "File size is stable. Starting rsync."
# Run rsync on the stable file
/usr/bin/rsync -av --ignore-existing "$LATEST_FILE" "$DEST_DIR"

echo "Sync complete."