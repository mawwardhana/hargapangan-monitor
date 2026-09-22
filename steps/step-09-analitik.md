# P09 — Analitik Historis & Saat Ini

## Tujuan
Mengubah gudang menjadi temuan bermakna, untuk **historis** dan **kondisi terkini**.

## Input
- `02_data/warehouse.db`, `snapshot.parquet`, `08_qa-report.csv`

## Langkah
1. Filter hanya seri **LULUS** / **PERINGATAN**.
2. Hitung metrik per seri (lihat `references/metode-analitik.md`):
   - **Tren** — slope regresi + % perubahan
   - **Volatilitas** — CV, rolling std 7/30
   - **Musiman** — indeks bulanan
   - **Disparitas** — rasio max/min, CV antarprovinsi
   - **Momentum** — MA7 vs MA30
   - **Era struktural** — deteksi breakpoint
3. **Snapshot terkini**: harga terbaru per komoditas-provinsi + perubahan vs hari sebelumnya.
4. **Pola 2 kelompok**: bandingkan disparitas komoditas diatur (HET) vs hortikultura.
5. **Pola wilayah**: identifikasi provinsi termurah/termahal yang konsisten.
6. Simpan `09_analitik.csv` + `09_snapshot.csv`.
7. Buat visual: garis tren 3 komoditas utama, bar disparitas antarprovinsi.
8. Simpan `.mermaid` + `.html` untuk tiap visual.

## Output
- `09_analitik.csv`, `09_snapshot.csv`, `09_tren.*`, `09_disparitas.*`

## Kriteria selesai
- Setiap metrik punya definisi operasional & angka dapat direproduksi.