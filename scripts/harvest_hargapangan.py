#!/usr/bin/env python3
"""Kolektor GetGridData1 - snapshot harian + backfill, dengan freshness probe.
Tahan tanpa pyyaml (memakai parser YAML mini bawaan)."""
import argparse, hashlib, json, random, re, time, urllib.parse, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE = "https://www.bi.go.id/hargapangan/WebSite/Home/GetGridData1"
HEADERS = {"X-Requested-With": "XMLHttpRequest", "Referer": "https://www.bi.go.id/hargapangan"}
BULAN = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]

DEF = {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0 Safari/537.36",
       "timeout_detik": 25, "throttle_detik": 1.8, "jitter_detik": 0.5, "max_retry": 3,
       "output_root": "output", "proyek": "default", "komoditas": [1], "provinsi": [0],
       "price_type": 1, "horizon": {"tgl_awal": "2023-01-01"}}


def _cast(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        return [_cast(x) for x in v[1:-1].split(",") if x.strip()]
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    if v.lower() in ("null", "none", "~"):
        return None
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d*\.\d+", v):
        return float(v)
    return v.strip('"\'')


def mini_yaml(text):
    """Parser YAML sederhana: skalar, list inline, list blok, nested satu level."""
    out, cur = {}, None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if line.startswith("- "):
            if cur is not None:
                if not isinstance(out.get(cur), list):
                    out[cur] = []
                out[cur].append(_cast(line[2:]))
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.split("#")[0].strip()
        if indent == 0:
            if v == "":
                cur = k
                out.setdefault(k, {})
            else:
                cur = None
                out[k] = _cast(v)
        else:
            if isinstance(out.get(cur), dict):
                out[cur][k] = _cast(v)
    return out


def load_cfg(path):
    cfg = dict(DEF)
    p = Path(path)
    if not p.exists():
        print(f"[warn] {path} tidak ada, pakai default")
        return cfg
    txt = p.read_text(encoding="utf-8")
    try:
        import yaml
        cfg.update(yaml.safe_load(txt) or {})
        print("[cfg] dibaca via pyyaml")
    except ImportError:
        cfg.update(mini_yaml(txt))
        print("[cfg] dibaca via parser mini (pyyaml tidak ada)")
    return cfg


def fmt_tanggal(d):
    return f"{BULAN[d.month-1]} {d.day:02d}, {d.year}"


def fetch(tgl, c, pt, pv, cfg):
    HEADERS["User-Agent"] = cfg["user_agent"]
    qs = urllib.parse.urlencode({"tanggal": tgl, "commodity": c, "priceType": pt,
        "isPasokan": 1, "jenis": 1, "periode": 1, "provId": pv,
        "_": int(time.time() * 1000)})
    url = f"{BASE}?{qs}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS),
                                timeout=cfg["timeout_detik"]) as r:
        return url, r.read().decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--mode", choices=["freshness", "backfill"], default="freshness")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    cfg = load_cfg(a.config)
    print(f"[cfg] proyek={cfg['proyek']} komoditas={cfg['komoditas']}")

    out = Path(cfg["output_root"]) / cfg["proyek"] / "01_backfill" / "raw"
    out.mkdir(parents=True, exist_ok=True)
    mf_path = out / "manifest.csv"
    new = not mf_path.exists()
    mf = open(mf_path, "a", encoding="utf-8")
    if new:
        mf.write("file,url,tanggal_diminta,tanggal_rilis,n_baris,http_status,sha256,fetched_at\n")

    today = date.today()
    kom, prov, pt = cfg["komoditas"], cfg["provinsi"], cfg["price_type"]

    _, body = fetch(fmt_tanggal(today), kom[0], pt, prov[0], cfg)
    obj = json.loads(body)
    rilis = obj["data"][0]["Tanggal"] if obj.get("data") else None
    print(f"[freshness] diminta={today} rilis_terakhir={rilis}")

    if a.mode == "freshness":
        tgl_list = [today]
    else:
        awal = cfg.get("horizon", {}).get("tgl_awal", "2023-01-01")
        y, m, d = map(int, awal.split("-"))
        start = date(y, m, d)
        # hari kerja saja
        tgl_list = [start + timedelta(days=i) for i in range((today - start).days + 1)
                    if (start + timedelta(days=i)).weekday() < 5]

    total = 0
    for t in tgl_list:
        ts = fmt_tanggal(t)
        for c in kom:
            for retry in range(int(cfg["max_retry"])):
                try:
                    url, body = fetch(ts, c, pt, prov[0], cfg)
                    o = json.loads(body)
                    n = len(o.get("data", []))
                    if n == 0:
                        break
                    sha = hashlib.sha256(body.encode()).hexdigest()[:16]
                    fn = f"{t.isoformat()}_c{c}.json"
                    (out / fn).write_text(body, encoding="utf-8")
                    if not a.dry_run:
                        mf.write(f"{fn},{url},{ts},{o['data'][0]['Tanggal']},{n},200,{sha},"
                                 f"{datetime.now(timezone.utc).isoformat()}\n")
                    total += 1
                    if total % 50 == 0:
                        print(f"  [ok] {total} file tersimpan... (terakhir {ts} c{c})")
                    break
                except Exception as e:
                    if retry == int(cfg["max_retry"]) - 1:
                        print(f"  [gagal] {ts} c{c}: {e}")
                    else:
                        time.sleep(2 ** retry)
            time.sleep(float(cfg["throttle_detik"]) + random.uniform(0, float(cfg["jitter_detik"])))
    mf.close()
    print(f"\nSelesai. {total} file -> {out}")


if __name__ == "__main__":
    main()