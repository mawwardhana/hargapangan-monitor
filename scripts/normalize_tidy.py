#!/usr/bin/env python3
"""Normalisasi JSON mentah GetGridData1 -> tabel panjang (tidy)."""
import csv, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

BULAN = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"Mei":5,"Jun":6,
         "Jul":7,"Agu":8,"Sep":9,"Okt":10,"Nov":11,"Des":12}
KOLOM = ["tanggal","tanggal_diminta","commodity_id","nama_komoditas","prov_id","nama_provinsi",
         "price_type_id","nilai","nilai_diff","nasional","kelompok","stddev","percentage",
         "tanggal_last","is_provinsi_baru","is_weekend_fill","source_url","endpoint","fetched_at"]


def parse_tgl(s):
    """'18 Sep 26' -> '2026-09-18'"""
    if not s:
        return None
    m = re.match(r"(\d{1,2})\s+(\w{3})\s+(\d{2})", s.strip())
    if not m:
        return None
    d, mo, y = m.groups()
    return f"20{y}-{BULAN.get(mo,1):02d}-{int(d):02d}"


def num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[^0-9.\-]", "", str(v))
    try:
        return float(s) if s not in ("", "-") else None
    except ValueError:
        return None


def main():
    raw = Path(sys.argv[1] if len(sys.argv) > 1 else "01_backfill/raw")
    outdir = Path(sys.argv[2] if len(sys.argv) > 2 else "02_data")
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    files = sorted(raw.glob("*.json"))
    for f in files:
        try:
            obj = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        m = re.search(r"_c(\d+)", f.stem)
        cid = int(m.group(1)) if m else None
        # tanggal_diminta dari nama file
        tgl_dim = f.stem.split("_")[0]
        for d in obj.get("data", []):
            tgl_resp = parse_tgl(d.get("Tanggal"))
            rows.append({
                "tanggal": tgl_resp,
                "tanggal_diminta": tgl_dim,
                "commodity_id": cid,
                "nama_komoditas": d.get("Komoditas"),
                "prov_id": d.get("ProvID"),
                "nama_provinsi": d.get("Provinsi"),
                "price_type_id": 1,
                "nilai": num(d.get("Nilai")),
                "nilai_diff": num(d.get("NilaiDiff")),
                "nasional": num(d.get("SemuaProvinsi")),
                "kelompok": d.get("Kelompok"),
                "stddev": num(d.get("stdDev")),
                "percentage": num(d.get("Percentage")),
                "tanggal_last": parse_tgl(d.get("TanggalLast")),
                "is_provinsi_baru": 1 if d.get("TanggalLast") is None else 0,
                "is_weekend_fill": 1 if tgl_dim != tgl_resp else 0,
                "source_url": "",
                "endpoint": "GetGridData1",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
    csv_path = outdir / "tidy.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=KOLOM)
        w.writeheader(); w.writerows(rows)
    print(f"{len(files)} file -> {len(rows)} baris -> {csv_path}")
    try:
        import pandas as pd
        pd.DataFrame(rows, columns=KOLOM).to_parquet(outdir / "tidy.parquet", index=False)
        print(f"parquet: {outdir / 'tidy.parquet'}")
    except Exception as e:
        print(f"[info] parquet dilewati ({e}); CSV tetap tersedia")


if __name__ == "__main__":
    main()