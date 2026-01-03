from __future__ import annotations

import os
import math
import time
import gc
import csv
import datetime as dt
from typing import Any, Dict, List, Optional, Tuple

import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.compute as pc
import pyarrow.parquet as pq

from goldmansachs.compass_pykx import Compass


# =========================
# CONFIG
# =========================
SI_PATH = "/workspaces/gsg-api/scripts/datasets/compass/data/SI_trades_labeled.csv"

# Use Compass exactly like you asked (no host/port)
REGION = "ldn"

OUT_DIR = "/workspaces/gsg-api/data/stacked_trades_rowid"
os.makedirs(OUT_DIR, exist_ok=True)

# Filtering rule you asked for:
#   exchangeTime after OrderCreationTime
#   size >= 0.5 * AbsExecutedQuantity
#
# We ALSO need an upper bound to keep queries small.
# If EndTime is missing, we cap by DEFAULT_LOOKAHEAD_S.
DEFAULT_LOOKAHEAD_S = 60 * 60  # 1 hour

# If a query times out, split the time window and retry
MIN_SPLIT_MS = 30_000          # don't split below 30 seconds
MAX_RECURSION = 18

# Optional: limit returned trades per row (prevents weird explosions on very liquid names)
# Set to None to disable.
MAX_TRADES_PER_ROW: Optional[int] = 2000

# If trades price needs scaling to match ExecutionPrice
TRADE_PRICE_SCALE = 0.01

# progress prints
PRINT_EVERY_ROWS = 50

# Debug limits (set to None for full run)
TEST_DAYS: Optional[int] = None         # e.g. 3
TEST_ROWS_PER_DAY: Optional[int] = None # e.g. 200


# =========================
# HELPERS
# =========================
DAY_MS = 24 * 3600 * 1000

def is_timeout_error(e: Exception) -> bool:
    msg = str(e)
    return ("Query timed out" in msg) or ("timed out" in msg.lower())

def q_date_literal(d: dt.date) -> str:
    return d.strftime("%Y.%m.%d")

def q_symbol(ric: str) -> str:
    s = str(ric).strip().replace("`", "")
    return "`" + s

def clamp_ms(ms: int) -> int:
    return max(0, min(int(ms), DAY_MS - 1))

def ms_to_time(ms: int) -> dt.time:
    ms = clamp_ms(ms)
    sec, milli = divmod(ms, 1000)
    hh, rem = divmod(sec, 3600)
    mm, ss = divmod(rem, 60)
    return dt.time(hh, mm, ss, milli * 1000)

def q_time_literal(t: dt.time) -> str:
    # q time literal: HH:MM:SS.mmm
    return t.strftime("%H:%M:%S.%f")[:-3]

def dt_to_ms_of_day(x: dt.datetime, day: dt.date) -> int:
    day0 = dt.datetime.combine(day, dt.time(0, 0, 0))
    return clamp_ms(int((x - day0).total_seconds() * 1000))

def safe_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        if isinstance(x, str):
            x = x.replace(",", "").strip()
            if x == "":
                return None
        return float(x)
    except Exception:
        return None

def safe_int(x: Any) -> Optional[int]:
    if x is None:
        return None
    try:
        if isinstance(x, str):
            x = x.replace(",", "").strip()
            if x == "":
                return None
        return int(round(float(x)))
    except Exception:
        return None

def arrow_try_parse_datetime(arr: pa.Array) -> pa.Array:
    """
    Parse mixed formats into timestamp[ns] using a few common patterns seen in your data.
    """
    if not pa.types.is_string(arr.type):
        arr = pc.cast(arr, pa.string())
    s = pc.utf8_upper(arr)

    p1 = pc.strptime(s, format="%a %d%b%y %I:%M:%S %p", unit="ns", error_is_null=True)  # Fri 1Sep23 09:22:21 AM
    p2 = pc.strptime(s, format="%d%b%y %I:%M:%S %p", unit="ns", error_is_null=True)
    p3 = pc.strptime(s, format="%d-%b-%y", unit="ns", error_is_null=True)              # 01-Sep-23
    p4 = pc.strptime(s, format="%Y-%m-%d", unit="ns", error_is_null=True)
    p5 = pc.strptime(s, format="%Y-%m-%d %H:%M:%S", unit="ns", error_is_null=True)

    return pc.coalesce(p1, p2, p3, p4, p5)

