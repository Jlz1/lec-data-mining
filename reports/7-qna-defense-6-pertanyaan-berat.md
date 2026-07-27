# 6 Pertanyaan Berat + Jawaban Lengkap
## Bahan Pertahanan Presentasi — HMDA Mortgage Credit Risk (Kelompok 2 / JOYSM)

Sumber pertanyaan: slide `Data Mining.pdf` (13 halaman).
Sumber jawaban: `reports/1-preprocessing-report.txt`, `2-clustering-report.txt`,
`3-association-rules.txt`, `3-explanation.md`, `4-anomaly-report.txt`,
`5-knowledge-discovery-report.md`, `data/processed_dataset.csv`, dan
`Final Project Details.pdf` (rubrik).

Tiap pertanyaan dirancang menyerang titik **paling rapuh** di slide — bukan
pertanyaan hafalan. Jawabannya ditulis dengan angka yang bisa diverifikasi
langsung ke file repo.

---

# PERTANYAAN 1 — PHASE 1 (Data Understanding & Preprocessing)
### Slide rujukan: hal. 4 "Data Snapshot"

> **Pertanyaan:**
> Slide Anda menulis "Sebelum: 100.000 × 99 kolom → Sesudah: 99.994 × 80 kolom,
> perubahan −6 baris duplikat, −19% kolom". Padahal laporan Anda sendiri
> menyebut **35 kolom dibuang** dari 99 — yang seharusnya menyisakan 64, bukan 80.
> **(a)** Rekonsiliasikan aritmetika 99 → 80 itu langkah demi langkah.
> **(b)** Di kotak "Sesudah Cleaning" Anda menulis *"Tipe data finansial sudah
> numerik"*. Buktikan. Kalau klaim itu ternyata tidak sepenuhnya benar, apa
> **konsekuensi berantainya** ke Fase 2, 3, dan 4 — dan mengapa itu bukan
> kesalahan kosmetik?

## Jawaban

### (a) Rekonsiliasi 99 → 80 kolom

Angka 80 **bukan** hasil pengurangan sederhana. Pipeline Fase 1 melakukan
*drop → create → encode → select*, sehingga jumlah kolom naik-turun:

| Langkah | Operasi | Kolom |
|---|---|---|
| 0 | Sampel awal HMDA 2022 | **99** |
| 1 | Drop 35 kolom (5 data leakage + 3 identifier/temporal + 30 missing >60% + 5 AUS + 14 detail applicant, dihitung sebagai *set union* sehingga overlap tidak dihitung ganda) | 64 |
| 2 | Binning: `income → income_bracket`, `loan_amount → loan_size` (2 kolom baru) | 66 |
| 3 | StandardScaler: `loan_amount_scaled`, `income_scaled`, `property_value_scaled` (3 kolom baru) | 69 |
| 4 | One-hot encoding 8 kolom kategorikal (6 asli + 2 hasil binning) → 8 kolom asli dihapus, **46** kolom biner dibuat | 107 |
| 5 | Feature selection (Pearson r > 0,8 + variance = 0) → buang **27** kolom | **80** |

Verifikasi silang langsung dari header `data/processed_dataset.csv`:
**37 kolom non-one-hot + 43 kolom one-hot = 80.** Rinciannya:
`derived_race_` 9, `purchaser_type_` 11, `loan_purpose_` 6, `derived_ethnicity_` 4,
`income_bracket_` 4, `loan_type_` 4, `loan_size_` 3, `derived_sex_` 2 → 43.

Dari 27 kolom yang dibuang: 3 adalah kolom *scaled* (r = 1,00 dengan aslinya),
1 `property_value`, 20 kolom non-one-hot lain (flag biner nyaris konstan, flag
`observed`, `census_tract`, metadata proses), dan 3 kolom one-hot yang sangat
jarang (`derived_sex_joint`, `derived_sex_sex not available`,
`derived_ethnicity_ethnicity not available`). Karena itu:
46 − 3 = 43 one-hot, dan 69 − 3(scaled) − 1 − 20 − 8(kategorikal asli) = 37 non-one-hot.

**Catatan jujur yang harus kami sampaikan sendiri:** kalimat slide "−19% kolom"
memberi kesan proses ini murni *pengurangan*. Yang sebenarnya terjadi adalah
99 → 64 (pembersihan) → 107 (pengayaan lewat binning + encoding) → 80 (seleksi
redundansi). Slide menyederhanakan tiga tahap jadi satu panah.

### (b) Klaim "tipe data finansial sudah numerik" — **tidak sepenuhnya benar**

Yang benar-benar dipaksa numerik di Fase 1 hanya **tiga** kolom:
`property_value`, `income`, `loan_amount` (`pd.to_numeric(errors='coerce')`).

Empat kolom finansial paling penting justru **tetap bertipe `object`/string**:

| Kolom | Kenapa masih string | Missing di dataset final |
|---|---|---|
| `interest_rate` | bercampur nilai `"Exempt"` | 34.670 (34,7%) |
| `combined_loan_to_value_ratio` (LTV) | bercampur `"Exempt"` | 32.693 (32,7%) |
| `rate_spread` | bercampur `"Exempt"` | 49.232 (49,2%) |
| `debt_to_income_ratio` (DTI) | dilaporkan HMDA sebagai *bucket* (`"20%-<30%"`, `">60%"`) di ekor distribusi, angka persis di tengah | 32.125 (32,1%) |

Total 277.763 sel kosong dari 7.999.520 sel = **3,47%** — bukan 0%. Penyebab
tambahannya: notebook memakai pola `df[col].fillna(x, inplace=True)`
(*chained assignment*). Di pandas 2.0+ dengan Copy-on-Write, pola ini
**tidak mengubah DataFrame asli**; pandas hanya melempar `ChainedAssignmentError`
sebagai peringatan, dan eksekusi tetap lanjut. Jadi imputasi "sudah dijalankan"
tetapi tidak berefek.

**Konsekuensi berantai — dan ini yang membuatnya bukan masalah kosmetik:**

1. **Fase 2 (fatal untuk penamaan cluster).** Seleksi fitur clustering memakai
   `select_dtypes(['int64','float64'])`. Karena keempat kolom di atas bertipe
   `object`, keempatnya **gugur otomatis**. Dari 14 fitur yang akhirnya masuk
   K-Means, tidak satu pun berupa harga kredit atau leverage individual —
   isinya `loan_amount`, `income`, plus 12 variabel geografis-demografis
   (msa/county/tract/kode ras-etnis). Artinya segmen "Premium **Agresif**"
   sebenarnya **tidak pernah melihat** LTV, bunga, atau DTI. Cek langsung ke
   data membuktikan LTV ketiga cluster nyaris identik (75,18% / 73,45% / 72,99%)
   dan bunga juga (4,87% / 4,73% / 4,69%) — jadi label "agresif" hanya sah kalau
   disandarkan pada rasio **pinjaman-ke-pendapatan** (2,39x / 2,47x / 1,53x),
   dan itulah yang kami lakukan di laporan Fase 2 Bagian 4.
