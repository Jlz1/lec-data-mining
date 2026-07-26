# Phase 3 — Association Rule Mining: Penjelasan per Cell

Dokumen ini menjelaskan notebook [`3-association-rule-mining.ipynb`](../notebooks/3-association-rule-mining.ipynb)
**cell per cell** (hanya cell yang berisi kode). Dataset: HMDA 2022 Public LAR
(data pengajuan kredit rumah di AS), ±99.994 baris, 80 kolom.

**Alur besar:** data mentah → ubah jadi item biner 0/1 (one-hot kategorikal + binning
numerik) → Apriori → frequent itemsets → association_rules (Support/Confidence/Lift) →
filter (lift, tautologi, diversity) → 10 rule terbaik → interpretasi bisnis → simpan ke `reports/`.

---

## Cell [1] — Load data

```python
df = pd.read_csv("../data/processed_dataset.csv", low_memory=False)
```

- Membaca dataset hasil Phase 1 (sudah bersih).
- `SAMPLE_SIZE = None` → memakai **seluruh** baris (99.994). Opsi sampling acak
  (`random_state=42`) hanya aktif kalau `SAMPLE_SIZE` diisi angka — saat ini mati,
  sehingga pipeline **deterministik** (run berapa kali pun hasilnya sama).
- Output: jumlah baris & kolom + `df.head()`.

---

## Cell [3] — Penyiapan item (membuat "keranjang" biner)

Inti pembentukan item 0/1 untuk Apriori. Tiga jenis kolom diperlakukan berbeda:

1. **Kolom yang sudah biner** (prefix `derived_sex_`, `loan_type_`, `loan_purpose_`,
   `purchaser_type_`, `income_bracket_`, `loan_size_`, dst) → dipaksa jadi 0/1
   (`to_numeric` → `fillna(0)` → `clip(0,1)`).
2. **Kolom kategorikal** (`state_code`, `lien_status`, `occupancy_type`,
   `debt_to_income_ratio`, dll) → `pd.get_dummies` (one-hot).
   - `cap_categories(...)` membatasi kolom *high-cardinality* (`state_code`,
     `derived_loan_product_type`, `derived_dwelling_category`) ke **top-10 + "other"**
     agar jumlah item tidak meledak.
   - Nilai sentinel (`8888`, `9999`) dan kosong → di-mapping ke `"missing"`.
3. **Kolom numerik kontinu** → **DI-BINNING BERBASIS DOMAIN** (`pd.cut` dengan batas
   standar industri KPR) lalu di-one-hot. **Ini pemenuhan requirement "discretize
   continuous variables".**

**Kenapa domain binning, bukan qcut otomatis?** Versi lama memakai `pd.qcut` dengan jumlah
bin dipilih otomatis lewat CV. Hasilnya batas kuantil yang **arbitrer dan tidak bisa
diinterpretasikan**: income terbelah di 71/127 (ribu USD), LTV di 82.976, dan `loan_term`
kolaps total — 74% data bernilai persis 360 bulan (KPR 30 tahun) sehingga satu bin berisi
72% observasi dan bin `(1, 300]` mencampur tenor 1 bulan dengan 25 tahun. CV mengukur
*keseimbangan ukuran bin*, bukan *kebermaknaan batasnya* — metrik yang salah untuk
association rule mining yang butuh item yang bisa dibaca.

**Batas domain yang dipakai (`DOMAIN_BINS`):**

| Kolom | Bins | Dasar |
|---|---|---|
| `loan_term` | ≤15thn / 15–25thn / 30thn (standar) / >30thn | Tenor adalah variabel **produk**: 95% data di nilai standar 120/180/240/300/360/480 bulan |
| `interest_rate` | ≤3% / 3–5% / 5–7% / >7% | Kisaran pasar KPR AS 2022; bunga ≤0% (354 baris) = invalid → missing |
| `combined_loan_to_value_ratio` | ≤80% / 80–95% / 95–100% / 100–120% | 80% = ambang DP konvensional (bebas PMI); 95–100% = program DP minimal (FHA/VA/USDA); >100% = utang melebihi nilai rumah; >120% (256 baris, max 27.778%!) = error input → missing |
| `income`, `loan_amount` | **tidak di-bin** | Bracket domain Phase 1 (`income_bracket_*`, `loan_size_*`) sudah dipakai sebagai item biner — versi lama mem-bin keduanya lalu membuangnya sebagai redundan (kerja sia-sia) |

