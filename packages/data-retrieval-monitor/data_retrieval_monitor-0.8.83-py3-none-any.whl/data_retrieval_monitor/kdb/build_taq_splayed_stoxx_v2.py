from __future__ import annotations

import os
import time
import gc
import datetime as dt
from typing import List, Dict, Any, Tuple, Optional

import polars as pl
import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.compute as pc
import pyarrow.parquet as pq

from goldmansachs.compass_pykx import Compass


# =========================
# CONFIG
# =========================
SI_PATH = "/workspaces/gsg-api/scripts/datasets/compass/data/SI_trades_labeled.csv"

HOST = "awsgateway.ln.prod.eqcompass.site.gs.com"
PORT = 9500
REGION = "ldn"

BASE_DIR = "/workspaces/gsg-api/data/compass_taq_stoxx_day_label"
OUT_DIR = os.path.join(BASE_DIR, "stacked_si_by_date_v3")
os.makedirs(OUT_DIR, exist_ok=True)

# Trade -> CSV assignment window padding
PRE_BUFFER_S = 120
POST_BUFFER_S = 120

# Extra quote padding so AJ has a "previous" quote available at window start
QUOTES_PRE_PAD_S = 900   # 15 min
QUOTES_POST_PAD_S = 300  # 5 min

# Start small; we auto-split further on timeouts
MAX_RICS_PER_QUERY = 25

# For debugging
TEST_DAYS: Optional[int] = 3   # set to None for full run


# =========================
# HELPERS
# =========================
def q_date_literal(d: dt.date) -> str:
    return d.strftime("%Y.%m.%d")


def q_time_literal(t: dt.time) -> str:
    # q time literal: HH:MM:SS.mmm
    return t.strftime("%H:%M:%S.%f")[:-3]


def q_symbol_list(rics: List[str]) -> str:
    """
    q symbol list:
      multiple: `A`B`C
      single:   enlist `A
      empty:    `symbols()
    """
    clean: List[str] = []
    for r in rics:
        if r is None:
            continue
        s = str(r).strip().replace("`", "")
        if s:
            clean.append(s)

    if not clean:
        return "`symbols()"
    sym = "`" + "`".join(clean)
    return f"enlist {sym}" if len(clean) == 1 else sym


def is_timeout_error(e: Exception) -> bool:
    msg = str(e)
    return ("Query timed out" in msg) or ("timed out" in msg.lower())


def compass_exec(compass: Any, qtxt: str):
    """
    Execute a Compass query with compatibility fallbacks.
    Avoids issues where some environments expose different call styles.
    """
    # Primary: documented method in your notebook
    if hasattr(compass, "run_query_sync"):
        return compass.run_query_sync(qtxt)

    # Fallbacks
    if callable(compass):
        return compass(qtxt)

    # If compass has a callable 'q' attribute, try it
    if hasattr(compass, "q") and callable(getattr(compass, "q")):
        return compass.q(qtxt)

    raise AttributeError("Compass object does not support query execution (no run_query_sync / callable / .q callable)")


def _arrow_parse_datetime_like(pa_tbl: pa.Table, col: str) -> pa.Table:
    if col not in pa_tbl.column_names:
        return pa_tbl
    idx = pa_tbl.schema.get_field_index(col)
    arr = pa_tbl.column(col)
    if not pa.types.is_string(arr.type):
        arr = pc.cast(arr, pa.string())

    s = pc.utf8_upper(arr)

    # "Fri 1Sep23 09:22:21 am"
    parsed_ts = pc.strptime(
        s,
        format="%a %d%b%y %I:%M:%S %p",
        unit="ns",
        error_is_null=True,
    )
    # "01-Sep-23"
    parsed_date = pc.strptime(
        s,
        format="%d-%b-%y",
        unit="ns",
        error_is_null=True,
    )
    parsed = pc.coalesce(parsed_ts, parsed_date)
    return pa_tbl.set_column(idx, col, parsed)


def _safe_float(expr: pl.Expr) -> pl.Expr:
    return expr.cast(pl.Utf8).str.replace_all(",", "").cast(pl.Float64, strict=False)


def _safe_int(expr: pl.Expr) -> pl.Expr:
    return (
        expr.cast(pl.Utf8)
            .str.replace_all(",", "")
            .cast(pl.Float64, strict=False)
            .round(0)
            .cast(pl.Int64, strict=False)
    )