2. **Fase 3 (justru terselamatkan).** Apriori butuh item kategorikal, jadi
   Fase 3 mem-*parse* ulang kolom-kolom ini dan mem-bin-nya berbasis domain
   (LTV ≤80% / 80–95% / 95–100% / 100–120%). Karena itu 4 dari 10 rule teratas
   justru berisi LTV dan `interest_rate` — variabel yang absen di Fase 2.
   Ini menjelaskan kenapa Fase 2 dan Fase 3 "melihat" hal berbeda.
3. **Fase 4 (jadi pembanding, bukan duplikat).** Fase 4 membersihkan eksplisit
   kolom finansial sehingga Isolation Forest berjalan di 12 fitur yang
   **memuat** LTV/bunga/DTI. Ruang fitur Fase 4 ≠ ruang fitur Fase 2. Inilah
   alasan teknis sebenarnya kenapa overlap DBSCAN × Isolation Forest hanya 32%
   (lihat Pertanyaan 4) — bukan karena salah satu metode gagal.

**Mitigasi yang sudah dilakukan:** Fase 2 dan Fase 4 melakukan imputasi ulang
independen (`X = df[features].apply(lambda x: x.fillna(x.median()))`) sebelum
data masuk model, jadi **tidak ada NaN yang benar-benar sampai ke algoritma**.
Yang tidak lengkap adalah file `processed_dataset.csv`-nya, bukan input model.

**Perbaikan yang seharusnya:** ganti `inplace=True` menjadi
`df[col] = df[col].fillna(...)`, dan lakukan `pd.to_numeric` pada keempat kolom
finansial **sebelum** feature selection — dengan `"Exempt"` diperlakukan sebagai
kategori terpisah (karena "Exempt" = lembaga pelapor dikecualikan melapor,
bukan data hilang acak / MCAR). Dengan itu, Fase 2 akan menghasilkan segmentasi
risiko kredit sungguhan, bukan segmentasi pendapatan–pinjaman–wilayah.

---

# PERTANYAAN 2 — PHASE 2 (Segmentation via Clustering)
### Slide rujukan: hal. 5 "Choosing K = 3" dan hal. 6 "Three Borrower Personas"

> **Pertanyaan:**
> Angka Anda sendiri melemahkan kesimpulan Anda. Silhouette K=3 = **0,1535**,
> sementara K=5 dan K=6 = **0,1516** — selisihnya **0,0019**, dan itu dihitung
> dari sampel 10.000 baris, bukan populasi. Elbow-nya juga tidak tegas: turun
> 8.640 di K=2→3 lalu 7.883 di K=3→4 — hanya **8,8% lebih kecil**, jauh dari
> "siku". ARI terhadap Ward hanya 0,356. Dengan tiga indikator lemah sekaligus,
> **bagaimana Anda membantah tuduhan bahwa K=3 dipilih karena enak diceritakan
> (tiga persona) dan bukan karena datanya?** Dan pertanyaan susulan: dengan
> LTV ketiga grup praktis sama, atas dasar apa Grup 2 Anda beri label "Agresif"?

## Jawaban

### 1. Kami tidak mengklaim K=3 "terbukti kuat" — kami mengklaim K=3 "terbaik yang tersedia"

Ini pembedaan yang kami pegang sejak laporan Fase 2 Bagian 3.2. Data lengkapnya:

| K | Inertia | Δ Inertia | Silhouette |
|---|---|---|---|
| 1 | ±138.953 | — | — |
| 2 | 124.579 | −14.374 | 0,1405 |
| **3** | **115.939** | **−8.640** | **0,1535 ← tertinggi** |
| 4 | 108.056 | −7.883 | 0,1338 |
| 5 | 100.897 | −7.159 | 0,1516 |
| 6 | 93.347 | −7.550 | 0,1516 |

Nilai 0,15 menurut konvensi Rousseeuw tergolong **struktur lemah–sedang**
(>0,50 baru "kuat"). Kami **tidak** menulis "cluster terpisah sempurna" di
slide mana pun; slide hal. 5 secara eksplisit menyebut *"0,15 = struktur
lemah-sedang, wajar untuk data finansial kontinu — bukan klaim 'terpisah
sempurna'"*. Ini bentuk kejujuran metodologis, bukan kelemahan yang disembunyikan.

### 2. Kenapa selisih 0,0019 tetap bisa dipertahankan

Tiga argumen, berurutan dari yang paling kuat:

**(a) Argumen parsimoni — K=3 dan K=5/6 secara statistik seri, jadi pemenangnya
adalah yang paling sederhana.** Jika K=3 (0,1535) dan K=6 (0,1516) tidak bisa
dibedakan secara statistik, maka menambah 3 cluster lagi **tidak membeli apa-apa**
sambil membayar dengan hilangnya interpretabilitas. Prinsip Occam berlaku:
model paling sederhana yang tidak kalah performanya adalah yang dipilih. Ini
argumen standar, bukan pembelaan *ad hoc*.

**(b) Argumen K=4 sebagai jebakan yang sengaja tidak kami ambil.** Perhatikan
K=4 justru **anjlok** ke 0,1338 — di bawah K=2 sekalipun. Kalau kami hanya
mengejar angka, kami akan pilih K=6. Fakta bahwa kurva silhouette naik-turun
(0,1405 → 0,1535 → 0,1338 → 0,1516) sendiri adalah bukti bahwa **datanya memang
kontinu, bukan bergugus**. Pasar KPR adalah spektrum pendapatan, bukan kotak
terpisah. Silhouette rendah di semua K adalah **temuan tentang datanya**, bukan
kegagalan model.

**(c) Argumen validasi eksternal — cross-tab, bukan angka ARI tunggal.**
ARI 0,356 memang moderat, tapi ARI adalah *satu angka ringkasan* yang menutupi
struktur. Cross-tabulasi K-Means vs Ward (n = 800, seed 42) jauh lebih informatif:

|  | Ward=0 | Ward=1 | Ward=2 |
|---|---|---|---|
| **K-Means=0** (Mass Market) | 277 | 5 | 50 |
| **K-Means=1** (Agresif) | 173 | 6 | 27 |
| **K-Means=2** (HNW Konservatif) | 20 | 0 | **242** |

Baca barisnya: **242 dari 262 anggota Cluster 2 (92%) tetap dikelompokkan
bersama oleh Ward** — algoritma dengan kriteria matematis yang sama sekali
berbeda (penggabungan varians hierarkis vs jarak ke centroid). Batas
"HNW-konservatif vs sisanya" adalah **struktur paling robust dalam data ini**.
Sebaliknya, Cluster 0 dan 1 saling tumpah ke Ward=0. Kesimpulan yang bisa
dipertanggungjawabkan: **data mendukung 2 batas dengan kekuatan berbeda** —
satu tegas (HNW vs non-HNW), satu gradual (mass-market vs agresif). K=3
menangkap keduanya; K=2 akan membuang batas gradual yang tetap punya nilai
bisnis; K=6 akan memecah spektrum kontinu secara sewenang-wenang.

