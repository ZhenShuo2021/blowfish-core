#!/bin/bash
set -e

repo_url="https://github.com/nunocoracao/blowfish"
repo_dir="temp_repo"
branch="main"

# checkout files
rm -rf $repo_dir
git clone --filter=blob:none --sparse --no-checkout --depth 1 --branch "$branch" "$repo_url" $repo_dir
cd $repo_dir
git sparse-checkout set assets archetypes config data i18n layouts release-versions static
git checkout

# delete unnecessary files
rm -rf -- .git assets/img assets/css/main.css *.js *.md *.json FUNDING.yml LICENSE netlify.toml
find . -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.webp" -o -iname "*.gif" -o -iname "*.ico" \) -delete


# delete old version files
cd ..
find . -maxdepth 1 \
  ! -name ".git" \
  ! -name ".github" \
  ! -name ".venv" \
  ! -name ".vscode" \
  ! -name "LICENSE" \
  ! -name "README.md" \
  ! -name "requirements.txt" \
  ! -name "update.sh" \
  ! -name "$repo_dir" \
  ! -name "." \
  ! -name ".." \
  -exec rm -rf {} +

# move the new versions out
echo "moving files out..."
shopt -s dotglob
mv -v -- ./$repo_dir/* ./

# clear folder
rmdir $repo_dir

# commit changes
# git add .
# git commit -m "update: use latest minimal build files"
