# Phase 4 — Anomaly and Outlier Detection: Penjelasan per Cell

Dokumen ini menjelaskan notebook [`4-anomaly-and-outlier-detection.ipynb`](../notebooks/4-anomaly-and-outlier-detection.ipynb)
**cell per cell** (hanya cell yang berisi kode). Dataset: `processed_dataset.csv`
(hasil Phase 1), 99.994 baris, 80 kolom.

**Alur besar:** bersihkan kolom finansial yang tersimpan sebagai string (`exempt`,
bucket DTI/usia) → deteksi anomali univariat (IQR, Z-score) → deteksi anomali
struktural multivariat (Isolation Forest) → reproduksi clustering Phase 2 (KMeans
+ DBSCAN) untuk cross-reference → gabungkan jadi tier kepercayaan anomali →
klasifikasi tipologi bisnis (Data Error / Potential Risk Signal / Rare
Legitimate / perlu review manual) → ekspor `reports/4-anomalies.csv` &
`reports/4-anomaly-report.txt`.

---

## Cell [1] — Load data

```python
df = pd.read_csv("../data/processed_dataset.csv", low_memory=False)
```

Memuat dataset hasil Phase 1 yang sama dipakai Phase 2 & 3 (99.994 baris x 80 kolom).

---

## Cell [2] — Pembersihan kolom finansial (exempt & bucket → numerik)

Beberapa kolom finansial (`combined_loan_to_value_ratio`, `interest_rate`,
`rate_spread`, `loan_term`, `total_loan_costs`, `origination_charges`,
`debt_to_income_ratio`, `applicant_age`) tersimpan sebagai **string**, bukan
`int64`/`float64` murni, karena bercampur dengan kategori non-numerik bawaan
skema HMDA:

- **`"exempt"`** → institusi pelapor dikecualikan melaporkan field itu untuk
  baris tersebut (bukan data hilang biasa) → di-map jadi `NaN`.
- **`debt_to_income_ratio`** → HMDA melaporkan DTI sebagai angka persis untuk
  rentang tengah (`"44"`), tapi sebagai *bucket* di ekor distribusi
  (`"<20%"`, `"20%-<30%"`, `"50%-60%"`, `">60%"`) demi privasi pemohon →
  di-map ke titik tengah rentang (mis. `"20%-<30%"` → `25.0`).
- **`applicant_age`** → dilaporkan sebagai kelompok usia (`"25-34"` dst.)
  dengan sentinel `8888` untuk "tidak tersedia" → sentinel di-map jadi `NaN`,
  bucket ke titik tengah.

Hasil: DataFrame `clean` berisi 15 kolom numerik siap pakai. `IF_FEATURES`
(12 kolom) mengecualikan `rate_spread`, `total_loan_costs`, `origination_charges`
dari matriks Isolation Forest karena missing > 50% (imputasi median pada
kolom sesparse itu akan mendominasi sinyal jarak, bukan mencerminkan anomali
sungguhan) — ketiganya tetap dipakai di analisis IQR/Z-score univariat karena
metode itu bekerja per kolom pada subset non-null saja.

---

## Cell [3] — Metode Statistik 1: IQR

Untuk tiap kolom: `lower = Q1 - 1.5*IQR`, `upper = Q3 + 1.5*IQR`; nilai di
luar rentang ditandai outlier. Robust terhadap skew karena berbasis kuantil,
bukan mean/std.

**Guard IQR degenerate:** `loan_term` punya `Q1 = Q3 = 360` (71,9% baris
persis 360 bulan/30 tahun, dicetak sebagai diagnostik saat guard terpicu)
sehingga `IQR = 0`. Tanpa guard, batas `lower == upper == 360` akan menandai
*setiap* pinjaman dengan tenor lain (15/20/40 tahun, dst.) sebagai
"outlier" murni artefak variabel produk yang sangat terpusat, bukan anomali
finansial sungguhan (konsisten dengan temuan Phase 3 tentang `loan_term`).
Kolom dengan `IQR == 0` karena itu dikecualikan dari flagging IQR —
`loan_term` menunjukkan 0,00% outlier IQR di ringkasan akhir dan tidak ikut
mengotori `stat_score`.

---

## Cell [4] — Metode Statistik 2: Z-score + gabungan

