# P10 — Prediksi & Backtest (ADAPTIF)

## Tujuan
Menghasilkan prakiraan harga yang **jujur** — dan tetap bekerja meski data masih pendek.

## Input
- `09_analitik.csv`, `02_data/warehouse.db`

## Langkah
1. Jalankan `scripts/forecast.py <db> <horizon>` (default horizon 7 hari).
2. Skrip melakukan **forward-fill** tanggal kosong agar seri kontinu.
3. Model dipilih otomatis sesuai panjang data (lihat `references/metode-prediksi.md`):
   - n = 1 : `single` (nilai itu; label "sangat indikatif")
   - n = 2 : `naive`, `mean`
   - n >= 3 : + moving average adaptif
   - n >= 5 : + `trend` (regresi linear)
   - n >= 7 : + `ma7`
   - n >= 14 & MAPE <= 15 : label "ok"
4. **Rolling-origin backtest** adaptif (maks 5 jendela terakhir).
5. Hitung MAE, RMSE, MAPE per model per seri.
6. Pilih model terbaik: MAPE terkecil, MAE sebagai pemecah seri.
7. Hasilkan prakiraan + **interval** dari sebaran residual (lower/upper).
8. Simpan `10_prediksi.csv` dan `10_backtest.csv`.

## Aturan
- **Jangan** laporkan prediksi tanpa backtest.
- `MAPE > 15%` **atau** `n < 14` -> label "indikatif, bukan presisi".
- `n = 1` -> label "sangat indikatif (1 titik)".
- Untuk data pendek, **naive/mean lebih dipercaya** daripada model kompleks.
- Jangan ekstrapolasi > 2x panjang data latih.

## Status uji (21 Sep 2026)
- Data uji: 206 baris, 67 seri
- Hasil: **476 baris prediksi**, 176 baris backtest, **0 seri dilewati**
- Sebaran model terpilih: naive 67, mean 67, ma2 36, trend 4, ma7 2

## Output
- `10_prediksi.csv`, `10_backtest.csv`, `10_prediksi.mermaid`/`.html` (opsional)

## Kriteria selesai
- Setiap seri (n >= 1) menghasilkan prakiraan + metrik error + label keandalan.