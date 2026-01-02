# Secapka

Framework CLI pour analyser des APK Android et produire un rapport JSON (et export SARIF).

## Installation
### pipx (recommandé)
```bash
pipx install secapka
secapka -V
```

## pip (venv)
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install secapka
secapka -V
```

## Utilisation
### Scan (APK/XAPK → JSON)
```bash
secapka scan app.apk -o report.json
secapka scan bundle.xapk -o report.json
```

## Afficher un rapport
```bash
secapka show report.json
secapka show report.json --full
```

## Export SARIF
```bash
secapka export report.json -o report.sarif
```

## Développement
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"

ruff format .
ruff check --fix .
pytest
```

[![PyPI](https://img.shields.io/pypi/v/secapka)](https://pypi.org/project/secapka/)
[![CI](https://github.com/Pi3rrhUs/Secapka/actions/workflows/ci.yml/badge.svg)](https://github.com/Pi3rrhUs/Secapka/actions/workflows/ci.yml)



