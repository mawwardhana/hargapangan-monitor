# P04 — Kolektor / Backfill

## Tujuan
Menarik snapshot harian secara berulang, sopan, dan tertelusur — sekaligus membangun deret waktu lewat **loop tanggal**.

## Input
- `config.yaml`, `03_uji-endpoint.csv`

## Langkah
1. Jalankan `scripts/harvest_hargapangan.py`.
2. Skrip wajib: header browser (3 header), throttle >= 1,2 dtk + jitter, retry backoff, timeout, dan **cache ke disk**.
3. **Tentukan mode**:
   - `freshness` — probe hari ini, tarik hanya yang belum ada (dipakai run harian).
   - `backfill` — loop tanggal dari `tgl_awal` ke `tgl_akhir`.
4. **Optimasi weekend**: tarik **hari kerja saja** (Sen–Jum). Sabtu/Minggu fallback ke Jumat — flag `is_weekend_fill=true`.
5. Untuk setiap (tanggal x komoditas): simpan respons mentah ke `01_backfill/raw/<tahun>/<tanggal>_c<commodity>.json`.
6. Simpan langsung ke SQLite (upsert) agar bisa resume bila terputus.
7. Tulis `manifest.csv`: file, url, tanggal_diminta, tanggal_rilis, n_baris, http_status, sha256, fetched_at.

## Aturan
- **Idempoten**: kombinasi (tanggal, komoditas) yang sudah ada -> lewati (resume-able).
- Maksimal 2 koneksi bersamaan.
- Hentikan dan laporkan bila 403/429 berulang.

## Output
- `01_backfill/raw/**/*.json`, `01_backfill/manifest.csv`, `02_data/warehouse.db`

## Kriteria selesai
- Manifest lengkap; setiap file punya hash; tanggal_rilis tercatat.
- Estimasi: 5 komoditas × ~780 hari kerja 2023–2026 ≈ 3.900 request ≈ 2 jam.