# Kontrak API — bi.go.id/hargapangan (PIHPPS Nasional)

> **Status:** TERVERIFIKASI pada 21–22 Sep 2026. Dokumen hidup — perbarui bila endpoint berubah.

## Identitas Sumber

**PIHPPS Nasional** — Pusat Informasi Harga Pangan Strategis Nasional
<https://www.bi.go.id/hargapangan>

## Endpoint Utama (SNAPSHOT)

```
GET https://www.bi.go.id/hargapangan/WebSite/Home/GetGridData1
```

Mengembalikan **1 tanggal x 1 komoditas x semua provinsi** = 33–35 baris.

### Header WAJIB

Tanpa ketiga header ini, server membalas **kosong**.

| Header | Nilai |
|---|---|
| `User-Agent` | browser wajar, mis. `Mozilla/5.0 (Windows NT 10.0; Win64; x64) ... Chrome/125.0 Safari/537.36` |
| `X-Requested-With` | `XMLHttpRequest` |
| `Referer` | `https://www.bi.go.id/hargapangan` |

### Parameter `GetGridData1`

| nama | nilai | catatan |
|---|---|---|
| `tanggal` | `Sep 21, 2026` | URL-encoded: `Sep%2021%2C%202026`. Format `MMM DD, YYYY` |
| `commodity` | `1`–`10` | lihat peta di bawah |
| `priceType` | `1` | 1 Tradisional, 2 Modern, 3 Grosir, 4 Produsen |
| `isPasokan` | `1` | mode harga |
| `jenis` | `1` atau `2` | hanya urutan; `1` = ascending harga |
| `periode` | `1` | harian |
| `provId` | `0` atau ID provinsi | `0` = semua (33–35 baris); ID = 1 baris |
| `_` | timestamp ms | anti-cache |

### Peta ID Komoditas (TERVERIFIKASI 22 Sep 2026)

| id | komoditas | nasional 21/09 (Rp/kg) | disparitas |
|---|---|---|---|
| 1 | Beras | 16.400 | 1,44× |
| 2 | Daging Ayam | 30.150 | — |
| 3 | Daging Sapi | 148.800 | 1,41× |
| 4 | Telur Ayam | 30.000 | 1,65× |
| 5 | Bawang Merah | 37.450 | 2,58× |
| 6 | Bawang Putih | 39.050 | 2,07× |
| 7 | Cabai Merah | 66.450 | **3,85×** |
| 8 | Cabai Rawit | 84.000 | 3,12× |
| 9 | Minyak Goreng | 23.000 | 1,38× |
| 10 | Gula Pasir | 19.650 | 1,38× |
| 11+ | (kosong) | — | — |

### Contoh URL lengkap

```
https://www.bi.go.id/hargapangan/WebSite/Home/GetGridData1?tanggal=Sep%2021%2C%202026&commodity=1&priceType=1&isPasokan=1&jenis=1&periode=1&provId=0&_=1789946726663
```

## Skema Respons

```json
{
  "data": [
    {
      "ProvID": 18,
      "Provinsi": "Nusa Tenggara Barat",
      "Tanggal": "18 Sep 26",
      "Komoditas": "Beras",
      "Nilai": 13900,
      "NilaiDiff": "Rp0",
      "SemuaProvinsi": 16400,
      "Kelompok": 5,
      "stdDev": 3100,
      "Percentage": 0,
      "SemuaPercentage": 0,
      "stdDevPercentage": null,
      "TanggalLast": "17 Sep 26",
      "TanggalInflasi": "18 Sep / 17 Sep",
      "show": true
    }
  ]
}
```

### Kamus field

