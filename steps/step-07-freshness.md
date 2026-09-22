# P07 — Freshness & Update Otomatis

## Tujuan
Menjamin data **selalu mutakhir**: tahu kapan server merilis data baru, dan menarik hanya yang belum ada.

## Input
- `config.yaml`, `02_data/warehouse.db`

## Langkah
1. Jalankan `scripts/check_freshness.py`.
2. **Probe**: minta tanggal hari ini -> baca `Tanggal` dari respons = `rilis_terakhir`.
3. **Bandingkan** dengan `max(tanggal)` di gudang = `max_gudang`.
4. Hitung **lag publikasi** = `hari_ini - rilis_terakhir`.
5. Tentukan aksi:
   - `SUDAH_TERBARU` — `rilis_terakhir == max_gudang`
   - `UPDATE_TERSEDIA` — ada tanggal di antaranya -> tarik
   - `GAGAL_PROBE` — endpoint tidak merespons
6. Tulis `07_freshness.json` (lihat `references/template-output.md`).
7. Jalankan update inkremental: tarik hanya hari kerja yang belum ada.

## Horizon 2 — Update Berkala (Selamanya)

Ini yang membuat sistem "hidup". Cukup **5 request/hari** (5 komoditas × 1 hari) = **6 detik**.

## Aturan
- Setiap run update **wajib** melewati pemeriksaan ini lebih dulu.
- Catat `lag_hari` sebagai metrik pemantauan sendiri.
- Otomatiskan via Windows Task Scheduler (`schtasks`) pada `jam_update`.
- Tambahkan **lock file** agar tidak tumpang tindih.
- Sediakan mode `--dry-run`.

## Output
- `07_freshness.json`, `log/run_<timestamp>.log`

## Kriteria selesai
- `07_freshness.json` berisi status + daftar tanggal yang perlu ditarik.
- Satu kali update inkremental sukses.