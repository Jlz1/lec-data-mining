# Rencana Slide Presentasi — HMDA 2022 Data Mining (Phase 1–5)

Disusun dari kondisi repo terbaru (commit `4732751 fix: dashboard`). Semua angka
di bawah sudah dicocokkan ke file sumber, bukan ke draf lama.

---

## A0. Urutan Fisik Deck (13 slide, 10 di antaranya dinilai)

| Posisi fisik | Slide | Phase | Isi inti (angka/aset kunci) | Dinilai? |
|---|---|---|---|---|
| 1 | **Cover** | — | Judul, subjudul ber-angka 99.994, sumber HMDA 2022, identitas mata kuliah | Tidak |
| 2 | **Member Group** | — | Nama + peran per anggota, dipetakan ke phase yang dikerjakan | Tidak |
| 3 | Slide 1 — Context & Central Question | Pengantar (lintas phase) | 99.994 × 80 kolom; pertanyaan sentral "apa yang tidak terlihat dari data mentah?"; 3 lensa analisis | Ya |
| 4 | Slide 2 — Data Snapshot | **Phase 1** — Preprocessing | Tabel before/after (100.000→99.994 baris, 99→80 kolom, 5 leakage→0, −27 redundan); alasan median/ambang 60%; siapa yang diwakili & tidak | Ya |
| 5 | Slide 3 — Bukti Pemilihan K | **Phase 2** — Clustering | Elbow + Silhouette (K=3 → 0,1535 tertinggi); ARI K-Means vs Ward = 0,356; cross-tab 92% stabilitas Grup 3 | Ya |
| 6 | Slide 4 — Profil 3 Segmen | **Phase 2** — Clustering | Scatter PCA 2D + tabel persona: 42.579 / 25.336 / 32.079; loan-to-income 2,39x / 2,47x / 1,53x | Ya |
| 7 | Slide 5 — Business Insight Clustering | **Phase 2** — Clustering | Temuan leverage paradoksal; aksi per segmen; DBSCAN 363 noise (7,26%); disclaimer fitur tanpa LTV/DTI | Ya |
| 8 | Slide 6 — Key Association Rules | **Phase 3** — ARM | Tabel 5 rules teratas (lift 38,0x → 10,7x); justifikasi min-support 0,001 / min-conf 0,6 / min-lift 2,0; alasan domain binning | Ya |
| 9 | Slide 7 — ARM Business Interpretation | **Phase 3** — ARM | Kenapa rule #1 (utang berlapis) penting; VA sebagai ekosistem tertutup; multifamily conf 100%; ceruk usia <25 | Ya |
| 10 | Slide 8 — Anomaly Findings | **Phase 4** — Anomaly Detection | Diagram overlap multi-metode; 12.217 (12,22%) → 3.320 prioritas (3,32%); tabel tipologi 2.693/372/179/76; masking Z-score & guard loan_term | Ya |
| 11 | Slide 9 — Cross-Phase Synthesis + Limitasi | **Phase 2+3+4** disintesis | 4 jawaban pertanyaan sentral; tautan Grup 3 ↔ Rare Legitimate; limitasi (korelasi≠kausalitas, 1 tahun, silhouette 0,154) | Ya |
| 12 | Slide 10 — Dashboard + Rekomendasi | **Phase 5** — Presentation | Screenshot 2–3 tab dari 7 tab Dash; 6 rekomendasi berprioritas dengan tie-in ke slide sumber | Ya |
| 13 | **Thank You / Q&A** | — | 3 angka pengingat (3 segmen · 10 pola · 3.320 kasus) + baris "korelasi, bukan kausalitas" | Tidak |

**Distribusi bobot per phase** (berguna untuk cek keseimbangan deck):
Phase 1 = 1 slide · Phase 2 = 3 slide · Phase 3 = 2 slide · Phase 4 = 1 slide ·
sintesis lintas phase = 2 slide (slide 1 & 9) · Phase 5 = 1 slide.

Phase 2 dapat porsi terbesar karena rubrik menuntut tiga hal terpisah di sana
(justifikasi K, profil cluster, validasi silang metode) — tidak muat dalam satu
slide. Phase 4 hanya 1 slide tapi padat; kalau waktu presentasi longgar, slide
8 adalah kandidat pertama untuk dipecah jadi dua (temuan vs tipologi).