# =========================
# READ LOCAL CSV
# =========================
def read_labeled_csv(path: str) -> pl.DataFrame:
    pa_tbl = pacsv.read_csv(path)
    for c in ["OrderCreationTime", "TradeDate", "StartTime", "EndTime", "LocalStartTime"]:
        pa_tbl = _arrow_parse_datetime_like(pa_tbl, c)

    df = pl.from_arrow(pa_tbl)

    # Add stable row id
    if hasattr(df, "with_row_index"):
        df = df.with_row_index("csv_row_id")
    else:
        df = df.with_row_count("csv_row_id")

    # Normalize
    df = df.with_columns([
        pl.col("RIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("RIC"),
        pl.col("ClientSide").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("ClientSide"),
        pl.col("GSSide").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("GSSide"),
    ])

    df = df.with_columns(
        pl.col("TradeDate").cast(pl.Datetime("ms"), strict=False).dt.date().alias("date")
    )

    for c in ["ExecutionPrice", "AbsExecutedDollarValue"]:
        if c in df.columns:
            df = df.with_columns(_safe_float(pl.col(c)).alias(c))
    if "AbsExecutedQuantity" in df.columns:
        df = df.with_columns(_safe_int(pl.col("AbsExecutedQuantity")).abs().alias("AbsExecutedQuantity"))

    # Build time columns
    start_exch = pl.col("StartTime").cast(pl.Datetime("ms"), strict=False)
    end_exch = pl.col("EndTime").cast(pl.Datetime("ms"), strict=False)
    local_start = pl.col("LocalStartTime").cast(pl.Datetime("ms"), strict=False)
    order_create = pl.col("OrderCreationTime").cast(pl.Datetime("ms"), strict=False)

    df = df.with_columns([
        pl.coalesce([start_exch, order_create, local_start]).alias("start_exch"),
        pl.coalesce([end_exch, start_exch, order_create, local_start]).alias("end_exch"),
        pl.coalesce([local_start, start_exch, order_create]).alias("start_local"),
    ])

    # Shift end_local using the Start->Local offset when possible
    tz_offset = (pl.col("start_local") - pl.col("start_exch"))
    df = df.with_columns([
        pl.when(pl.col("end_exch").is_not_null() & tz_offset.is_not_null())
          .then(pl.col("end_exch") + tz_offset)
          .otherwise(pl.col("end_exch"))
          .alias("end_local")
    ])

    # Ensure end >= start
    df = df.with_columns([
        pl.when(pl.col("end_exch") < pl.col("start_exch")).then(pl.col("start_exch")).otherwise(pl.col("end_exch")).alias("end_exch"),
        pl.when(pl.col("end_local") < pl.col("start_local")).then(pl.col("start_local")).otherwise(pl.col("end_local")).alias("end_local"),
    ])

    df = df.drop_nulls(subset=["csv_row_id", "date", "RIC", "ClientSide"])
    return df


# =========================
# DAY TIME BOUNDS (for query filters)
# =========================
def day_time_bounds(local_day: pl.DataFrame, d: dt.date) -> Tuple[str, str, str, str]:
    """
    Returns:
      trade_tmin, trade_tmax, quote_tmin, quote_tmax  as q time literals
    Uses BOTH exch + local to avoid excluding data if timezone basis is wrong.
    """
    def _min_dt(cols: List[str]) -> Optional[dt.datetime]:
        vals = []
        for c in cols:
            if c in local_day.columns:
                v = local_day.select(pl.col(c).min()).item()
                if v is not None:
                    vals.append(v)
        return min(vals) if vals else None

    def _max_dt(cols: List[str]) -> Optional[dt.datetime]:
        vals = []
        for c in cols:
            if c in local_day.columns:
                v = local_day.select(pl.col(c).max()).item()
                if v is not None:
                    vals.append(v)
        return max(vals) if vals else None

    min_start = _min_dt(["start_exch", "start_local"])
    max_end = _max_dt(["end_exch", "end_local"])

    day0 = dt.datetime.combine(d, dt.time(0, 0, 0))
    day1 = dt.datetime.combine(d, dt.time(23, 59, 59, 999000))

    if min_start is None:
        min_start = day0
    if max_end is None:
        max_end = day1

    trade_min = max(day0, min_start - dt.timedelta(seconds=PRE_BUFFER_S))
    trade_max = min(day1, max_end + dt.timedelta(seconds=POST_BUFFER_S))

    quote_min = max(day0, trade_min - dt.timedelta(seconds=QUOTES_PRE_PAD_S))
    quote_max = min(day1, trade_max + dt.timedelta(seconds=QUOTES_POST_PAD_S))

    return (
        q_time_literal(trade_min.time()),
        q_time_literal(trade_max.time()),
        q_time_literal(quote_min.time()),
        q_time_literal(quote_max.time()),
    )


# =========================
# REMOTE QUERY (TRADES + AJ QUOTES)
# =========================
def build_q_joined(d: dt.date, rics: List[str], tmin_trade: str, tmax_trade: str, tmin_quote: str, tmax_quote: str) -> str:
    """
    IMPORTANT: quotes filter MUST be 'RIC in rics' (or tradedRics).
    Never use RIC=RIC (no filter) or you'll pull the entire quotes partition.
    """
    d_q = q_date_literal(d)
    rics_q = q_symbol_list(rics)

    return f"""
d:{d_q};
rics:{rics_q};

tmin_trade:{tmin_trade};
tmax_trade:{tmax_trade};

tmin_quote:{tmin_quote};
tmax_quote:{tmax_quote};

trades_raw: select
    date,
    primaryRIC,
    tradeRIC:RIC,
    RIC:$[not null primaryRIC; primaryRIC; RIC],
    exchangeTime,
    trade_dt: date + exchangeTime,
    price,
    size
  from trades
  where date=d,
        eutradetype=`SI,
        not null exchangeTime,
        exchangeTime within (tmin_trade; tmax_trade),
        (primaryRIC in rics) | (RIC in rics);

quotes_raw: select
    RIC,
    exchangeTime,
    bid,
    ask
  from quotes
  where date=d,
        RIC in rics,
        not null exchangeTime,
        exchangeTime within (tmin_quote; tmax_quote),
        not null bid, not null ask,
        bid>0, ask>0;

/ If base tables are already ordered (very common), xasc is redundant. If you suspect ordering issues,
 / uncomment these two lines (but they can be expensive on big pulls).
/ trades_raw: `RIC`exchangeTime xasc trades_raw;
/ quotes_raw: `RIC`exchangeTime xasc quotes_raw;

tag: aj[`RIC`exchangeTime; trades_raw; quotes_raw];
tag
"""


def fetch_joined_one(compass: Compass, d: dt.date, rics: List[str], tmin_trade: str, tmax_trade: str, tmin_quote: str, tmax_quote: str) -> pl.DataFrame:
    if not rics:
        return pl.DataFrame()

    qtxt = build_q_joined(d, rics, tmin_trade, tmax_trade, tmin_quote, tmax_quote)
    tbl = compass_exec(compass, qtxt)   # returns a PyKX table-like
    pa_tbl = tbl.pa()
    df = pl.from_arrow(pa_tbl)

    if df.is_empty():
        return df

    # Normalize columns
    df = df.with_columns([
        pl.col("date").cast(pl.Date),
        pl.col("RIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase(),
        pl.col("tradeRIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase(),
        pl.col("primaryRIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase(),

        pl.col("trade_dt").cast(pl.Datetime("ms"), strict=False).alias("trade_ts"),
        pl.col("price").cast(pl.Float64, strict=False).alias("trade_price"),
        pl.col("size").cast(pl.Int64, strict=False).alias("trade_size"),

        pl.col("bid").cast(pl.Float64, strict=False),
        pl.col("ask").cast(pl.Float64, strict=False),
    ]).select([
        "date", "RIC", "tradeRIC", "primaryRIC",
        "trade_ts", "trade_price", "trade_size",
        "bid", "ask",
    ]).drop_nulls(subset=["date", "RIC", "trade_ts", "trade_price", "trade_size"])

    return df


def fetch_joined_adaptive(
    compass: Compass,
    d: dt.date,
    rics: List[str],
    tmin_trade: str,
    tmax_trade: str,
    tmin_quote: str,
    tmax_quote: str,
    depth: int = 0,
) -> pl.DataFrame:
    """
    Try fetching a chunk. If it times out, split the RIC list and retry recursively.
    """
    if not rics:
        return pl.DataFrame()

    try:
        return fetch_joined_one(compass, d, rics, tmin_trade, tmax_trade, tmin_quote, tmax_quote)
    except Exception as e:
        if is_timeout_error(e) and len(rics) > 1:
            mid = len(rics) // 2
            left = rics[:mid]
            right = rics[mid:]
            print(f"[{d}] [timeout] split rics {len(rics)} -> {len(left)} + {len(right)}", flush=True)
            df1 = fetch_joined_adaptive(compass, d, left, tmin_trade, tmax_trade, tmin_quote, tmax_quote, depth + 1)
            df2 = fetch_joined_adaptive(compass, d, right, tmin_trade, tmax_trade, tmin_quote, tmax_quote, depth + 1)
            if df1.is_empty():
                return df2
            if df2.is_empty():
                return df1
            return pl.concat([df1, df2], how="vertical")
        raise


# =========================
# ASSIGN TRADES -> CSV ROWS
# =========================
def stack_assign_by_timewindow(
    trades: pl.DataFrame,
    local_day: pl.DataFrame,
    start_col: str,
    end_col: str,
) -> pl.DataFrame:
    if trades.is_empty() or local_day.is_empty():
        return pl.DataFrame()

    keep = [
        "csv_row_id", "date", "RIC", "ClientSide", "GSSide",
        "OrderID", "TradingAlgorithm",
        "ExecutionPrice", "AbsExecutedQuantity", "AbsExecutedDollarValue",
        start_col, end_col
    ]
    keep = [c for c in keep if c in local_day.columns]

    loc = (
        local_day
        .select(keep)
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
            (pl.col("order_start") - pl.duration(seconds=PRE_BUFFER_S)).alias("start_win"),
            (pl.col("order_end") + pl.duration(seconds=POST_BUFFER_S)).alias("end_win"),
        ])
        .drop_nulls(subset=["csv_row_id", "RIC", "start_win", "end_win"])
        .sort(["RIC", "start_win"])
    )

    tr = trades.sort(["RIC", "trade_ts"])

    # Asof match by (RIC, trade_ts -> start_win)
    joined = tr.join_asof(
        loc,
        left_on="trade_ts",
        right_on="start_win",
        by="RIC",
        strategy="backward",
    )

    # Filter to those within the chosen row's end_win
    joined = joined.filter(
        pl.col("csv_row_id").is_not_null() &
        (pl.col("trade_ts") <= pl.col("end_win"))
    )

    if joined.is_empty():
        return joined

    joined = joined.with_columns([
        (0.5 * (pl.col("bid") + pl.col("ask"))).alias("mid"),
        (pl.col("ask") - pl.col("bid")).alias("spread"),
        (pl.col("trade_price") - (0.5 * (pl.col("bid") + pl.col("ask")))).alias("px_minus_mid"),
        pl.when(pl.col("trade_price") > (0.5 * (pl.col("bid") + pl.col("ask")))).then(1)
          .when(pl.col("trade_price") < (0.5 * (pl.col("bid") + pl.col("ask")))).then(-1)
          .otherwise(0)
          .alias("trade_sign_vs_mid"),
    ])

    out_cols = [
        "csv_row_id", "date", "RIC", "ClientSide", "GSSide",
        "OrderID", "TradingAlgorithm",
        "ExecutionPrice", "AbsExecutedQuantity", "AbsExecutedDollarValue",
        "order_start", "order_end",
        "trade_ts", "trade_price", "trade_size",
        "bid", "ask", "mid", "spread", "px_minus_mid", "trade_sign_vs_mid",
        "tradeRIC", "primaryRIC",
    ]
    out_cols = [c for c in out_cols if c in joined.columns]
    return joined.select(out_cols)


# =========================
# MAIN
# =========================
def main() -> None:
    local_all = read_labeled_csv(SI_PATH)
    dates: List[dt.date] = (
        local_all.select("date").unique().sort("date").to_series().to_list()
    )

    print(f"[LOCAL] rows={local_all.height} unique_days={len(dates)}", flush=True)

    if TEST_DAYS is not None:
        dates = dates[:TEST_DAYS]
        print(f"[INIT] TEST_DAYS={TEST_DAYS} -> running only {len(dates)} day(s)", flush=True)

    print("[INIT] creating Compass client ...", flush=True)
    compass = Compass(host=HOST, port=PORT, region=REGION)
    print("[INIT] Compass client created.", flush=True)

    # If THIS times out, it’s not your q text — you can’t reach the service reliably.
    try:
        compass_exec(compass, "1+1")
        print("[INIT] Compass smoke test OK (1+1).", flush=True)
    except Exception as e:
        print(f"[FATAL] Compass smoke test failed: {e}", flush=True)
        raise

    coverage_rows: List[Dict[str, Any]] = []
    manifest_paths: List[str] = []

    for di, d in enumerate(dates, 1):
        t0 = time.perf_counter()

        local_day = local_all.filter(pl.col("date") == d)
        local_rows = local_day.height
        rics_day = local_day.select("RIC").unique().to_series().to_list()

        tmin_trade, tmax_trade, tmin_quote, tmax_quote = day_time_bounds(local_day, d)

        print(
            f"[{di}/{len(dates)}] {d} local_rows={local_rows} unique_rics={len(rics_day)} "
            f"trade_range={tmin_trade}-{tmax_trade} quote_range={tmin_quote}-{tmax_quote}",
            flush=True
        )

        # Process per RIC chunk; build BOTH time-modes, then pick the better one at the end
        chunks = [rics_day[i:i + MAX_RICS_PER_QUERY] for i in range(0, len(rics_day), MAX_RICS_PER_QUERY)]
        stacked_exch_parts: List[pl.DataFrame] = []
        stacked_local_parts: List[pl.DataFrame] = []

        for ci, rchunk in enumerate(chunks, 1):
            print(f"[{d}] remote fetch chunk {ci}/{len(chunks)} rics={len(rchunk)} ...", flush=True)

            # Fetch remote trades+quotes with adaptive split on timeout
            remote = fetch_joined_adaptive(compass, d, rchunk, tmin_trade, tmax_trade, tmin_quote, tmax_quote)
            print(f"[{d}] remote chunk {ci}/{len(chunks)} rows={remote.height}", flush=True)

            if remote.is_empty():
                continue

            # Only local rows relevant to this chunk
            local_chunk = local_day.filter(pl.col("RIC").is_in(rchunk))

            # Assign using both time bases
            ex = stack_assign_by_timewindow(remote, local_chunk, "start_exch", "end_exch")
            lo = stack_assign_by_timewindow(remote, local_chunk, "start_local", "end_local")

            if not ex.is_empty():
                stacked_exch_parts.append(ex)
            if not lo.is_empty():
                stacked_local_parts.append(lo)

            del remote, local_chunk, ex, lo
            gc.collect()

        stacked_exch = pl.concat(stacked_exch_parts, how="vertical") if stacked_exch_parts else pl.DataFrame()
        stacked_local = pl.concat(stacked_local_parts, how="vertical") if stacked_local_parts else pl.DataFrame()

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

        print(
            f"[{d}] DONE matched_rows={matched_rows}/{local_rows} coverage={coverage:.1%} "
            f"trade_rows={trades_rows} avg_trades/row={avg_trades_per_row:.2f} time_mode={time_mode} "
            f"elapsed={elapsed:.1f}s",
            flush=True
        )

        # Write parquet
        if not stacked.is_empty():
            out_path = os.path.join(OUT_DIR, f"stacked_si_{d.strftime('%Y-%m-%d')}.parquet")
            pq.write_table(stacked.to_arrow(), out_path, compression="zstd")
            manifest_paths.append(out_path)
            print(f"[{d}] wrote {out_path}", flush=True)
        else:
            print(f"[{d}] no rows to write", flush=True)

        coverage_rows.append({
            "date": d,
            "local_rows": local_rows,
            "matched_rows": matched_rows,
            "coverage": coverage,
            "trade_rows_written": trades_rows,
            "avg_trades_per_row": avg_trades_per_row,
            "time_mode": time_mode,
            "elapsed_s": elapsed,
        })

        del local_day, stacked_exch_parts, stacked_local_parts, stacked_exch, stacked_local, stacked
        gc.collect()

    # Coverage + manifest
    cov = pl.DataFrame(coverage_rows).sort("date")
    cov_path = os.path.join(OUT_DIR, "_coverage_by_date.csv")
    cov.write_csv(cov_path)

    man_path = os.path.join(OUT_DIR, "_manifest.txt")
    with open(man_path, "w") as f:
        for p in manifest_paths:
            f.write(p + "\n")

    print(f"[DONE] out_dir={OUT_DIR}", flush=True)
    print(f"[DONE] coverage_csv={cov_path}", flush=True)
    print(f"[DONE] manifest={man_path}", flush=True)


if __name__ == "__main__":
    main()