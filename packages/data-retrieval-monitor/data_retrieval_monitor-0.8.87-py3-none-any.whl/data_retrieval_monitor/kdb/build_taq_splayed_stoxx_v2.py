from __future__ import annotations

import os
import math
import time
import gc
import csv
import datetime as dt
from typing import Any, Dict, List, Optional

import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.compute as pc
import pyarrow.parquet as pq

from goldmansachs.compass_pykx import Compass


# =========================
# CONFIG
# =========================
SI_PATH = "/workspaces/gsg-api/scripts/datasets/compass/data/SI_trades_labeled.csv"
OUT_DIR = "/workspaces/gsg-api/data/merged_trades_rowid_debug"
os.makedirs(OUT_DIR, exist_ok=True)

REGION = "ldn"

DEFAULT_LOOKAHEAD_S = 60 * 60
MAX_TRADES_PER_ROW: Optional[int] = 2000
TRADE_PRICE_SCALE = 0.01

PRINT_EVERY_ROWS = 50

# Debug controls
DEBUG = True
DEBUG_MAX_ERRORS = 5              # only do the heavy debug ladder for first N failures
DEBUG_PRINT_FULL_QTXT = True      # print full q query on failure (can be long)
DEBUG_SAVE_FAILED_QTXT = True     # write failing qtxt to files in OUT_DIR

# Debug limits (set to None for full run)
TEST_DAYS: Optional[int] = None
TEST_ROWS_PER_DAY: Optional[int] = None


# =========================
# HELPERS
# =========================
DAY_MS = 24 * 3600 * 1000

def q_date_literal(d: dt.date) -> str:
    return d.strftime("%Y.%m.%d")

def q_symbol(ric: str) -> str:
    return "`" + str(ric).strip().replace("`", "")

def clamp_ms(ms: int) -> int:
    return max(0, min(int(ms), DAY_MS - 1))

def ms_to_time(ms: int) -> dt.time:
    ms = clamp_ms(ms)
    sec, milli = divmod(ms, 1000)
    hh, rem = divmod(sec, 3600)
    mm, ss = divmod(rem, 60)
    return dt.time(hh, mm, ss, milli * 1000)

def q_time_literal(t: dt.time) -> str:
    return t.strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm

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
    if not pa.types.is_string(arr.type):
        arr = pc.cast(arr, pa.string())
    s = pc.utf8_upper(arr)
    p1 = pc.strptime(s, format="%a %d%b%y %I:%M:%S %p", unit="ns", error_is_null=True)
    p2 = pc.strptime(s, format="%d%b%y %I:%M:%S %p", unit="ns", error_is_null=True)
    p3 = pc.strptime(s, format="%d-%b-%y", unit="ns", error_is_null=True)
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


def summarize_result(res: Any, max_rows: int = 5) -> str:
    """
    Print-friendly summary for Compass result objects.
    """
    # Try scalar
    try:
        py = res.py()
        return f"(py) {py!r}"
    except Exception:
        pass

    # Try Arrow table
    try:
        t = res.pa()
        msg = f"(pa) rows={t.num_rows} cols={t.num_columns} names={t.column_names}"
        if t.num_rows and t.num_rows <= max_rows:
            msg += f" data={t.to_pydict()}"
        return msg
    except Exception:
        pass

    return f"(repr) {res!r}"


