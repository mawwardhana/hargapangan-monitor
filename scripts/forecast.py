#!/usr/bin/env python3
"""Prediksi ADAPTIF - bekerja dengan data SANGAT pendek (minimal 1 titik).
n=1:single, n=2:naive+mean, n>=3:+ma adaptif, n>=5:+trend, n>=7:+ma7, n>=14:label ok."""
import csv, math, sqlite3, sys
from collections import defaultdict
from datetime import date
from pathlib import Path


def mae(y, yh): return sum(abs(a - b) for a, b in zip(y, yh)) / max(len(y), 1)


def mape(y, yh):
    v = [abs(a - b) / a for a, b in zip(y, yh) if a]
    return 100 * sum(v) / max(len(v), 1)


def _trend(h):
    n = len(h)
    if n < 2: return h[-1]
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(h) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, h))
    den = sum((x - mx) ** 2 for x in xs) or 1
    return my + (num / den) * (n - mx)


def models_for(n):
    if n < 2: return {"single": lambda h: h[-1]}
    m = {"naive": lambda h: h[-1], "mean": lambda h: sum(h) / len(h)}
    if n >= 3:
        w = min(3, max(2, n // 3))
        m[f"ma{w}"] = (lambda ww: lambda h: sum(h[-ww:]) / min(ww, len(h)))(w)
    if n >= 5: m["trend"] = _trend
    if n >= 7: m["ma7"] = lambda h: sum(h[-7:]) / min(7, len(h))
    return m


def backtest(y, fn, max_windows=5):
    start = max(1, len(y) - max_windows)
    return [(mae([y[k]], [fn(y[:k])]), mape([y[k]], [fn(y[:k])]))
            for k in range(start, len(y))]


def ffill(items):
    if not items: return items
    out = [items[0]]
    for t, v in items[1:]:
        try:
            gap = (date.fromisoformat(t) - date.fromisoformat(out[-1][0])).days
        except Exception:
            gap = 1
        for g in range(1, gap):
            d = date.fromordinal(date.fromisoformat(out[-1][0]).toordinal() + g)
            out.append((d.isoformat(), out[-1][1]))
        out.append((t, v))
    return out


def main():
    db = Path(sys.argv[1] if len(sys.argv) > 1 else "02_data/warehouse.db")
    hor = int(sys.argv[2] if len(sys.argv) > 2 else 7)
    con = sqlite3.connect(db)
    rows = con.execute("SELECT tanggal, commodity_id, prov_id, nilai FROM fakta_harga ORDER BY 1").fetchall()
    con.close()
    g = defaultdict(list)
    for t, c, p, v in rows:
        if v is not None: g[(c, p)].append((t, v))

    preds, back = [], []
    skipped = 0
    for (c, p), raw in sorted(g.items()):
        raw.sort()
        items = ffill(raw)
        y = [i[1] for i in items]
        n = len(y)
        if n < 1:
            skipped += 1; continue
        mset = models_for(n)
        for name, fn in mset.items():
            errs = backtest(y, fn)
            if errs:
                back.append({"commodity_id": c, "prov_id": p, "model": name, "n_data": n,
                             "mae": round(sum(e[0] for e in errs) / len(errs), 2),
                             "mape": round(sum(e[1] for e in errs) / len(errs), 2),
                             "n_jendela": len(errs)})
        cand = [b for b in back if b["commodity_id"] == c and b["prov_id"] == p]
        best = min(cand, key=lambda x: (x["mape"], x["mae"])) if cand else {"model": "single", "mape": 0.0}
        base = mset.get(best["model"], lambda h: h[-1])(y)
        resid = [abs(y[k] - mset.get(best["model"], lambda h: h[-1])(y[:k]))
                 for k in range(max(1, n - 5), n)]
        spread = (sum(resid) / len(resid)) if resid else (abs(base) * 0.03)
        if n >= 14 and best["mape"] <= 15: note = "ok"
        elif n == 1: note = "sangat indikatif (1 titik)"
        else: note = "indikatif, bukan presisi"
        last = items[-1][0]
        for h in range(1, hor + 1):
            preds.append({"tanggal_terakhir": last, "commodity_id": c, "prov_id": p, "h": h,
                          "prediksi": round(base, 0), "lower": round(base - spread, 0),
                          "upper": round(base + spread, 0), "model": best["model"],
                          "n_data": n, "mape": best["mape"], "catatan": note})

    for name, data in (("03_analitik/10_backtest.csv", back), ("03_analitik/10_prediksi.csv", preds)):
        pth = Path(name); pth.parent.mkdir(parents=True, exist_ok=True)
        if data:
            with open(pth, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(data[0].keys())); w.writeheader(); w.writerows(data)
        print(f"{name}: {len(data)} baris")
    seri = {(b['commodity_id'], b['prov_id']) for b in back}
    print(f"seri dianalisis: {len(seri)}; dilewati: {skipped}")


if __name__ == "__main__":
    main()