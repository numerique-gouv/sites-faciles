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
git fetch --all
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

    # Use find to expand wildcard directory paths (e.g. **/migrations)
    matched_dirs=$(find . -type d -path "./$raw_path" 2>/dev/null | while read -r dir; do
        if git ls-files --error-unmatch "$dir/" >/dev/null 2>&1 || \
           git ls-files --cached --others --exclude-standard | grep -q "^${dir#./}/"; then
            echo "$dir"
        fi
    done)

    if [[ -z "$matched_dirs" ]]; then
        echo "⚠️ No matching directories for '$raw_path'"
        continue
    fi

    for dir in $matched_dirs; do
        echo "📂 Searching in tracked files under: $dir"

        # Get all tracked files inside this directory
        tracked_files=$(git ls-files "$dir")

        if [[ -z "$tracked_files" ]]; then
            echo "⚠️ No tracked files in directory '$dir'"
            continue
        fi

        # Find files containing the search string
        files_to_edit=$(echo "$tracked_files" | xargs grep -l "$search" || true)

        if [[ -z "$files_to_edit" ]]; then
            echo "⚠️ No tracked files in '$dir' containing '$search'"
            continue
        fi

        # Apply replacements with cross-platform sed
        while IFS= read -r file; do
            echo "✏️ Rewriting: $file"
            "${SED_INPLACE[@]}" "s|$search|$replace|g" "$file"
        done <<< "$files_to_edit"
    done
done < "$SEARCH_REPLACE"

echo "🆕 Prepare sites_faciles tree"
mkdir -p "$SUBFOLDER"
grep -vxFf $DO_NOT_MOVE <(ls -A) | while read file; do
  echo "🗄️ Moving: $file"
  mv $file "$SUBFOLDER/"
done


echo "🎬 FIN. The repo were synced. Manually check though as it is not battle-tested yet..."
