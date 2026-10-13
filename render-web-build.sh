#!/usr/bin/env bash
set -euo pipefail

project_dir="$PWD/proyecto"
flutter_dir="$PWD/.flutter-sdk"
source_zip="$PWD/Vamos_MVP_Fullstack_1.9.7.zip"

if [[ ! -f "$source_zip" ]]; then
  echo "No se encontró Vamos_MVP_Fullstack_1.9.7.zip."
  exit 1
fi

rm -rf "$project_dir"
mkdir -p "$project_dir"
unzip -q "$source_zip" -d "$project_dir"

if [[ ! -x "$flutter_dir/bin/flutter" ]]; then
  rm -rf "$flutter_dir"
  git clone --depth 1 --branch 3.47.2 \
    https://github.com/flutter/flutter.git "$flutter_dir"
fi

export PATH="$flutter_dir/bin:$PATH"

cd "$project_dir/vamos_app"

flutter config --enable-web
flutter create --platforms=web --project-name=vamos_app .

rm -f test/widget_test.dart

flutter pub get

flutter build web \
  --release \
  --base-href / \
  --dart-define=API_BASE_URL=https://vamos-api.onrender.com/api/v1
