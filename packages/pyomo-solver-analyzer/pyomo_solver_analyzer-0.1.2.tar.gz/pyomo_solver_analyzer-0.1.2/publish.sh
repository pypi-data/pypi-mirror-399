#!/bin/bash

# Script to update PyPI version, build, and upload to PyPI

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if pyproject.toml exists
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

# Extract current version
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')

if [ -z "$CURRENT_VERSION" ]; then
    print_error "Could not find version in pyproject.toml"
    exit 1
fi

print_info "Current version: $CURRENT_VERSION"

# Parse version components
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Increment patch version
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"

print_info "New version: $NEW_VERSION"

# Ask for confirmation
read -p "Proceed with publishing version $NEW_VERSION? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_error "Publishing cancelled."
    exit 1
fi

# Update version in pyproject.toml
print_status "Updating version in pyproject.toml..."
sed -i '' "s/^version = \"${CURRENT_VERSION}\"/version = \"${NEW_VERSION}\"/" pyproject.toml

# Verify the update
UPDATED_VERSION=$(grep '^version = ' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
if [ "$UPDATED_VERSION" != "$NEW_VERSION" ]; then
    print_error "Failed to update version in pyproject.toml"
    exit 1
fi
print_status "Version updated to $NEW_VERSION"

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# Build the library
print_status "Building library..."
python3 -m build

# Check if build was successful
if [ $? -ne 0 ]; then
    print_error "Build failed"
    exit 1
fi
print_status "Build completed successfully"

# Upload to PyPI
print_status "Uploading to PyPI..."
python3 -m twine upload dist/* --skip-existing

if [ $? -eq 0 ]; then
    print_status "Successfully published version $NEW_VERSION to PyPI"
    print_info "Don't forget to commit and tag this release!"
    print_info "  git add pyproject.toml"
    print_info "  git commit -m 'Release v${NEW_VERSION}'"
    print_info "  git tag -a v${NEW_VERSION} -m 'Version ${NEW_VERSION}'"
    print_info "  git push origin main --tags"
else
    print_error "Upload to PyPI failed"
    exit 1
fi
