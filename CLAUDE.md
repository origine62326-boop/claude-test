# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projects in this repository

This repo holds a few independent CLI tools (no shared build/test setup):

- `x_pdca.py` + `modules/` — X (Twitter) account PDCA tracker. Stdlib only, JSON storage in `data/`.
- `fx_predict.py` + `fx_modules/` — USD/JPY rate forecaster using an LSTM (TensorFlow/Keras). Fetches daily closes from Yahoo Finance's public chart API (`query1.finance.yahoo.com/v8/finance/chart/JPY=X`), caches history and the trained model under `data/` (gitignored). Run with `python fx_predict.py`; see README for options.
- `dance_video_editor.py` — video editing script (Pillow/imageio).
- `USDJPY_LowRisk_Trend_EA/` — MQL4 low-risk trend-following EA for Rakuten MT4 (USD/JPY, H1). See its `CHANGELOG.md` for phase status; not yet feature-complete (Phase 1-4 of 9).
- `trading-system/` — Python pipeline that parses MT4 Strategy Tester exports (HTML) and analyzes backtests for the EA above: `mt4/` (EA copy + MT4-side export instructions), `analysis/` (parsing + metrics, each module is also a standalone CLI), `scripts/` (orchestration: `run_analysis.py`, `compare_backtests.py`, `validate_release.py`), `configs/*.yaml` (acceptance criteria, risk limits), `prompts/` (review prompt templates), `tests/` (pytest, run from `trading-system/`). Has its own `requirements.txt`, README_JP.md, CHANGELOG.md, TODO.md. MT4 has no direct connection to this sandbox — report exports are handed off manually (see `trading-system/mt4/README_MT4_JP.md`).

## Conventions

- Each tool is self-contained: its own `modules/`-style package, own `ui.py` for ANSI-colored CLI output and text-based (ASCII) graphs — no charting libraries. (`trading-system/` is the exception, being a multi-module Python pipeline with its own tests/configs.)
- Generated/user data lives under `data/` and is gitignored (`data/*.json`, `data/*.keras`); only `data/.gitkeep` is tracked. `trading-system/` mirrors this convention under its own `reports/` and `outputs/` trees.
- Dependencies are aggregated in the single root `requirements.txt` for the Python CLI tools; `trading-system/` keeps its own `requirements.txt` since it's a separate pipeline with different dependencies (bs4, lxml, PyYAML, pytest).