def parse_datetime_columns(tbl: pa.Table, cols: List[str]) -> pa.Table:
    for c in cols:
        if c not in tbl.column_names:
            continue
        idx = tbl.schema.get_field_index(c)
        col = tbl.column(c)
        if isinstance(col, pa.ChunkedArray):
            col = col.combine_chunks()
        parsed = arrow_try_parse_datetime(col)
        tbl = tbl.set_column(idx, c, parsed)
    return tbl


# =========================
# CSV LOAD
# =========================
def load_csv_rows(path: str) -> List[Dict[str, Any]]:
    """
    Returns list of dict rows with python-native datetimes/dates, and adds csv_row_id.
    """
    tbl = pacsv.read_csv(path)
    tbl = parse_datetime_columns(tbl, ["TradeDate", "OrderCreationTime", "StartTime", "EndTime", "LocalStartTime"])

    rows_raw = tbl.to_pylist()
    out: List[Dict[str, Any]] = []

    for i, r in enumerate(rows_raw):
        ric = (r.get("RIC") or "")
        ric = ric.strip().upper()
        if not ric:
            continue

        # TradeDate -> date
        td = r.get("TradeDate")
        if isinstance(td, dt.datetime):
            day = td.date()
        elif isinstance(td, dt.date):
            day = td
        else:
            continue

        client = (r.get("ClientSide") or "").strip().upper()
        if client not in ("BUY", "SELL"):
            continue

        # numeric
        abs_qty = safe_int(r.get("AbsExecutedQuantity"))
        exec_px = safe_float(r.get("ExecutionPrice"))
        abs_dv = safe_float(r.get("AbsExecutedDollarValue"))

        # times
        oc = r.get("OrderCreationTime")
        st = r.get("StartTime")
        et = r.get("EndTime")

        # We must have OrderCreationTime for your requested filter.
        # If missing, we fallback to StartTime (still “after start”), but that’s not strictly order creation.
        order_creation = oc if isinstance(oc, dt.datetime) else (st if isinstance(st, dt.datetime) else None)
        if order_creation is None:
            continue

        end_time = et if isinstance(et, dt.datetime) else None

        out.append({
            "csv_row_id": i,
            "date": day,
            "RIC": ric,
            "ClientSide": client,
            "GSSide": (r.get("GSSide") or None),
            "OrderID": str(r.get("OrderID")) if r.get("OrderID") is not None else None,
            "TradingAlgorithm": str(r.get("TradingAlgorithm")) if r.get("TradingAlgorithm") is not None else None,
            "OrderCreationTime": order_creation,
            "StartTime": st if isinstance(st, dt.datetime) else None,
            "EndTime": end_time,
            "ExecutionPrice": exec_px,
            "AbsExecutedQuantity": abs_qty,
            "AbsExecutedDollarValue": abs_dv,
        })

    return out


# =========================
# KDB QUERY (TRADES ONLY)
# =========================
def build_trades_q(
    day: dt.date,
    ric: str,
    t0_ms: int,
    t1_ms: int,
    min_size: int,
    max_rows: Optional[int],
) -> str:
    """
    Trades query:
      - date=day
      - eutradetype=`SI
      - exchangeTime within (t0;t1)
      - exchangeTime >= t0  (redundant but explicit)
      - same ric (primaryRIC or RIC)
      - size >= min_size
      - compute trade_dt and scaled price in q (cheap)
    """
    d_q = q_date_literal(day)
    ric_q = q_symbol(ric)
    t0 = q_time_literal(ms_to_time(t0_ms))
    t1 = q_time_literal(ms_to_time(t1_ms))

    limit_prefix = ""
    if isinstance(max_rows, int) and max_rows > 0:
        # take earliest N rows after sorting by exchangeTime
        limit_prefix = f"{max_rows}#"

    return f"""
d:{d_q};
ric:{ric_q};
t0:{t0};
t1:{t1};
minSize:{int(min_size)};

t: select
      date,
      primaryRIC,
      tradeRIC:RIC,
      canonRIC:$[not null primaryRIC; primaryRIC; RIC],
      exchangeTime,
      trade_dt: date + exchangeTime,
      trade_price_raw: price,
      trade_price: {TRADE_PRICE_SCALE}*price,
      size
    from trades
    where date=d,
          eutradetype=`SI,
          not null exchangeTime,
          exchangeTime within (t0; t1),
          exchangeTime>=t0,
          ((primaryRIC=ric) | (RIC=ric)),
          size>=minSize;

t: `exchangeTime xasc t;
{limit_prefix} t
"""

