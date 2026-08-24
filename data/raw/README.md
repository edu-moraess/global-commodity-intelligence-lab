# RAW layer (immutable daily dumps)

Place daily datasets here following:

```
data/raw/YYYY/MM/YYYY-MM-DD.json
```

Example:

```
data/raw/2026/08/2026-08-24.json
```

Files must conform to `src/ingestion/schema.py` (`DailyDataset`).

After placing a file, run:

```bash
python scripts/ingest_daily.py --date 2026-08-24
```

With `config.toml` `data_mode = "auto"`, Streamlit will pick the latest valid RAW automatically.
