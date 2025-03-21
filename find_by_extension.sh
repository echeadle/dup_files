#!/bin/bash

# Usage: ./find_by_extension.sh /path/to/search .ext

SEARCH_DIR=$1
EXTENSION=$2

if [[ -z "$SEARCH_DIR" || -z "$EXTENSION" ]]; then
  echo "Usage: $0 <search_directory> <file_extension>"
  echo "Example: $0 ~/projects .mako"
  exit 1
fi

# Use find to search for the file extension, case-insensitive
find "$SEARCH_DIR" -type f -iname "*$EXTENSION"
