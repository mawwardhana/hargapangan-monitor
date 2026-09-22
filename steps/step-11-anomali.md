# P11 — Anomali & Alert

## Tujuan
Menangkap lonjakan/penurunan harga tidak wajar secepatnya.

## Input
- `02_data/warehouse.db`, `09_analitik.csv`

## Langkah
1. Aturan alert (lihat `references/metode-analitik.md`):
   - **Z-score rolling** `|z| > 3` -> KRITIS
   - **Perubahan harian** `> 5%` -> WASPADA
   - **Bollinger** keluar pita `MA20 ± 2std` -> WASPADA
   - **Deviasi musiman** `> 2x` simpangan -> KRITIS
2. Jalankan deteksi untuk seluruh seri LULUS.
3. Klasifikasi: INFO / WASPADA / KRITIS.
4. **Anti alert-fatigue**: gabungkan alert beruntun seri sama dalam 3 hari.
5. Simpan `11_alert.csv`: tanggal, komoditas, provinsi, nilai, ambang, deviasi, level, pesan.
6. Buat ringkasan alert harian + visual.

## Catatan dari Data

Hanya **Cabai Merah & Cabai Rawit** menunjukkan perubahan harian >5% (Babel +12,97%, DIY +11,17%, Papbar +11,08%, Sulut -9,63%, Jambi -9,29%, Kalteng -8,02%). Komoditas lain nyaris 0,00%.

## Output
- `11_alert.csv`, `11_alert.mermaid`/`.html`

## Kriteria selesai
- Setiap alert punya bukti angka + level + rekomendasi tindak lanjut.