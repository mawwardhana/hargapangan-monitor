#!/usr/bin/env python3
"""QA: kelengkapan, missing, duplikat, outlier, anomali provinsi baru."""
import csv, sqlite3, sys, statistics as st
from collections import defaultdict
from pathlib import Path


def main():
    db = Path(sys.argv[1] if len(sys.argv) > 1 else "02_data/warehouse.db")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "03_analitik/08_qa-report.csv")
    con = sqlite3.connect(db)
    rows = con.execute(
        "SELECT tanggal, commodity_id, prov_id, nilai, is_provinsi_baru FROM fakta_harga").fetchall()
    con.close()

    g = defaultdict(list)
    for t, c, p, v, pb in rows:
        g[(c, p)].append((t, v, pb))

    rep = []
    for (c, p), items in sorted(g.items()):
        items.sort()
        hari = [i[0] for i in items]
        vals = [i[1] for i in items if i[1] is not None]
        prov_baru = sum(1 for i in items if i[2])
        missing = sum(1 for i in items if i[1] is None)
        dup = len(hari) - len(set(hari))
        outl = 0
        if len(vals) >= 4:
            q1, q3 = st.quantiles(vals, n=4)[0], st.quantiles(vals, n=4)[2]
            iqr = q3 - q1
            outl = sum(1 for v in vals if v < q1 - 1.5*iqr or v > q3 + 1.5*iqr)
        kel = round(100 * (1 - missing / max(len(items), 1)), 2)
        status = "LULUS" if kel >= 90 and dup == 0 else ("PERINGATAN" if kel >= 80 else "GAGAL")
        rep.append({"commodity_id": c, "prov_id": p, "total_baris": len(items),
                    "hari_unik": len(set(hari)), "missing_pct": round(100*missing/max(len(items),1), 2),
                    "duplikat": dup, "outlier": outl, "prov_baru": prov_baru,
                    "kelengkapan_pct": kel, "status": status})

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rep[0].keys()) if rep else [])
        w.writeheader(); w.writerows(rep)
    gagal = sum(1 for r in rep if r["status"] == "GAGAL")
    print(f"{len(rep)} seri dianalisis; GAGAL={gagal} -> {out}")


if __name__ == "__main__":
    main()