**Jadi jawaban jujurnya:** K=3 dipilih karena (i) silhouette tertinggi meski
tipis, (ii) parsimoni ketika hasilnya seri, dan (iii) satu-satunya nilai K yang
dikonfirmasi oleh algoritma independen lewat cross-tab. Interpretasi bisnis
adalah **tie-breaker terakhir**, bukan alasan utama — dan urutan itu penting.

**Yang seharusnya kami lakukan untuk menutup pertanyaan ini sepenuhnya:**
menjalankan silhouette pada beberapa sampel berbeda (mis. 20× bootstrap 10.000
baris) untuk mendapat *confidence interval*. Kalau CI K=3 dan K=6 bertumpang
tindih — dan kemungkinan besar iya — maka klaim "K=3 tertinggi" harus turun
menjadi "K=3 tidak kalah dari kandidat mana pun". Ini keterbatasan yang kami akui.

### 3. Kenapa Grup 2 disebut "Agresif" padahal LTV-nya sama

Karena label itu **tidak** bersandar pada LTV, dan kami menyatakannya eksplisit
di laporan Fase 2 Bagian 4:

| Cluster | Populasi | Income (mean aktual) | Loan (mean aktual) | **Loan/Income** | LTV | Bunga |
|---|---|---|---|---|---|---|
| 0 Mass Market | 42.579 (42,58%) | $107.483 | $256.726 | 2,39x | 75,18% | 4,87% |
| 1 Premium Agresif | 25.336 (25,34%) | $152.332 | $375.773 | **2,47x** | 73,45% | 4,73% |
| 2 HNW Konservatif | 32.079 (32,08%) | $207.565 | $317.120 | **1,53x** | 72,99% | 4,69% |

Rentang LTV hanya ~2,2 poin persen — dan Cluster 0 justru tertinggi. Karena itu
laporan kami menulis hitam di atas putih: *"LTV BUKAN variabel yang membedakan
ketiga segmen, dan laporan ini TIDAK mengklaim demikian."* Pembeda satu-satunya
adalah **kelipatan pinjaman terhadap pendapatan tahunan**: Cluster 2 meminjam
1,53x, sekitar **38% lebih hemat** dari dua cluster lain.

Konsekuensi yang juga kami batasi: rendahnya Loan/Income Cluster 2 **tidak**
berarti mereka menyetor uang muka lebih besar (LTV mereka sama). Penjelasan yang
konsisten dengan data: mereka **membeli properti yang lebih murah relatif
kemampuannya**. Membedakan kedua hipotesis itu butuh data aset/tabungan yang
tidak ada di HMDA.

---

# PERTANYAAN 3 — PHASE 3 (Association Rule Mining)
### Slide rujukan: hal. 7 "Association Rules"

> **Pertanyaan:**
> Tiga hal di slide ini bermasalah sekaligus.
> **(a)** Aturan #10 di slide Anda **identik kata per kata** dengan aturan #9
> (keduanya "Kredit Veteran berbunga rendah → Ginnie Mae"). Rubrik mensyaratkan
> **10 rule non-trivial**. Berarti Anda hanya menyajikan 9. Rule ke-10 yang
> sebenarnya apa, dan kenapa hilang?
> **(b)** Aturan #3 punya **confidence = 1,000**: "multifamily → occupancy
> investasi". Itu bukan pola perilaku, itu **definisi**. Anda mengklaim sudah
> membuang tautologi lewat `CORRELATED_GROUPS` — kenapa yang ini lolos, dan
> apakah lift 13,51 itu penemuan atau artefak?
> **(c)** Aturan #1 punya lift 38,02 tapi **support hanya 0,002 (±200 baris)**
> dan **confidence 0,608**. Slide Anda menulis "**hampir pasti**". Pertahankan
> pilihan kata itu, atau tarik.

## Jawaban

### (a) Ya — slide hal. 7 salah, dan ini kesalahan kami

Aturan #10 yang benar, sesuai `reports/3-association-rules.txt`:

> **JIKA** `debt_to_income_ratio > 60%` **DAN** rumah manufactured (1–4 unit)
> **MAKA** tenor 15–25 tahun
> (support = 0,004 · confidence = 0,807 · **lift = 8,09**)

Interpretasi bisnisnya: kredit rumah pabrikan umumnya bertenor lebih pendek dari
30 tahun standar — plafonnya kecil dan sebagian berbentuk *chattel loan* (kredit
barang bergerak, bukan KPR beragun tanah), sehingga tenor mengikuti umur ekonomis
unit, bukan umur tanah. DTI >60% memperkuat pola ini: nasabah dengan beban utang
sangat tinggi diarahkan ke produk bertenor pendek berplafon kecil.

Aturan ini justru **paling penting secara risiko** dari seluruh top-10 karena ia
satu-satunya yang menautkan **DTI ekstrem** dengan tipe properti — dan ia hilang
dari slide. Deliverable "10 rule" tetap terpenuhi di file `.txt` dan `.csv`
(4.016 rule lengkap), tapi **slide harus diperbaiki** sebelum presentasi.

### (b) Aturan #3 memang tautologi lunak — dan kami membelanya sebagai *validasi*, bukan sebagai *penemuan*

Fakta teknisnya: `derived_dwelling_category = multifamily:site-built` →
`occupancy_type_3` (investasi) dengan confidence **1,000** (bukan 0,99 — persis
semua baris). Confidence sempurna adalah **tanda diagnostik** bahwa relasinya
struktural, bukan perilaku. Filter `CORRELATED_GROUPS` kami memang menghapus
1.697 rule tautologis, tapi grup yang terdaftar adalah pasangan **atribut yang
secara definisi sama** (`loan_type` ↔ `derived_loan_product_type`,
`derived_dwelling_category` ↔ `construction_method`/`total_units`,
`reverse_mortgage` ↔ `applicant_age_above_62`). Pasangan
`dwelling_category` ↔ `occupancy_type` **tidak** terdaftar karena secara
skema HMDA keduanya field independen — properti 5+ unit *secara hukum* boleh
owner-occupied (pemilik tinggal di salah satu unit). Jadi filter kami tidak
salah secara logika skema; yang terjadi adalah **realitas pasar** membuat
kombinasi itu nol di sampel 99.994 baris ini.

**Posisi jujur yang kami ambil:** aturan #3 sebaiknya **tidak** dihitung sebagai
"penemuan pola tersembunyi". Nilainya adalah sebagai **sanity check** — ia
membuktikan pipeline Apriori kami mengembalikan relasi yang memang benar, jadi
lift 38x pada aturan #1 tidak bisa dituduh sekadar bug. Kalau penguji menuntut
10 rule yang seluruhnya non-trivial, aturan #3 layak diganti dengan rule
berikutnya dari 4.016 rule di `3-association-rules.csv` yang confidence-nya
< 1,00. Perbaikan konkret: tambahkan
`("derived_dwelling_category_multifamily", "occupancy_type_3")` ke
`CORRELATED_GROUPS`, lalu jalankan ulang `select_report_rules`.

