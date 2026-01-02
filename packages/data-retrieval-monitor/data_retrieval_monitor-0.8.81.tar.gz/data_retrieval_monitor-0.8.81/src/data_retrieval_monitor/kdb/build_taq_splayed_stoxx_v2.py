"""
Goal
----
Build a *stacked* (trade-level) training dataset:

- Input: SI_trades_labeled.csv (≈ 8.9k rows). Target label: ClientSide ∈ {BUY, SELL}
- Remote: kdb tables `trades` + `quotes`
- For each trading day:
  1) Pull all SI trades for the RICs we need (and do AJ/as-of join to quotes in q)
  2) Assign each trade row to exactly ONE CSV row via time-window mapping (handles multiple CSV rows per same date+RIC)
  3) Output parquet per day + coverage report

Key output columns
------------------
- csv_row_id : stable row id from the CSV (unique across entire file)
- ClientSide : label repeated on each stacked trade row
- trade_ts, trade_price, trade_size, bid, ask, mid, spread, px_minus_mid, trade_sign_vs_mid
- plus selected CSV columns (OrderID, TradingAlgorithm, ExecutionPrice, AbsExecutedQuantity, etc.)

Notes
-----
- This uses *time-window assignment* so you do NOT get date+RIC many-to-many cross products.
- It auto-tries two time bases (Start/End vs LocalStart shifted) and picks whichever yields higher daily coverage.
"""

from __future__ import annotations

import os
import time
import gc
import datetime as dt
from typing import List, Dict, Any, Optional

# GS internal libs (as in your notebook)
from goldmansachs.compass_pykx import Compass

# Data libs (as in your notebook)
import pykx as kx
import polars as pl
import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.compute as pc
import pyarrow.parquet as pq


# =========================
# CONFIG
# =========================
SI_PATH = "/workspaces/gsg-api/scripts/datasets/compass/data/SI_trades_labeled.csv"

HOST = "awsgateway.ln.prod.eqcompass.site.gs.com"
PORT = 9500
REGION = "ldn"

BASE_DIR = "/workspaces/gsg-api/data/compass_taq_stoxx_day_label"
OUT_DIR = os.path.join(BASE_DIR, "stacked_si_by_date_v2")
os.makedirs(OUT_DIR, exist_ok=True)

# Time window buffers (tune if needed)
PRE_BUFFER_S = 120    # include trades up to 2min BEFORE order start
POST_BUFFER_S = 120   # include trades up to 2min AFTER order end

# Query batching (avoid gigantic q strings if many RICs in a day)
MAX_RICS_PER_QUERY = 400

# Compass query retries
QUERY_RETRIES = 3


# =========================
# SMALL HELPERS
# =========================
def q_date_literal(d: dt.date) -> str:
    """q date literal: YYYY.MM.DD"""
    return d.strftime("%Y.%m.%d")


def q_symbol_list(rics: List[str]) -> str:
    """
    Build a q symbol list literal.
    - multiple: `A`B`C
    - single: enlist `A
    - empty: `symbols()
    """
    clean = []
    for r in rics:
        if r is None:
            continue
        s = str(r).strip().replace("`", "")
        if s:
            clean.append(s)

    if not clean:
        return "`symbols()"

    sym = "`" + "`".join(clean)
    if len(clean) == 1:
        return f"enlist {sym}"
    return sym


def run_query_with_retries(compass: Compass, qtxt: str, retries: int = QUERY_RETRIES) -> Any:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            return compass.run_query_sync(qtxt)
        except Exception as e:
            last_err = e
            print(f"[WARN] Compass query failed (attempt {attempt}/{retries}): {e}")
            time.sleep(1.5 * attempt)
    raise last_err


def _arrow_parse_datetime_like(pa_tbl: pa.Table, col: str) -> pa.Table:
    """
    Parse mixed datetime formats in a column:
      - "Fri 1Sep23 09:22:21 am"
      - "01-Sep-23"
    into timestamp[ns].
    """
    if col not in pa_tbl.column_names:
        return pa_tbl

    idx = pa_tbl.schema.get_field_index(col)
    arr = pa_tbl.column(col)
    if not pa.types.is_string(arr.type):
        arr = pc.cast(arr, pa.string())

    # normalize AM/PM case for strptime
    s = pc.utf8_upper(arr)

    parsed_ts = pc.strptime(
        s,
        format="%a %d%b%y %I:%M:%S %p",
        unit="ns",
        error_is_null=True,
    )
    parsed_date = pc.strptime(
        s,
        format="%d-%b-%y",
        unit="ns",
        error_is_null=True,
    )
    parsed = pc.coalesce(parsed_ts, parsed_date)
    return pa_tbl.set_column(idx, col, parsed)