### Cover
Judul + subjudul + identitas mata kuliah. Jangan taruh isi analisis di sini.

- Judul: **Knowledge Discovery di Pasar KPR Amerika 2022**
- Subjudul: *Segmentasi, Pola Tersembunyi, dan Deteksi Anomali dari 99.994
  Pengajuan KPR* — angka ini langsung memberi skala tanpa perlu slide isi.
- Sumber data: HMDA (Home Mortgage Disclosure Act) 2022
- Mata kuliah / CAWU 5 / Data Mining Project / 2026

### Member Group
Nama + peran per anggota. Peran lebih berguna daripada NIM saja, karena
penguji sering bertanya "siapa yang mengerjakan bagian ini?" saat Q&A.
Kontributor repo: Yonami, Jeremy Emmanuel Susilo, Steven Kukilo.
Petakan ke phase yang dikerjakan (Preprocessing / Clustering / ARM /
Anomaly / Dashboard & Presentation) supaya jelas siapa menjawab apa.

### Thank You / Q&A
Jangan dibiarkan kosong — ini slide yang paling lama tampil di layar selama
sesi tanya jawab. Isi minimal:

- "Terima kasih — Pertanyaan?"
- **3 angka pengingat** yang paling ingin kamu tanamkan, mis.
  3 segmen · 10 pola asosiasi · 3.320 kasus prioritas
- Baris kecil: *"Korelasi, bukan kausalitas — seluruh temuan adalah asosiasi
  statistik."* Kalimat ini di layar saat Q&A menjaga kamu dari klaim
  berlebihan ketika ditanya spontan.

---

## A. Audit Struktur 10 Slide (versi awal) vs Rubrik

| Aspek rubrik | Ada di rencana awal? | Catatan |
|---|---|---|
| Context & central question | Ya (slide 1) | Aman |
| Data snapshot + alasan preprocessing | Ya (slide 2) | Perlu tambah "dataset ini mewakili siapa & tidak mewakili siapa" |
| **Bukti pemilihan K (Elbow + Silhouette)** | **TIDAK ADA** | Rubrik menyebut ini *wajib* — bukti "K selection" |
| **Adjusted Rand Index (validasi silang metode)** | **TIDAK ADA** | Rubrik menyebut ARI eksplisit di Corroboration level 4 |
| Cluster profile + persona | Ya (slide 3–4) | Aman |
| ARM rules + interpretasi | Ya (slide 5–6) | Tambahkan justifikasi threshold (min-support/confidence/lift) |
| **Diagram kesepakatan multi-metode anomali** | Setengah (slide 7) | Rubrik minta diagram overlap IQR vs Z vs IF vs DBSCAN, bukan hanya narasi |
| Cross-phase synthesis | Ya (slide 8) | Aman |
| Dashboard | Ya (slide 9) | Dashboard punya 7 tab, jangan cuma 1 screenshot |
| **Limitasi (korelasi ≠ kausalitas, keterwakilan)** | **TIDAK ADA** | Rubrik menyebut ini eksplisit di baris Phase 5 |
| Rekomendasi strategis | Ya (slide 10) | Aman |

**Kesimpulan:** 3 hal wajib rubrik hilang → bukti K, ARI, dan limitasi.
Solusinya bukan menambah slide sampai 13, tapi menyelipkan bukti K + ARI ke
slide clustering, dan menjadikan limitasi bagian dari slide sintesis/penutup.

---

## B. Koreksi Data yang HARUS Dibereskan Sebelum Bikin Slide

Setelah commit `76e4128 fix: perbaiki data cluster`, angka di
`cluster_profile_summary.csv` (yang dipakai dashboard) **berbeda** dari angka di
`2-clustering-report.txt` dan `5-knowledge-discovery-report.md`. Pakai angka CSV
(sumber terbaru), jangan angka report lama.

| Cluster | Report lama (income) | CSV terbaru (income) | Loan amount (CSV) | Loan/Income |
|---|---|---|---|---|
| Grup 1 — Kelas Menengah (42,58%, n=42.579) | $105.580 | **$107.483** | $256.726 | **2,39x** |
| Grup 2 — Peminjam Agresif (25,34%, n=25.336) | $143.800 | **$152.332** | $375.773 | **2,47x** |
| Grup 3 — Konservatif/HNW (32,08%, n=32.079) | $204.680 | **$207.565** | $317.120 | **1,53x** |

