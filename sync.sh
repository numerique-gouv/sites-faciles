#!/bin/bash

NEW_FILES="new-files.txt"
DO_NOT_MOVE="do-not-touch.txt"
SEARCH_REPLACE="search-and-replace.csv"
SUBFOLDER="sites_faciles"

# Detect OS for sed compatibility
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_INPLACE=("sed" "-i" "")
else
    SED_INPLACE=("sed" "-i")
fi

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


echo "📝 Rewrite files to namespace everything"
while IFS=, read -r search replace raw_path; do
    echo "🔁 $search > $replace in $raw_path"

    # Get files tracked by git in raw_path, filtered by search string
    matched_files=$(git ls-files "$raw_path" | xargs grep -l "$search" || true)

    if [[ -z "$matched_files" ]]; then
        echo "⚠️ Warning: No tracked files in '$raw_path' containing '$search'"
        continue
    fi

    while IFS= read -r file; do
        echo "✏️ Rewriting: $file"
        "${SED_INPLACE[@]}" "s|$search|$replace|g" "$file"
    done <<< "$matched_files"
done < "$SEARCH_REPLACE"


ls -la sites_faciles/content_manager

# echo "🆕 Prepare sites_faciles tree"
# mkdir -p "$SUBFOLDER"
# grep -vxFf $DO_NOT_MOVE <(ls -A) | while read file; do
#   echo "🗄️ Moving: $file"
#   mv $file "$SUBFOLDER/"
# done


echo "🎬 FIN. The repo were synced. Manually check though as it is not battle-tested yet..."
