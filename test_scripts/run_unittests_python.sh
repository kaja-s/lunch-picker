#!/bin/bash

echo "===== [1/7] Toolchain check ====="
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is not installed or not on PATH."
  exit 69
fi
PYTHON_BIN=$(command -v python3)
echo "Python binary: $PYTHON_BIN"
python3 --version

echo ""
echo "===== [2/7] Argument validation ====="
if [ -z "$1" ]; then
  echo "Error: No source build folder provided."
  echo "Usage: $0 <source_build_folder>"
  exit 1
fi
SOURCE_FOLDER="$1"
if [ ! -d "$SOURCE_FOLDER" ]; then
  echo "Error: Source build folder '$SOURCE_FOLDER' does not exist or is not a directory."
  exit 2
fi
echo "Source build folder: $(cd "$SOURCE_FOLDER" && pwd)"

echo ""
echo "===== [3/7] Working directory setup ====="
WORKING_FOLDER=".tmp/python_${1//\//_}"
if [ -d "$WORKING_FOLDER" ]; then
  echo "Working folder '$WORKING_FOLDER' exists — wiping contents."
  rm -rf "${WORKING_FOLDER:?}"/*
else
  echo "Working folder '$WORKING_FOLDER' does not exist — creating it."
  mkdir -p "$WORKING_FOLDER"
fi
echo "Working folder: $(pwd)/$WORKING_FOLDER"

echo ""
echo "===== [4/7] Copy build ====="
echo "Copying from '$SOURCE_FOLDER' to '$WORKING_FOLDER'..."
cp -R "$SOURCE_FOLDER"/. "$WORKING_FOLDER"/
echo "Copy complete."

echo ""
echo "===== [5/7] Enter working directory ====="
echo "Moving to: $(pwd)/$WORKING_FOLDER"
cd "$WORKING_FOLDER" || { echo "Error: Could not enter '$WORKING_FOLDER'."; exit 69; }
echo "Now in: $(pwd)"

echo ""
echo "===== [6/7] Install dependencies ====="
echo "Creating virtual environment at $(pwd)/.venv using $PYTHON_BIN..."
python3 -m venv .venv || { echo "Error: Failed to create venv."; exit 69; }
echo "Virtual environment created."

echo "Installing dependencies from requirements.txt into $(pwd)/.venv..."
./.venv/bin/pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  ./.venv/bin/pip install -r requirements.txt || exit $?
else
  echo "No requirements.txt found — skipping dependency install."
fi
echo "Dependency install complete."

echo ""
echo "===== [7/7] Run unit tests ====="
echo "Test command: ./.venv/bin/pytest tests/ -v"
echo "Working directory: $(pwd)"
./.venv/bin/pytest tests/ -v
EXIT_CODE=$?
echo ""
echo "===== Test run complete: exit code $EXIT_CODE | working folder: $(pwd) ====="
exit $EXIT_CODE