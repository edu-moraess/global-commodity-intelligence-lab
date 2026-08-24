#!/usr/bin/env python3
"""
Daily ingestion orchestrator — Phase 2A

Usage:
  python scripts/ingest_daily.py                  # latest RAW date available
  python scripts/ingest_daily.py --date 2026-08-24
  python scripts/ingest_daily.py --path data/raw/2026/08/2026-08-24.json

Flow:
  RAW JSON → validate → enrich → processed parquet → append historical

Does NOT call Grok or GitHub API. Only processes files already on disk.
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.ingestion.loader import (
    load_raw_by_date,
    load_json,
    dataset_to_commodities_df,
    dataset_to_macro_df,
    dataset_to_geopolitics_df,
    list_available_raw_dates,
    save_processed,
    _date_path,
)
from src.ingestion.validator import validate_raw_payload, quality_report
from src.processing.transformations import enrich_commodities
from src.processing.historical import append_historical

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("ingest_daily")


def resolve_date(args: argparse.Namespace) -> date | None:
    if args.path:
        p = Path(args.path)
        if not p.exists():
            log.error("Path not found: %s", p)
            return None
        try:
            return date.fromisoformat(p.stem)
        except ValueError:
            log.error("Cannot parse date from filename stem: %s", p.stem)
            return None
    if args.date:
        return date.fromisoformat(args.date)
    dates = list_available_raw_dates()
    if not dates:
        log.error("No RAW files under data/raw/")
        return None
    return dates[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description="GCIL daily RAW → processed → historical")
    parser.add_argument("--date", help="YYYY-MM-DD")
    parser.add_argument("--path", help="Explicit path to RAW JSON")
    parser.add_argument("--skip-historical", action="store_true")
    args = parser.parse_args()

    d = resolve_date(args)
    if d is None:
        return 1

    path = Path(args.path) if args.path else _date_path(d)
    log.info("Ingesting RAW: %s", path)

    if not path.exists():
        log.error("RAW file missing: %s", path)
        return 1

    payload = load_json(path)
    ok, errors, ds = validate_raw_payload(payload)
    if not ok or ds is None:
        log.error("Validation failed: %s", errors)
        return 1

    log.info(
        "Validated OK | dataset_date=%s | commodities=%d | macro=%d | geo=%d",
        ds.dataset_date,
        len(ds.commodities),
        len(ds.macro),
        len(ds.geopolitics),
    )

    cmd = enrich_commodities(dataset_to_commodities_df(ds))
    macro = dataset_to_macro_df(ds)
    geo = dataset_to_geopolitics_df(ds)

    qr = quality_report(cmd)
    log.info("Quality: %s%% | records=%s | issues=%s", qr.get("completeness"), qr.get("records"), qr.get("issues"))

    p_cmd = save_processed(cmd, "commodities_daily")
    log.info("Processed commodities → %s", p_cmd)
    if not macro.empty:
        log.info("Processed macro → %s", save_processed(macro, "macro_daily"))
    if not geo.empty:
        log.info("Processed geopolitics → %s", save_processed(geo, "geopolitics_daily"))

    if not args.skip_historical and not cmd.empty:
        hist_path = append_historical(cmd, name="commodities_history")
        log.info("Historical append → %s (deduped on date+asset)", hist_path)

    log.info("Ingest complete for %s", d.isoformat())
    return 0


if __name__ == "__main__":
    sys.exit(main())
