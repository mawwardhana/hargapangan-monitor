# P03 — Uji Endpoint & Parameter

## Tujuan
Memetakan respons tiap kombinasi parameter yang akan dipakai.

## Input
- `config.yaml`, `02_api-contract.json`

## Langkah
1. Untuk setiap komoditas di config, kirim 1 request uji (tanggal hari ini).
2. Catat: HTTP status, jumlah baris, apakah `Provinsi`/`Nilai` terisi.
3. Uji juga `provId` spesifik bila config memakai provinsi tertentu.
4. Identifikasi **lag publikasi**: selisih tanggal diminta vs `Tanggal` diterima.
5. Simpan `03_uji-endpoint.csv`: endpoint, parameter, status, n_record, tanggal_rilis, catatan.

## Aturan
- Throttle >= 1,2 dtk antar-request.
- Bila ada komoditas yang kosong, tandai dan **jangan** ikutkan di koleksi.

## Output
- `03_uji-endpoint.csv`

## Kriteria selesai
- Semua komoditas di config punya status OK atau ditandai gagal.