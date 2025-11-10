#!/bin/bash

# This script renames files in a specified directory by replacing characters
# that are not ideal for filenames with a hyphen '-'.
#
# Usage:
#   ./check_filename.sh [path]
#
# If [path] is not provided, it defaults to the current directory.

# Set the target directory from the first argument, or default to '.'
TARGET_DIR=${1:-.}

# Check if the target directory exists
if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: Directory '$TARGET_DIR' not found."
  exit 1
fi

echo "Scanning directory: $TARGET_DIR"

# Use find to locate all files and pipe them to the while loop
# -print0 and read -d '' handle filenames with spaces or special characters
find "$TARGET_DIR" -type f | while IFS= read -r FILEPATH; do
  # Extract the directory and filename
  DIR=$(dirname "$FILEPATH")
  FILENAME=$(basename "$FILEPATH")

  # Create the new filename by replacing unwanted characters with a hyphen
  # Unwanted characters include: \ / : * ? " < > | and any whitespace
  NEW_FILENAME=$(echo "$FILENAME" | sed -E 's/[\\/:"*?<>|[:space:]]+/-/g')

  # Check if the filename needs to be changed
  if [ "$FILENAME" != "$NEW_FILENAME" ]; then
    # Construct the new full path
    NEW_FILEPATH="$DIR/$NEW_FILENAME"

    # Rename the file, checking for potential name collisions
    if [ -e "$NEW_FILEPATH" ]; then
      echo "Skipping rename of '$FILENAME' to '$NEW_FILENAME' because destination already exists."
    else
      echo "Renaming '$FILENAME' to '$NEW_FILENAME'"
      mv "$FILEPATH" "$NEW_FILEPATH"
    fi
  fi
done

echo "File check and renaming complete."
