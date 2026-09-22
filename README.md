# hargapangan-monitor

**Sistem informasi monitoring & analitik harga bahan pangan** berbasis API publik
[PIHPPS Nasional](https://www.bi.go.id/hargapangan) — Pusat Informasi Harga Pangan
Strategis Nasional.

Skill ini mengubah endpoint JSON internal situs menjadi **big data time-series
dinamis** untuk analisis **historis**, **monitoring**, dan **proyeksi** — dengan
jaminan **data selalu mutakhir**.

---

## Fitur

- 📊 **10 komoditas pangan strategis** (Beras, Daging, Telur, Bawang, Cabai, Minyak, Gula)
- 🗺️ **34 provinsi** per snapshot
- ⏳ **Data harian sejak 2018** (~8 tahun)
- 🔄 **Freshness-first** — server menandai tanggal rilis, sistem tarik hanya yang baru
- 📈 **EDA lengkap** — tren, volatilitas, musiman, disparitas, anomali, proyeksi
- 🔒 **Provenance** — setiap baris menyimpan `source_url`, `endpoint`, `fetched_at`
- 🧩 **Dinamis via `config.yaml`** — parameter tidak dihardcode
- 🌱 **Hidup & tumbuh** — backfill sekali, update berkala selamanya, layani permintaan apa pun

---

## Filosofi

> **Backfill sekali → Update selamanya → Layani apa pun**

Tiga horizon:
1. **H1 Backfill awal** (sekali) — isi fondasi historis
2. **H2 Update berkala** (selamanya) — ~5 request/hari = 6 detik
3. **H3 Ad-hoc** (kapan saja) — query gudang untuk permintaan apa pun

---

## Struktur

```
hargapangan-monitor/
├── SKILL.md              ← wrapper / orkestrator
├── config.yaml           ← parameter per-proyek
├── .gitignore
├── README.md
├── steps/                ← 12 langkah P01–P12
├── references/           ← kontrak API, skema, metode, template
└── scripts/              ← kolektor, normalisasi, gudang, EDA, prediksi
```

### 12 Langkah

| Kode | Aktivitas |
|---|---|
| P01 | Inisiasi & lingkup → `config.yaml` |
| P02 | Kontrak API (inspect network) |
| P03 | Uji endpoint & parameter |
| P04 | Kolektor / backfill JSON |
| P05 | Normalisasi & tidy |
| P06 | Gudang time-series + upsert |
| P07 | **Freshness** & update otomatis |
| P08 | QA & validasi |
| P09 | Analitik historis & saat ini |
| P10 | Prediksi & backtest (adaptif) |
| P11 | Anomali & alert |
| P12 | Dashboard & laporan |

---

## API yang Dipakai

**Base:** `https://www.bi.go.id/hargapangan/WebSite/Home/`

| Endpoint | Fungsi |
|---|---|
| `GetGridData1` | **snapshot** — 1 tanggal × 1 komoditas × semua provinsi |
| `GetCommoditiesTree` | hierarki komoditas |
| `GetProvinceAll` | daftar provinsi |
| `GetRegencyAll?province_id=N` | kota/kabupaten |
| `GetType` | jenis harga (1=Tradisional, 2=Modern, 3=Grosir, 4=Produsen) |
| `GetHistogramData` | distribusi per tanggal |
| `GetChartData?tempId=...` | deret waktu (terbatas mode DTD) |

### Header wajib

```
User-Agent: Mozilla/5.0 ...
X-Requested-With: XMLHttpRequest
Referer: https://www.bi.go.id/hargapangan
```

### Peta 10 Komoditas

| ID | Komoditas | ID | Komoditas |
|---|---|---|---|
| 1 | Beras | 6 | Bawang Putih |
| 2 | Daging Ayam | 7 | Cabai Merah |
| 3 | Daging Sapi | 8 | Cabai Rawit |
| 4 | Telur Ayam | 9 | Minyak Goreng |
| 5 | Bawang Merah | 10 | Gula Pasir |

### Temuan analitik dari data (21 Sep 2026)

| Komoditas | Nasional (Rp/kg) | Disparitas antarwilayah |
|---|---|---|
| Minyak Goreng | 23.000 | 1,38× |
| Gula Pasir | 19.650 | 1,38× |
| Daging Sapi | 148.800 | 1,41× |
| Beras | 16.400 | 1,44× |
| Telur Ayam | 30.000 | 1,65× |
| Bawang Putih | 39.050 | 2,07× |
| Bawang Merah | 37.450 | 2,58× |
| Cabai Rawit | 84.000 | 3,12× |
| Cabai Merah | 66.450 | **3,85×** |

**Pola 2 kelompok:** komoditas diatur (HET) cenderung merata (1,38–1,44×); hortikultura cenderung timpang (2,07–3,85×).

---

## Cara Pakai

### 1. Pasang lewat DeepSeek++

Library → **GitHub** → paste URL repo ini.

### 2. Panggil skill

```
/hargapangan-monitor
```

### 3. Sesuaikan lingkup

Edit `config.yaml`:

```yaml
proyek: analisis-cabai-2024
komoditas: [7, 8]          # Cabai Merah, Cabai Rawit
provinsi: [0]              # semua
horizon:
  tgl_awal: "2023-01-01"
```

### 4. Jalankan pipeline

```bash
# 1. Koleksi / backfill
python scripts/harvest_hargapangan.py --config config.yaml --mode backfill

# 2. Normalisasi
python scripts/normalize_tidy.py 04_raw 05_tidy

# 3. Gudang
python scripts/build_warehouse.py 05_tidy/tidy.csv warehouse.db

# 4. Freshness
python scripts/check_freshness.py warehouse.db

# 5. QA
python scripts/qa_validate.py warehouse.db

# 6. Prediksi
python scripts/forecast.py warehouse.db 7

# 7. Dashboard
python scripts/render_dashboard.py warehouse.db
```

---

## Persyaratan

- **Python 3.10+** (stdlib cukup untuk pipeline inti)
- **Opsional:** `pyyaml` (baca config), `pandas` + `pyarrow` (parquet)
- **MCP aktif** di DeepSeek++ untuk menjalankan skrip

Tanpa dependensi opsional, skrip tetap jalan dengan penurunan kualitas.

---

## Etika & Batasan

- API ini adalah **endpoint internal situs publik**, bukan API resmi ber-SLA.
- Wajib **throttle ≥ 1,2 detik** + jitter, **cache lokal**, dan **berhenti** bila 403/429 berulang.
- Selalu simpan respons mentah — jaring pengaman bila skema berubah.
- Hormati server: jangan paralel masif.

---

## Sumber Data

**PIHPPS Nasional** — Pusat Informasi Harga Pangan Strategis Nasional
<https://www.bi.go.id/hargapangan>

---

## Lisensi

Belum ditetapkan. Tambahkan `LICENSE` bila akan dibagikan publik.