def _safe_float_from_any(expr: pl.Expr) -> pl.Expr:
    """Parse numbers that might be strings with commas."""
    return (
        expr.cast(pl.Utf8)
            .str.replace_all(",", "")
            .cast(pl.Float64, strict=False)
    )


def _safe_int_from_any(expr: pl.Expr) -> pl.Expr:
    """Parse ints that might be strings with commas/decimals; rounds."""
    return (
        expr.cast(pl.Utf8)
            .str.replace_all(",", "")
            .cast(pl.Float64, strict=False)
            .round(0)
            .cast(pl.Int64, strict=False)
    )


# =========================
# READ LOCAL LABELED CSV
# =========================
def read_labeled_csv(si_path: str) -> pl.DataFrame:
    """
    Returns a Polars DF with:
      - csv_row_id (stable)
      - date (pl.Date)
      - RIC (upper, stripped)
      - ClientSide/GSSide (upper)
      - parsed order_start/end in TWO variants:
          * start_exch/end_exch  (StartTime/EndTime)
          * start_local/end_local (LocalStartTime shifted)
    """
    pa_tbl = pacsv.read_csv(si_path)

    # Parse datetime-like columns (avoids ArrowInvalid / mixed formats)
    for c in ["OrderCreationTime", "TradeDate", "StartTime", "EndTime", "LocalStartTime"]:
        pa_tbl = _arrow_parse_datetime_like(pa_tbl, c)

    df = pl.from_arrow(pa_tbl)

    # Add stable id
    if hasattr(df, "with_row_index"):
        df = df.with_row_index("csv_row_id")
    else:
        df = df.with_row_count("csv_row_id")

    # Normalize key columns
    df = df.with_columns([
        pl.col("RIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("RIC"),
        pl.col("ClientSide").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("ClientSide"),
        pl.col("GSSide").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("GSSide"),
    ])

    # date = TradeDate as pure date
    if "TradeDate" not in df.columns:
        raise ValueError("TradeDate column not found in labeled CSV")
    df = df.with_columns(
        pl.col("TradeDate").cast(pl.Datetime("ms"), strict=False).dt.date().alias("date")
    )

    # Numeric parsing (commas safe)
    if "ExecutionPrice" in df.columns:
        df = df.with_columns(_safe_float_from_any(pl.col("ExecutionPrice")).alias("ExecutionPrice"))
    if "AbsExecutedQuantity" in df.columns:
        df = df.with_columns(_safe_int_from_any(pl.col("AbsExecutedQuantity")).abs().alias("AbsExecutedQuantity"))
    if "AbsExecutedDollarValue" in df.columns:
        df = df.with_columns(_safe_float_from_any(pl.col("AbsExecutedDollarValue")).abs().alias("AbsExecutedDollarValue"))

    # Build two time bases:
    # A) exchange-like: StartTime/EndTime
    start_exch = pl.col("StartTime").cast(pl.Datetime("ms"), strict=False)
    end_exch = pl.col("EndTime").cast(pl.Datetime("ms"), strict=False)

    # B) local-like: LocalStartTime + same duration as End-Start (if present)
    local_start = pl.col("LocalStartTime").cast(pl.Datetime("ms"), strict=False)
    # offset = LocalStartTime - StartTime
    tz_offset = (local_start - start_exch)

    # If EndTime exists and tz_offset exists: end_local = EndTime + offset
    # Else fallback to LocalStartTime (or EndTime, or StartTime)
    end_local = (
        pl.when(end_exch.is_not_null() & tz_offset.is_not_null())
          .then(end_exch + tz_offset)
          .otherwise(
              pl.coalesce([
                  pl.col("LocalStartTime").cast(pl.Datetime("ms"), strict=False),
                  pl.col("EndTime").cast(pl.Datetime("ms"), strict=False),
                  pl.col("StartTime").cast(pl.Datetime("ms"), strict=False),
                  pl.col("OrderCreationTime").cast(pl.Datetime("ms"), strict=False),
              ])
          )
    )

    df = df.with_columns([
        # fallbacks for exch times
        pl.coalesce([
            start_exch,
            pl.col("OrderCreationTime").cast(pl.Datetime("ms"), strict=False),
            local_start,
        ]).alias("start_exch"),
        pl.coalesce([
            end_exch,
            start_exch,
            pl.col("OrderCreationTime").cast(pl.Datetime("ms"), strict=False),
            local_start,
        ]).alias("end_exch"),

        # fallbacks for local times
        pl.coalesce([
            local_start,
            start_exch,
            pl.col("OrderCreationTime").cast(pl.Datetime("ms"), strict=False),
        ]).alias("start_local"),
        end_local.alias("end_local"),
    ])

    # Ensure end >= start for both variants
    df = df.with_columns([
        pl.when(pl.col("end_exch") < pl.col("start_exch")).then(pl.col("start_exch")).otherwise(pl.col("end_exch")).alias("end_exch"),
        pl.when(pl.col("end_local") < pl.col("start_local")).then(pl.col("start_local")).otherwise(pl.col("end_local")).alias("end_local"),
    ])

    # Keep only valid rows
    df = df.drop_nulls(subset=["csv_row_id", "date", "RIC", "ClientSide"])

    return df


# =========================
# FETCH REMOTE TRADES+QUOTES (per day, per RIC-set)
# =========================
def fetch_remote_day(compass: Compass, d: dt.date, rics: List[str]) -> pl.DataFrame:
    """
    Pull SI trades for this day and these rics (matches either RIC or primaryRIC),
    AJ join to quotes in q, and return a Polars DF.

    Output columns (normalized):
      date (Date)
      RIC (canonical, uses primaryRIC when present)
      tradeRIC (original trades RIC)
      primaryRIC
      exchangeTime
      price, size
      bid, ask, mid
      trade_ts (Datetime[ms])
      trade_price (Float64)
      trade_size (Int64)
    """
    if not rics:
        return pl.DataFrame()

    d_q = q_date_literal(d)
    rics_q = q_symbol_list(rics)

    # NOTE: We create a canonical RIC in q:
    #   RIC: $[not null primaryRIC; primaryRIC; tradeRIC]
    # so quotes join + downstream matching use the same key.
    qtxt = f"""
d:{d_q};
rics:{rics_q};

trades_raw: select
    date,
    primaryRIC,
    tradeRIC:RIC,
    RIC:$[not null primaryRIC; primaryRIC; RIC],
    exchangeTime,
    price,
    size
  from trades
  where date=d,
        eutradetype=`SI,
        not null exchangeTime,
        (primaryRIC in rics) | (RIC in rics);

trades_raw: distinct trades_raw;
trades_raw: `RIC`exchangeTime xasc trades_raw;

tradedRics: $[0=count trades_raw; `symbols(); exec distinct RIC from trades_raw];
tmax: $[0=count trades_raw; 0Np; max trades_raw`exchangeTime];

quotes_raw: select RIC, exchangeTime, bid, ask, mid:0.5*(bid+ask)
  from quotes
  where date=d,
        RIC in tradedRics,
        not null exchangeTime,
        exchangeTime<=tmax,
        not null bid, not null ask,
        bid>0, ask>0;

quotes_raw: `RIC`exchangeTime xasc quotes_raw;

tag: aj[`RIC`exchangeTime; trades_raw; quotes_raw];
tag
"""

    tbl = run_query_with_retries(compass, qtxt)
    pa_tbl = tbl.pa()
    df_raw = pl.from_arrow(pa_tbl)

    if df_raw.is_empty():
        return df_raw

    # Normalize types + build full timestamp trade_ts = date + exchangeTime
    df = (
        df_raw
        .with_columns([
            pl.col("RIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("RIC"),
            pl.col("tradeRIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("tradeRIC"),
            pl.col("primaryRIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("primaryRIC"),

            pl.col("date").cast(pl.Date).alias("date"),

            (pl.col("date").cast(pl.Datetime("ms")) + pl.col("exchangeTime").cast(pl.Duration("ms"))).alias("trade_ts"),

            pl.col("price").cast(pl.Float64, strict=False).alias("trade_price"),
            pl.col("size").cast(pl.Int64, strict=False).alias("trade_size"),

            pl.col("bid").cast(pl.Float64, strict=False).alias("bid"),
            pl.col("ask").cast(pl.Float64, strict=False).alias("ask"),
            pl.col("mid").cast(pl.Float64, strict=False).alias("mid"),
        ])
        .select([
            "date", "RIC", "tradeRIC", "primaryRIC",
            "trade_ts", "trade_price", "trade_size",
            "bid", "ask", "mid",
        ])
        .drop_nulls(subset=["date", "RIC", "trade_ts", "trade_price", "trade_size"])
        .sort(["RIC", "trade_ts"])
    )

    return df


# =========================
# ASSIGN TRADES -> CSV ROWS (unique id)
# =========================
def stack_assign_by_timewindow(
    trades: pl.DataFrame,
    local_day: pl.DataFrame,
    start_col: str,
    end_col: str,
    pre_buffer_s: int = PRE_BUFFER_S,
    post_buffer_s: int = POST_BUFFER_S,
) -> pl.DataFrame:
    """
    Map each trade to exactly ONE csv_row_id:
      - asof join on (RIC, start_win) using trade_ts
      - keep only trades <= end_win

    This avoids date+RIC many-to-many explosions when local has multiple rows per RIC/day.
    """
    if trades.is_empty() or local_day.is_empty():
        return pl.DataFrame()

    # Keep only the local columns we actually need downstream
    local_keep = [
        "csv_row_id", "date", "RIC", "ClientSide", "GSSide",
        "OrderID", "TradingAlgorithm",
        "ExecutionPrice", "AbsExecutedQuantity", "AbsExecutedDollarValue",
        start_col, end_col
    ]
    local_keep = [c for c in local_keep if c in local_day.columns]

    loc = (
        local_day
        .select(local_keep)
        .with_columns([
            pl.col(start_col).cast(pl.Datetime("ms"), strict=False).alias("order_start"),
            pl.col(end_col).cast(pl.Datetime("ms"), strict=False).alias("order_end"),
        ])
        .with_columns([
            pl.when(pl.col("order_end") < pl.col("order_start"))
              .then(pl.col("order_start"))
              .otherwise(pl.col("order_end"))
              .alias("order_end")
        ])
        .with_columns([
            (pl.col("order_start") - pl.duration(seconds=pre_buffer_s)).alias("start_win"),
            (pl.col("order_end") + pl.duration(seconds=post_buffer_s)).alias("end_win"),
        ])
        .drop_nulls(subset=["csv_row_id", "RIC", "start_win", "end_win"])
        .sort(["RIC", "start_win"])
    )

    # asof join: for each trade time, find the most recent order start_win <= trade_ts (within each RIC)
    joined = trades.join_asof(
        loc,
        left_on="trade_ts",
        right_on="start_win",
        by="RIC",
        strategy="backward",
        suffix="_order",
    )

    # keep only trades inside assigned window
    joined = joined.filter(
        pl.col("csv_row_id").is_not_null() &
        (pl.col("trade_ts") <= pl.col("end_win"))
    )

    if joined.is_empty():
        return joined

    # derived features
    joined = joined.with_columns([
        (pl.col("ask") - pl.col("bid")).alias("spread"),
        (pl.col("trade_price") - pl.col("mid")).alias("px_minus_mid"),
        (
            pl.when(pl.col("trade_price") > pl.col("mid")).then(1)
              .when(pl.col("trade_price") < pl.col("mid")).then(-1)
              .otherwise(0)
        ).alias("trade_sign_vs_mid"),
    ])

    # final stable schema
    out_cols = [
        "csv_row_id", "date", "RIC",
        "ClientSide", "GSSide",
        "OrderID", "TradingAlgorithm",
        "ExecutionPrice", "AbsExecutedQuantity", "AbsExecutedDollarValue",
        "order_start", "order_end",
        "trade_ts", "trade_price", "trade_size",
        "bid", "ask", "mid",
        "spread", "px_minus_mid", "trade_sign_vs_mid",
        "tradeRIC", "primaryRIC",
    ]
    out_cols = [c for c in out_cols if c in joined.columns]
    return joined.select(out_cols)


# =========================
# MAIN PIPELINE
# =========================
def main() -> None:
    # 1) Read local labeled csv
    local_all = read_labeled_csv(SI_PATH)
    n_days = local_all.select("date").n_unique()
    print(f"[LOCAL] rows={local_all.height} unique_days={n_days}")

    # 2) Date list
    dates: List[dt.date] = (
        local_all
        .select("date")
        .unique()
        .sort("date")
        .to_series()
        .to_list()
    )

    # 3) Compass client
    compass = Compass(host=HOST, port=PORT, region=REGION)

    coverage_rows: List[Dict[str, Any]] = []
    manifest_paths: List[str] = []
    total_saved_trades = 0

    for d in dates:
        t0 = time.perf_counter()

        local_day = local_all.filter(pl.col("date") == d)
        local_rows = local_day.height

        # RICs needed for this day
        rics_day: List[str] = (
            local_day.select("RIC").unique().to_series().to_list()
        )

        # 4) Fetch remote in chunks (RIC batching)
        remote_parts: List[pl.DataFrame] = []
        for i in range(0, len(rics_day), MAX_RICS_PER_QUERY):
            chunk = rics_day[i:i + MAX_RICS_PER_QUERY]
            try:
                remote_parts.append(fetch_remote_day(compass, d, chunk))
            except Exception as e:
                print(f"[WARN] {d} remote chunk {i//MAX_RICS_PER_QUERY} failed: {e}")

        remote_day = pl.concat(remote_parts, how="vertical") if remote_parts else pl.DataFrame()

        # 5) Assign trades -> csv rows using BOTH time-bases; pick better coverage
        stacked_exch = stack_assign_by_timewindow(
            remote_day, local_day,
            start_col="start_exch", end_col="end_exch",
            pre_buffer_s=PRE_BUFFER_S, post_buffer_s=POST_BUFFER_S
        )

        stacked_local = stack_assign_by_timewindow(
            remote_day, local_day,
            start_col="start_local", end_col="end_local",
            pre_buffer_s=PRE_BUFFER_S, post_buffer_s=POST_BUFFER_S
        )

        matched_exch = stacked_exch.select("csv_row_id").n_unique() if not stacked_exch.is_empty() else 0
        matched_local = stacked_local.select("csv_row_id").n_unique() if not stacked_local.is_empty() else 0

        if matched_local > matched_exch:
            stacked = stacked_local
            time_mode = "LocalStartTime-shifted"
            matched_rows = matched_local
        else:
            stacked = stacked_exch
            time_mode = "StartTime/EndTime"
            matched_rows = matched_exch

        trades_rows = stacked.height if not stacked.is_empty() else 0
        coverage = (matched_rows / local_rows) if local_rows else 0.0
        avg_trades_per_row = (trades_rows / matched_rows) if matched_rows else 0.0

        elapsed = time.perf_counter() - t0
        remote_rows = remote_day.height if not remote_day.is_empty() else 0

        print(
            f"[{d}] local_rows={local_rows} matched_rows={matched_rows} "
            f"coverage={coverage:.1%} trades_rows={trades_rows} avg_trades/row={avg_trades_per_row:.2f} "
            f"remote_rows={remote_rows} time_mode={time_mode} elapsed={elapsed:.1f}s"
        )

        # 6) Save parquet per date
        if not stacked.is_empty():
            out_path = os.path.join(OUT_DIR, f"stacked_si_{d.strftime('%Y-%m-%d')}.parquet")
            pq.write_table(stacked.to_arrow(), out_path, compression="zstd")
            manifest_paths.append(out_path)
            total_saved_trades += trades_rows

        coverage_rows.append({
            "date": d,
            "local_rows": local_rows,
            "matched_rows": matched_rows,
            "coverage": coverage,
            "trades_rows": trades_rows,
            "avg_trades_per_row": avg_trades_per_row,
            "remote_rows": remote_rows,
            "time_mode": time_mode,
            "elapsed_s": elapsed,
        })

        # Free memory
        del remote_day, remote_parts, stacked_exch, stacked_local, stacked, local_day
        gc.collect()

    # 7) Write coverage + manifest
    cov = pl.DataFrame(coverage_rows).sort("date")
    cov_path = os.path.join(OUT_DIR, "_coverage_by_date.csv")
    cov.write_csv(cov_path)

    man_path = os.path.join(OUT_DIR, "_manifest.txt")
    with open(man_path, "w") as f:
        for p in manifest_paths:
            f.write(p + "\n")

    print(f"[DONE] out_dir={OUT_DIR}")
    print(f"[DONE] parquet_files={len(manifest_paths)} total_saved_trade_rows={total_saved_trades}")
    print(f"[DONE] coverage_csv={cov_path}")
    print(f"[DONE] manifest={man_path}")


if __name__ == "__main__":
    main()