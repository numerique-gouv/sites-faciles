#!/bin/bash

NEW_FILES="new-files.txt"
DO_NOT_MOVE="do-not-touch.txt"
SEARCH_REPLACE="search-and-replace.csv"
SUBFOLDER="sites_faciles"

echo "🔄 Reset the repo to latest commit on the main branch"
git fetch origin
git reset --hard origin/main
git clean -fd

shopt -s globstar nullglob  # Enable ** matching and prevent empty globs from expanding to literal

echo "📝 Rewrite files to namespace everything"
# while IFS=, read -r search replace path; do
#     echo "$search > $replace in $path"
#     if [ -d "$path" ]; then
#         grep -rl "$search" "$path" | xargs sed -i "s|$search|$replace|g"
#     else
#         echo "⚠️ Warning: Path '$path' does not exist or is not a directory. Skipping..."
#     fi
# done < "$SEARCH_REPLACE"

while IFS=, read -r search replace raw_path; do
    echo "$search > $replace in $raw_path"

    # Expand wildcard path to actual directories
    for path in $raw_path; do
        if [ -d "$path" ]; then
            grep -rl "$search" "$path" | xargs sed -i "s|$search|$replace|g"
        else
            echo "⚠️ Warning: Path '$path' does not exist or matched nothing. Skipping..."
        fi
    done
done < "$SEARCH_REPLACE"

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


echo "🎬 FIN. The repo were synced. Manually check though as it is not battle-tested yet..."