Catatan tambahan yang harus kami akui: aturan #5 dan #6 punya **antecedent yang
tumpang tindih** dengan #3 (keduanya berawal dari `multifamily:site-built`), jadi
3 dari 10 slot laporan sebenarnya bercerita tentang segmen yang sama. `diversity
caps` kami bekerja pada *consequent group*, bukan pada *antecedent*. Itu celah
desain yang nyata.

### (c) "Hampir pasti" untuk confidence 0,608 — **kami tarik**

Angka aturan #1: support 0,002 · confidence **0,608** · lift **38,02**.
Yang benar secara statistik: *"6 dari 10 pinjaman kedua yang dijual ke pembeli
non-GSE berakhir dengan CLTV di atas nilai rumah — 38x lebih sering dibanding
peluang acak."* Kata "hampir pasti" hanya sah untuk confidence ≥ 0,90.
Redaksi slide yang benar: **"mayoritas (61%)"**, dengan lift 38x disebut
terpisah sebagai ukuran kekuatan asosiasi.

Dua hal yang perlu dijelaskan agar tidak terdengar seperti kami sekadar mengalah:

**Kenapa lift 38x bisa muncul dari confidence 61%?** Karena `lift =
confidence / support(consequent)`. Bin `CLTV 100–120%` hanya menempati **2,5%**
populasi. Jadi 0,608 / 0,016 ≈ 38. Lift tinggi **bukan** karena aturannya pasti,
tapi karena konsekuennya **langka**. Ini justru inti nilainya: kami menemukan
kondisi yang melipatgandakan peluang kejadian langka × 38 — persis jenis sinyal
yang berguna untuk *early warning* kredit, dan persis jenis sinyal yang **hilang**
kalau kami memakai min_support konvensional 1%.

**Pertahanan min_support = 0,001.** Ambang 1% pada 99.994 baris menuntut ±1.000
transaksi per pola. Produk yang paling berisiko di portofolio KPR — second
mortgage/piggyback, rumah manufactured, VA jumbo, multifamily — semuanya
berpopulasi **di bawah 1%**. Memakai ambang 1% berarti secara sistematis membuang
seluruh *rare-but-critical signal* dan hanya menyisakan pola "KPR konvensional
30 tahun" yang sudah diketahui semua orang. Support 0,001 ≈ 100 transaksi masih
di atas ambang stabilitas praktis, dan **lift ≥ 2,0 pada tahap pelaporan**
(berbeda dari `min_lift = 1,5` di tahap penambangan yang menghasilkan 4.016 rule)
yang menyaring pola yang muncul hanya karena dominasi pasar.

**Satu keterbatasan yang tetap harus diakui:** dengan support 0,002 (±200 baris),
interval kepercayaan confidence-nya lebar. Estimasi kasar 95% CI untuk p = 0,608
dengan n ≈ 200 adalah sekitar **0,54–0,68**. Jadi klaim yang aman adalah
"mayoritas", bukan angka presisi 60,8%.

### Koreksi redaksi lain di slide hal. 7 (sebaiknya dibetulkan sebelum presentasi)

| # | Slide menulis | Yang benar |
|---|---|---|
| 01 | "hampir pasti" | "mayoritas (confidence 61%)" |
| 02 | "Pasangan muda (<25 tahun)" | itemnya `co_applicant_age_<25` → **co-applicant**, bukan pemohon utama (laporan Fase 5 sempat menulis "pemohon" — tidak konsisten) |
| 06 | "Pembelian **bangunan baru** ... **selalu** memerlukan Jumbo" | itemnya `loan_purpose_1` = **pembelian rumah** (bukan konstruksi baru), dan confidence 0,707 → "umumnya", bukan "selalu" |
| 07 | "Refinance **tanpa uang muka**" | refinance tidak punya uang muka; LTV 95–100% pada refi berarti **ekuitas tersisa minimal** |
| 10 | duplikat #09 | ganti dengan rule DTI >60% + manufactured → tenor 15–25thn (lift 8,09) |

---

# PERTANYAAN 4 — PHASE 4 (Anomaly & Outlier Detection)
### Slide rujukan: hal. 9 "Anomaly Findings" dan hal. 10 (kotak "Limitation")

> **Pertanyaan:**
> Slide Anda menampilkan 3.320 baris prioritas, lalu memecahnya jadi 179 Data
> Error + 76 Risk Signal + 372 Legitimate = **627 baris, atau 18,9%**. Sisanya
> **2.693 baris (81,1%) tidak terklasifikasi**. Rubrik Fase 4 menuntut
> *"each flagged anomaly classified as data error, rare case, or risk signal
> **with specific supporting evidence**"*. **Bagaimana Anda mempertahankan bahwa
> fase ini bukan "menandai lalu menyerah"?** Susulan: Anda menyebut overlap
> DBSCAN × Isolation Forest hanya **32%** dan menyebutnya "validasi independen".
> Kalau dua metode hanya sepakat 32%, bukankah lebih tepat disimpulkan bahwa
> **68%-nya salah satu metode keliru**? Dan kalau mengganti `contamination` dari
> 5% ke `'auto'` mengubah total anomali dari 5,00% ke 7,64%, angka mana yang
> Anda minta stakeholder percayai?

## Jawaban

### 1. Struktur temuan Fase 4 (agar angkanya tidak tertukar)

| Lapis | Definisi | Jumlah | % populasi |
|---|---|---|---|
| Tersentuh ≥1 metode | IQR **atau** Z-score **atau** Isolation Forest | 12.217 | 12,22% |
| **Prioritas investigasi** | tier *Confirmed* (≥2 metode) + *High Confidence* | **3.320** | 3,32% |
| — *Confirmed* | ≥2 metode sepakat | 3.237 | 3,24% |
| — *High Confidence* | ≥2 metode **DAN** cocok dengan noise DBSCAN Fase 2 | **83** | 0,08% |
| Suspected (1 metode) | tidak masuk prioritas | 8.897 | 8,90% |
| Normal | — | 87.777 | 87,78% |

Perhatikan: 3.320 bukan 12.217. Fase ini sudah **menyaring 73%** dari kandidat
anomali sebelum sampai ke tipologi.

### 2. Soal 81,1% "Unclassified" — kami membelanya, bukan meminta maaf

**Tiga argumen:**

**(a) Ini konsekuensi desain dari tipologi berbasis aturan yang ketat.** Ketiga
kategori kami didefinisikan dengan batas *falsifiable*, bukan label bebas:

- **Data Error (179)** — pelanggaran batas fisik/logis: usia bangunan negatif,
  LTV > 150% tanpa struktur piggyback yang wajar, bunga ≤ 0%, tenor > 480 bulan,
  income = 0 dengan pinjaman disetujui.
- **Potential Risk Signal (76)** — income ≤ Q1 populasi **DAN** loan ≥ Q3
  **DAN** (LTV ≥ 95% **atau** DTI ≥ 50%); atau `rate_spread ≥ 5`
  (indikasi *higher-priced mortgage* / HOEPA-adjacent).
- **Rare Legitimate (372)** — income ≥ Q3 **DAN** LTV ≤ 60% **DAN** loan ≥ Q3.

