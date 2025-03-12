#!/bin/bash

NEW_FILES="new-files.txt"
DO_NOT_MOVE="do-not-touch.txt"
SEARCH_REPLACE="search-and-replace.csv"
SUBFOLDER="sites_faciles"

# Step 2: Reset the repository to origin/main while keeping new-files.txt
git fetch origin
git reset --hard origin/main
git clean -fd
git restore --source=fork/main $DO_NOT_MOVE
git restore --source=fork/main $NEW_FILES

# Step 3: Move all files (except those in files-to-keep.txt) into sites_faciles
mkdir -p "$SUBFOLDER"
grep -vxFf $DO_NOT_MOVE <(ls -A) | while read file; do
  echo "Moving: $file"
  mv "$file" "$SUBFOLDER/$file"
done

# Step 4: Read new-files.txt and restore files from fork/main
while IFS= read -r file; do
    git restore --source=fork/main $file
done < "$NEW_FILES"

# Step 5: Read search-and-replace.csv and apply replacements in sites_faciles
while IFS=, read -r search replace; do
    grep -rl "$search" "$SUBFOLDER" | xargs sed -i "s|$search|$replace|g"
done < "$SEARCH_REPLACE"

echo "Script execution completed!"

