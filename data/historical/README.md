# HISTORICAL layer (append-only)

Built by `append_historical()` during ingest.

Primary file:
- commodities_history.parquet

Deduplicated on (date, asset). Safe to re-run ingest for the same day.