Distribusi hasil: loan_term 12,9/10,3/75,0/1,8% · interest_rate 11,0/48,6/33,9/6,5% ·
CLTV 65,2/20,6/11,8/2,5%. Bin dominan 75% pada `loan_term` memang mencerminkan realitas
pasar (KPR 30 tahun adalah produk standar) — bedanya dengan qcut, sekarang batasnya jujur
dan setiap bin punya arti.

**Pembersihan item:**
- Item yang selalu 0 dibuang.
- Item **struktural/sentinel** (`missing`, `exempt`, `_1111`, `_8888`, `_9999`) dibuang
  (7 kolom). Alasannya: co-occurrence item ini bersifat **definisional/regulatif** (mis.
  properti multifamily SELALU tanpa conforming limit), bukan pola perilaku nasabah — kalau
  dibiarkan menghasilkan lift "palsu" tinggi yang mendominasi & membuat aturan trivial.
- Hasil akhir: **135 item**.

---

## Cell [4] — Studi statistik jumlah bin (justifikasi)

Studi formal sebagai **pembanding metodologis** (pipeline final tetap memakai
`DOMAIN_BINS` dari Cell [3]):

- **Estimator jumlah bin**: Freedman-Diaconis (`_fd_bins`), Sturges (`_sturges_bins`),
  akar kuadrat (`_sqrt_bins`). Untuk data besar & skewed ini ketiganya menghasilkan angka
  besar (>10) sehingga tersaring — seleksi efektif jatuh ke pool `{3,4,5}`.
- **Penilai = CV** antar bin (`_evaluate_bins`, `_pick_best`).
- Menghitung juga `skew` dan `outlier_share` per kolom (mengonfirmasi data sangat
  berekor panjang: income skew ≈ 276, loan_amount skew ≈ 53).
- Output: `summary_df` (tabel ringkas per kolom).

---

## Cell [5] — Perbandingan 3 teknik binning untuk data outlier

Membandingkan tiga cara menangani outlier saat binning:

- `qcut` — equal-frequency (tiap bin jumlah baris sama).
- `winsor_cut` — potong ekstrem persentil 1–99% lalu equal-width.
- `log_cut` — transformasi log lalu equal-width.

Dinilai dengan CV rata-rata: `qcut` terkecil (CV ≈ 0,197 vs winsor 0,999 vs log 1,174)
karena bekerja pada **peringkat/posisi** data, bukan nilai absolut. **Tapi angka rata-rata
ini menyembunyikan kegagalan `loan_term`**: CV qcut untuk loan_term sendiri = 0,92 (bin
terbesar 72.359 baris ≈ 72% data). Kesimpulan yang jujur: qcut unggul secara keseimbangan
statistik, namun **kalah secara interpretabilitas** — inilah alasan pipeline final memakai
domain binning. Output: `compare_df` + tabel rekomendasi per kolom.

---

## Cell [7] — Gambar 1: distribusi bin per kolom

Membuat `3-binning_per_column.png`: untuk `income` & `loan_amount` (kolom paling
ber-outlier), menampilkan histogram distribusi asli + hasil 3 teknik binning
(qcut/winsor/log) lengkap dengan nilai CV per teknik. Visual membuktikan qcut paling merata.

---

## Cell [8] — Gambar 2: heatmap CV + rata-rata per teknik

Membuat `3-binning_cv_comparison.png`: (kiri) heatmap CV teknik × kolom (merah = tidak
merata, hijau = merata); (kanan) bar rata-rata CV per teknik dengan pemenang (qcut) ditandai
"★ TERBAIK". Ini ringkasan visual dari justifikasi pemilihan teknik.

---

## Cell [10] — Apriori & filtering

Mesin penambangan aturan.

**Parameter:** `MIN_SUPPORT=0.001`, `MIN_CONF=0.6`, `MIN_LIFT=1.5`, `MAX_LEN=3`,
`MAX_ITEMSETS=150`.

> **Catatan dua ambang lift (sering disalahpahami sebagai inkonsistensi):**
> `MIN_LIFT=1.5` adalah ambang **penambangan** di Cell [10] — menghasilkan 4.016 rule
> yang tersimpan lengkap di `3-association-rules.csv`. Sementara `lift ≥ 2.0` adalah
> ambang **seleksi pelaporan** di Cell [12] (`select_report_rules`) — dipakai untuk
> memilih 10 rule terkuat yang ditampilkan di laporan & dashboard. Jadi keduanya benar
> dan berlaku di tahap berbeda, bukan angka yang saling bertentangan.

