#!/usr/bin/env python3
"""Bangun gudang SQLite dari tidy.csv dengan upsert idempoten + log revisi."""
import csv, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

PK = ["tanggal","commodity_id","prov_id","price_type_id"]
KOLOM = ["tanggal","tanggal_diminta","commodity_id","nama_komoditas","prov_id","nama_provinsi",
         "price_type_id","nilai","nilai_diff","nasional","kelompok","stddev","percentage",
         "tanggal_last","is_provinsi_baru","is_weekend_fill","source_url","endpoint","fetched_at"]
DDL = """CREATE TABLE IF NOT EXISTS fakta_harga (
  tanggal TEXT, tanggal_diminta TEXT, commodity_id INTEGER, nama_komoditas TEXT,
  prov_id INTEGER, nama_provinsi TEXT, price_type_id INTEGER,
  nilai REAL, nilai_diff REAL, nasional REAL, kelompok INTEGER, stddev REAL,
  percentage REAL, tanggal_last TEXT, is_provinsi_baru INTEGER, is_weekend_fill INTEGER,
  source_url TEXT, endpoint TEXT, fetched_at TEXT,
  PRIMARY KEY (tanggal, commodity_id, prov_id, price_type_id));"""


def main():
    tidy = Path(sys.argv[1] if len(sys.argv) > 1 else "02_data/tidy.csv")
    db = Path(sys.argv[2] if len(sys.argv) > 2 else "02_data/warehouse.db")
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.execute(DDL)
    con.execute("CREATE TABLE IF NOT EXISTS log_revisi (ts TEXT, pk TEXT, nilai_lama REAL, nilai_baru REAL)")
    cur = con.cursor()
    n_baru = n_upd = n_dup = 0
    with open(tidy, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            key = tuple(r[k] for k in PK)
            old = cur.execute(
                "SELECT nilai FROM fakta_harga WHERE tanggal=? AND commodity_id=? AND prov_id=? AND price_type_id=?",
                key).fetchone()
            if old is None:
                n_baru += 1
            elif abs((old[0] or 0) - float(r["nilai"] or 0)) > 1e-9:
                n_upd += 1
                cur.execute("INSERT INTO log_revisi VALUES (?,?,?,?)",
                            (datetime.now(timezone.utc).isoformat(), str(key), old[0], r["nilai"]))
            else:
                n_dup += 1
            cur.execute(
                f"INSERT OR REPLACE INTO fakta_harga ({','.join(KOLOM)}) VALUES ({','.join('?'*len(KOLOM))})",
                [r[k] if r[k] != '' else None for k in KOLOM])
    con.commit()
    total = cur.execute("SELECT COUNT(*) FROM fakta_harga").fetchone()[0]
    print(f"baru={n_baru} update={n_upd} duplikat={n_dup} total={total} -> {db}")
    con.close()


if __name__ == "__main__":
    main()