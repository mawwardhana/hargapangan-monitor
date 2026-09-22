# P05 — Normalisasi & Tidy

## Tujuan
Mengubah JSON mentah menjadi tabel panjang konsisten sesuai `references/skema-tidy.md`.

## Input
- `01_backfill/raw/**/*.json`, `manifest.csv`

## Langkah
1. Jalankan `scripts/normalize_tidy.py`.
2. Terapkan skema `fakta_harga` (lihat `references/skema-tidy.md`) dengan 18 kolom termasuk: `tanggal_diminta`, `tanggal`, `tanggal_last`, `is_provinsi_baru`, `is_weekend_fill`.
3. Parsing:
   - `Tanggal` `18 Sep 26` -> `2026-09-18`
   - `NilaiDiff` `Rp100` / `-Rp150` -> `100.0` / `-150.0`
   - `Nilai` -> float
4. **Derivasi flag**:
   - `is_provinsi_baru` = true bila `TanggalLast` null (anomali Kepri)
   - `is_weekend_fill` = true bila tanggal ≠ tanggal_balas
5. Tambahkan provenance: `source_url`, `endpoint`, `fetched_at`.
6. Simpan `02_data/tidy.parquet` + `tidy.csv`.

## Aturan
- Jangan buang baris; tandai anomali dengan kolom flag bila perlu.
- Pastikan kolom identik di semua batch.

## Output
- `02_data/tidy.parquet`, `02_data/tidy.csv`

## Kriteria selesai
- Skema kolom konsisten dan tipe data benar.