| field | arti |
|---|---|
| `ProvID` | ID provinsi |
| `Provinsi` | nama provinsi |
| `Tanggal` | tanggal data (format `DD MMM YY`) |
| `Komoditas` | nama komoditas |
| `Nilai` | harga (Rp) |
| `NilaiDiff` | selisih vs hari sebelumnya, string `Rp0` / `Rp100` / `-Rp150` |
| `SemuaProvinsi` | **rata-rata nasional** (sudah dihitung server) |
| `Kelompok` | kelompok harga 1–5 (1 tertinggi, 5 terendah) |
| `stdDev` | simpangan baku antarprovinsi (sudah dihitung server) |
| `Percentage` | % perubahan provinsi vs hari sebelumnya |
| `SemuaPercentage` | % perubahan nasional |
| `TanggalLast` | tanggal data sebelumnya |
| `TanggalInflasi` | label periode perbandingan |
| `show` | flag tampil |

> **Bonus:** `SemuaProvinsi`, `stdDev`, `Kelompok`, `Percentage` sudah dihitung server → pakai untuk **validasi silang**, bukan dihitung ulang.

## Perilaku FRESHNESS (kunci "selalu mutakhir")

- Minta tanggal **hari ini** atau **masa depan** → server membalas **tanggal rilis terakhir**.
- Contoh: minta `Sep 21` → dapat `18 Sep 26`; minta `Sep 22` → tetap `18 Sep 26`.
- Selisih `diminta - dirilis` = **lag publikasi** (contoh: 3 hari).

## Pola Weekend

| tahun | Sabtu/Minggu |
|---|---|
| 2026 | fallback ke **Jumat** sebelumnya (`Tanggal` = Jumat) |
| 2023 | **KOSONG** (`data: []`) |

**Implikasi:** simpan `tanggal_balas` (tanggal dari respons) untuk deduplikasi. Tarik **hari kerja saja** (Sen–Jum) — hemat ~28% request.

## Backfill (terbukti bekerja)

| diminta | diterima |
|---|---|
| Sep 18 2025 | 18 Sep 25 |
| Sep 18 2024 | 18 Sep 24 |
| Sep 18 2023 | 18 Sep 23 |
| Sep 18 2020 | 18 Sep 20 (34 provinsi lengkap) |
| Jan 01 2019 | 01 Jan 19 (2 baris saja) |

## Coverage Historis (hasil dense probe)

- Data tersedia **sejak Januari 2018** (8,5 tahun)
- Frekuensi **harian** (hari kerja)
- Hit rate aktual **~95%+**
- Bulan konsisten kosong: **Mei, Agustus, Oktober, Desember** (karena rilis bergeser, bukan hilang)

## Anomali Provinsi Baru (Kepri ProvID 5)

Pola konsisten di 9/9 komoditas:
```json
{ "ProvID": 5, "Provinsi": "Kepulauan Riau",
  "NilaiDiff": null, "Kelompok": 6,
  "TanggalLast": null, "TanggalInflasi": null }
```

**Arti:** provinsi baru masuk survei — belum punya pembanding. **Bukan error.**
**Tindakan:** tandai `is_provinsi_baru = true`.

## Endpoint Pendukung

| endpoint | isi |
|---|---|
| `GetCommoditiesTree` | hierarki komoditas (`TreeID`, `ParentID`) |
| `GetProvinceAll?filter=["province_id",0]` | daftar provinsi |
| `GetRegencyAll?province_id=N` | kota/kabupaten |
| `GetType?filter=["price_type_id",1]` | jenis harga |
| `GetHistogramData?tanggal=...&commodity=...` | distribusi |
| `GetChartData?tempId=...&comName=...&skip=0&take=20` | deret waktu (terbatas mode DTD) |
| `GetGridData` | daftar survey (1=Harga, 2=Pasokan, 5=SPH) |

## Estimasi Volume Backfill

| skenario | komoditas | periode | hari kerja | request | durasi @1,8 dtk |
|---|---|---|---|---|---|
| Ringan | 5 | 2023–2026 | ~780 | ~3.900 | **~2 jam** |
| Sedang | 7 | 2020–2026 | ~1.400 | ~9.800 | ~5 jam |
| Penuh | 10 | 2018–2026 | ~1.800 | ~18.000 | ~9 jam |

## Catatan Etika

Ini API internal situs publik, **bukan** API resmi ber-SLA. Selalu: throttle ≥ 1,2 dtk + jitter, cache lokal, hentikan bila 403/429 berulang, dan simpan hasil ke disk.