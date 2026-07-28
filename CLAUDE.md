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

## FX Research Platform (trading-system/)

Added 2026-07-28 on branch `claude/fx-research-platform-foundation-v0.1.0`. These rules apply
specifically to `trading-system/` and do not change the conventions above for the other tools in
this repo.

- `trading-system/RESEARCH_CHARTER.md` is the top-level specification for anything under
  `trading-system/research/` and for FX research work in general. Lower-level specs, code, and
  configs must not contradict it; if they do, fix the lower-level spec or propose a charter revision.
- A claim with no traceable source (BIS/FRB/ECB/BoJ/CFTC, peer-reviewed research, official API/broker
  specs, etc.) is a Hypothesis (`H`) or Unclassified (`U`) — never promote it to Evidence just because
  a backtest or experiment looked good.
- Before implementing a new rule, feature, or scoring weight for the research platform, confirm there
  is a registered `hypothesis_id` (and, once running, an `experiment_id`) for it in
  `trading-system/research/hypotheses/` and `trading-system/research/experiments/`.
  Don't add trading rules or features just because they "seem like they'd work."
  See `trading-system/research/governance/RESEARCH_RULES.md`.
  This does not apply to the existing MQL4 EA's own Phase-numbered development track, which is
  independent of the research platform's Phase R0-R9 roadmap.
- Never adjust parameters, features, or acceptance criteria after looking at test-period results.
  Test periods and acceptance criteria are registered before running an experiment; if a change is
  needed afterward, open a new `experiment_id` instead of editing the old one.
- No lookahead: features and models must not use information that would not have been available at
  decision time.
- When required data is missing or of insufficient quality, the correct output is WAIT — not a guess.
  WAIT is a normal outcome, not a failure to route around.
- Signal (direction) and Risk (position sizing, daily/consecutive-loss limits, spread/session
  constraints, emergency stop) are treated as separate concerns going forward. Risk Engine logic must
  never overwrite Signal Engine's direction — if risk says BLOCK, the final decision is WAIT.
- Live-account trading features (new broker/API connections, enabling real-money order placement)
  require explicit human approval before implementation — do not wire these up proactively.
  `AllowLiveTrading` (or equivalent) stays `false` by default.
- Don't delete existing files as part of cleanup; flag duplicates/legacy candidates in
  `trading-system/research/audits/CURRENT_SYSTEM_AUDIT.md` instead and let a human decide.
- Never commit secrets (API keys, broker credentials, tokens) to this repo.
