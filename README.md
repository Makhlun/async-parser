# async-parser

An asynchronous scraper for [DOU.ua](https://jobs.dou.ua/vacancies/) job listings. It runs every night on GitHub Actions, upserts every vacancy into SQLite, and keeps a history of when each listing first appeared and when it disappeared.

I built it phase by phase as a learning project. It went from a one-page synchronous script to a concurrent, scheduled, tested pipeline.

```
fetch (aiohttp, concurrent) → parse (BeautifulSoup) → store (SQLite upsert) → commit (GitHub Actions, daily)
```

## Structure

```
src/
  main.py          # wires fetch → parse → store, times the fetch, exits 1 on failure
  fetcher.py       # Fetcher: CSRF token + concurrent pagination against DOU's xhr endpoint
  decorators.py    # @retry (exponential backoff) and @limit_concurrency (semaphore)
  parser.py        # Parser: HTML fragment → list of vacancy dicts
  storage.py       # Storage: SQLite schema + upsert
data/
  vacancies.db     # the accumulated data, updated nightly by the workflow
  sample.html      # saved DOU page used by the tests
tests/
  test_parser.py   # pytest suite for the parser (no network)
.github/workflows/
  scrape.yml       # nightly scheduled run
pytest.ini
requirements.txt
```

## Setup and running

Requires Python 3.10.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` must be saved as **UTF-8**. In Windows PowerShell 5.1, `pip freeze > requirements.txt` writes UTF-16, which GitHub shows as a binary file. Regenerate it from Git Bash, or in PowerShell with:

```
python -m pip freeze | Out-File -Encoding ascii requirements.txt
```

Run the scraper from the repository root:

```
python src/main.py
```

Run the tests:

```
python -m pytest -v
```

A normal run looks like this:

```
[INFO] fetcher: Fetched with 200 status.
[INFO] fetcher: Fetched 5 pages.
...
[INFO] fetcher: Reached last record. Fetched 141 pages.
[INFO] __main__: Fetching took 10.16 seconds.
[INFO] storage: Total written rows: 5629 at "./data/vacancies.db" file.
```

## How it works

### Fetching: DOU's pagination
The vacancy list loads through a "load more" button, not page URLs. The fetcher reproduces what the browser does:

1. A `GET` to the vacancies page returns a `csrftoken` cookie.
2. Each further page is a `POST` to `/vacancies/xhr-load/` with the token and a `count` offset that grows by 40. A `Referer` header is required.
3. The response is JSON, `{html, num, last}`. `html` is a fragment containing up to 40 vacancies.

Some quirks I found by probing:
- Just past the end, DOU returns `html: ""` with `last: true`.
- Far past the end, it returns `{"error": true, ...}` with **HTTP 200**, so `raise_for_status()` doesn't catch it.

### Concurrency: waves
An offset can't be computed from the previous response if requests run in parallel, so offsets are computed up front (`page × 40`) and requested in **waves** of 5 with `asyncio.gather`:

- after each wave, fragments with no html are dropped;
- the loop stops as soon as any response has `last: true` or comes back empty;
- `MAX_PAGES = 1000` is a safety cap. Hitting it logs a warning, because it means the data from that run is incomplete.

Requests go through two decorators:
- `@retry`: 3 attempts with exponential backoff, on network errors and timeouts. 4xx errors are not retried, except `429 Too Many Requests`, which honours `Retry-After`.
- `@limit_concurrency`: an `asyncio.Semaphore(5)` shared by all calls, so at most 5 requests are in flight at once. `@retry` sits above it, so a request that is backing off doesn't hold a slot.

### Benchmark
I measured the fetch only, with `time.perf_counter()`, on the same full run (~144 pages, ~5750 vacancies). Sequential means waves of size 1: same code, no concurrency. Three runs each, on 2026-10-02:

| Version | Runs | Average |
|---|---|---|
| Sequential | 20.67 s, 20.42 s, 19.88 s | **~20.3 s** |
| Waves of 5 | 5.44 s, 5.53 s, 5.94 s | **~5.6 s** |

That's about **3.6× faster**. The work is I/O-bound: each request spends most of its ~145 ms waiting for DOU's server, and while one request waits, the event loop sends the others. It isn't the ideal 5× because `gather` waits for the **slowest** request in each wave before the next wave can start, so finished slots sit idle. Async wouldn't help CPU-bound work like parsing, since everything runs in one thread.

On GitHub's servers the same fetch takes ~10 s, because every request has to travel further to reach DOU.

### Parsing
`Parser.parse(html)` finds every `li.l-vacancy` and extracts `post_date`, `title`, `link`, `company`, `salary`, `location` and `description`. A vacancy missing a date, title or link is skipped. Optional fields become `None`.

Links are normalised: hot vacancies come with `?from=list_hot`, which is stripped (`urlsplit` → `_replace(query="")`) so the same vacancy always has the same link. Whether a vacancy was hot is kept separately as `is_hot`.

### Storage: SQLite with history
One table, `vacancies`, with `link` as the natural key:

| Column | Notes |
|---|---|
| `id` | surrogate key |
| `link` | `NOT NULL UNIQUE`, without the query string |
| `title`, `post_date` | `NOT NULL` |
| `company`, `salary`, `location`, `description` | nullable |
| `is_hot` | 0/1 |
| `first_seen` | UTC ISO timestamp of the first run that saw it, never updated |
| `last_seen` | UTC ISO timestamp of the latest run that saw it |
| `updated_at` | set when title, company or salary change |

Every run is one **upsert** (`INSERT ... ON CONFLICT(link) DO UPDATE`). New vacancies are inserted, and existing ones get their fields and `last_seen` refreshed. The timestamp is taken **once per run**, so all vacancies seen in a run share the same `last_seen`.

That makes closed vacancies a query, not extra state:

```sql
SELECT link, title, company, first_seen, last_seen
FROM vacancies
WHERE last_seen < (SELECT MAX(last_seen) FROM vacancies);
```

`post_date` and `salary` are stored **raw** (e.g. `"2 жовтня"`, `"$2000–3500"`). DOU's dates have no year, so turning them into real dates is a transformation step. It belongs in a separate layer, where the logic can be fixed and rerun without losing the source (ELT).

### Automation
`.github/workflows/scrape.yml` runs daily at 00:15 UTC (and on demand via **Run workflow**). On each run it:
1. checks out the repo, which brings in yesterday's `vacancies.db`;
2. installs the requirements and runs `main.py`;
3. commits the updated database as `Scraped YYYY-MM-DD` and pushes it.

The repo is the memory between runs. If the scraper fails, `main.py` exits with code 1, the run turns red, nothing is committed, and GitHub sends an email.

### Tests
`pytest` against `data/sample.html`, a saved DOU page with 20 vacancies. Four of its hot links have the query string removed, so the sample contains both hot and regular vacancies to test `is_hot` against. No network is needed, and the suite runs in well under a second:

- the vacancy count matches the sample;
- `is_hot` is always a boolean, and both values occur;
- `link`, `title` and `post_date` are never empty (parametrized, one case per field);
- links are absolute DOU URLs with no query string;
- HTML without vacancies returns `[]`.

These tests check **my code**, not DOU. If DOU changes its markup, they keep passing. That's caught at runtime instead, by the zero-vacancy warning and the red workflow run.

## What I'd do differently

- **The database in git.** Committing a binary file daily grows the repo's history by roughly 100+ KB a day. It's fine for a learning project, but the real answer is cloud storage or a warehouse.
- **Waves vs a continuous queue.** Keeping 5 requests in flight all the time, starting a new one whenever any finishes, would remove the idle time inside each wave and get closer to 5×. Waves were simpler to reason about for stopping at the last page.
## Next steps

- A transformation layer (dbt, on DuckDB or BigQuery): parse `post_date` with a month lookup seed and year inference, split `salary` into min, max and currency, and derive `is_active`.
- Data quality tests on the clean models (`unique`, `not_null`, accepted values).
- A CI workflow that runs `pytest` on every pull request.
