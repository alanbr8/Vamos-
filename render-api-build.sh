#!/usr/bin/env bash
set -euo pipefail

repo_dir="$PWD"
project_dir="$repo_dir/proyecto"
source_zip="$repo_dir/Vamos_MVP_Fullstack_1.9.7_Revision_Sofia.zip"

test -f "$source_zip"
rm -rf "$project_dir"
mkdir -p "$project_dir"
unzip -q "$source_zip" -d "$project_dir"
nested_dir="$project_dir/Vamos_MVP_Fullstack_1.9.7 (1)"
if [[ -d "$nested_dir/backend" ]]; then
  cp -a "$nested_dir/." "$project_dir/"
  rm -rf "$nested_dir"
fi

python3 "$repo_dir/tool/sofia-review/prepare.py" "$project_dir"
python3 "$repo_dir/tool/chat-expiry/apply.py" "$project_dir"
test -f "$project_dir/backend/src/review-panel.ts"

cd "$project_dir/backend"
cat > tsconfig.build.json <<'JSON'
{
  "extends": "./tsconfig.json",
  "compilerOptions": { "rootDir": "./src" },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist", "test", "src/**/*.spec.ts"]
}
JSON
npm ci --include=dev
npm run build
test -f dist/main.js
test -f dist/review-panel.js
