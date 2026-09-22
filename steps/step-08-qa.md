# P08 — QA & Validasi

## Tujuan
Memastikan gudang layak dianalisis sebelum dipakai untuk kesimpulan.

## Input
- `02_data/warehouse.db`, `snapshot.parquet`

## Langkah
1. Jalankan `scripts/qa_validate.py`.
2. Uji:
   - **Kelengkapan** — jumlah hari unik vs rentang yang diharapkan (deteksi gap)
   - **Missing** — % `nilai` kosong per komoditas/wilayah
   - **Duplikat** — cek PK ganda
   - **Outlier** — IQR (Q1-1.5IQR, Q3+1.5IQR) dan/atau z-score
   - **Kewajaran** — `nilai <= 0` atau satuan tidak konsisten
   - **Konsistensi waktu** — tanggal masa depan / format salah
   - **Validasi silang** — bandingkan `nasional` & `stddev` hitung-ulang dengan nilai server (harus dekat)
   - **Deteksi anomali Kepri** — `is_provinsi_baru=true`, `kelompok=6`
3. Beri **skor kualitas** 0-100 per komoditas-wilayah.
4. Simpan `08_qa-report.csv` + ringkasan `08_qa.html`.
5. Tandai dataset **GAGAL** (mis. kelengkapan < 80%) agar tidak dipakai untuk prediksi.

## Output
- `08_qa-report.csv`, `08_qa.html`

## Kriteria selesai
- Setiap seri punya status LULUS / PERINGATAN / GAGAL + alasan.