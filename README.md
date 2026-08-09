# async-parser

An asynchronous web parser, built phase by phase as a learning project:
fetch → parse → store, with retries, rate limiting and scheduled runs.

Status: **Phase 0 — project skeleton.** Nothing runs yet.

## Structure

```
src/
  fetcher.py   # gets the raw HTML
  parser.py    # turns HTML into records
  storage.py   # writes records to disk
  main.py      # wires the three together
data/          # scraped output (gitignored)
tests/         # pytest suite
```

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
