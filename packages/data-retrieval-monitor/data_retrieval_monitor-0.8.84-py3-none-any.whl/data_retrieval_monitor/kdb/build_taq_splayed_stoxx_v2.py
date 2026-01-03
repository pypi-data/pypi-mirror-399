from __future__ import annotations

import os
import time
import gc
import datetime as dt
from typing import List, Dict, Any, Optional, Tuple

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
OUT_DIR = os.path.join(BASE_DIR, "stacked_si_by_date_localaj")
os.makedirs(OUT_DIR, exist_ok=True)

# We use CSV times to define the query window:
PRE_BUFFER_S = 120     # include trades up to 2 minutes BEFORE StartTime
POST_BUFFER_S = 120    # include trades up to 2 minutes AFTER EndTime

# For as-of join, we only need quotes BEFORE trade time.
# We'll request some padding before the earliest trade time to ensure there's a previous quote available.
QUOTES_PRE_PAD_S = 900   # 15 minutes

# Safety: if a window is huge, split on timeout until it becomes manageable.
MIN_SPLIT_MS = 30_000     # do not split below 30 seconds windows (ms)
MAX_RECURSION = 20

# Price scaling: your screenshot shows you scale trades price by 0.01 to match ExecutionPrice
TRADE_PRICE_SCALE = 0.01
# Leave quotes as-is (matches your screenshot behavior). If you later realize quotes are also scaled,
# change this to 0.01.
QUOTE_PRICE_SCALE = 1.0

# Debug: run only first N days
TEST_DAYS: Optional[int] = 3   # set to None for full run


# =========================
# HELPERS
# =========================
def is_timeout_error(e: Exception) -> bool:
    msg = str(e)
    return ("Query timed out" in msg) or ("timed out" in msg.lower())


def q_date_literal(d: dt.date) -> str:
    return d.strftime("%Y.%m.%d")


def ms_to_time(ms: int) -> dt.time:
    """Milliseconds since midnight -> python time with ms precision."""
    ms = max(0, min(ms, 24 * 3600 * 1000 - 1))
    sec, milli = divmod(ms, 1000)
    hh, rem = divmod(sec, 3600)
    mm, ss = divmod(rem, 60)
    return dt.time(hh, mm, ss, milli * 1000)


def q_time_literal(t: dt.time) -> str:
    """q time literal: HH:MM:SS.mmm"""
    return t.strftime("%H:%M:%S.%f")[:-3]


def q_symbol(ric: str) -> str:
    """Build q symbol literal like `ANE.MC"""
    s = str(ric).strip().replace("`", "")
    return "`" + s


def compass_exec(compass: Compass, qtxt: str):
    """Single execution path: always use run_query_sync to avoid pykx ctx confusion."""
    return compass.run_query_sync(qtxt)