`z = (x - mean) / std`; `|z| > 3` ditandai outlier. Dibandingkan berdampingan
dengan IQR untuk mendeteksi **efek masking**: outlier ekstrem sendiri
menggelembungkan `std`, sehingga nilai yang "cukup ekstrem" tidak lolos
ambang 3-sigma. Contoh nyata: `combined_loan_to_value_ratio` (maksimum riil
27.778%!) — IQR menangkap 1,27% baris sebagai outlier, Z-score cuma 0,02%,
karena nilai-nilai ekstrem menarik `std` sedemikian besar sehingga LTV
"hanya" 150-200% tidak lagi terlihat ekstrem secara Z-score. Kolom
percentage/bucket yang sudah dibatasi rentangnya (`debt_to_income_ratio`,
`applicant_age`, `tract_minority_population_percent`) menunjukkan 0% outlier
di kedua metode — konsisten dengan pelajaran Phase 3 bahwa variabel yang
secara alami *bounded*/kategorikal tidak cocok diperlakukan sebagai kontinu
murni.

`stat_flag = iqr_flags | z_flags` (union), lalu `stat_score` = jumlah kolom
yang menandai tiap baris sebagai outlier — dipakai sebagai salah satu sinyal
di tier kepercayaan anomali nanti.

---

## Cell [5] — Visualisasi boxplot 6 kolom finansial utama

Boxplot untuk `loan_amount`, `income`, `combined_loan_to_value_ratio`,
`interest_rate`, `debt_to_income_ratio`, `rate_spread`, dengan garis putus
merah menandai batas IQR. Sumbu-y di-clip ke persentil 0,1–99,5% (bukan
di-drop dari data, hanya dibatasi tampilan) supaya box & whisker tetap
terbaca meski ada ekor sangat ekstrem (mis. income sampai >$1 juta, LTV
sampai 27.778%). `outlier_pct` di judul tetap dihitung dari IQR **asli**
(tidak diclip). Disimpan ke `reports/4-outlier_boxplots.png`.

---

## Cell [6] — Isolation Forest (anomali struktural)

IQR & Z-score bekerja per-kolom (univariat) — tidak bisa menangkap
**kombinasi** nilai yang masing-masing wajar sendiri-sendiri tapi janggal
bersama (mis. income rendah + LTV tinggi + loan besar, walau tak satupun
kolom individual ekstrem). Isolation Forest mengisolasi titik lewat partisi
acak berulang: titik anomali butuh lebih sedikit split untuk terisolasi.

- Fitur: 12 kolom `IF_FEATURES`, di-scale `StandardScaler`, NaN diisi median
  per kolom.
- `contamination=0.05` mengikuti rekomendasi Phase 1 (rentang 5–10%).
- Hasil: 5.000 baris (5,00%) ditandai anomali struktural.

Histogram skor disimpan ke `reports/4-isolation_forest_scores.png`.

---

## Cell [7] — Reproduksi KMeans Phase 2

Phase 2 tidak menyimpan label cluster ke file terpisah, sehingga langkah
clustering-nya **direproduksi persis**: fitur auto-selected yang sama
(`nunique > 5` pada kolom `int64`/`float64`), `random_state=42`, K=3. Karena
seed dan input identik, hasilnya deterministik dan sebanding satu-satu
dengan laporan Phase 2. Jarak Euclidean tiap titik ke centroid cluster
miliknya sendiri dihitung; 5% titik terjauh per cluster ditandai
`kmeans_outlier` — perluasan dari Phase 2 (yang hanya melaporkan populasi per
cluster, bukan outlier struktural di dalamnya).

Lalu DBSCAN Phase 2 (`eps=2.0`, `min_samples=10`, sampel 5.000 baris,
`np.random.seed(42)`) direproduksi ulang pada subset baris yang sama. Hasil:
363 dari 5.000 noise (7,26%) — **cocok persis** dengan angka di laporan
Phase 2, mengonfirmasi reproduksibilitas.

---

## Cell [8] — Tabel anomali komposit & tier kepercayaan

Semua sinyal digabung ke `anomaly_df`: `stat_score`, `if_score`/`if_flag`,
`kmeans_cluster`/`kmeans_outlier`, `dbscan_noise`. Fungsi `assign_tier`
menentukan tingkat kepercayaan tiap baris:

| Tier | Syarat |
|---|---|
| **High Confidence** | IF flag **dan** stat_score≥2 **dan** (kmeans_outlier atau dbscan_noise) |
| **Confirmed (2 metode)** | IF flag **dan** (stat_score≥2 **atau** cross-ref cluster) |
| **Suspected (1 metode)** | IF flag **atau** stat_score≥2 |
| **Normal** | tidak ada yang terpenuhi |

Cross-tab IF-flag vs KMeans-outlier dan IF-flag vs DBSCAN-noise dicetak untuk
mengukur overlap antar metode — inilah pemenuhan requirement "cross-reference
detected anomalies with cluster outliers from Phase 2".

---

## Cell [9] — Visualisasi cross-reference

Scatter `income` vs `loan_amount` (skala log), diwarnai per tier. Titik
"Normal" digambar transparan di belakang agar pola anomali menonjol.
Disimpan ke `reports/4-anomaly_crossref.png`.

---

## Cell [10] — Investigasi tipologi anomali

Setiap baris bertier != "Normal" diperiksa dengan aturan bisnis
(`classify_typology`), prioritas urutan:

1. **Data Error** — pelanggaran batas fisik/logis mustahil: usia bangunan
   negatif, LTV > 150%, suku bunga ≤ 0%, tenor > 480 bulan (>40 tahun, di
   luar produk KPR AS manapun), atau income = 0 dengan pinjaman disetujui.
2. **Potential Risk Signal** — income rendah (≤Q1 populasi) + pinjaman besar
   (≥Q3) + leverage tinggi (LTV≥95% atau DTI≥50%), atau `rate_spread≥5`
   (indikasi *higher-priced mortgage*).
3. **Rare Legitimate** — income tinggi (≥Q3) + LTV rendah (≤60%) + pinjaman
   besar (≥Q3) — profil cocok Cluster 2 Phase 2 ("High-Net-Worth
   Conservative Borrowers").
4. **Unclassified / Manual Review** — anomali nyata secara statistik/
   struktural tapi tidak cocok pola baku manapun; ~84% dari 3.387 baris
   prioritas (tier Confirmed + High Confidence) jatuh di sini — realistis,
   karena tidak semua penyimpangan statistik punya penjelasan otomatis.

---

## Cell [11] — Contoh konkret per tipologi

Menampilkan 5 sampel per kategori tipologi (kolom bisnis relevan saja) untuk
verifikasi manual bahwa aturan klasifikasi masuk akal terhadap data nyata.

---

## Cell [12] — Ekspor `reports/4-anomalies.csv`

Seluruh 10.318 baris bertier != "Normal" diekspor dengan kolom asli (loan
amount, income, LTV, dst.) + skor tiap metode + tier + tipologi, diurutkan
prioritas (High Confidence → Confirmed → Suspected). File ini dimaksudkan
untuk ditindaklanjuti tim underwriting/data engineering secara langsung.

---

## Cell [13] — Ekspor `reports/4-anomaly-report.txt`

Merangkai seluruh temuan (ringkasan eksekutif, metode statistik, Isolation
Forest, cross-reference Phase 2, distribusi tier, tipologi, rekomendasi
bisnis) jadi laporan naratif untuk pembaca non-teknis.

---

## Cell [14] — Ringkasan penutup

Mencetak ringkasan angka akhir (total anomali, prioritas investigasi) dan
daftar file deliverable yang dihasilkan.

---

## Ringkasan Deliverable

| File | Isi |
|---|---|
| `reports/4-anomalies.csv` | 10.318 baris anomali + skor tiap metode + tier + tipologi |
| `reports/4-anomaly-report.txt` | Laporan naratif lengkap (ringkasan eksekutif s/d rekomendasi bisnis) |
| `reports/4-outlier_boxplots.png` | Distribusi & batas IQR — 6 kolom finansial utama |
| `reports/4-isolation_forest_scores.png` | Distribusi skor anomali Isolation Forest |
| `reports/4-anomaly_crossref.png` | Peta income vs loan_amount per tier anomali |

**Angka kunci:** 10.318 baris (10,32%) ditandai anomali oleh minimal satu
metode; 3.387 baris (3,39%) di tier prioritas (Confirmed/High Confidence).
Dari baris prioritas: 4,4% Data Error, 1,6% Potential Risk Signal, 9,8% Rare
Legitimate, 84,2% perlu review manual.