**Langkah:**
1. Filter item ke yang `support ≥ MIN_SUPPORT`, batasi maksimal 150 item teratas (hemat
   memori), konversi ke `bool` → 124 item.
2. `apriori(...)` → **88.680 frequent itemsets** (max_len=3, low_memory).
3. `association_rules(metric="confidence", min_threshold=0.6)` → menghitung
   **Support, Confidence, Lift** tiap rule.
4. `apply_filters(...)` — filter "meaningful & non-trivial":
   - `lift ≥ 1.5`,
   - konsekuen dibatasi **1 item** (mudah dibaca),
   - **penghapusan tautologi** via `CORRELATED_GROUPS` (rule yang kedua sisinya dari
     atribut yang secara definisi sama, mis. `loan_type` ↔ `derived_loan_product_type`,
     `derived_dwelling_category` ↔ `construction_method`/`total_units`,
     `reverse_mortgage` ↔ `above_62` [syarat legal HECM], atau antar-atribut usia
     applicant/co-applicant) → **1.697 rule terhapus**. Tiap item diatribusikan ke
     **satu prefix terpanjang** supaya `applicant_age_above_62_*` tidak salah match
     dengan prefix `applicant_age_` (bug versi lama yang diam-diam membuang SEMUA
     rule ber-`above_62`).
5. **Relaksasi otomatis**: kalau rule < 10, confidence diturunkan bertahap (0,55 → 0,50 →
   0,45) agar deliverable minimal 10 rule selalu tercapai (tidak terpicu di sini).

**Hasil: 4.016 rule lolos filter.**

---

## Cell [12] — Seleksi 10 rule untuk laporan + ekspor

`select_report_rules(...)` memilih 10 rule terbaik:
- ambang `lift ≥ 2.0`,
- urut `lift → confidence → support`,
- **diversity caps** per kelompok konsekuen (`CONSEQUENT_GROUPS`) agar 10 rule tidak
  seragam (mis. tidak semua tentang "loan_product"),
- buang antecedent duplikat (`core_antecedent_key`); bucket ordinal (DTI, bin LTV) dikolaps
  supaya rule yang cuma beda rentang tidak tampil dobel.

**Ekspor:**
- `3-association-rules.csv` — seluruh 4.016 rule (ranked).
- `3-association-rules.txt` — ringkasan top-10.

(`safe_write_*` otomatis menulis ke file alternatif kalau file aslinya sedang terkunci.)

---

## Cell [13] — Append analisis binning ke report

Menambahkan bagian **"ANALISIS TEKNIK BINNING UNTUK DATA OUTLIER"** ke
`3-association-rules.txt`: karakteristik data (skew, outlier share), perbandingan CV
3 teknik **beserta masalah masing-masing**, lalu kesimpulan jujur: qcut menang CV tapi
batasnya tidak bermakna & rusak di `loan_term` → keputusan final = **domain binning**,
lengkap dengan daftar batas domain + distribusi aktual tiap bin. Ini menjelaskan keputusan
diskretisasi secara tertulis untuk pembaca laporan.

---

## Cell [14] — Interpretasi bisnis per aturan (Top 10)

Pemenuhan deliverable **"business commentary"**.
- `CODE_MEANING` & `BIN_LABELS` menerjemahkan kode HMDA → bahasa awam (mis.
  `loan_type_3` = "pinjaman VA", `occupancy_type_3` = "properti investasi",
  `purchaser_type_2` = "dijual ke Ginnie Mae").
- `humanize_items(...)` mengubah antecedent/consequent jadi kalimat. Label bin domain
  sudah bahasa manusia dari sononya (mis. `loan_term_bin_30thn (KPR standar)` →
  "tenor 30thn (KPR standar)") — tidak perlu lagi parser interval.
- `business_note(...)` memberi komentar bisnis spesifik per pola (segmen entry-level rumah
  manufactured, multifamily = investasi, VA ↔ Ginnie Mae, USDA = LTV tinggi, dll).
- Hasil di-append ke `3-association-rules.txt` bagian **"INTERPRETASI BISNIS PER ATURAN"**.

---

## File output Phase 3
- `reports/3-association-rules.csv` — seluruh rule terfilter (ranked).
- `reports/3-association-rules.txt` — top-10 + analisis binning + interpretasi bisnis.
- `reports/3-binning_per_column.png`, `reports/3-binning_cv_comparison.png` — visual binning.