def _arrow_parse_datetime_like(pa_tbl: pa.Table, col: str) -> pa.Table:
    """
    Parse mixed datetime strings like:
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

    s = pc.utf8_upper(arr)

    parsed_ts = pc.strptime(
        s, format="%a %d%b%y %I:%M:%S %p", unit="ns", error_is_null=True
    )
    parsed_date = pc.strptime(
        s, format="%d-%b-%y", unit="ns", error_is_null=True
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
# READ LOCAL CSV + BUILD ORDER WINDOWS
# =========================
def read_labeled_csv(path: str) -> pl.DataFrame:
    pa_tbl = pacsv.read_csv(path)
    for c in ["OrderCreationTime", "TradeDate", "StartTime", "EndTime", "LocalStartTime"]:
        pa_tbl = _arrow_parse_datetime_like(pa_tbl, c)

    df = pl.from_arrow(pa_tbl)

    # stable id
    if hasattr(df, "with_row_index"):
        df = df.with_row_index("csv_row_id")
    else:
        df = df.with_row_count("csv_row_id")

    # normalize keys/labels
    df = df.with_columns([
        pl.col("RIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("RIC"),
        pl.col("ClientSide").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("ClientSide"),
        pl.col("GSSide").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("GSSide"),
    ])

    if "TradeDate" not in df.columns:
        raise ValueError("TradeDate not found in CSV")

    df = df.with_columns(
        pl.col("TradeDate").cast(pl.Datetime("ms"), strict=False).dt.date().alias("date")
    )

    # parse numbers
    if "ExecutionPrice" in df.columns:
        df = df.with_columns(_safe_float(pl.col("ExecutionPrice")).alias("ExecutionPrice"))
    if "AbsExecutedQuantity" in df.columns:
        df = df.with_columns(_safe_int(pl.col("AbsExecutedQuantity")).abs().alias("AbsExecutedQuantity"))
    if "AbsExecutedDollarValue" in df.columns:
        df = df.with_columns(_safe_float(pl.col("AbsExecutedDollarValue")).abs().alias("AbsExecutedDollarValue"))

    # time columns
    start_exch = pl.col("StartTime").cast(pl.Datetime("ms"), strict=False)
    end_exch = pl.col("EndTime").cast(pl.Datetime("ms"), strict=False)
    local_start = pl.col("LocalStartTime").cast(pl.Datetime("ms"), strict=False)
    order_create = pl.col("OrderCreationTime").cast(pl.Datetime("ms"), strict=False)

    df = df.with_columns([
        pl.coalesce([start_exch, order_create, local_start]).alias("start_exch"),
        pl.coalesce([end_exch, start_exch, order_create, local_start]).alias("end_exch"),
    ])

    # ensure end >= start
    df = df.with_columns([
        pl.when(pl.col("end_exch") < pl.col("start_exch"))
          .then(pl.col("start_exch"))
          .otherwise(pl.col("end_exch"))
          .alias("end_exch"),
    ])

    df = df.drop_nulls(subset=["csv_row_id", "date", "RIC", "ClientSide", "start_exch", "end_exch"])
    return df


def build_local_windows_for_day(local_day: pl.DataFrame) -> pl.DataFrame:
    """
    Creates:
      order_start/order_end (Datetime)
      start_win/end_win (Datetime) with buffer
    """
    return (
        local_day
        .with_columns([
            pl.col("start_exch").alias("order_start"),
            pl.col("end_exch").alias("order_end"),
        ])
        .with_columns([
            (pl.col("order_start") - pl.duration(seconds=PRE_BUFFER_S)).alias("start_win"),
            (pl.col("order_end") + pl.duration(seconds=POST_BUFFER_S)).alias("end_win"),
        ])
        .sort(["RIC", "start_win"])
    )


def merge_intervals_ms(starts: List[int], ends: List[int]) -> List[Tuple[int, int]]:
    """Merge overlapping [start,end] intervals (ms). Assumes starts/ends aligned lists."""
    pairs = sorted(zip(starts, ends), key=lambda x: x[0])
    out: List[Tuple[int, int]] = []
    for s, e in pairs:
        if not out:
            out.append((s, e))
            continue
        ps, pe = out[-1]
        if s <= pe + 1:
            out[-1] = (ps, max(pe, e))
        else:
            out.append((s, e))
    return out


def day_ric_intervals(local_ric: pl.DataFrame) -> List[Tuple[int, int]]:
    """
    Build merged buffered intervals in ms since midnight for one (day, RIC).
    """
    if local_ric.is_empty():
        return []

    # compute ms since midnight for start_win/end_win
    tmp = local_ric.select([
        pl.col("date").first().alias("date"),
        pl.col("start_win"),
        pl.col("end_win"),
    ])

    d = tmp.select(pl.col("date").first()).item()
    day0 = dt.datetime.combine(d, dt.time(0, 0, 0))

    # Extract to python lists (small; local_ric typically small)
    starts_ms: List[int] = []
    ends_ms: List[int] = []

    for row in tmp.iter_rows(named=True):
        sdt: dt.datetime = row["start_win"]
        edt: dt.datetime = row["end_win"]
        s = int((sdt - day0).total_seconds() * 1000)
        e = int((edt - day0).total_seconds() * 1000)
        s = max(0, min(s, 24 * 3600 * 1000 - 1))
        e = max(0, min(e, 24 * 3600 * 1000 - 1))
        if e < s:
            e = s
        starts_ms.append(s)
        ends_ms.append(e)

    return merge_intervals_ms(starts_ms, ends_ms)


# =========================
# KDB QUERIES (NO AJ IN KDB)
# =========================
def q_trades(d: dt.date, ric: str, t0: str, t1: str) -> str:
    """
    Pull SI trades for (date, ric) in [t0, t1].
    We keep primaryRIC + RIC and will canonicalize in python.
    """
    return f"""
