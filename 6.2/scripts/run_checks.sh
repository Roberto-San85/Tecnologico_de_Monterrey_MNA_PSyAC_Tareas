#!/usr/bin/env bash
set -euo pipefail

# Detecta raíz (carpeta 6.2)
ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "==> Running flake8"
flake8 src tests

echo "==> Running pylint"
if [[ -d "src" ]]; then
  pylint src tests
else
  pylint tests
fi

echo "==> Running unit tests with coverage"
coverage run -m unittest discover -s tests -p "test_*.py" -v
coverage report -m --include="src/*"
