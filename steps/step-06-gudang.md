# P06 — Gudang Time-Series & Upsert

## Tujuan
Menyatukan semua tidy menjadi satu gudang yang tumbuh tanpa duplikasi.

## Input
- `02_data/tidy.parquet`

## Langkah
1. Jalankan `scripts/build_warehouse.py`.
2. Buat tabel fakta `fakta_harga` dengan **PK gabungan**:
   `(tanggal, commodity_id, prov_id, price_type_id)`
3. Buat dimensi: `dim_komoditas`, `dim_wilayah`, `dim_tipe_harga`.
4. **Upsert** (insert-or-replace) agar revisi sumber menimpa data lama.
5. Catat `log_ingest.csv`: run_id, waktu, n_baru, n_update, n_duplikat.
6. Bila nilai berubah untuk PK sama, catat di `log_revisi.csv`.
7. Ekspor `snapshot.parquet` untuk langkah berikutnya.

## Aturan
- Gudang **append + upsert**, tidak pernah truncate otomatis.
- Simpan riwayat revisi.
- **Gudang berperan sebagai pustaka serbaguna** — EDA & permintaan ad-hoc membaca dari sini.

## Output
- `02_data/warehouse.db`, `snapshot.parquet`, `log_ingest.csv`, `log_revisi.csv`

## Kriteria selesai
- `COUNT(*)` berhasil dan tidak ada duplikat PK.