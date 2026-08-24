# Global Commodity Intelligence Lab

**Quantitative intelligence platform for global commodities**  
Energy · Metals · Agriculture · Fertilizers · Macro · Geopolitics

Phase 1 — Core platform (this repository).  
**A automação diária do Grok será integrada em uma etapa posterior.**

---

## Objective

Receive a structured daily dataset (future Grok automation) and deliver:

- Professional Streamlit quantitative terminal
- Immutable RAW layer by date
- Processed + Historical layers
- Full quant engine (returns, volatility regimes, z-score, RSI, MACD, SMAs, momentum, correlation, curve structure, seasonality)
- Macro & Geopolitical engines
- Forecast architecture ready for MODEL / GROK / MARKET signals
- Clear DEMO vs LIVE data status

---

## Architecture

```
DATA INGESTION → PROCESSING → QUANT → DATABASE (file) → UI (Streamlit)
```

```
global-commodity-intelligence-lab/
├── app/                    # Streamlit multipage UI
│   ├── app.py
│   ├── pages/              # 01–11 dedicated dashboards
│   └── components/         # charts, cards, layout
├── src/
│   ├── ingestion/          # schema, loader, validator
│   ├── processing/         # normalization, transformations, historical
│   ├── quantitative/       # returns, vol, zscore, technical, correlation…
│   ├── forecasting/        # directional stub + evaluation hooks
│   ├── macro/
│   ├── geopolitics/
│   └── database/           # repository abstraction
├── data/
│   ├── raw/YYYY/MM/YYYY-MM-DD.json   # immutable
│   ├── processed/
│   ├── historical/
│   └── mock/               # synthetic validation only
├── reports/
├── tests/
├── scripts/
├── requirements.txt
├── config.toml
├── .env.example
└── README.md
```

---

## Stack

- Python 3.10+
- Streamlit
- Pandas / NumPy / PyArrow
- Plotly
- Pydantic (official data contract)
- Pytest

---

## Data Contract

Official schema lives in `src/ingestion/schema.py`.

Primary format: **JSON**  
Tabular exchange: **CSV**  
Historical / analytics: **Parquet**

Key fields per commodity (nullable when absent):

`date, asset, ticker, category, subcategory, currency, unit,`  
`spot_price, front_future, future_m1…m12,`  
`daily_change, weekly_change, monthly_change,`  
`volume, open_interest, implied_volatility, historical_volatility,`  
`z_score, rsi, macd, moving_average_20/50/200, momentum,`  
`curve_structure, seasonality_score, volatility_regime,`  
`directional_probability, directional_bias,`  
`supply_risk, demand_risk, macro_score, geopolitical_score, sentiment_score,`  
`cot_net_position, etf_flow, forecast, source, source_timestamp`

Missing values → `null` / `NaN`. Never invent numbers.

---

## Data Layers

| Layer       | Path                         | Mutability      | Purpose                          |
|-------------|------------------------------|-----------------|----------------------------------|
| RAW         | `data/raw/YYYY/MM/YYYY-MM-DD.json` | Immutable     | Original daily dump              |
| PROCESSED   | `data/processed/*.parquet`   | Regenerable     | Normalized daily tables          |
| HISTORICAL  | `data/historical/*.parquet`  | Append-only     | Multi-day / multi-year analysis  |
| MOCK        | `data/mock/mock_daily.json`  | Synthetic only  | Architecture validation          |

**Never mix MOCK with RAW silently.** The UI always shows `DEMO / MOCK DATA` when mock is active.

---

## Quant Engine

- Returns: 1D / 5D / 21D + rolling
- Volatility: rolling, percentile, regimes (`LOW_VOL` … `EXTREME_VOL`)
- Z-score (configurable window)
- RSI, MACD, SMA 20/50/200
- Momentum composite
- Correlation matrix (requires history)
- Seasonality (requires multi-year history)
- Curve: `CONTANGO` / `BACKWARDATION` / `FLAT` / `UNKNOWN`

---

## Forecast Architecture

Sources (enum):

- `MODEL_FORECAST`
- `GROK_FORECAST`
- `MARKET_SIGNAL`

Evaluation hooks prepared: hit ratio, error, Brier, calibration, directional accuracy.  
**No fictitious forecasts are shown as real.**

---

## Installation & Local Run

```bash
git clone https://github.com/edu-moraess/global-commodity-intelligence-lab.git
cd global-commodity-intelligence-lab
python -m venv .venv
source .venv/bin/activate   # or Windows equivalent
pip install -r requirements.txt
```

Run Streamlit:

```bash
streamlit run app/app.py
```

By default the app loads **mock** data and clearly labels it as DEMO.

---

## Tests

```bash
pytest tests/ -v
```

Coverage includes schema validation, quality report, returns, z-score, RSI, MACD, volatility regimes, curve classification, enrichment pipeline.

---

## Future Grok Integration (Phase 2+)

The daily Grok automation (09:00) will:

1. Produce a JSON payload conforming to `src/ingestion/schema.py`
2. Write it to `data/raw/YYYY/MM/YYYY-MM-DD.json`
3. Commit to this repository
4. Trigger processing → historical append → dashboard refresh

**This Phase 1 does not implement or modify any existing Grok workflow.**

---

## Roadmap

| Phase | Description                          |
|-------|--------------------------------------|
| 1     | Core platform (this repo)            |
| 2     | Grok → GitHub ingestion              |
| 3     | Automated daily dataset              |
| 4     | Advanced forecasting                 |
| 5     | Forecast backtesting                 |
| 6     | Cloud deployment                     |

---

## Security

- `.env` is gitignored
- No secrets, tokens or credentials in source
- `.env.example` provided for documentation only

---

## License

Private / internal use unless otherwise stated.

---

*Built as a professional quantitative terminal — not a tutorial demo.*
