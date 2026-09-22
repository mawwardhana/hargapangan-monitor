# Metode Prediksi (ADAPTIF)

## Prinsip

**Tidak ada prediksi tanpa backtest.** Setiap angka prakiraan harus disertai metrik error dari data historis.

## Mode ADAPTIF

Skrip `forecast.py` menyesuaikan model dengan **panjang data yang tersedia**. Tidak ada ambang minimum kaku — seri dengan **≥ 1 titik** sudah bisa diprediksi.

| panjang data (n) | model yang dipakai |
|---|---|
| n = 1 | `single` (nilai itu; label "sangat indikatif") |
| n = 2 | `naive`, `mean` |
| n ≥ 3 | + moving average adaptif (window = min(3, n//3)) |
| n ≥ 5 | + `trend` (regresi linear sederhana) |
| n ≥ 7 | + `ma7` |
| n ≥ 14 & MAPE ≤ 15% | label "ok" |

Model terbaik dipilih otomatis berdasarkan **MAPE terkecil**, lalu MAE sebagai pemecah seri.

## Forward-fill

Tanggal kosong diisi nilai terakhir (**forward-fill**) agar seri kontinu sebelum dihitung.

## Rolling-origin Backtest (Adaptif)

Jumlah jendela menyesuaikan panjang data (maksimal 5 jendela terakhir):

```
start = max(1, n - 5)
untuk k dari start s.d. n-1:
    prediksi = model(data[:k])
    bandingkan dengan data[k]
```

## Metrik Error

```
MAE   = mean(|y - y_hat|)
RMSE  = sqrt(mean((y - y_hat)^2))
MAPE  = mean(|y - y_hat| / y) * 100
sMAPE = mean(2|y - y_hat| / (|y| + |y_hat|)) * 100
```

## Interval Ketidakpastian

Dihitung dari **sebaran residual backtest** (maksimal 5 titik terakhir):

```
spread = mean(|y[k] - prediksi[k]|)
lower  = base - spread
upper  = base + spread
```

## Aturan Keputusan

1. Pilih model dengan **MAPE terkecil + stabil** antar jendela.
2. **MAPE > 15% ATAU n < 14** → tandai "indikatif, bukan presisi".
3. `n = 1` → "sangat indikatif (1 titik)".
4. Selalu sertakan `n_data` di output agar pengguna tahu tingkat keandalan.
5. Jangan ekstrapolasi lebih dari **2x panjang data latih**.
6. Untuk data pendek, prioritaskan **naive/mean** — model kompleks justru menyesatkan.

## Kolom Output `10_prediksi.csv`

| kolom | arti |
|---|---|
| `tanggal_terakhir` | titik data terakhir yang dipakai |
| `commodity_id`, `prov_id` | seri |
| `h` | horizon (1..N hari ke depan) |
| `prediksi` | nilai tengah prakiraan |
| `lower` / `upper` | batas bawah/atas (dari residual) |
| `model` | model terpilih untuk seri ini |
| `n_data` | jumlah titik data historis |
| `mape` | error backtest model terpilih |
| `catatan` | `ok` / `indikatif` / `sangat indikatif` |

## Kolom Output `10_backtest.csv`

| kolom | arti |
|---|---|
| `commodity_id`, `prov_id` | seri |
| `model` | nama model |
| `n_data` | panjang data |
| `mae`, `mape` | metrik error |
| `n_jendela` | jumlah jendela backtest |

## Hasil Uji Nyata (21 Sep 2026)

- Data uji: 206 baris, 67 seri
- Hasil: **476 baris prediksi**, 176 baris backtest, **0 seri dilewati**
- Sebaran model terpilih: naive 67, mean 67, ma2 36, trend 4, ma7 2

## Catatan Dependensi

- Cukup **stdlib** (semua dihitung manual, tanpa numpy).
- Holt-Winters / ARIMA bersifat **opsional** bila `statsmodels` tersedia.