def fetch_trades_adaptive(
    compass: Compass,
    day: dt.date,
    ric: str,
    t0_ms: int,
    t1_ms: int,
    min_size: int,
    max_rows: Optional[int],
    depth: int = 0,
) -> pa.Table:
    if t1_ms < t0_ms:
        t1_ms = t0_ms
    if depth > MAX_RECURSION:
        raise RuntimeError(f"MAX_RECURSION exceeded for {day} {ric} {t0_ms}-{t1_ms}")

    qtxt = build_trades_q(day, ric, t0_ms, t1_ms, min_size, max_rows)
    try:
        res = compass.run_query_sync(qtxt)
        return res.pa()
    except Exception as e:
        if is_timeout_error(e) and (t1_ms - t0_ms) > MIN_SPLIT_MS and t1_ms > t0_ms:
            mid = (t0_ms + t1_ms) // 2
            print(f"[{day} {ric}] trades query timeout -> split window {q_time_literal(ms_to_time(t0_ms))}-{q_time_literal(ms_to_time(t1_ms))}", flush=True)
            left = fetch_trades_adaptive(compass, day, ric, t0_ms, mid, min_size, max_rows, depth + 1)
            right = fetch_trades_adaptive(compass, day, ric, mid + 1, t1_ms, min_size, max_rows, depth + 1)
            if left.num_rows == 0:
                return right
            if right.num_rows == 0:
                return left
            return pa.concat_tables([left, right], promote=True)
        raise


# =========================
# OUTPUT MERGE + WRITE
# =========================
OUTPUT_SCHEMA = pa.schema([
    ("csv_row_id", pa.int64()),
    ("date", pa.date32()),
    ("RIC", pa.string()),
    ("ClientSide", pa.string()),
    ("GSSide", pa.string()),
    ("OrderID", pa.string()),
    ("TradingAlgorithm", pa.string()),
    ("OrderCreationTime", pa.timestamp("ms")),
    ("StartTime", pa.timestamp("ms")),
    ("EndTime", pa.timestamp("ms")),
    ("ExecutionPrice", pa.float64()),
    ("AbsExecutedQuantity", pa.int64()),
    ("AbsExecutedDollarValue", pa.float64()),
    ("min_trade_size", pa.int64()),

    # trades fields
    ("trade_dt", pa.timestamp("ms")),
    ("exchangeTime", pa.time32("ms")),
    ("trade_price_raw", pa.float64()),
    ("trade_price", pa.float64()),
    ("trade_size", pa.int64()),
    ("tradeRIC", pa.string()),
    ("primaryRIC", pa.string()),
    ("canonRIC", pa.string()),
])

def repeat_array(value: Any, n: int, typ: pa.DataType) -> pa.Array:
    return pa.array([value] * n, type=typ)

