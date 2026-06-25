#!/bin/bash

# Install-inline variant: no prepare_environment_python.sh found.
# Stages the build into .tmp/, creates a venv, installs deps, and runs pytest.

UNRECOVERABLE_ERROR_EXIT_CODE=69

echo "===== [1/8] Toolchain check ====="
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    printf "Error: Python interpreter not found. Please install Python.\n"
    exit $UNRECOVERABLE_ERROR_EXIT_CODE
fi
echo "Python binary: $(command -v "$PYTHON_CMD")"
"$PYTHON_CMD" --version

echo ""
echo "===== [2/8] Argument validation ====="
if [ -z "$1" ]; then
    printf "Error: No build folder name provided.\n"
    printf "Usage: $0 <build_folder_name> <conformance_tests_folder>\n"
    exit $UNRECOVERABLE_ERROR_EXIT_CODE
fi
if [ -z "$2" ]; then
    printf "Error: No conformance tests folder name provided.\n"
    printf "Usage: $0 <build_folder_name> <conformance_tests_folder>\n"
    exit $UNRECOVERABLE_ERROR_EXIT_CODE
fi
BUILD_FOLDER="$1"
CONFORMANCE_TESTS_FOLDER="$2"
echo "Build folder:            $BUILD_FOLDER"
echo "Conformance tests folder: $CONFORMANCE_TESTS_FOLDER"

echo ""
echo "===== [3/8] Capture original working directory ====="
current_dir=$(pwd)
echo "Captured current_dir:            $current_dir"
echo "Resolved conformance tests path: $current_dir/$CONFORMANCE_TESTS_FOLDER"

echo ""
echo "===== [4/8] Working directory setup (install-inline variant) ====="
WORKING_FOLDER=".tmp/python_${BUILD_FOLDER//\//_}"
echo "Working folder: $(pwd)/$WORKING_FOLDER"
if [ -d "$WORKING_FOLDER" ]; then
    echo "Working folder exists — wiping contents."
    find "$WORKING_FOLDER" -mindepth 1 -exec rm -rf {} +
else
    echo "Working folder does not exist — creating it."
    mkdir -p "$WORKING_FOLDER"
fi

echo ""
echo "===== [5/8] Copy build ====="
echo "Copying from '$BUILD_FOLDER' to '$WORKING_FOLDER'..."
cp -R "$BUILD_FOLDER"/. "$WORKING_FOLDER"/
echo "Copy complete."

echo ""
echo "===== [6/8] Enter working directory ====="
echo "Moving to: $(pwd)/$WORKING_FOLDER"
cd "$WORKING_FOLDER" 2>/dev/null
if [ $? -ne 0 ]; then
    printf "Error: Could not enter working folder '%s'.\n" "$WORKING_FOLDER"
    exit $UNRECOVERABLE_ERROR_EXIT_CODE
fi
echo "Now in: $(pwd)"

echo ""
echo "===== [7/8] Install dependencies ====="
echo "Creating virtual environment at $(pwd)/.venv using $PYTHON_CMD..."
VENV_DIR=".venv"
start_seconds=$SECONDS

if ! "$PYTHON_CMD" -m venv "$VENV_DIR"; then
    printf "Error: Failed to create virtual environment in '%s'.\n" "$VENV_DIR"
    exit $UNRECOVERABLE_ERROR_EXIT_CODE
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    printf "Error: Failed to activate virtual environment at '%s/bin/activate'.\n" "$VENV_DIR"
    exit $UNRECOVERABLE_ERROR_EXIT_CODE
fi
echo "Virtual environment activated: $VIRTUAL_ENV"

pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt || exit $?
else
    echo "No requirements.txt found — skipping."
fi

if ! command -v pytest &>/dev/null; then
    echo "pytest not found in venv — installing..."
    pip install pytest || exit $?
fi

echo "Requirements setup completed in $((SECONDS - start_seconds)) seconds."

echo ""
echo "===== [8/8] Run conformance tests ====="
echo "Test command: pytest \"$current_dir/$CONFORMANCE_TESTS_FOLDER\" -v"
echo "Working directory: $(pwd)"
echo "VIRTUAL_ENV:  $VIRTUAL_ENV"
echo ""

output=$(pytest "$current_dir/$CONFORMANCE_TESTS_FOLDER" -v 2>&1)
exit_code=$?

echo "$output"

# pytest exits 5 when no tests are collected; also guard on output
if [ $exit_code -eq 5 ] || echo "$output" | grep -qE "collected 0 items|no tests ran"; then
    printf "\nError: No conformance tests discovered.\n"
    exit 1
fi

echo ""
echo "===== Test run complete (install-inline variant) ====="
echo "Test command:  pytest \"$current_dir/$CONFORMANCE_TESTS_FOLDER\" -v"
echo "Exit code:     $exit_code"
echo "current_dir:   $current_dir"
echo "Working folder: $(pwd)"

exit $exit_code