# =========================
# CSV LOAD
# =========================
def load_csv_rows(path: str) -> List[Dict[str, Any]]:
    tbl = pacsv.read_csv(path)
    tbl = parse_datetime_columns(tbl, ["TradeDate", "OrderCreationTime", "StartTime", "EndTime", "LocalStartTime"])
    rows_raw = tbl.to_pylist()

    out: List[Dict[str, Any]] = []
    for i, r in enumerate(rows_raw):
        ric = (r.get("RIC") or "").strip().upper()
        if not ric:
            continue

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

        abs_qty = safe_int(r.get("AbsExecutedQuantity"))
        exec_px = safe_float(r.get("ExecutionPrice"))
        abs_dv = safe_float(r.get("AbsExecutedDollarValue"))

        oc = r.get("OrderCreationTime")
        st = r.get("StartTime")
        et = r.get("EndTime")

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
# Q BUILDERS (with/without time cast)
# =========================
def build_trades_q(
    *,
    day: dt.date,
    ric: str,
    t0_ms: int,
    t1_ms: int,
    min_size: int,
    max_rows: Optional[int],
    time_mode: str = "cast",   # "cast" or "raw"
) -> str:
    """
    time_mode:
      - "raw":   exchangeTime >= t0, exchangeTime <= t1
      - "cast":  (time exchangeTime) >= t0, (time exchangeTime) <= t1   <-- safer
    """
    d_q = q_date_literal(day)
    ric_q = q_symbol(ric)
    t0 = q_time_literal(ms_to_time(t0_ms))
    t1 = q_time_literal(ms_to_time(t1_ms))

    cap = ""
    if isinstance(max_rows, int) and max_rows > 0:
        cap = f"{max_rows}#"

    if time_mode == "raw":
        time_pred = "exchangeTime >= t0, exchangeTime <= t1"
    elif time_mode == "cast":
        time_pred = "(time exchangeTime) >= t0, (time exchangeTime) <= t1"
    else:
        raise ValueError(f"Unknown time_mode={time_mode}")

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
      exchangeTime,
      trade_dt: date + exchangeTime,
      trade_price_raw: price,
      trade_price: {TRADE_PRICE_SCALE} * price,
      trade_size: size
    from trades
    where date=d,
          eutradetype=`SI,
          not null exchangeTime,
          {time_pred},
          ((primaryRIC = ric) | (RIC = ric)),
          size >= minSize;

t: `exchangeTime xasc t;
{cap} t
"""


# =========================
# DEBUG LADDER (pinpoint which predicate causes 'rank)
# =========================
def debug_rank_ladder(compass: Compass, *, day: dt.date, ric: str, t0_ms: int, t1_ms: int, min_size: int) -> None:
    d_q = q_date_literal(day)
    ric_q = q_symbol(ric)
    t0 = q_time_literal(ms_to_time(t0_ms))
    t1 = q_time_literal(ms_to_time(t1_ms))

    print("\n========== DEBUG RANK LADDER ==========", flush=True)
    print(f"[DEBUG] day={day} ric={ric} t0={t0} t1={t1} min_size={min_size}", flush=True)

    # 1) Meta (types)
    q_meta = "select c,t from meta trades where c in `date`eutradetype`RIC`primaryRIC`exchangeTime`size`price"
    try:
        res = compass.run_query_sync(q_meta)
        print("[DEBUG] meta trades subset:", summarize_result(res), flush=True)
    except Exception as e:
        print(f"[DEBUG] meta trades subset FAILED: {e}", flush=True)

    # 2) Sample rows (very small)
    q_sample = f"""
d:{d_q}; ric:{ric_q};
5#select date,eutradetype,RIC,primaryRIC,exchangeTime,size,price
  from trades
  where date=d,
        ((primaryRIC=ric) | (RIC=ric))
"""
    try:
        res = compass.run_query_sync(q_sample)
        print("[DEBUG] sample rows:", summarize_result(res), flush=True)
    except Exception as e:
        print(f"[DEBUG] sample rows FAILED: {e}", flush=True)

    # 3) Step-by-step counts
    steps = [
        ("count base (date + ric)", f"""
d:{d_q}; ric:{ric_q};
count select from trades where date=d, ((primaryRIC=ric) | (RIC=ric))
"""),
        ("count + eutradetype=SI", f"""
d:{d_q}; ric:{ric_q};
count select from trades where date=d, eutradetype=`SI, ((primaryRIC=ric) | (RIC=ric))
"""),
        ("count + not null exchangeTime", f"""
d:{d_q}; ric:{ric_q};
count select from trades where date=d, eutradetype=`SI, not null exchangeTime, ((primaryRIC=ric) | (RIC=ric))
"""),
        ("count + RAW time filter", f"""
d:{d_q}; ric:{ric_q}; t0:{t0}; t1:{t1};
count select from trades where date=d, eutradetype=`SI, not null exchangeTime, exchangeTime>=t0, exchangeTime<=t1, ((primaryRIC=ric) | (RIC=ric))
"""),
        ("count + CAST time filter", f"""
d:{d_q}; ric:{ric_q}; t0:{t0}; t1:{t1};
count select from trades where date=d, eutradetype=`SI, not null exchangeTime, (time exchangeTime)>=t0, (time exchangeTime)<=t1, ((primaryRIC=ric) | (RIC=ric))
"""),
        ("count + CAST time + size>=minSize", f"""
d:{d_q}; ric:{ric_q}; t0:{t0}; t1:{t1}; minSize:{int(min_size)};
count select from trades where date=d, eutradetype=`SI, not null exchangeTime, (time exchangeTime)>=t0, (time exchangeTime)<=t1, ((primaryRIC=ric) | (RIC=ric)), size>=minSize
"""),
        ("sample with CAST time + size", f"""
d:{d_q}; ric:{ric_q}; t0:{t0}; t1:{t1}; minSize:{int(min_size)};
5#select date,RIC,primaryRIC,exchangeTime,size,price
  from trades
  where date=d, eutradetype=`SI, not null exchangeTime,
        (time exchangeTime)>=t0, (time exchangeTime)<=t1,
        ((primaryRIC=ric) | (RIC=ric)), size>=minSize
