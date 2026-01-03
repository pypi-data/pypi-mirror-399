#!/bin/bash

set -eu

cd "$(dirname "$0")/.."

PKG="django_schedules"
echo "--> Running isort"
uv run isort "${PKG}"
echo "--> Running pylint"
uv run pylint --exit-zero --jobs 0 "${PKG}"
echo "--> Running ruff"
uv run ruff check
uv run ruff format
echo "--> Running mypy"
set +e  # mypy has no flag to exit with 0
uv run mypy "${PKG}"
set -e
echo "--> Running ty"
uv run ty check --exit-zero
# echo "--> Running tox"
# uv run tox

# Run the scripts
CMDS=()
for cmd in "${CMDS[@]}"; do
    uv run "${cmd}" --version
done