def build_merged_table(row: Dict[str, Any], trades: pa.Table, min_size: int) -> pa.Table:
    n = trades.num_rows
    if n == 0:
        return pa.Table.from_arrays([pa.array([], type=f.type) for f in OUTPUT_SCHEMA], schema=OUTPUT_SCHEMA)

    # pull trade columns (cast to stable types)
    def get_col(name: str, typ: pa.DataType) -> pa.Array:
        arr = trades[name]
        if isinstance(arr, pa.ChunkedArray):
            arr = arr.combine_chunks()
        return pc.cast(arr, typ)

    # Some kdb/arrow conversions may produce timestamp[ns]; cast to ms
    trade_dt = get_col("trade_dt", pa.timestamp("ms"))
    exchange_time = get_col("exchangeTime", pa.time32("ms"))
    trade_price_raw = get_col("trade_price_raw", pa.float64())
    trade_price = get_col("trade_price", pa.float64())
    trade_size = get_col("size", pa.int64())
    tradeRIC = get_col("tradeRIC", pa.string())
    primaryRIC = get_col("primaryRIC", pa.string())
    canonRIC = get_col("canonRIC", pa.string())

    arrays = [
        repeat_array(int(row["csv_row_id"]), n, pa.int64()),
        repeat_array(row["date"], n, pa.date32()),
        repeat_array(row["RIC"], n, pa.string()),
        repeat_array(row["ClientSide"], n, pa.string()),
        repeat_array(row.get("GSSide"), n, pa.string()),
        repeat_array(row.get("OrderID"), n, pa.string()),
        repeat_array(row.get("TradingAlgorithm"), n, pa.string()),
        repeat_array(row.get("OrderCreationTime"), n, pa.timestamp("ms")),
        repeat_array(row.get("StartTime"), n, pa.timestamp("ms")),
        repeat_array(row.get("EndTime"), n, pa.timestamp("ms")),
        repeat_array(row.get("ExecutionPrice"), n, pa.float64()),
        repeat_array(row.get("AbsExecutedQuantity"), n, pa.int64()),
        repeat_array(row.get("AbsExecutedDollarValue"), n, pa.float64()),
        repeat_array(int(min_size), n, pa.int64()),

        trade_dt,
        exchange_time,
        trade_price_raw,
        trade_price,
        trade_size,
        tradeRIC,
        primaryRIC,
        canonRIC,
    ]

    return pa.Table.from_arrays(arrays, schema=OUTPUT_SCHEMA)


