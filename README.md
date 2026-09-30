# hck2609

Tectonic Hackathon, 30/09/2026.

> **How might we turn fragmented organisational knowledge into a trusted shared resource?**

## The problem

The same question ("How long is our parental leave?") is answered differently across
emails, SharePoint, Teams threads, PDFs, slides, Word files, spreadsheets and wiki pages.
Some answers are current and official. Others are outdated but labelled "Final", unapproved
drafts, hearsay, or informal replies. Employees can't tell which one to trust.

Our approach: ingest every format into one common shape, extract **trust signals** from the
metadata (author role, version and status, location, dates, draft markers, reactions), and use
them to rank documents, detect conflicts and surface the answer that deserves trust.

## Data

`data/raw/` holds a synthetic dataset for a fictional client (Vandenberg Logistics NV):
80 documents = 10 HR topics x 8 formats. Each topic appears once per format, with conflicting
versions. See `data/raw/README.md` for details.

| Folder | Format | | Folder | Format |
|---|---|---|---|---|
| `01_emails` | `.eml` | | `05_powerpoint` | `.pptx` |
| `02_sharepoint` | `.json` item exports | | `06_word` | `.docx` |
| `03_teams_messages` | `.json` channel threads | | `07_excel` | `.xlsx` |
| `04_pdf` | `.pdf` | | `08_wiki_markdown` | `.md` |

Reference files next to the documents:
- `manifest.csv`: what participants get (doc_id, path, format)
- `questions.csv`: 10 employee questions with the correct answer and the trustworthy / untrustworthy doc_ids
- `ground_truth.csv`: per-document trust labels, stated vs correct value, metadata issues

## How it works

```
data/raw (8 formats) ──▶ transform.convert_raw ──▶ data/processed (80 JSON files)
                                                          │
                              trust signals, ranking, conflict detection  (analysis/)
                                                          │
                                                   Dash app (ui/)
```

Every document is converted to the same three-field JSON, so later stages don't care about
the original format:

```json
{ "type": "email | sharepoint | teams_thread | pdf | powerpoint | word | excel | markdown",
  "metadata": { "...": "author, dates, status, version, ..." },
  "body": "text (a list of messages for teams_thread)" }
```

### Status

| Stage | State |
|---|---|
| Ingestion of all 8 formats to JSON (`processing/transform.py`) | Done: 80 files in `data/processed/` |
| Trust scoring, retrieval and ranking, conflict detection (`analysis/`) | Not started |
| Demo UI (`ui/app.py`) | Dash front end for the bundled `open-jev` model; not yet connected to the documents |
| `pipeline.py`, `ingestion/load.py`, `analysis/insights.py`, `clean()` | Placeholders that run on dummy data |

### Ideas to build next

1. **Retrieval and ranking:** given a question, return the most trustworthy document.
2. **Trust score per document**, evaluated against `ground_truth.csv`.
3. **Conflict detection:** flag topics where documents disagree.

## Project structure

```
hck2609/
├── data/
│   ├── raw/                  # input documents and reference CSVs (committed)
│   └── processed/            # generated JSON, one flat file per document (committed)
├── src/hck2609/
│   ├── contracts.py          # shared types between modules
│   ├── pipeline.py           # glue: ingestion → processing → analysis
│   ├── ingestion/load.py     # load_raw()
│   ├── processing/transform.py  # one *_to_json() per format, plus convert_raw()
│   ├── analysis/insights.py  # analyse(): trust signals and insights
│   ├── ui/app.py             # Dash front end
│   └── open-jev/             # vendored open-source Jev model (uv workspace member)
├── tests/                    # pytest
├── AGENTS.md                 # rules for coding agents (CLAUDE.md imports it)
└── pyproject.toml            # dependencies, managed with uv
```

## Getting started

Requirements: [uv](https://docs.astral.sh/uv/). It installs Python 3.13 for you.

```bash
git clone https://github.com/jasperas/hck2609.git && cd hck2609
uv sync                                   # create .venv and install everything
uv run pytest                             # sanity check: should pass
```

### Run it

```bash
# 1. Convert all raw documents into data/processed/*.json
uv run python -c "from hck2609.processing.transform import convert_raw; print(len(convert_raw()), 'files')"

# 2. Run the pipeline in the terminal (currently dummy data)
uv run hck2609

# 3. Launch the Dash UI, then open http://127.0.0.1:8050
uv run python src/hck2609/ui/app.py
```

Step 1 is safe to re-run: it overwrites `data/processed/` with identical output.

### Checks before a PR

```bash
uv run ruff check . && uv run ruff format . && uv run pytest
```

Run ruff on your own code, not the vendored `src/hck2609/open-jev/`, which has existing lint findings.

## Working as a team

- **One folder, one owner.** Suggested split: ingestion/processing, analysis (trust logic), UI.
  Don't edit someone else's folder without a heads-up.
- **Contracts first.** Shared types live in `contracts.py`. Change it and `pipeline.py` rarely and together.
- **Small branches, small PRs.** Pull `main` often. Commit small and early.
- **Dependencies:** `uv add <package>`, then commit both `pyproject.toml` and `uv.lock`. Never hand-merge `uv.lock`; take either side and run `uv lock`.

## Known gaps

- `main.py` in the repo root is an unrelated leftover pyglet demo. `pyglet` isn't a dependency, so it won't run.
- PDFs are read from their text layer only (no OCR).
- Converted Teams threads keep their messages as a list, so replies and reactions stay available as trust signals.
