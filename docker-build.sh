#!/bin/bash
# Docker build script with automatic version detection
set -e

# Get version information from Git
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT=$(git rev-parse --short HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
VERSION=$(git describe --tags --always)

echo "🐳 Building RAG Fetch Docker image..."
echo "📦 Version: $VERSION"
echo "📅 Build Date: $BUILD_DATE"
echo "🔨 Git Commit: $GIT_COMMIT"
echo "🌿 Git Branch: $GIT_BRANCH"
echo

# Build the Docker image with version information
docker build \
  --target production \
  --build-arg BUILD_DATE="$BUILD_DATE" \
  --build-arg GIT_COMMIT="$GIT_COMMIT" \
  --build-arg GIT_BRANCH="$GIT_BRANCH" \
  --build-arg VERSION="$VERSION" \
  -t rag-fetch:$VERSION \
  -t rag-fetch:latest \
  .

echo "✅ Build complete!"
echo
echo "🔍 To inspect version labels:"
echo "docker inspect rag-fetch:$VERSION | grep -A 20 Labels"
echo
echo "🚀 To run the container:"
echo "docker-compose up -d"
echo
echo "📊 To check version via health endpoint:"
echo "curl http://localhost:8080/health"