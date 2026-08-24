# Global Commodity Intelligence Lab

**Quantitative intelligence platform for global commodities**  
Energy · Metals · Agriculture · Fertilizers · Macro · Geopolitics

**Phase 2A — Real data pipeline prepared** (AUTO / MOCK / RAW).  
**A automação diária do Grok será integrada em uma etapa posterior (Phase 2B).**

---

## Objective

Receive a structured daily dataset and deliver:

- Professional Streamlit quantitative terminal
- Immutable RAW layer by date
- Processed + Historical layers
- Full quant engine
- Macro & Geopolitical engines
- Clear **LIVE / RAW** vs **DEMO / MOCK** status

---

## Data modes (`config.toml`)

```toml
[app]
data_mode = "auto"   # auto | mock | raw
```

| Mode | Behaviour |
|------|-----------|
| `auto` (default) | Latest **valid** RAW if present → else MOCK |
| `mock` | Always MOCK |
| `raw` | RAW only; clear error if none / invalid |

Never mixes MOCK and RAW in the same load.

---

## Architecture

```
DATA INGESTION → PROCESSING → QUANT → DATABASE (file) → UI (Streamlit)
```

```
global-commodity-intelligence-lab/
├── app/                    # Streamlit multipage UI
├── src/
│   ├── ingestion/          # schema, loader, validator
│   ├── processing/         # normalization, transformations, historical
│   ├── quantitative/
│   ├── forecasting/
│   ├── macro/ · geopolitics/
│   └── database/           # repository (AUTO/MOCK/RAW)
├── data/
│   ├── raw/YYYY/MM/YYYY-MM-DD.json   # versioned source of truth
│   ├── processed/
│   ├── historical/                   # append-only parquet
│   └── mock/
├── scripts/ingest_daily.py           # RAW → process → historical
├── tests/
├── config.toml
└── requirements.txt
```

---

## Daily ingest (local / CI)

Place a schema-valid JSON at:

```
data/raw/YYYY/MM/YYYY-MM-DD.json
```

Then:

```bash
python scripts/ingest_daily.py --date 2026-08-24
# or
python scripts/ingest_daily.py --path data/raw/2026/08/2026-08-24.json
```

This validates → enriches → writes processed parquet → appends historical (deduped on date+asset).

Streamlit with `data_mode=auto` will pick the latest valid RAW automatically.

---

## Installation & Local Run

```bash
git clone https://github.com/edu-moraess/global-commodity-intelligence-lab.git
cd global-commodity-intelligence-lab
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app/app.py
```

Without RAW files the UI runs in **DEMO / MOCK DATA** (explicitly labelled).

---

## Tests

```bash
pytest tests/ -v
```

---

## Data Contract

Official schema: `src/ingestion/schema.py` (`DailyDataset`).  
Primary format JSON · historical Parquet · CSV for tabular exchange.

---

## Future Grok Integration (Phase 2B — not in this commit)

1. Grok produces JSON conforming to the schema  
2. Writes `data/raw/YYYY/MM/YYYY-MM-DD.json`  
3. Commits to this repository  
4. `scripts/ingest_daily.py` (or CI) processes → historical → dashboard

**Phase 2A does not implement Grok automation, webhooks, or scheduling.**

---

## Roadmap

| Phase | Description |
|-------|-------------|
| 1 | Core platform |
| **2A** | **Real data pipeline preparation (this)** |
| 2B | Grok → GitHub ingestion |
| 3 | Automated daily dataset |
| 4 | Advanced forecasting |
| 5 | Forecast backtesting |
| 6 | Cloud deployment |

---

## Security

- `.env` gitignored · no secrets in source · `.env.example` only

---

*Built as a professional quantitative terminal — not a tutorial demo.*