Alternatifnya adalah melonggarkan definisi sampai semua 3.320 baris "masuk
kotak". Itu akan menaikkan angka klasifikasi jadi 100% dan **menurunkan nilai
bisnisnya jadi nol**, karena 76 baris Risk Signal yang benar-benar berbahaya
akan tenggelam di antara ribuan false positive. Kami memilih **presisi di atas
cakupan**, dan itu keputusan sadar.

**(b) "Unclassified" bukan berarti "tidak diinvestigasi" — ia adalah kategori
temuan tersendiri.** Rekomendasinya spesifik: *watchlist audit manual per-kasus
oleh underwriter, diprioritaskan dari tier High Confidence*. Nilai fase ini
adalah **menyempitkan 99.994 baris menjadi 3.320 (3,32%) yang layak dilihat
manusia** — pengurangan beban kerja 30x. Klaim bahwa setiap penyimpangan
statistik pasti punya penjelasan bisnis otomatis adalah klaim yang **tidak
jujur**, dan justru itu yang dilarang rubrik.

**(c) Bukti bahwa 2.693 baris itu bukan sampah acak:** hasil penyilangan Fase 5
menunjukkan kategori "Perlu Tinjauan Manual" **menumpuk secara sistematis** di
Grup 2 — 49,0% dari 2.693 baris, padahal Grup 2 hanya 25,3% populasi
(**konsentrasi 1,93x**, tertinggi di seluruh analisis). Kalau baris-baris ini
noise acak, distribusinya akan mengikuti proporsi populasi. Ia tidak. Jadi
"unclassified" tetap membawa informasi: **ia menunjuk ke Grup 2 sebagai pusat
gravitasi risiko operasional**, dan itu langsung dapat ditindaklanjuti sebagai
alokasi kapasitas tim underwriting.

**Yang seharusnya kami tambahkan** untuk menutup kritik ini sepenuhnya: analisis
*feature contribution* per baris unclassified (mis. SHAP untuk Isolation Forest,
atau sekadar mencatat kolom mana yang paling ekstrem per baris), sehingga tiap
baris watchlist datang dengan alasan "kenapa saya di sini". Itu belum kami
lakukan dan kami akui sebagai gap.

### 3. Overlap 32% — bukan bukti kegagalan, tapi konsekuensi ruang fitur berbeda

Angkanya: DBSCAN Fase 2 menandai **363 noise dari 5.000 sampel (7,26%)**;
116 di antaranya (**32,0%**) juga ditandai Isolation Forest.

Argumennya berpijak pada Pertanyaan 1(b): **kedua metode tidak melihat variabel
yang sama.**

| | DBSCAN (Fase 2) | Isolation Forest (Fase 4) |
|---|---|---|
| Ruang fitur | 14 fitur auto-selected: didominasi geografis-demografis (msa_md, county, tract\_\*, kode ras/etnis) | 12 fitur inti finansial: **termasuk** LTV, interest_rate, DTI, loan_term |
| Yang ditangkap | outlier **struktur wilayah/demografi** | outlier **kombinasi finansial** |
| Sifat | densitas lokal (eps=2,0, min_samples=10) | isolasi rekursif (n_estimators=200) |

Kalau overlap-nya mendekati 100%, itu justru **mencurigakan** — artinya kedua
metode redundan dan cross-reference-nya tidak menambah informasi. Overlap 32%
berarti: 68% anomali finansial **tidak** aneh secara geografis, dan sebaliknya.
Itu dua sudut pandang yang saling melengkapi.

Dan justru karena itu, **83 baris "High Confidence" menjadi bermakna**: baris
yang janggal di **dua ruang fitur yang independen sekaligus**. Kalau kedua metode
memakai fitur yang sama, "kesepakatan" mereka tidak akan membuktikan apa pun.

**Batasan yang kami akui terbuka (dan sudah ada di slide hal. 10):**
DBSCAN dijalankan ulang di Fase 4 hanya pada **sampel 5.000 baris** dengan
parameter identik Fase 2 — jadi angka overlap ini berlaku pada subset tersampel,
bukan sensus 99.994 baris. Alasannya kompleksitas DBSCAN O(N²).

### 4. Sensitivitas hyperparameter — angka mana yang harus dipercaya

Fakta: `contamination = 5%` (tetap) → 5,00% baris ditandai.
`contamination = 'auto'` → **7.642 baris (7,64%)**.

Ini bukan cacat implementasi, ini **sifat matematis** Isolation Forest:
`contamination` adalah *kuantil pemotongan skor*, bukan parameter yang dipelajari
dari data. Menyetel 5% berarti **memerintahkan** model menandai persis 5% —
angka outputnya jadi asumsi Anda sendiri, bukan temuan. `'auto'` memakai ambang
dari paper asli Liu, Ting & Zhou (2008), sehingga jumlahnya ditentukan struktur
data. Kami memilih `'auto'` karena tugas ini **discovery**, bukan pemenuhan
kuota audit.

**Jawaban langsung untuk stakeholder:** jangan percayai angka 7,64% **maupun**
5,00% sebagai "jumlah anomali sebenarnya" — keduanya adalah *setelan sensitivitas*,
bukan pengukuran. Yang **stabil terhadap perubahan hyperparameter** adalah:

1. **Tier *Confirmed* (3.237)** — butuh kesepakatan ≥2 metode, jadi tidak bisa
   digerakkan oleh satu parameter saja.
2. **Tier *High Confidence* (83)** — butuh kesepakatan lintas dua ruang fitur.
3. **179 Data Error** — berbasis batas fisik/logis (LTV > 150%, bunga ≤ 0%),
   **sama sekali tidak bergantung** pada `contamination`. Ini angka yang paling
   bisa dipertanggungjawabkan di seluruh Fase 4.

Itulah alasan slide kami menonjolkan 3.320 dan 83, bukan 7,64%.

---

# PERTANYAAN 5 — PHASE 5 (Visualization & Knowledge Presentation)
### Slide rujukan: hal. 10 "Cross-Phase Synthesis" dan hal. 11 "Dashboard Preview"

> **Pertanyaan:**
> Rubrik Fase 5 punya satu pertanyaan sentral: *"What did we discover that was
> not already obvious from the raw data?"* Slide hal. 10 menjawabnya dengan
> 4 poin. Tapi **poin 1** ("kolom finansial ternyata tersimpan sebagai teks") dan
> **poin 3** ("74% loan_term persis 360 bulan") **bukan pengetahuan bisnis** —
> keduanya bisa ditemukan dalam 5 detik dengan `df.dtypes` dan
> `df['loan_term'].value_counts()`, tanpa clustering, tanpa Apriori, tanpa
> Isolation Forest. Anda mengaku 14 minggu untuk menemukan **metadata Anda sendiri**.
> **Sebutkan temuan yang benar-benar HANYA bisa muncul dari data mining, dan
> tunjukkan mekanisme lintas-fasenya secara konkret** — kalau tidak ada, Fase 5
> Anda gagal menjawab pertanyaan sentralnya.

## Jawaban

### 1. Kami terima premisnya — dua dari empat poin memang bukan penemuan