"""),
    ]

    for label, qtxt in steps:
        try:
            res = compass.run_query_sync(qtxt)
            print(f"[DEBUG] {label}: OK -> {summarize_result(res)}", flush=True)
        except Exception as e:
            print(f"[DEBUG] {label}: FAILED -> {e}", flush=True)
            print("[DEBUG] failing q:\n" + qtxt.strip(), flush=True)

    print("========== END DEBUG ==========\n", flush=True)


# =========================
# OUTPUT SCHEMA
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
    # trades
    ("trade_dt", pa.timestamp("ms")),
    ("exchangeTime", pa.time32("ms")),
    ("trade_price_raw", pa.float64()),
    ("trade_price", pa.float64()),
    ("trade_size", pa.int64()),
    ("tradeRIC", pa.string()),
    ("primaryRIC", pa.string()),
])

def repeat_array(value: Any, n: int, typ: pa.DataType) -> pa.Array:
    return pa.array([value] * n, type=typ)

def build_merged_table(row: Dict[str, Any], trades: pa.Table, min_size: int) -> pa.Table:
    n = trades.num_rows
    if n == 0:
        return pa.Table.from_arrays([pa.array([], type=f.type) for f in OUTPUT_SCHEMA], schema=OUTPUT_SCHEMA)

    def get_col(name: str, typ: pa.DataType) -> pa.Array:
        arr = trades[name]
        if isinstance(arr, pa.ChunkedArray):
            arr = arr.combine_chunks()
        return pc.cast(arr, typ)

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
        # trades (cast to stable types)
        get_col("trade_dt", pa.timestamp("ms")),
        get_col("exchangeTime", pa.time32("ms")),
        get_col("trade_price_raw", pa.float64()),
        get_col("trade_price", pa.float64()),
        get_col("trade_size", pa.int64()),
        get_col("tradeRIC", pa.string()),
        get_col("primaryRIC", pa.string()),
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
    compass.run_query_sync("1+1")
    print("[INIT] Compass sanity OK (1+1).", flush=True)

    # error logging
    err_path = os.path.join(OUT_DIR, "_errors.csv")
    if not os.path.exists(err_path):
        with open(err_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "csv_row_id", "RIC", "t0", "t1", "min_size", "time_mode", "error"])

    debug_errors_used = 0
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
            abs_qty = row.get("AbsExecutedQuantity")
            if abs_qty is None or abs_qty <= 0:
                continue
            min_size = int(math.ceil(0.5 * abs_qty))

            oc: dt.datetime = row["OrderCreationTime"]
            t0_ms = dt_to_ms_of_day(oc, day)

            et: Optional[dt.datetime] = row.get("EndTime")
            if isinstance(et, dt.datetime):
                t1_ms = dt_to_ms_of_day(et, day)
                if t1_ms < t0_ms:
                    t1_ms = clamp_ms(t0_ms + DEFAULT_LOOKAHEAD_S * 1000)
            else:
                t1_ms = clamp_ms(t0_ms + DEFAULT_LOOKAHEAD_S * 1000)

            # Try "cast" time-mode first (safer). If it fails with rank, also try "raw".
            for time_mode in ("cast", "raw"):
                qtxt = build_trades_q(
                    day=day, ric=ric, t0_ms=t0_ms, t1_ms=t1_ms,
                    min_size=min_size, max_rows=MAX_TRADES_PER_ROW,
                    time_mode=time_mode
                )

                try:
                    res = compass.run_query_sync(qtxt)
                    trades = res.pa()
                    break
                except Exception as e:
                    # log error
                    with open(err_path, "a", newline="") as f:
                        csv.writer(f).writerow([
                            day.isoformat(), row["csv_row_id"], ric,
                            q_time_literal(ms_to_time(t0_ms)), q_time_literal(ms_to_time(t1_ms)),
                            min_size, time_mode, str(e)
                        ])

                    print(f"[WARN] {day} row_id={row['csv_row_id']} RIC={ric} time_mode={time_mode} failed: {e}", flush=True)

                    if DEBUG and ("'rank" in str(e)) and debug_errors_used < DEBUG_MAX_ERRORS:
                        debug_errors_used += 1

                        if DEBUG_PRINT_FULL_QTXT:
                            print("\n[DEBUG] FULL QTXT SENT:\n" + qtxt.strip() + "\n", flush=True)

                        if DEBUG_SAVE_FAILED_QTXT:
                            qfile = os.path.join(
                                OUT_DIR, f"failed_q_rank_{day.strftime('%Y-%m-%d')}_row{row['csv_row_id']}_{time_mode}.q"
                            )
                            with open(qfile, "w") as ff:
                                ff.write(qtxt)
                            print(f"[DEBUG] saved failing q to {qfile}", flush=True)

                        debug_rank_ladder(
                            compass,
                            day=day, ric=ric,
                            t0_ms=t0_ms, t1_ms=t1_ms,
                            min_size=min_size
                        )

                    trades = None  # keep trying next time_mode
                    continue

            if trades is None or trades.num_rows == 0:
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
    print(f"[DONE] errors_csv={err_path}", flush=True)


if __name__ == "__main__":
    main()