> **STATUS: SEMUA 5 POIN DI BAWAH SUDAH DIPERBAIKI.**
> `2-clustering-report.txt`, `5-knowledge-discovery-report.md`, `3-explanation.md`, dan
> `dashboard/app.py` kini memakai angka MEAN AKTUAL dari `cluster_profile_summary.csv`
> sebagai angka utama, narasi leverage sudah berbasis rasio pinjaman-ke-pendapatan
> (bukan LTV), dua ambang lift sudah dijelaskan terpisah, dan urutan rule sudah sama.
> Dashboard juga mendapat grafik pembanding LTV vs loan-to-income di tab Segmentasi.
> Satu temuan tambahan di luar daftar ini ikut diperbaiki: klaim Grup 2 "sumber
> pendapatan bunga terbesar" hanya benar **per nasabah** (~$17.763) — secara **total
> portofolio** Grup 1 lebih besar (~$532jt vs ~$450jt) karena jumlah nasabahnya 1,7x.
> Daftar di bawah dipertahankan sebagai catatan audit.

**Klaim yang harus diubah (penting — ini bisa jadi bahan bantai penguji):**

1. Report Phase 5 bilang Grup 3 punya "LTV sangat rendah, uang muka sangat
   besar". Data aktual: avg LTV Grup 1 = 75,18% / Grup 2 = 73,45% / Grup 3 =
   72,99%. **Nyaris identik.** Bukti leverage rendah Grup 3 bukan LTV,
   melainkan **rasio pinjaman terhadap pendapatan (1,53x vs 2,47x)**. Ganti
   narasinya ke loan-to-income.
2. Klaim Grup 2 "rasio DTI tinggi" tidak diverifikasi di manapun — hapus atau
   ganti jadi "loan-to-income tertinggi (2,47x)".
3. Avg interest rate ketiga cluster juga nyaris sama (4,87 / 4,73 / 4,69) —
   jangan klaim ada perbedaan harga kredit antar segmen.
4. `5-knowledge-discovery-report.md` lampiran menulis `min_lift = 1,5`,
   sedangkan `3-association-rules.txt` menulis `min_lift >= 2,0`. Samakan ke
   **2,0** (itu yang dipakai untuk filter laporan).
5. Urutan rule berbeda antar file: Pola #4 di report Phase 5 (lift 10,72)
   sebenarnya rule ke-7. Rule #4 asli = non-conforming + Ginnie Mae → VA Loan
   (lift 12,53), sesuai dashboard. Samakan urutan ke `3-association-rules.txt`.

**Aset visual yang belum ada** (hanya hidup di dalam notebook, belum diekspor
ke `reports/`): grafik Elbow, Silhouette, dendrogram Ward, scatter PCA cluster.
Yang sudah ada PNG: `3-arm_scatter_plot`, `3-arm_network_graph`,
`3-binning_*`, `4-outlier_boxplots`, `4-isolation_forest_scores`,
`4-anomaly_crossref`. Scatter PCA bisa dibangun ulang dari `pca_clusters.csv`
(3.000 baris sampel, sudah ada kolom `pca_x`, `pca_y`, `cluster_name`).

---

## C. Isi Detail Slide 1–10

### Slide 1 — Konteks & Pertanyaan Sentral
**Visual:** minimal — judul besar + 3 angka kunci.

- Domain: pasar KPR Amerika, data HMDA 2022 (regulator mewajibkan seluruh
  lembaga pemberi KPR melaporkan setiap pengajuan).
- Skala yang dianalisis: **99.994 pengajuan × 80 kolom**, sampel acak
  (seed 42) dari raw HMDA 2022.
- Masalah bisnis: bank memperlakukan pemohon KPR sebagai satu massa homogen;
  laporan agregat standar hanya menampilkan rata-rata.
- **Pertanyaan sentral (benang merah seluruh deck):**
  *"Apa yang kami temukan yang TIDAK terlihat dari data mentah atau laporan
  ringkasan biasa?"*
- Sebut sekilas 3 lensa analisis: segmentasi, pola asosiasi, deteksi anomali.

**Jangan** taruh daftar tools/library di slide ini.

---

### Slide 2 — Phase 1: Data Snapshot
**Visual:** 1 tabel before/after (angka besar, 5 baris saja). Correlation
heatmap hanya kalau kamu benar-benar menjelaskan feature selection dari situ.

