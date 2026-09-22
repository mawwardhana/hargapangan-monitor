# Metode Analitik

## 1. Tren

**Kemiringan regresi linear** pada `nilai` vs indeks hari:
```
slope = cov(x, y) / var(x)
```
Interpretasi: Rp/hari. Positif = naik.

**Persen perubahan** periode:
```
pct = (nilai_t - nilai_t-n) / nilai_t-n * 100
```

## 2. Volatilitas

**Koefisien variasi (CV):**
```
CV = std(nilai) / mean(nilai)
```
- CV < 5% = stabil
- 5–15% = sedang
- \> 15% = volatil

**Rolling std** 7 dan 30 hari untuk melihat perubahan rezim.

## 3. Musiman

**Indeks musiman bulanan:**
```
IM_bulan = rata2(nilai di bulan itu) / rata2(nilai setahun)
```
- IM > 1,1 = bulan mahal
- IM < 0,9 = bulan murah

## 4. Disparitas antarwilayah

**Rasio disparitas:**
```
D = nilai_max / nilai_min
```

**Koefisien variasi antarprovinsi** (pakai `stdDev`/`SemuaProvinsi` dari server):
```
CV_prov = stdDev / SemuaProvinsi
```

**Identifikasi outlier wilayah**: provinsi di luar `mean ± 1.5 * std`.

### Temuan dari data (21 Sep 2026) — Pola 2 Kelompok

| Kelompok | Komoditas | Disparitas |
|---|---|---|
| **Diatur (HET)** | Minyak Goreng 1,38× · Gula Pasir 1,38× · Daging Sapi 1,41× · Beras 1,44× | rendah |
| **Hortikultura** | Bawang Putih 2,07× · Bawang Merah 2,58× · Cabai Rawit 3,12× · Cabai Merah 3,85× | tinggi |

**Hipotesis:** HET/distribusi terorganisir → harga merata; mudah busuk + distribusi rumit → harga timpang.

### Pola Wilayah Konsisten (semua 10 komoditas)

| Posisi | Provinsi |
|---|---|
| Termurah | Sulawesi Selatan, Jawa Timur, NTB |
| Termahal | Papua, Papua Barat, Maluku Utara |

## 5. Momentum

- MA7 vs MA30 → golden cross (MA7 naik lewat MA30) = sinyal kenaikan
- Perubahan harian (%) dari `Percentage`

## 6. Anomali (dipakai P11)

| metode | rumus | level |
|---|---|---|
| Z-score rolling | `(x - mean_30) / std_30` | \|z\| > 3 = KRITIS |
| Perubahan harian | `abs(nilai_t - nilai_t-1) / nilai_t-1` | > 5% = WASPADA |
| Bollinger | di luar `MA20 ± 2*std20` | keluar pita = WASPADA |
| Deviasi musiman | selisih > 2x simpangan musiman | = KRITIS |

### Temuan volatilitas (21 Sep 2026)

Hanya **Cabai Merah & Cabai Rawit** menunjukkan perubahan harian >5%:

| Provinsi | Perubahan |
|---|---|
| Babel | +12,97% |
| DIY | +11,17% |
| Papua Barat | +11,08% |
| Sulut | −9,63% |
| Jambi | −9,29% |
| Kalteng | −8,02% |

Komoditas lain nyaris tidak bergerak (kebanyakan 0,00%).

## 7. Era Struktural (Tren Jangka Panjang)

**Contoh Beras Nasional:**
| Era | Periode | Karakter |
|---|---|---|
| Stabil | 2018–2022 | Rp11.650–12.050 |
| Lonjakan | 2023 | +15% (12.750 → 14.650) |
| Plateau | 2024–2026 | Rp15.200–16.350 |

**Metode:** deteksi breakpoint via perubahan slope bergulir.

## Rumus Cepat (tanpa numpy)

Semua di atas bisa dihitung dengan `statistics` (stdlib): `mean`, `stdev`, `median`, `quantiles`.