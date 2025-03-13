#!/bin/bash

NEW_FILES="new-files.txt"
DO_NOT_MOVE="do-not-touch.txt"
SEARCH_REPLACE="search-and-replace.csv"
SUBFOLDER="sites_faciles"

echo "🔄 Reset the repo to latest commit on the main branch"
git fetch origin
git reset --hard origin/main
git clean -fd

echo "♻️ Get back list of files to keep from the fork"
git restore --source=fork/main $NEW_FILES
while IFS= read -r file; do
    echo "$file"
    git restore --source=fork/main $file
done < "$NEW_FILES"

ls -la sites_faciles/content_manager

echo "🆕 Prepare sites_faciles tree"
mkdir -p "$SUBFOLDER"
grep -vxFf $DO_NOT_MOVE <(ls -A) | while read file; do
  echo "🗄️ Moving: $file"
  mv $file "$SUBFOLDER/"
done


echo "📝 Rewrite files to namespace everything"
while IFS=, read -r search replace; do
    echo "$search > $replace"
    grep -rl "$search" "$SUBFOLDER" | xargs sed -i "s|$search|$replace|g"
done < "$SEARCH_REPLACE"

echo "🎬 FIN. The repo were synced. Manually check though as it is not battle-tested yet..."