| | Sebelum | Sesudah |
|---|---|---|
| Baris | 100.000 | 99.994 (6 duplikat dihapus) |
| Kolom | 99 | 80 (−19%) |
| Kolom data leakage | 5 | 0 |
| Kolom redundan (r > 0,8) | — | −27 |

Teks yang harus keluar dari mulut kamu (bukan semua ditulis di slide):

- **Kenapa 5 kolom dibuang duluan:** `action_taken` + `denial_reason_1–4`
  adalah *outcome* — hanya diketahui SETELAH keputusan kredit. Menyertakannya
  di tugas unsupervised = data leakage.
- **Kenapa ambang missing 60%:** kolom pemohon ke-2/3/4/5 di skema HMDA
  >97% kosong karena mayoritas pengajuan hanya punya 1 pemohon — mengimputasi
  kolom sekosong itu = mengarang data.
- **Kenapa median, bukan mean:** data finansial right-skewed berat.
  Contohnya: income mean $153.575 vs median $95.000, karena ada 162 baris
  income > $2 juta dan satu nilai $1,075 miliar (hampir pasti error entri).
- **Kenapa binning pakai batas industri, bukan quantile:** dijelaskan lebih
  jauh di slide 5, tapi sebut di sini bahwa quantile menang secara CV (0,197
  vs 0,999 vs 1,174) tapi batasnya tidak bisa dibaca sebagai angka bisnis.
- **Dataset ini mewakili siapa:** hanya orang yang benar-benar mengajukan KPR
  ke lembaga pelapor HMDA, tahun 2022 saja. **Tidak mewakili** rumah tangga
  yang tidak pernah mengajukan, dan 2022 adalah tahun kenaikan suku bunga
  agresif The Fed — pola bisa berbeda di tahun lain.

Kejujuran yang menaikkan nilai, bukan menurunkan: sebut bahwa 3,47% sel di
`processed_dataset.csv` masih kosong karena bug chained assignment pandas
Copy-on-Write, **dan** bahwa Phase 2 & 4 melakukan imputasi ulang independen
sebelum model, jadi tidak ada NaN yang masuk ke model manapun.

---

### Slide 3 — Phase 2: Bukti Pemilihan K (SLIDE BARU, WAJIB)
**Visual:** grafik Elbow + Silhouette berdampingan.

| K | Inertia | Silhouette |
|---|---|---|
| 2 | 124.579 | 0,1405 |
| **3** | **115.939** | **0,1535 ← tertinggi** |
| 4 | 108.056 | 0,1338 |
| 5 | 100.897 | 0,1516 |
| 6 | 93.347 | 0,1516 |

Poin bicara:

- Elbow melandai setelah K=3; Silhouette tertinggi juga di K=3.
- **Katakan terus terang:** nilai absolut 0,15 tergolong lemah-sedang
  (konvensi: >0,5 baru struktur kuat). Klaim yang valid bukan "cluster
  terpisah sempurna", melainkan *"K=3 adalah pemisahan relatif terbaik yang
  tersedia dan satu-satunya yang juga masuk akal secara bisnis"*. Pasar KPR
  memang spektrum kontinu, bukan kotak terpisah.
- **Validasi silang metode (ini yang dicari rubrik):** Adjusted Rand Index
  K-Means vs Agglomerative-Ward (k=3, sampel 800 identik) = **0,356** →
  kesepakatan moderat. Cross-tab menunjukkan Cluster 3 (HNW) paling stabil:
  **242 dari 262 anggotanya (92%)** tetap dikelompokkan bersama oleh Ward.
  Batas "kaya-konservatif vs sisanya" = struktur paling robust; batas
  "kelas menengah vs peminjam agresif" nyata tapi gradual.

---

### Slide 4 — Phase 2: Profil 3 Segmen (Persona)
**Visual:** scatter PCA 2D berwarna per cluster (dari `pca_clusters.csv`) +
tabel profil ringkas.

| Persona | Populasi | Avg income | Avg loan | Loan/Income |
|---|---|---|---|---|
| **Grup 1 — Mass Market / Urban** | 42.579 (42,6%) | $107.483 | $256.726 | 2,39x |
| **Grup 2 — Premium Upgraders (Agresif)** | 25.336 (25,3%) | $152.332 | $375.773 | **2,47x** |
| **Grup 3 — High-Net-Worth Konservatif** | 32.079 (32,1%) | $207.565 | $317.120 | **1,53x** |