d:{q_date_literal(d)};
ric:{q_symbol(ric)};
t0:{t0};
t1:{t1};
select date, primaryRIC, RIC, exchangeTime, price, size
  from trades
  where date=d,
        eutradetype=`SI,
        not null exchangeTime,
        exchangeTime within (t0; t1),
        (primaryRIC=ric) | (RIC=ric)
"""


def q_quotes(d: dt.date, ric: str, t0: str, t1: str) -> str:
    """
    Pull quotes for (date, ric) in [t0, t1].
    """
    return f"""
d:{q_date_literal(d)};
ric:{q_symbol(ric)};
t0:{t0};
t1:{t1};
select date, RIC, exchangeTime, bid, ask
  from quotes
  where date=d,
        RIC=ric,
        not null exchangeTime,
        exchangeTime within (t0; t1),
        not null bid, not null ask,
        bid>0, ask>0
"""


def fetch_table(compass: Compass, qtxt: str) -> pl.DataFrame:
    tbl = compass_exec(compass, qtxt)
    pa_tbl = tbl.pa()
    return pl.from_arrow(pa_tbl)


def fetch_trades_adaptive(
    compass: Compass,
    d: dt.date,
    ric: str,
    start_ms: int,
    end_ms: int,
    depth: int = 0,
) -> pl.DataFrame:
    """
    Adaptive split on timeout for trades query.
    """
    if depth > MAX_RECURSION:
        raise RuntimeError(f"Exceeded MAX_RECURSION while fetching trades for {d} {ric}")

    t0 = q_time_literal(ms_to_time(start_ms))
    t1 = q_time_literal(ms_to_time(end_ms))
    try:
        df = fetch_table(compass, q_trades(d, ric, t0, t1))
        return df
    except Exception as e:
        if is_timeout_error(e) and (end_ms - start_ms) > MIN_SPLIT_MS:
            mid = (start_ms + end_ms) // 2
            print(f"[{d} {ric}] trades timeout -> split {t0}-{t1} into halves", flush=True)
            left = fetch_trades_adaptive(compass, d, ric, start_ms, mid, depth + 1)
            right = fetch_trades_adaptive(compass, d, ric, mid + 1, end_ms, depth + 1)
            if left.is_empty():
                return right
            if right.is_empty():
                return left
            return pl.concat([left, right], how="vertical")
        raise


def fetch_quotes_adaptive(
    compass: Compass,
    d: dt.date,
    ric: str,
    start_ms: int,
    end_ms: int,
    depth: int = 0,
) -> pl.DataFrame:
    """
    Adaptive split on timeout for quotes query.
    """
    if depth > MAX_RECURSION:
        raise RuntimeError(f"Exceeded MAX_RECURSION while fetching quotes for {d} {ric}")

    t0 = q_time_literal(ms_to_time(start_ms))
    t1 = q_time_literal(ms_to_time(end_ms))
    try:
        df = fetch_table(compass, q_quotes(d, ric, t0, t1))
        return df
    except Exception as e:
        if is_timeout_error(e) and (end_ms - start_ms) > MIN_SPLIT_MS:
            mid = (start_ms + end_ms) // 2
            print(f"[{d} {ric}] quotes timeout -> split {t0}-{t1} into halves", flush=True)
            left = fetch_quotes_adaptive(compass, d, ric, start_ms, mid, depth + 1)
            right = fetch_quotes_adaptive(compass, d, ric, mid + 1, end_ms, depth + 1)
            if left.is_empty():
                return right
            if right.is_empty():
                return left
            return pl.concat([left, right], how="vertical")
        raise


# =========================
# LOCAL JOINS
# =========================
def normalize_trades(df: pl.DataFrame) -> pl.DataFrame:
    if df.is_empty():
        return df

    # Canonicalize RIC := primaryRIC when present else RIC
    df = df.with_columns([
        pl.when(pl.col("primaryRIC").is_not_null())
          .then(pl.col("primaryRIC"))
          .otherwise(pl.col("RIC"))
          .cast(pl.Utf8)
          .str.strip_chars()
          .str.to_uppercase()
          .alias("RIC"),

        pl.col("date").cast(pl.Date).alias("date"),
        pl.col("price").cast(pl.Float64, strict=False).alias("price_raw"),
        (pl.col("price").cast(pl.Float64, strict=False) * TRADE_PRICE_SCALE).alias("trade_price"),
        pl.col("size").cast(pl.Int64, strict=False).alias("trade_size"),
    ])

    # trade_ts = date midnight + exchangeTime duration
    df = df.with_columns([
        (pl.col("date").cast(pl.Datetime("ms")) + pl.col("exchangeTime").cast(pl.Duration("ms"))).alias("trade_ts")
    ])

    return df.select([
        "date", "RIC", "trade_ts", "trade_price", "trade_size",
        "primaryRIC", "price_raw", "exchangeTime"
    ]).drop_nulls(subset=["date", "RIC", "trade_ts", "trade_price", "trade_size"])


def normalize_quotes(df: pl.DataFrame) -> pl.DataFrame:
    if df.is_empty():
        return df

    df = df.with_columns([
        pl.col("RIC").cast(pl.Utf8).str.strip_chars().str.to_uppercase().alias("RIC"),
        pl.col("date").cast(pl.Date).alias("date"),
        (pl.col("bid").cast(pl.Float64, strict=False) * QUOTE_PRICE_SCALE).alias("bid"),
        (pl.col("ask").cast(pl.Float64, strict=False) * QUOTE_PRICE_SCALE).alias("ask"),
    ])

    df = df.with_columns([
        (pl.col("date").cast(pl.Datetime("ms")) + pl.col("exchangeTime").cast(pl.Duration("ms"))).alias("quote_ts")
    ])

    return df.select([
        "date", "RIC", "quote_ts", "bid", "ask"
    ]).drop_nulls(subset=["date", "RIC", "quote_ts", "bid", "ask"])


def trades_asof_quotes(trades: pl.DataFrame, quotes: pl.DataFrame) -> pl.DataFrame:
    """
    As-of join in python:
      trades (RIC, trade_ts) <- backward asof <- quotes (RIC, quote_ts)
    """
    if trades.is_empty() or quotes.is_empty():
        return pl.DataFrame()

    t = trades.sort(["RIC", "trade_ts"])
    q = quotes.sort(["RIC", "quote_ts"])

    out = t.join_asof(
        q,
        left_on="trade_ts",
        right_on="quote_ts",
        by="RIC",
        strategy="backward",
    )

    out = out.drop_nulls(subset=["bid", "ask"])

    out = out.with_columns([
        (0.5 * (pl.col("bid") + pl.col("ask"))).alias("mid"),
        (pl.col("ask") - pl.col("bid")).alias("spread"),
        (pl.col("trade_price") - (0.5 * (pl.col("bid") + pl.col("ask")))).alias("px_minus_mid"),
        pl.when(pl.col("trade_price") > (0.5 * (pl.col("bid") + pl.col("ask")))).then(1)
          .when(pl.col("trade_price") < (0.5 * (pl.col("bid") + pl.col("ask")))).then(-1)
          .otherwise(0)
          .alias("trade_sign_vs_mid"),
    ])

    return out


def assign_trades_to_csv_rows(trades_q: pl.DataFrame, local_ric: pl.DataFrame) -> pl.DataFrame:
    """
    Assign each trade to exactly one csv_row_id using:
      asof join on start_win + filter trade_ts <= end_win
    """
    if trades_q.is_empty() or local_ric.is_empty():
        return pl.DataFrame()

    local_map = (
        local_ric
        .select([
            "csv_row_id", "date", "RIC", "ClientSide", "GSSide",
            "OrderID", "TradingAlgorithm",
            "ExecutionPrice", "AbsExecutedQuantity", "AbsExecutedDollarValue",
            "order_start", "order_end", "start_win", "end_win"
        ])
        .sort(["RIC", "start_win"])
    )

    tr = trades_q.sort(["RIC", "trade_ts"])

    joined = tr.join_asof(
        local_map,
        left_on="trade_ts",
        right_on="start_win",
        by="RIC",
        strategy="backward",
    )

    joined = joined.filter(
        pl.col("csv_row_id").is_not_null() &
        (pl.col("trade_ts") <= pl.col("end_win"))
    )

    if joined.is_empty():
        return joined

    # Keep a clean schema
    cols = [
        "csv_row_id", "date", "RIC",
        "ClientSide", "GSSide",
        "OrderID", "TradingAlgorithm",
        "ExecutionPrice", "AbsExecutedQuantity", "AbsExecutedDollarValue",
        "order_start", "order_end",
        "trade_ts", "trade_price", "trade_size",
        "bid", "ask", "mid", "spread", "px_minus_mid", "trade_sign_vs_mid",
        "primaryRIC", "price_raw",
    ]
    cols = [c for c in cols if c in joined.columns]
    return joined.select(cols)


# =========================
# MAIN
# =========================
def main() -> None:
    local_all = read_labeled_csv(SI_PATH)
    dates = local_all.select("date").unique().sort("date").to_series().to_list()

    print(f"[LOCAL] rows={local_all.height} unique_days={len(dates)}", flush=True)

    if TEST_DAYS is not None:
        dates = dates[:TEST_DAYS]
        print(f"[INIT] TEST_DAYS={TEST_DAYS} -> running {len(dates)} day(s)", flush=True)

    print("[INIT] creating Compass client ...", flush=True)
    compass = Compass(host=HOST, port=PORT, region=REGION)
    print("[INIT] Compass client created.", flush=True)

    # smoke test
    try:
        compass_exec(compass, "1+1")
        print("[INIT] Compass smoke test OK.", flush=True)
    except Exception as e:
        print(f"[FATAL] Compass smoke test failed: {e}", flush=True)
        raise

    coverage_rows: List[Dict[str, Any]] = []
    manifest: List[str] = []

    for di, d in enumerate(dates, 1):
        t_day0 = time.perf_counter()

        local_day = local_all.filter(pl.col("date") == d)
        local_day = build_local_windows_for_day(local_day)

        local_rows = local_day.height
        rics = local_day.select("RIC").unique().to_series().to_list()

        print(f"\n[{di}/{len(dates)}] {d} START local_rows={local_rows} unique_rics={len(rics)}", flush=True)

        out_path = os.path.join(OUT_DIR, f"stacked_si_{d.strftime('%Y-%m-%d')}.parquet")
        writer: Optional[pq.ParquetWriter] = None

        day_matched_ids = set()
        day_trade_rows_written = 0

        for ric_i, ric in enumerate(rics, 1):
            local_ric = local_day.filter(pl.col("RIC") == ric)
            intervals = day_ric_intervals(local_ric)

            print(f"[{d}] RIC {ric_i}/{len(rics)} {ric} local_rows={local_ric.height} intervals={len(intervals)}", flush=True)

            if not intervals:
                continue

            for int_i, (s_ms, e_ms) in enumerate(intervals, 1):
                # 1) fetch trades in this interval
                try:
                    trades_raw = fetch_trades_adaptive(compass, d, ric, s_ms, e_ms)
                except Exception as e:
                    print(f"[WARN] [{d} {ric}] trades interval {int_i}/{len(intervals)} failed: {e}", flush=True)
                    continue

                if trades_raw.is_empty():
                    continue

                trades = normalize_trades(trades_raw)
                if trades.is_empty():
                    continue

                # Determine quote window based on ACTUAL trade times (much smaller than CSV window)
                tmin = trades.select(pl.col("trade_ts").min()).item()
                tmax = trades.select(pl.col("trade_ts").max()).item()

                day0 = dt.datetime.combine(d, dt.time(0, 0, 0))
                tmin_ms = int((tmin - day0).total_seconds() * 1000)
                tmax_ms = int((tmax - day0).total_seconds() * 1000)

                q_start_ms = max(0, tmin_ms - QUOTES_PRE_PAD_S * 1000)
                q_end_ms = max(q_start_ms, tmax_ms)

                # 2) fetch quotes (only around trade times)
                try:
                    quotes_raw = fetch_quotes_adaptive(compass, d, ric, q_start_ms, q_end_ms)
                except Exception as e:
                    print(f"[WARN] [{d} {ric}] quotes interval {int_i}/{len(intervals)} failed: {e}", flush=True)
                    continue

                quotes = normalize_quotes(quotes_raw)
                if quotes.is_empty():
                    continue

                # 3) local asof join trades<-quotes
                tq = trades_asof_quotes(trades, quotes)
                if tq.is_empty():
                    continue

                # 4) assign trades -> csv_row_id
                stacked = assign_trades_to_csv_rows(tq, local_ric)
                if stacked.is_empty():
                    continue

                # write streaming
                table = stacked.to_arrow()
                if writer is None:
                    writer = pq.ParquetWriter(out_path, table.schema, compression="zstd")
                writer.write_table(table)

                day_trade_rows_written += stacked.height
                ids = stacked.select("csv_row_id").unique().to_series().to_list()
                for x in ids:
                    day_matched_ids.add(int(x))

                # cleanup
                del trades_raw, trades, quotes_raw, quotes, tq, stacked, table
                gc.collect()

        if writer is not None:
            writer.close()
            manifest.append(out_path)
            wrote = True
        else:
            wrote = False
            # ensure no empty file is left behind
            if os.path.exists(out_path):
                try:
                    os.remove(out_path)
                except Exception:
                    pass

        matched_rows = len(day_matched_ids)
        coverage = matched_rows / local_rows if local_rows else 0.0
        avg_trades_per_row = (day_trade_rows_written / matched_rows) if matched_rows else 0.0
        elapsed = time.perf_counter() - t_day0

        print(
            f"[{d}] DONE wrote={wrote} matched_rows={matched_rows}/{local_rows} "
            f"coverage={coverage:.1%} trade_rows={day_trade_rows_written} "
            f"avg_trades/row={avg_trades_per_row:.2f} elapsed={elapsed:.1f}s",
            flush=True
        )

        coverage_rows.append({
            "date": d,
            "local_rows": local_rows,
            "matched_rows": matched_rows,
            "coverage": coverage,
            "trade_rows_written": day_trade_rows_written,
            "avg_trades_per_row": avg_trades_per_row,
            "wrote_parquet": wrote,
            "elapsed_s": elapsed,
        })

        del local_day
        gc.collect()

    cov = pl.DataFrame(coverage_rows).sort("date")
    cov_path = os.path.join(OUT_DIR, "_coverage_by_date.csv")
    cov.write_csv(cov_path)

    man_path = os.path.join(OUT_DIR, "_manifest.txt")
    with open(man_path, "w") as f:
        for p in manifest:
            f.write(p + "\n")

    print(f"\n[DONE] out_dir={OUT_DIR}", flush=True)
    print(f"[DONE] parquet_files={len(manifest)}", flush=True)
    print(f"[DONE] coverage_csv={cov_path}", flush=True)
    print(f"[DONE] manifest={man_path}", flush=True)


if __name__ == "__main__":
    main()