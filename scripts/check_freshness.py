#!/usr/bin/env python3
"""Cek apakah server punya data lebih baru daripada yang ada di gudang."""
import json, sqlite3, sys, time, urllib.parse, urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

BASE = "https://www.bi.go.id/hargapangan/WebSite/Home/GetGridData1"
BULAN = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0 Safari/537.36"
PETA = {v: i for i, v in enumerate(BULAN, 1)}


def to_iso(s):
    if not s:
        return None
    p = s.split()
    return f"20{p[2]}-{PETA.get(p[1],1):02d}-{int(p[0]):02d}"


def probe(today):
    qs = urllib.parse.urlencode({"tanggal": f"{BULAN[today.month-1]} {today.day:02d}, {today.year}",
        "commodity": 1, "priceType": 1, "isPasokan": 1, "jenis": 1, "periode": 1,
        "provId": 0, "_": int(time.time()*1000)})
    req = urllib.request.Request(f"{BASE}?{qs}", headers={
        "User-Agent": UA, "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.bi.go.id/hargapangan"})
    with urllib.request.urlopen(req, timeout=25) as r:
        obj = json.loads(r.read().decode("utf-8"))
    return obj["data"][0]["Tanggal"] if obj.get("data") else None


def main():
    db = Path(sys.argv[1] if len(sys.argv) > 1 else "02_data/warehouse.db")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "03_analitik/07_freshness.json")
    today = date.today()
    result = {"diminta": today.isoformat(), "rilis_terakhir": None, "lag_hari": None,
              "max_di_gudang": None, "perlu_tarik": [], "status": "GAGAL_PROBE"}
    try:
        rilis = to_iso(probe(today))
        result["rilis_terakhir"] = rilis
        if rilis:
            result["lag_hari"] = (today - datetime.fromisoformat(rilis).date()).days
    except Exception as e:
        result["error"] = str(e)
        print(json.dumps(result, indent=2))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return

    if db.exists():
        con = sqlite3.connect(db)
        mx = con.execute("SELECT MAX(tanggal) FROM fakta_harga").fetchone()[0]
        con.close()
        result["max_di_gudang"] = mx
        if mx and result["rilis_terakhir"]:
            if mx >= result["rilis_terakhir"]:
                result["status"] = "SUDAH_TERBARU"
            else:
                result["status"] = "UPDATE_TERSEDIA"
                d0 = datetime.fromisoformat(mx).date()
                d1 = datetime.fromisoformat(result["rilis_terakhir"]).date()
                cur, need = d1, []
                while cur > d0:
                    need.append(cur.isoformat())
                    cur = date.fromordinal(cur.toordinal() - 1)
                result["perlu_tarik"] = sorted(need)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()