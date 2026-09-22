#!/usr/bin/env python3
"""Bangun dashboard HTML + Chart.js dari SQLite + freshness."""
import json, sqlite3, sys
from pathlib import Path

TPL = """<!DOCTYPE html><html lang="id"><head><meta charset="utf-8">
<title>Monitoring Harga Pangan</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>body{{font-family:system-ui;margin:24px;background:#f7f8fa}}
.cards{{display:flex;gap:16px;flex-wrap:wrap}}
.card{{background:#fff;border-radius:10px;padding:16px 20px;box-shadow:0 1px 4px #0001;min-width:180px}}
.card b{{font-size:22px;display:block}}
canvas{{background:#fff;border-radius:10px;padding:12px;margin-top:20px}}</style></head>
<body><h1>Monitoring Harga Pangan</h1>
<p>Status: <b>{status}</b> | Rilis terakhir: <b>{rilis}</b> | Lag: <b>{lag} hari</b></p>
<div class="cards">{cards}</div>
<canvas id="c1" height="90"></canvas><canvas id="c2" height="90"></canvas>
<script>
const T={tren},D={disp};
new Chart(document.getElementById('c1'),{{type:'line',data:{{labels:T.labels,datasets:T.sets}},options:{{plugins:{{title:{{display:true,text:'Tren Harga'}}}}}}}});
new Chart(document.getElementById('c2'),{{type:'bar',data:{{labels:D.labels,datasets:[{{label:'Harga',data:D.values,backgroundColor:'#2563eb'}}]}},options:{{plugins:{{title:{{display:true,text:'Disparitas Antarprovinsi'}}}}}}}});
</script></body></html>"""


def main():
    db = Path(sys.argv[1] if len(sys.argv) > 1 else "02_data/warehouse.db")
    fr = Path("03_analitik/07_freshness.json")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "04_laporan/12_dashboard.html")
    status, rilis, lag = "-", "-", "-"
    if fr.exists():
        j = json.loads(fr.read_text(encoding="utf-8"))
        status, rilis, lag = j.get("status"), j.get("rilis_terakhir"), j.get("lag_hari")

    tren, disp, cards = {"labels": [], "sets": []}, {"labels": [], "values": []}, []
    if db.exists():
        con = sqlite3.connect(db)
        r = con.execute("SELECT nama_komoditas, nilai FROM fakta_harga ORDER BY tanggal DESC LIMIT 1").fetchone()
        if r:
            cards.append(f"<div class='card'>{r[0]}<b>Rp{r[1]:,.0f}</b></div>")
        for c, nama in con.execute("SELECT DISTINCT commodity_id, nama_komoditas FROM fakta_harga LIMIT 5"):
            rows = con.execute("SELECT tanggal, nilai FROM fakta_harga WHERE commodity_id=? AND prov_id=0 ORDER BY tanggal", (c,)).fetchall()
            if rows:
                tren["labels"] = [r[0] for r in rows]
                tren["sets"].append({"label": nama, "data": [r[1] for r in rows], "borderWidth": 2, "tension": .3})
        maxd = con.execute("SELECT MAX(tanggal) FROM fakta_harga").fetchone()[0]
        rows = con.execute("SELECT nama_provinsi, nilai FROM fakta_harga WHERE tanggal=? AND prov_id!=0 ORDER BY nilai DESC LIMIT 10", (maxd,)).fetchall()
        disp = {"labels": [r[0] for r in rows], "values": [r[1] for r in rows]}
        con.close()

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(TPL.format(status=status, rilis=rilis, lag=lag, cards="".join(cards),
                              tren=json.dumps(tren, ensure_ascii=False),
                              disp=json.dumps(disp, ensure_ascii=False)), encoding="utf-8")
    print(f"dashboard -> {out}")


if __name__ == "__main__":
    main()