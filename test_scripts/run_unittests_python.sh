#!/bin/bash

set -e

echo "===== [1/7] Toolchain check ====="
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is not installed or not on PATH."
  exit 69
fi

PYTHON=$(command -v python3)
echo "Python interpreter: $PYTHON"
"$PYTHON" --version

echo ""
echo "===== [2/7] Argument validation ====="
if [ -z "$1" ]; then
  echo "Error: No source build folder provided."
  echo "Usage: $0 <source_build_folder>"
  exit 1
fi

SOURCE_FOLDER="$1"
echo "Source build folder: $(cd "$SOURCE_FOLDER" && pwd)"

echo ""
echo "===== [3/7] Working directory setup ====="
WORKING_FOLDER=".tmp/python_$1"
echo "Working folder: $(pwd)/$WORKING_FOLDER"

if [ -d "$WORKING_FOLDER" ]; then
  echo "Working folder exists — wiping contents..."
  rm -rf "${WORKING_FOLDER:?}"/*
else
  echo "Working folder does not exist — creating it..."
  mkdir -p "$WORKING_FOLDER"
fi

echo ""
echo "===== [4/7] Copy the build ====="
echo "Copying from '$SOURCE_FOLDER' to '$WORKING_FOLDER'..."
cp -R "$SOURCE_FOLDER"/. "$WORKING_FOLDER"/
echo "Copy complete."

echo ""
echo "===== [5/7] Enter working directory ====="
cd "$WORKING_FOLDER" || { echo "Error: Could not enter working folder '$WORKING_FOLDER'."; exit 2; }
echo "Now in: $(pwd)"

echo ""
echo "===== [6/7] Install dependencies ====="
echo "Creating Python virtual environment at $(pwd)/.venv ..."
"$PYTHON" -m venv .venv
echo "Virtual environment created."

echo "Installing dependencies from requirements.txt into .venv ..."
./.venv/bin/pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  echo "Found requirements.txt — running: ./.venv/bin/pip install -r requirements.txt"
  ./.venv/bin/pip install -r requirements.txt || exit $?
else
  echo "No requirements.txt found — skipping package install."
fi
echo "Dependency install complete."

echo ""
echo "===== [7/7] Run unit tests ====="
echo "Test command: ./.venv/bin/pytest"
echo "Working directory: $(pwd)"
echo ""
./.venv/bin/pytest
TEST_EXIT=$?

echo ""
echo "===== Summary ====="
echo "Test command : ./.venv/bin/pytest"
echo "Working folder: $(pwd)"
echo "Exit code     : $TEST_EXIT"
exit $TEST_EXIT