Pakai nama persona, jangan "Cluster 0/1/2". Ciri tambahan:

- Grup 1: area dengan persentase minoritas lebih tinggi, usia bangunan tua
  (~39,7 tahun) → first-time buyer & pasar KPR standar.
- Grup 2: kawasan paling makmur, bangunan paling baru → upgrade hunian.
- Grup 3: pendapatan tertinggi tapi pinjaman hanya menengah.

**Segmen paling mengejutkan = Grup 3.** Sorot di sini, bukan di slide lain.

---

### Slide 5 — Phase 2: Business Insight & Aksi Awal
**Visual:** minimal, teks dominan (3 kolom = 3 segmen).

- **Temuan kontra-intuitif:** kelompok TERKAYA justru paling SEDIKIT
  berhutang relatif terhadap pendapatan (1,53x), sementara Grup 2 yang
  pendapatannya lebih rendah justru paling agresif (2,47x). Ini membalik
  asumsi "makin kaya makin besar pinjamannya".
- Aksi per segmen:
  - Grup 1 → KPR standar, proses cepat, volume = stabilitas portofolio.
  - Grup 2 → produk premium + monitoring beban utang; sumber pendapatan
    bunga terbesar tapi eksposur leverage tertinggi.
  - Grup 3 → **bukan produk KPR**, tapi wealth management & priority banking;
    probabilitas gagal bayar terendah.
- DBSCAN (eps=2,0, min_samples=10, sampel 5.000) menandai **363 titik noise
  (7,26%)** yang tidak masuk ketiga segmen → jembatan ke slide anomali.

**Disclaimer wajib di slide ini:** fitur pembentuk cluster adalah
loan_amount + income + konteks wilayah, **bukan** interest_rate/LTV/DTI
(keempatnya tersimpan sebagai teks di data sumber sehingga gugur dari filter
dtype numerik). Jadi ini segmentasi *income-loan-geografis*, bukan segmentasi
risiko kredit murni. Kalau penguji tanya "kenapa LTV antar cluster sama?",
jawabannya ada di sini.

---

### Slide 6 — Phase 3: Key Association Rules
**Visual:** ini memang **tabel**, bukan diagram. Opsional tambahkan scatter
support × confidence diwarnai lift (`3-arm_scatter_plot.png`).

Tampilkan 5 rules teratas sebagai kalimat, dengan lift di ujung:

1. **KPR kedua (subordinate lien) + dijual ke pembeli non-GSE → LTV
   100–120%** — conf 0,608, **lift 38,0x**
2. **Co-applicant usia <25 + tenor 15–25 thn → rumah manufactured** —
   conf 0,864, **lift 19,7x**
3. **Hunian multifamily site-built → properti investasi** — conf **1,000**,
   lift 13,5x
4. **Non-conforming + dijual ke Ginnie Mae → pinjaman VA** — conf 0,940,
   lift 12,5x
5. **LTV 95–100% + cash-out refinance → pinjaman VA** — conf 0,804,
   lift 10,7x

**Justifikasi threshold (jangan dilewat, ini bagian rubrik):**

- `min_support = 0,001` (~100 transaksi): pada 100 ribu baris, ambang
  konvensional 1–5% berarti butuh 1.000–5.000 kejadian; segmen kritikal
  seperti second mortgage, manufactured housing, dan VA/jumbo populasinya
  di bawah 1% — akan hilang total.
- `min_confidence = 0,6`: untuk kebijakan underwriting/marketing, bank butuh
  kepastian mayoritas; top rules aktual mencapai 0,70–1,00.
- `min_lift >= 2,0`: menyingkirkan pola yang muncul semata karena dominasi
  pasar (mis. KPR 30 tahun konvensional), sehingga yang tersisa hanya
  hubungan non-obvious.
- **Kenapa domain binning, bukan quantile:** quantile menang CV (0,197)
  tapi memecah income di angka acak 71/127 ribu dan merusak `loan_term`
  (75% data persis 360 bulan → satu bin berisi 72% data). Batas domain
  (LTV 80/95/100%, bunga 3/5/7%, tenor 15/25/30 thn) bisa langsung dibaca
  sebagai keputusan bisnis.

---

