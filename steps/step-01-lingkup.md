# P01 — Inisiasi & Lingkup

## Tujuan
Menetapkan lingkup monitoring dan **menuliskannya ke `config.yaml`** — satu-satunya tempat parameter hidup.

## Input
- Permintaan pengguna (komoditas, wilayah, horizon, fitur)

## Langkah
1. Tetapkan **komoditas** dari peta 1-10 (lihat `references/api-contract.md`).
2. Tetapkan **provinsi**: `[0]` untuk nasional, atau daftar ID provinsi.
3. Tetapkan **jenis harga**: 1 Tradisional, 2 Modern, 3 Grosir, 4 Produsen.
4. Tetapkan **horizon**: `rolling` (mengikuti ketersediaan) atau `fixed` + `mundur_hari`.
5. Tetapkan **frekuensi** & jam update.
6. Nyalakan **fitur** yang dibutuhkan (historis, saat_ini, prediksi, anomali).
7. Tulis semua ke `config.yaml` di folder skill.
8. Buat struktur output: `<output_root>/<proyek>/`.

## Output
- `config.yaml` terisi
- `<output_root>/<proyek>/01_lingkup/01_lingkup.md`

## Kriteria selesai
- `config.yaml` valid dan `01_lingkup.md` memuat semua asumsi + batasan.
