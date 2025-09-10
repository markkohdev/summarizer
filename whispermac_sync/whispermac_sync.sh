#!/usr/bin/env zsh

# Paths to your source and destination directories
SOURCE_DIR="$HOME/Library/Application Support/MacWhisper/GlobalRecordings/"
DEST_DIR="$HOME/Library/CloudStorage/Dropbox/Note Systems/whispermac_work/global_recordings_sync_watched"

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