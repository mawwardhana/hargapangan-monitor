# P02 — Kontrak API (inspect network)

## Tujuan
Mengunci kontrak endpoint sebelum menarik data.

## Input
- `config.yaml`

## Langkah
1. Buka `references/api-contract.md` — kontrak sudah terverifikasi (GetGridData1, header, parameter, skema, freshness, peta 10 komoditas, pola weekend, anomali Kepri).
2. Verifikasi endpoint pendukung: `GetProvinceAll`, `GetCommoditiesTree`, `GetType`.
3. Lakukan **uji probe** untuk memastikan kontrak masih berlaku:
   - Kirim 1 request dengan tanggal hari ini.
   - Periksa apakah field `Tanggal`, `Nilai`, `SemuaProvinsi` masih ada.
4. Bila struktur berubah, perbarui `references/api-contract.md` dan catat di log.
5. Ekspor kontrak mesin ke `02_api-contract.json`.

## Aturan
- **Jangan menebak** nama parameter. Hanya catat yang benar-benar terlihat di DevTools atau sudah terverifikasi.
- Header wajib: `User-Agent` browser, `X-Requested-With: XMLHttpRequest`, `Referer: https://www.bi.go.id/hargapangan`. Tanpa ini respons kosong.

## Output
- `02_api-contract.md` (tersalin/terverifikasi)
- `02_api-contract.json`

## Kriteria selesai
- Probe berhasil dan kontrak cocok dengan dokumen referensi.