### Slide 7 — Phase 3: Business Interpretation
**Visual:** teks dominan. Boleh pakai `3-arm_network_graph.png` kecil.

Jangan ulang tabel — jelaskan **kenapa** rules itu penting:

- **Rule #1 (lift 38x) — jebakan utang berlapis:** CLTV second mortgage
  dihitung gabungan dengan KPR utama, sehingga piggyback/HELOC mudah
  mendorong total utang melewati nilai rumah. Karena tidak lolos syarat
  Fannie/Freddie, pinjaman berisiko ini dijual ke pembeli non-GSE — risiko
  berpindah keluar dari sistem GSE. → peluang: produk konsolidasi utang /
  credit insurance.
- **VA Loan bukan sekadar produk, tapi ekosistem tertutup:** tiga rule
  terpisah (#4, #5, #9) semuanya bermuara ke rantai VA → Ginnie Mae →
  LTV tinggi. Di data mentah, VA hanya satu nilai di satu kolom.
- **Ceruk generasi muda:** usia <25 + tenor menengah → manufactured housing
  dengan confidence 86,4%. Tidak ada laporan standar yang menyorot jalur ini.
- **Non-obvious relationship yang paling layak dipresentasikan:**
  multifamily → occupancy investasi dengan **confidence 100%** — artinya
  kategori "hunian" di HMDA sebenarnya menyembunyikan segmen landlord/investor
  yang perlu produk berbeda total.

---

### Slide 8 — Phase 4: Anomaly Findings
**Visual (wajib):** diagram kesepakatan antar metode — Venn/overlap
IQR vs Z-score vs Isolation Forest vs DBSCAN noise. Dukung dengan
`4-anomaly_crossref.png` (peta income vs loan_amount per tier).

Angka inti:

- Dianalisis: 99.994 baris × 12 fitur numerik inti.
- **12.217 baris (12,22%)** ditandai minimal 1 dari 3 metode.
- **3.320 baris (3,32%)** masuk prioritas: tier Confirmed (2 metode) = 3.237,
  High Confidence (2 metode + cocok outlier cluster Phase 2) = 83.
- Isolation Forest sendiri: 7.642 baris (7,64%), contamination='auto'.
- Overlap IF dengan DBSCAN noise: **32,0%** dari 363 titik noise.

**Tipologi (dari 3.320 prioritas) — ini inti slide:**

| Tipologi | Jumlah | Aksi |
|---|---|---|
| Unclassified / Manual Review | 2.693 (81,1%) | Watchlist audit berkala |
| Rare Legitimate | 372 (11,2%) | **Prospek wealth management** |
| Data Error | 179 (5,4%) | Kembalikan ke tim data engineering |
| Potential Risk Signal | 76 (2,3%) | Manual underwriting review |

Dua poin metodologis yang menunjukkan kamu paham, bukan asal jalankan library:

- **Efek masking Z-score:** di kolom income, IQR menangkap 6,31% outlier
  sementara Z-score hanya 0,01% — outlier ekstrem menggelembungkan standar
  deviasi sehingga menyembunyikan dirinya sendiri. Ini alasan memakai lebih
  dari satu metode.
- **Guard `loan_term`:** IQR-degenerate (Q1=Q3=360 bulan, 74% data). Tanpa
  guard, IQR akan menandai SEMUA tenor 15/20/40 tahun sebagai "anomali" —
  25%+ false positive. Kolom ini dikecualikan dari flagging IQR tapi tetap
  dipakai Isolation Forest (multivariat, tidak bergantung Q1/Q3).
- **Kenapa overlap dengan DBSCAN tidak 100%:** dua ruang fitur berbeda —
  Phase 2 geografis-demografis, Phase 4 finansial. Baris yang tertangkap
  keduanya justru anomali paling meyakinkan.

---

### Slide 9 — Cross-Phase Synthesis + Limitasi
**Visual:** diagram sintesis lintas phase (Phase 2 → 3 → 4 saling menunjuk).

**Jawaban atas pertanyaan sentral slide 1 — 4 temuan:**

1. **Leverage paradoksal.** Kelompok terkaya ($207k) meminjam paling sedikit
   relatif pendapatan (1,53x); Grup 2 ($152k) paling agresif (2,47x).
2. **VA Loan adalah ekosistem, bukan kolom.** Tiga rule independen membentuk
   rantai VA → Ginnie Mae → LTV tinggi, dengan confidence 80–94%.
3. **Generasi muda punya jalur produk tersendiri** (manufactured housing,
   tenor pendek) yang belum digarap.
4. **Anomali menghasilkan prospek, bukan hanya alarm.** 372 dari 3.320 kasus
   prioritas ternyata nasabah "terlalu sehat" — dan profilnya cocok persis
   dengan Grup 3 Phase 2. Dua metode berbeda menunjuk kelompok yang sama.

**Tautan antar phase (ini yang bikin nilai sintesis naik):**
Grup 3 Phase 2 (HNW konservatif) = cluster paling stabil lintas metode
(92% konsisten dengan Ward) = tipologi "Rare Legitimate" Phase 4. Temuan
yang sama muncul dari tiga jalur analisis independen.

**Limitasi (bagian rubrik, jangan dihilangkan):**

- **Korelasi ≠ kausalitas.** "Usia <25 → manufactured housing" (lift 19,7x)
  bukan berarti usia menyebabkan pilihan itu. Semua rekomendasi di slide 10
  adalah **hipotesis yang layak diuji**, bukan kepastian.
- **Snapshot satu tahun.** 2022 = tahun kenaikan suku bunga agresif The Fed.
- **Keterwakilan.** HMDA hanya mencakup yang benar-benar mengajukan KPR.
- **Kekuatan struktur cluster sedang, bukan kuat** (silhouette 0,154,
  ARI 0,356).
- **Kode ras/etnis ikut sebagai fitur jarak Euclidean** walau bersifat
  nominal → nama segmen merujuk profil finansial, **bukan** klasifikasi
  demografis, dan tidak boleh dipakai untuk keputusan yang membedakan
  individu berdasar ras/etnis.
- **Sampling untuk algoritma berat:** DBSCAN 5.000 baris, Hierarchical 800
  baris (kompleksitas O(N²)/O(N³)), seed tetap.

---

### Slide 10 — Dashboard + Rekomendasi Strategis
**Visual:** screenshot dashboard (2–3 tab, bukan hanya satu).

Dashboard Python Dash, 7 tab: Common Information, Segmentation Nasabah,
Visualization ARM, Market Distribution, Anomaly Detection, Strategic
Recommendation, Metodologi & Validitas. Tunjukkan yang interaktif
(scatter PCA & tabel rules), bukan halaman statis.

**Rekomendasi berprioritas — setiap butir tie-in ke slide sumbernya:**

| # | Rekomendasi | Dari slide |
|---|---|---|
| 1 | Tiga jalur produk terpisah: Stabilitas (Grup 1) / Premium + monitoring beban utang (Grup 2) / **Wealth Management, bukan KPR** (Grup 3) | 4–5 |
| 2 | Konversi 372 nasabah "Rare Legitimate" jadi pipeline relationship manager — daftar prospek yang sudah tervalidasi 2 metode | 8 + 9 |
| 3 | Early-warning flag otomatis: LTV >100% + KPR berlapis + DTI >60% | 6 + 8 |
| 4 | Bundle produk Veteran (VA + Ginnie Mae) — ekosistem tertutup dengan confidence 80–94% | 6–7 |
| 5 | Fast-track kredit manufactured housing untuk segmen usia <25 | 6–7 |
| 6 | Audit 179 baris Data Error ke tim data engineering — perbaiki validasi batas di pipeline Phase 1 | 8 |

Tutup dengan mengulang pertanyaan sentral slide 1 dan jawaban satu kalimat.

---

## D. Checklist Sebelum Deck Dianggap Selesai

- [ ] Sinkronkan angka income cluster di `2-clustering-report.txt` &
      `5-knowledge-discovery-report.md` ke `cluster_profile_summary.csv`
- [ ] Ganti klaim "Grup 3 LTV rendah" → "loan-to-income 1,53x"
- [ ] Hapus/ganti klaim "Grup 2 DTI tinggi" (tidak terverifikasi)
- [ ] Samakan `min_lift` (2,0) di semua report
- [ ] Samakan urutan rule #4 antar report & dashboard
- [ ] Ekspor PNG: Elbow, Silhouette, dendrogram Ward, scatter PCA
- [ ] Buat diagram Venn/overlap multi-metode anomali (belum ada)
- [ ] Buat diagram sintesis lintas phase untuk slide 9 (belum ada)
