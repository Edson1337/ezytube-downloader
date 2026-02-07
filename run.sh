#!/bin/bash
cd "$(dirname "$0")"
export PATH="$PWD/bin:$PATH"
uv run python src/main.py
