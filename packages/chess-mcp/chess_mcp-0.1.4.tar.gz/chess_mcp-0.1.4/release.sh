#!/bin/bash

# Release script for chess-mcp package
# Usage: ./release.sh [KIND]
# KIND can be: patch, minor, major (default: patch)

set -e  # Exit on any error

# Get the bump kind from argument or default to patch
kind=${1:-patch}

echo "🚀 Starting release process with kind: $kind"

# Bump the version using uv
uv version --bump $kind

# Get the new version
v=$(uv version | awk '{print $NF}')

echo "📦 New version: $v"

# Update version in server.json
sed -i "s/\"version\": \"[^\"]*\"/\"version\": \"$v\"/g" server.json

# Add files to git
git add pyproject.toml server.json

# Commit the changes
git commit -m "chore: release v$v"

# Create and push tag
git tag "v$v"
git push origin HEAD
git push origin "v$v"

echo "✅ Released v$v"