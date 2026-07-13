# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projects in this repository

This repo holds a few independent CLI tools (no shared build/test setup):

- `x_pdca.py` + `modules/` — X (Twitter) account PDCA tracker. Stdlib only, JSON storage in `data/`.
- `fx_predict.py` + `fx_modules/` — USD/JPY rate forecaster using an LSTM (TensorFlow/Keras). Fetches daily closes from Yahoo Finance's public chart API (`query1.finance.yahoo.com/v8/finance/chart/JPY=X`), caches history and the trained model under `data/` (gitignored). Run with `python fx_predict.py`; see README for options.
- `dance_video_editor.py` — video editing script (Pillow/imageio).

## Conventions

- Each tool is self-contained: its own `modules/`-style package, own `ui.py` for ANSI-colored CLI output and text-based (ASCII) graphs — no charting libraries.
- Generated/user data lives under `data/` and is gitignored (`data/*.json`, `data/*.keras`); only `data/.gitkeep` is tracked.
- Dependencies are aggregated in the single root `requirements.txt`.
