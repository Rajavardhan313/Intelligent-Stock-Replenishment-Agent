#!/bin/bash
cd "$(dirname "$0")/.."
# activate venv if exists
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi
python main.py >> output/etl_run.log 2>&1
