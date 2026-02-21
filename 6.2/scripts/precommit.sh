#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
HOOK_PATH="$ROOT_DIR/../.git/hooks/pre-commit"

if [[ "${1:-}" == "--install" ]]; then
  if [[ ! -d "$ROOT_DIR/../.git/hooks" ]]; then
    echo "No se encontró .git/hooks. ¿Estás en el repo correcto?" >&2
    exit 1
  fi
  cat > "$HOOK_PATH" <<'EOF'
#!/usr/bin/env bash
# Pre-commit hook: bloquea commits si fallan lint/pruebas/cobertura.
# Para forzar (NO recomendado): export BYPASS_HOOK=1 antes de 'git commit'.

if [[ "${BYPASS_HOOK:-0}" == "1" ]]; then
  echo "[pre-commit] BYPASS_HOOK=1 -> saltando validaciones" >&2
  exit 0
fi

set -euo pipefail
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT/6.2"

./scripts/run_checks.sh
EOF
  chmod +x "$HOOK_PATH"
  echo "Hook pre-commit instalado en $HOOK_PATH"
  exit 0
fi

# Ejecuta los checks (modo directo)
"$ROOT_DIR/scripts/run_checks.sh"