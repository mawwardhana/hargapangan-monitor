# P12 — Dashboard & Laporan

## Tujuan
Menyajikan hasil siap-lihat dan siap-bagi.

## Input
- Output P08–P11

## Langkah
1. Jalankan `scripts/render_dashboard.py`.
2. Bangun `12_dashboard.html`:
   - **Kartu ringkasan** — harga terbaru, perubahan vs kemarin, jumlah alert kritis, **status freshness + lag publikasi**
   - **Chart.js** — garis tren multi-komoditas, bar disparitas antarprovinsi
   - **Tabel** alert aktif + prediksi N hari
   - **Daftar** wilayah termahal/termurah
   - Data chart dari JSON yang bisa diedit ulang
3. Sertakan **Mermaid xychart-beta** untuk grafik ringan di chat/laporan.
4. Susun `12_laporan.md` (lihat `references/template-output.md`): ringkasan eksekutif, temuan, alert, prakiraan, keterbatasan, provenance.
5. (Opsional) ekspor `12_laporan.html` untuk cetak/screenshot.

## Format Output Prioritas
- `.txt` — naratif/laporan
- `.csv` — tabulasi data
- `.png` — visualisasi (via screenshot HTML)
- Tambahan: `.md`, `.mermaid`, `.json`, `.html`

## Output
- `12_dashboard.html`, `12_laporan.md`, `12_laporan.html` (opsional)

## Kriteria selesai
- Dashboard terbuka tanpa error, semua chart terisi data nyata, laporan menyebut sumber + tanggal pengambilan + lag publikasi.