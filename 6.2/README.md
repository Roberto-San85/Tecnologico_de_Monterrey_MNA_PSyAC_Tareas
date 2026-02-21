# Actividad 6.2 – Sistema de Reservaciones

Este proyecto se construye paso a paso, con buenas prácticas de commits, pruebas unitarias,
cobertura y analizadores estáticos (Flake8 y Pylint).

## Cómo validar
```bash
cd 6.2
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
./scripts/run_checks.sh
```
## Hook pre-commit
```bash
cd 6.2
./scripts/precommit.sh --install
# Para saltarlo (no recomendado):
# BYPASS_HOOK=1 git commit -m "..."
```