# =========================
# MAIN
# =========================
def main() -> None:
    rows = load_csv_rows(SI_PATH)
    rows.sort(key=lambda r: (r["date"], r["RIC"], r["csv_row_id"]))
    unique_days = sorted({r["date"] for r in rows})

    print(f"[LOCAL] rows={len(rows)} unique_days={len(unique_days)}", flush=True)

    if TEST_DAYS is not None:
        unique_days = unique_days[:TEST_DAYS]
        keep = set(unique_days)
        rows = [r for r in rows if r["date"] in keep]
        print(f"[DEBUG] TEST_DAYS={TEST_DAYS} -> rows={len(rows)} days={len(unique_days)}", flush=True)

    rows_by_day: Dict[dt.date, List[Dict[str, Any]]] = {}
    for r in rows:
        rows_by_day.setdefault(r["date"], []).append(r)

    print("[INIT] creating Compass client ...", flush=True)
    compass = Compass(region=REGION)
    print("[INIT] Compass client created.", flush=True)

    # small sanity query (optional)
    try:
        compass.run_query_sync("1+1")
        print("[INIT] Compass sanity OK (1+1).", flush=True)
    except Exception as e:
        print(f"[FATAL] Compass sanity failed: {e}", flush=True)
        raise

    coverage_stats: List[Dict[str, Any]] = []
    manifest: List[str] = []

    for di, day in enumerate(unique_days, 1):
        day_rows = rows_by_day.get(day, [])
        if TEST_ROWS_PER_DAY is not None:
            day_rows = day_rows[:TEST_ROWS_PER_DAY]

        print(f"\n[{di}/{len(unique_days)}] {day} START csv_rows={len(day_rows)}", flush=True)

        out_path = os.path.join(OUT_DIR, f"merged_trades_rowid_{day.strftime('%Y-%m-%d')}.parquet")
        writer: Optional[pq.ParquetWriter] = None

        matched_csv_rows = 0
        total_trade_rows_written = 0
        t0_day = time.perf_counter()

        for ri, row in enumerate(day_rows, 1):
            if ri == 1 or (ri % PRINT_EVERY_ROWS == 0):
                print(f"[{day}] progress {ri}/{len(day_rows)} matched={matched_csv_rows} trade_rows={total_trade_rows_written}", flush=True)

            ric = row["RIC"]

            # size >= half AbsExecutedQuantity
            abs_qty = row.get("AbsExecutedQuantity")
            if abs_qty is None or abs_qty <= 0:
                # If quantity is missing, we cannot apply your requested filter reliably.
                # To avoid huge pulls, skip these rows by default.
                # If you prefer to include them with min_size=0, change this behavior.
                continue

            min_size = int(math.ceil(0.5 * abs_qty))

            # start: OrderCreationTime (required by your rule)
            oc: dt.datetime = row["OrderCreationTime"]
            t0_ms = dt_to_ms_of_day(oc, day)

            # end: EndTime if present else cap to DEFAULT_LOOKAHEAD_S
            et: Optional[dt.datetime] = row.get("EndTime")
            if isinstance(et, dt.datetime):
                t1_ms = dt_to_ms_of_day(et, day)
                if t1_ms < t0_ms:
                    t1_ms = clamp_ms(t0_ms + DEFAULT_LOOKAHEAD_S * 1000)
            else:
                t1_ms = clamp_ms(t0_ms + DEFAULT_LOOKAHEAD_S * 1000)

            # Fetch trades (adaptive split on timeout)
            try:
                trades = fetch_trades_adaptive(
                    compass=compass,
                    day=day,
                    ric=ric,
                    t0_ms=t0_ms,
                    t1_ms=t1_ms,
                    min_size=min_size,
                    max_rows=MAX_TRADES_PER_ROW,
                )
            except Exception as e:
                print(f"[WARN] {day} csv_row_id={row['csv_row_id']} RIC={ric} query failed: {e}", flush=True)
                continue

            if trades.num_rows == 0:
                continue

            merged = build_merged_table(row, trades, min_size)
            if merged.num_rows == 0:
                continue

            if writer is None:
                writer = pq.ParquetWriter(out_path, OUTPUT_SCHEMA, compression="zstd")

            writer.write_table(merged)
            total_trade_rows_written += merged.num_rows
            matched_csv_rows += 1

            del trades, merged
            gc.collect()

        if writer is not None:
            writer.close()
            manifest.append(out_path)
            wrote = True
        else:
            wrote = False
            if os.path.exists(out_path):
                try:
                    os.remove(out_path)
                except Exception:
                    pass

        elapsed = time.perf_counter() - t0_day
        coverage = (matched_csv_rows / len(day_rows)) if day_rows else 0.0
        avg_trades_per_row = (total_trade_rows_written / matched_csv_rows) if matched_csv_rows else 0.0

        print(
            f"[{day}] DONE wrote={wrote} matched_rows={matched_csv_rows}/{len(day_rows)} "
            f"coverage={coverage:.1%} trade_rows={total_trade_rows_written} "
            f"avg_trades/row={avg_trades_per_row:.2f} elapsed={elapsed:.1f}s",
            flush=True
        )

        coverage_stats.append({
            "date": day.isoformat(),
            "csv_rows": len(day_rows),
            "matched_rows": matched_csv_rows,
            "coverage": coverage,
            "trade_rows_written": total_trade_rows_written,
            "avg_trades_per_row": avg_trades_per_row,
            "wrote_parquet": wrote,
            "elapsed_s": elapsed,
        })

        gc.collect()

    # Write coverage + manifest
    cov_path = os.path.join(OUT_DIR, "_coverage_by_date.csv")
    if coverage_stats:
        with open(cov_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(coverage_stats[0].keys()))
            w.writeheader()
            w.writerows(coverage_stats)

    man_path = os.path.join(OUT_DIR, "_manifest.txt")
    with open(man_path, "w") as f:
        for p in manifest:
            f.write(p + "\n")

    print(f"\n[DONE] out_dir={OUT_DIR}", flush=True)
    print(f"[DONE] parquet_files={len(manifest)}", flush=True)
    print(f"[DONE] coverage_csv={cov_path}", flush=True)
    print(f"[DONE] manifest={man_path}", flush=True)

    # Also print a quick coverage summary to the console
    if coverage_stats:
        worst = sorted(coverage_stats, key=lambda x: x["coverage"])[:10]
        print("\n[SUMMARY] 10 worst coverage days:", flush=True)
        for r in worst:
            print(r, flush=True)


if __name__ == "__main__":
    main()