Poin 1 (dtype = teks) dan poin 3 (74% loan_term = 360) adalah **temuan kualitas
data**, dan penguji benar bahwa keduanya bisa ditemukan dengan satu perintah.
Kami mempertahankannya di slide bukan sebagai "penemuan", melainkan sebagai
**rantai sebab** yang menjelaskan kenapa Fase 2 dan Fase 4 melihat hal berbeda —
tapi framing slide kami memang menempatkannya setara dengan temuan bisnis, dan
itu keliru secara komunikasi. Slide hal. 10 sebaiknya memisahkan dua kategori:
*"apa yang kami pelajari tentang datanya"* vs *"apa yang kami temukan tentang
pasarnya"*.

### 2. Empat temuan yang **secara struktural mustahil** muncul tanpa mining

Kriteria yang kami pakai untuk menyebut sesuatu "hanya bisa dari mining":
**temuan itu memerlukan label yang tidak ada di data mentah**. Cluster ID,
lift, dan tier anomali semuanya *dihasilkan* oleh algoritma — tanpa label itu,
tabulasi apa pun tidak akan menghasilkan angka berikut.

---

#### Temuan A — Paradoks Leverage: yang paling kaya justru paling sedikit meminjam

| | Grup 1 | Grup 2 | Grup 3 |
|---|---|---|---|
| Income | $107.483 | $152.332 | **$207.565 (tertinggi)** |
| Loan | $256.726 | $375.773 | $317.120 |
| **Loan ÷ Income** | 2,39x | **2,47x (tertinggi)** | **1,53x (terendah)** |

**Kenapa tidak terlihat di data mentah:** laporan standar menampilkan
*rata-rata pendapatan* dan *rata-rata pinjaman* sebagai dua angka terpisah.
Rasio antar keduanya **per segmen** hanya ada setelah segmen itu sendiri
dibentuk — dan segmen bukan kolom yang ada di HMDA. Kalau Anda memotong data
dengan kolom yang tersedia (state, loan_type, race), Anda tidak akan pernah
mendapat pembelahan ini karena grup-grup itu terbentuk dari **kombinasi
income × loan × konteks wilayah**, bukan dari satu kolom.

**Kenapa ini membalik asumsi:** intuisi bank adalah "makin kaya nasabah, makin
besar pinjamannya". Data menunjukkan kelipatannya justru **menurun** di segmen
teratas. Implikasi langsung: Grup 3 bukan target produk KPR — mereka target
**wealth management**, karena kapasitas pinjam mereka sengaja tidak dipakai.

---

#### Temuan B — Investor properti multifamily duduk di segmen mass-market, bukan segmen kaya

Menempelkan label cluster Fase 2 ke pola ARM Fase 3:

| Pola ARM | Grup 1 (42,6% pop.) | Grup 2 (25,3%) | Grup 3 (32,1%) |
|---|---|---|---|
| Multifamily / investor (#3,#5,#6) | **74,6% → 1,75x** | 19,1% (0,75x) | 6,4% (0,20x) |
| Jumbo / non-conforming (#4,#5,#6) | 21,7% (0,51x) | 36,2% (1,43x) | 42,1% (1,31x) |
| Rumah manufactured (#2,#10) | 50,9% (1,20x) | 14,2% (0,56x) | 34,9% (1,09x) |
| VA / Veteran (#4,#7,#9) | 42,0% (0,99x) | 29,5% (1,17x) | 28,5% (0,89x) |

**1,75x adalah konsentrasi tertinggi di seluruh analisis** — dan arahnya
berlawanan dengan dugaan. Penjelasan yang konsisten dengan profil Grup 1
(properti lebih tua, area urban lama): mereka membeli **rumah petak/apartemen
kecil lama untuk disewakan**, bukan gedung mewah.

**Mekanismenya jelas mustahil tanpa dua fase:** ARM memberi *perilaku apa*
(multifamily → investasi), clustering memberi *siapa* (Grup 1). Tidak ada satu
kolom pun di HMDA berisi "segmen nasabah", jadi persilangan ini tidak bisa
dibuat dengan pivot table biasa.

**Implikasi bisnis yang langsung berubah:** produk "KPR Investasi Properti"
**jangan** dipasarkan sebagai produk premium — pasar terbesarnya di segmen
mass-market. Ini keputusan positioning yang akan salah tanpa temuan ini.

Temuan bonus di tabel yang sama: **VA Loan menyebar hampir merata (0,89x–1,17x)
di ketiga segmen** — status veteran **memotong semua kelas ekonomi**. Artinya
program bundling veteran harus punya varian untuk ketiga segmen, bukan
dirancang untuk satu.

---

#### Temuan C — Fase 5 **membantah** hipotesis Fase 4 sendiri

Fase 4 menduga tipologi "Rare Legitimate" (372 baris, "terlalu sehat") identik
dengan Grup 3 HNW. Setelah `row_index` disilangkan ke label cluster:

| Tipologi anomali | Grup 1 | Grup 2 | Grup 3 |
|---|---|---|---|
| Rare Legitimate (372) | 22,3% (0,52x) | **38,7% (1,53x)** | 39,0% (1,22x) |

Hanya **39,0%** yang benar berada di Grup 3. Sebanyak **38,7% justru di Grup 2**
— segmen yang selama ini kami sendiri labeli "agresif/berisiko" — dan dengan
**konsentrasi lebih tinggi** (1,53x vs 1,22x).

**Kenapa ini temuan kelas atas:** ia bukan konfirmasi, ia **falsifikasi**.
Analisis yang hanya mengonfirmasi dugaannya sendiri adalah analisis yang lemah.
Konsekuensi operasionalnya konkret dan mahal: kalau bank menyaring daftar
prospek wealth management **berdasarkan label segmen** (ambil Grup 3 saja),
mereka membuang **hampir separuh pipeline**. Rekomendasi kami karena itu
eksplisit: gunakan langsung 372 baris dari `reports/4-anomalies.csv`
(filter `typology == "Rare Legitimate"`), **lintas segmen**.

---

#### Temuan D — Grup 2 adalah pusat gravitasi anomali, dikonfirmasi dua metode yang tak saling bicara

| Tipologi anomali | Grup 1 | Grup 2 | Grup 3 |
|---|---|---|---|
| Perlu Tinjauan Manual (2.693) | 25,7% (0,60x) | **49,0% → 1,93x** | 25,3% (0,79x) |
| Sinyal Risiko Kredit (76) | 39,5% (0,93x) | **36,8% (1,45x)** | 23,7% (0,74x) |
| Data Error (179) | **56,4% (1,33x)** | 20,1% (0,79x) | 23,5% (0,73x) |

Grup 2 hanya 25,3% populasi tetapi memuat **49% kasus yang perlu diperiksa
manusia**. Bobot argumennya: **dua metode dengan matematika yang sama sekali
berbeda** — K-Means (jarak Euclidean ke centroid, ruang fitur
income–loan–geografis) dan Isolation Forest (isolasi rekursif, ruang fitur
finansial termasuk LTV/DTI) — sampai ke segmen yang **sama** sebagai titik
perhatian. Ini korroborasi independen, bukan satu model mengulang dirinya.
Implikasi: **alokasikan kapasitas underwriting mengikuti Grup 2, jangan dibagi rata.**

Temuan sampingan yang bersifat operasional: **56,4% Data Error ada di Grup 1
(1,33x)**. Ini bukan temuan pasar, ini temuan proses — kontrol input data untuk
pengajuan segmen mass-market kemungkinan paling longgar. Kandidat perbaikan
pertama untuk tim data engineering.

---

### 3. Ringkasan jawaban atas pertanyaan sentral rubrik

> **Yang tidak jelas dari data mentah adalah semua hal yang butuh label buatan
> algoritma.** Data mentah HMDA punya kolom `income`, `loan_amount`,
> `occupancy_type`. Ia **tidak** punya kolom "segmen nasabah", "lift", atau
> "tier anomali". Keempat temuan di atas adalah persilangan antar label buatan
> itu — dan dua di antaranya (Temuan B dan C) **membantah dugaan yang tampak
> masuk akal** di masing-masing fase. Itulah bentuk konkret pengetahuan berlapis:
> clustering memberi **siapa**, ARM memberi **perilaku apa**, deteksi anomali
> memberi **mana yang perlu diperiksa** — dan hanya gabungan ketiganya yang
> menghasilkan arahan tindakan spesifik.

**Batas klaim untuk seluruh bagian ini:** semua angka di atas adalah
**konsentrasi statistik, bukan sebab-akibat**. "Investor multifamily menumpuk di
Grup 1" tidak berarti berada di Grup 1 *menyebabkan* seseorang jadi investor.
Dan karena label cluster Fase 2 dibentuk tanpa variabel harga kredit
(lihat Pertanyaan 1), penyilangan ini membandingkan segmen
"pendapatan–pinjaman–wilayah" dengan pola produk — **bukan** dengan segmen
risiko kredit formal.

---

# PERTANYAAN 6 — KEBUTUHAN INFORMASI STAKEHOLDER
### ⚠️ Ini masuk **PHASE 5 — Visualization and Knowledge Presentation**

**Kenapa Phase 5, bukan Phase 1?** Rubrik `Final Project Details.pdf` menempatkan
kriteria *"Knowledge Report — translates all findings into plain business
language, answers the central discovery question directly and specifically"* dan
*"Dashboard — accessible to a non-technical audience"* seluruhnya di bawah
**Phase 5 (bobot 20%)**, dengan owner **Insight Communicator**. Slide yang
bersangkutan — hal. 8 "Business Interpretation", hal. 11 "Dashboard Preview",
hal. 12 "Strategic Recommendation" — semuanya deliverable Phase 5.

*(Catatan: akar pertanyaannya memang ada di Phase 1 — bagian "Objective" di
slide hal. 3 yang menetapkan 3 pertanyaan bisnis. Tapi kewajiban **memenuhi
kebutuhan informasi stakeholder** dinilai di Phase 5.)*

---

> **Pertanyaan:**
> Slide hal. 8 "Business Interpretation" hanya memuat **tiga judul tanpa satu
> angka pun**: Credit Risk Action, Product Marketing Action, Cross-Selling Action.
> Slide hal. 12 mendaftar **enam rekomendasi strategis** — juga tanpa ukuran
> dampak, tanpa biaya, tanpa pemilik, tanpa jadwal.
> Anggap saya **Chief Risk Officer** dan rekan saya **Head of Retail Banking**.
> Kami harus **menyetujui atau menolak** salah satu dari enam rekomendasi itu
> **besok pagi**.
> **(a)** Informasi apa persisnya yang kami butuhkan yang **tidak ada** di slide Anda?
> **(b)** Dari daftar itu, mana yang **bisa** Anda hitung dari data yang Anda punya,
> dan mana yang **secara fundamental tidak tersedia di HMDA sama sekali**?
> **(c)** Ada satu hambatan yang membuat salah satu rekomendasi Anda **tidak bisa
> dieksekusi sama sekali** dalam bentuk sekarang. Sebutkan.

## Jawaban

### (a) Kerangka kebutuhan informasi stakeholder — 6 blok

Setiap keputusan investasi produk/risiko menuntut enam blok informasi. Slide
kami baru mengisi blok 1 dan sebagian blok 6.

| # | Blok informasi | Pertanyaan yang dijawab | Status di slide kami |
|---|---|---|---|
| 1 | **Ukuran & identitas populasi sasaran** | Berapa nasabah? Siapa persisnya? | ✅ jumlah ada · ❌ identitas tidak ada |
| 2 | **Dampak finansial (ukuran)** | Berapa tambahan pendapatan / kerugian yang dihindari? | ❌ tidak ada |
| 3 | **Biaya & effort implementasi** | Berapa FTE, berapa lama, sistem apa? | ❌ tidak ada |
| 4 | **Risiko & guardrail kepatuhan** | Apa yang bisa salah? Regulasi apa yang tersentuh? | ❌ tidak ada |
| 5 | **Kepemilikan & jadwal** | Siapa PIC? Kapan review? | ❌ tidak ada |
| 6 | **Ukuran keberhasilan & desain validasi** | Bagaimana kami tahu ini berhasil? | ⚠️ implisit |

### Contoh pengisian — Rekomendasi "Layanan Wealth Management Nasabah Crazy Rich" (slide hal. 12)

| Blok | Isi yang dibutuhkan CRO / Head of Retail |
|---|---|
| **1. Populasi** | 372 baris `typology == "Rare Legitimate"` di `reports/4-anomalies.csv` — **lintas segmen**, bukan disaring dari Grup 3 (hanya 39,0% ada di sana). Populasi sekunder: 32.079 anggota Grup 3 (Loan/Income 1,53x). |
| **2. Dampak** | Kapasitas pinjam yang belum terpakai. Grup 3: income $207.565 × 2,4x (kelipatan wajar pasar) = ±$498K potensi, aktual $317K → **selisih ±$181K per nasabah**. Yang kami **belum** punya: berapa % dari selisih itu bisa dikonversi ke AUM, dan berapa fee rate-nya. |
| **3. Biaya** | Jumlah relationship manager, biaya akuisisi per nasabah, integrasi CRM. **Tidak ada di HMDA maupun di analisis kami.** |
| **4. Risiko & kepatuhan** | ⚠️ **Kritis.** `applicant_race_1` dan `applicant_ethnicity_1` **ikut menjadi fitur jarak Euclidean** di K-Means Fase 2. Setiap daftar prospek yang diturunkan dari label cluster karena itu **berpotensi tersentuh ECOA / Fair Lending / Regulation B**. Ini alasan tambahan — di luar alasan statistik di Temuan C — kenapa daftar prospek **harus** diambil dari tipologi anomali (kriteria murni finansial: income ≥ Q3, LTV ≤ 60%, loan ≥ Q3), **bukan** dari label cluster. |
| **5. Kepemilikan** | PIC, target tanggal, gerbang keputusan. Tidak ada di slide. |
| **6. Validasi** | Rekomendasi kami adalah **hipotesis dari data observasional 1 tahun**, bukan hasil eksperimen. Desain yang jujur: A/B test — hubungi 186 dari 372, tahan 186 sebagai kontrol, ukur konversi 90 hari. |

### (b) Mana yang bisa dihitung, mana yang mustahil dari HMDA

**Bisa dihitung sekarang** (data ada di repo):

- Ukuran populasi setiap rekomendasi (372 / 76 / 179 / 2.693 / 42.579 / 25.336 / 32.079).
- Proxy pendapatan bunga tahunan: loan × rata-rata bunga cluster.
  Grup 1 ≈ **$12.502/nasabah** (256.726 × 4,87%) → **±$532 juta portofolio**.
  Grup 2 ≈ **$17.763/nasabah** (375.773 × 4,73%) → **±$450 juta portofolio**.
  **Nuansa yang wajib disampaikan:** Grup 2 unggul **per kepala**, tapi Grup 1
  unggul **per portofolio** karena jumlah nasabahnya 1,7x lipat. Rekomendasi
  yang hanya melihat "nilai per nasabah" akan salah memprioritaskan.
- Alokasi kapasitas underwriting: 49% beban tinjauan manual ada di Grup 2.
- Positioning produk: KPR investasi multifamily → pasar terbesarnya Grup 1 (1,75x).

**Secara fundamental tidak tersedia di HMDA — berapa lama pun kami menganalisis:**

| Yang dibutuhkan | Kenapa tidak ada |
|---|---|
| **Default rate / NPL / tunggakan** | HMDA merekam **pengajuan**, bukan kinerja pinjaman. Semua klaim "risiko lebih rendah/tinggi" di laporan kami adalah **inferensi dari beban utang**, bukan hasil pengukuran gagal bayar. |
| **Aset, tabungan, kekayaan bersih** | Tidak dilaporkan. Inilah sebabnya kami **tidak bisa** membuktikan Grup 3 menyetor DP lebih besar (LTV mereka sama dengan grup lain). |
| **Credit score (FICO)** | Hanya `applicant_credit_score_type` (jenis model skor), bukan nilainya — dan kolom itu pun terbuang di seleksi fitur. |
| **Biaya operasional bank, margin, cost of funds** | Data internal bank, bukan data publik. Tanpa ini, ROI rekomendasi mana pun tidak bisa dihitung. |
| **Perilaku setelah akad** (pelunasan dipercepat, refinance ulang, churn) | Snapshot 1 tahun tanpa pengenal pelanggan yang persisten. |
| **Elastisitas terhadap penawaran** | Butuh eksperimen, bukan data observasional. |

### (c) Hambatan yang membuat satu rekomendasi **tidak bisa dieksekusi**

> **HMDA Public LAR adalah data yang di-de-identifikasi.**

`lei` dan `universal_loan_identifier` sudah kami buang di Fase 1, dan HMDA versi
publik memang **tidak memuat nama, alamat, nomor kontak, atau ID nasabah**. Level
data adalah **pengajuan (application-level)**, bukan pelanggan.

Konsekuensinya langsung menghantam **Rekomendasi 4** di laporan Fase 5:
*"bentuk tim relationship manager khusus yang **proaktif menghubungi** 372
nasabah Profil Konservatif."*

**372 orang itu tidak bisa dihubungi.** Mereka adalah baris anonim di dataset
publik federal. Menghubungi mereka bukan sekadar sulit — secara data
**tidak mungkin**, dan kalaupun mungkin akan menyentuh isu privasi.

**Perumusan ulang yang jujur dan tetap bernilai:** yang dihasilkan proyek ini
**bukan daftar nasabah**, melainkan **spesifikasi aturan penyaringan** yang bisa
dijalankan bank di database internalnya sendiri:

```
Aturan prospek Wealth Management (turunkan ke sistem CRM bank):
    income               >= Q1_populasi ... gunakan Q3 populasi bank
    combined_LTV         <= 60%
    loan_amount          >= Q3 populasi
    JANGAN saring berdasarkan label segmen  (hanya 39% ada di Grup 3)
    JANGAN gunakan variabel ras/etnis       (ECOA / Regulation B)
```

Hal yang sama berlaku untuk Rekomendasi 5 ("sistem peringatan dini"): yang kami
serahkan adalah **ambang deteksi** (income ≤ Q1 **DAN** loan ≥ Q3 **DAN**
(LTV ≥ 95% **atau** DTI ≥ 50%); atau `rate_spread ≥ 5`), bukan daftar nama.

**Ini sebenarnya menaikkan nilai proyek, bukan menurunkannya.** Sebuah daftar
372 nama akan basi dalam sebulan. Sebuah **aturan yang tervalidasi lintas metode**
bisa dijalankan setiap hari terhadap pipeline pengajuan yang masuk. Itulah
deliverable Fase 5 yang sesungguhnya — dan itulah yang seharusnya tertulis di
slide hal. 8 dan hal. 12, menggantikan tiga judul tanpa angka.

---

## Lampiran: Ringkasan koreksi slide yang muncul dari 6 pertanyaan ini

| Slide | Masalah | Perbaikan |
|---|---|---|
| hal. 4 | "Tipe data finansial sudah numerik" — tidak benar untuk interest_rate/LTV/DTI/rate_spread | Ganti jadi "3 kolom inti dipaksa numerik; 4 kolom harga kredit tetap string — konsekuensinya dijelaskan di Fase 2" |
| hal. 4 | "99 → 80 kolom, −19%" menyembunyikan tahap pengayaan | Tampilkan 99 → 64 → 107 → 80 |
| hal. 6 | Label "Premium **Agresif**" bisa disalahpahami sebagai berbasis LTV | Tambahkan catatan kaki: pembeda = Loan/Income, LTV ketiganya ±73–75% |
| hal. 7 #01 | "hampir pasti" untuk confidence 0,608 | "mayoritas (61%), lift 38x" |
| hal. 7 #06 | "bangunan baru" & "selalu" | "pembelian rumah" & "umumnya (71%)" |
| hal. 7 #07 | "tanpa uang muka" untuk refinance | "ekuitas tersisa minimal (LTV 95–100%)" |
| hal. 7 #10 | **duplikat #09** | Ganti: DTI >60% + manufactured → tenor 15–25thn (lift 8,09) |
| hal. 9 | 3 tipologi hanya menutup 18,9% dari 3.320 | Tampilkan eksplisit "2.693 (81,1%) = watchlist audit manual — kategori temuan, bukan kegagalan" |
| hal. 10 | Poin 1 & 3 adalah temuan metadata, disajikan setara temuan bisnis | Pisahkan "tentang datanya" vs "tentang pasarnya" |
| hal. 8 | Tiga judul tanpa angka | Isi tiap judul dengan populasi + dampak + guardrail |
| hal. 12 | 6 rekomendasi tanpa ukuran/pemilik/biaya | Tambahkan kolom: populasi, proxy dampak, PIC, cara validasi |
| hal. 12 | "hubungi 372 nasabah" tidak dapat dieksekusi | Ubah jadi spesifikasi aturan penyaringan untuk CRM internal bank |
