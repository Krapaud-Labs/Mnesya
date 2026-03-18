#!/bin/bash

set -e

BUMP=${1:-patch}

if [[ "$BUMP" != "patch" && "$BUMP" != "minor" && "$BUMP" != "major" ]]; then
  echo "Usage: ./release.sh [patch|minor|major]"
  exit 1
fi

APP_JSON="frontend/app.json"

CURRENT=$(node -e "console.log(require('./$APP_JSON').expo.version)")
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

if [[ "$BUMP" == "major" ]]; then
  MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0
elif [[ "$BUMP" == "minor" ]]; then
  MINOR=$((MINOR + 1)); PATCH=0
else
  PATCH=$((PATCH + 1))
fi

NEW_VERSION="$MAJOR.$MINOR.$PATCH"

# Update version in app.json
node -e "
const fs = require('fs');
const json = JSON.parse(fs.readFileSync('$APP_JSON', 'utf8'));
json.expo.version = '$NEW_VERSION';
fs.writeFileSync('$APP_JSON', JSON.stringify(json, null, 2) + '\n');
"

echo "Version bumped: $CURRENT → $NEW_VERSION"

git add $APP_JSON
git commit -m "chore: bump version to $NEW_VERSION"
git push

echo "Launching EAS build..."
cd frontend && eas build --platform ios --profile production
