# Skrip hargapangan-monitor

Urutan pemakaian:

```bash
# 1. Koleksi (freshness = harian; backfill = historis)
python harvest_hargapangan.py --mode freshness
python harvest_hargapangan.py --mode backfill

# 2. Normalisasi
python normalize_tidy.py 04_raw 05_tidy

# 3. Gudang
python build_warehouse.py 05_tidy/tidy.csv 06_warehouse.db

# 4. Cek freshness
python check_freshness.py 06_warehouse.db 07_freshness.json

# 5. QA
python qa_validate.py 06_warehouse.db 08_qa-report.csv

# 6. Prediksi
python forecast.py 06_warehouse.db 7

# 7. Dashboard
python render_dashboard.py 06_warehouse.db 12_dashboard.html

# 8. Mermaid -> HTML (screenshot manual)
python render_mermaid.py diagram.mermaid "Judul" diagram
```

## Dependensi

- **Wajib:** Python 3.10+ (stdlib saja cukup: `sqlite3`, `csv`, `json`, `urllib`, `statistics`)
- **Opsional:** `pyyaml` (baca config), `pandas` + `pyarrow` (parquet)

Tanpa dependensi opsional, skrip tetap jalan dengan penurunan kualitas (config default, output CSV).
