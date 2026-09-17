#!/usr/bin/env bash
set -euo pipefail

project_dir="$PWD/proyecto"
flutter_dir="$PWD/.flutter-sdk"
source_zip="$PWD/Vamos_MVP_Fullstack_1.8.0.zip"

if [[ ! -f "$source_zip" ]]; then
  echo "No se encontró Vamos_MVP_Fullstack_1.8.0.zip en la raíz del repositorio."
  exit 1
fi

if [[ -d "$project_dir" ]]; then
  rm -rf "$project_dir"
fi
mkdir -p "$project_dir"
unzip -q "$source_zip" -d "$project_dir"

if [[ ! -x "$flutter_dir/bin/flutter" ]]; then
  if [[ -d "$flutter_dir" ]]; then
    rm -rf "$flutter_dir"
  fi
  git clone --depth 1 --branch 3.47.2 https://github.com/flutter/flutter.git "$flutter_dir"
fi

export PATH="$flutter_dir/bin:$PATH"

cd "$project_dir/vamos_app"
flutter config --enable-web
flutter create --platforms=web --project-name=vamos_app .

sed -i 's/<title>vamos_app<\/title>/<title>Vamos!! · Carpool Bolivia<\/title>/' web/index.html
sed -i 's/"name": "vamos_app"/"name": "Vamos!!"/' web/manifest.json
sed -i 's/"short_name": "vamos_app"/"short_name": "Vamos!!"/' web/manifest.json

if [[ -f assets/brand/app_icon.png ]]; then
  cp assets/brand/app_icon.png web/favicon.png
  cp assets/brand/app_icon.png web/icons/Icon-192.png
  cp assets/brand/app_icon.png web/icons/Icon-512.png
  cp assets/brand/app_icon.png web/icons/Icon-maskable-192.png
  cp assets/brand/app_icon.png web/icons/Icon-maskable-512.png
fi

flutter pub get
flutter build web \
  --release \
  --base-href / \
  --dart-define=API_BASE_URL=https://vamos-api.onrender.com/api/v1
