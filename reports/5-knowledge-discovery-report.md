# Knowledge Discovery Report
## Pasar Kredit Pemilikan Rumah (KPR) Amerika 2022
### HMDA Data Mining Project — Phase 5

**Disusun oleh:** Insight Communicator Team  
**Data Sumber:** Home Mortgage Disclosure Act (HMDA) 2022  
**Total Data Dianalisis:** 99.994 pengajuan KPR  

---

## Bagian 1: Latar Belakang & Pertanyaan Bisnis

Pasar KPR Amerika adalah salah satu pasar keuangan terbesar di dunia. Setiap tahun, jutaan pengajuan kredit diproses oleh ratusan lembaga keuangan. Dari luar, proses ini tampak sederhana: nasabah mengajukan, bank menilai, kredit disetujui atau ditolak.

Namun di balik laporan ringkasan standar yang biasanya disajikan kepada manajemen, terdapat pola-pola perilaku yang tidak terlihat — hubungan tersembunyi antara jenis produk, profil nasabah, dan risiko keuangan — yang hanya bisa ditemukan melalui analisis data secara mendalam.

**Pertanyaan Sentral yang Kami Jawab:**
> *Apa yang kami temukan yang TIDAK sudah jelas dari data mentah atau laporan ringkasan biasa?*

---

## Bagian 2: Metodologi (Versi Non-Teknis)

Kami menggunakan tiga pendekatan analisis yang bekerja secara berlapis:

| Teknik | Analogi Sederhana | Yang Dihasilkan |
|---|---|---|
| **Clustering** | Mengelompokkan nasabah seperti segmentasi pasar | 3 profil nasabah yang berbeda |
| **Association Rules (ARM)** | Menemukan "kalau beli A, biasanya juga beli B" di dunia KPR | 10 pola perilaku tersembunyi |
| **Anomaly Detection** | Menemukan transaksi yang "aneh" di antara puluhan ribu data | 3.301 kasus yang butuh perhatian |

---

## Bagian 3: Temuan Utama

### 3.1 Pasar KPR Terbagi Menjadi 3 Segmen yang Sangat Berbeda

Analisis clustering mengungkap bahwa nasabah KPR **tidak bisa disamaratakan**. Mereka terbagi secara alami menjadi tiga kelompok dengan strategi keuangan yang sangat kontras:

#### Grup 1: Kelas Menengah — Tulang Punggung Pasar (42,6%)
- Pembeli rumah pertama atau kelas menengah tipikal
- Pendapatan rata-rata: **$105.580/tahun**
- Nilai pinjaman: Moderat, proporsional dengan pendapatan
- Ciri khas: Membeli properti yang usianya lebih lama, menghindari risiko berlebihan
- **Nilai Strategis:** Segmen terbesar — menjadi penjamin stabilitas portofolio KPR

#### Grup 2: Peminjam Agresif — Pendorong Pendapatan Bunga (25,3%)
- Profesional berpendapatan tinggi yang memaksimalkan leverage
- Pendapatan rata-rata: **$143.800/tahun**
- Nilai pinjaman rata-rata: **$376.044** — jauh di atas proporsi pendapatannya
- Ciri khas: Membeli rumah baru di kawasan premium, rasio Debt-to-Income tinggi
- **Nilai Strategis:** Sumber pendapatan bunga terbesar, namun berisiko paling tinggi

#### Grup 3: Konservatif / High-Net-Worth — Pelanggan Tersembunyi (32,1%)
- Pendapatan tertinggi namun meminjam jauh di bawah kemampuan
- Pendapatan rata-rata: **$204.680/tahun**
- LTV (Loan-to-Value) sangat rendah — uang muka sangat besar
- Ciri khas: Tidak tergiur memaksimalkan kredit meski sanggup
- **Nilai Strategis:** Risiko gagal bayar (NPL) paling rendah, prospek ideal Wealth Management

> **Yang Tidak Terlihat di Data Mentah:** Berdasarkan data mentah, kita hanya bisa melihat bahwa ada nasabah berpenghasilan tinggi dan rendah. Yang tidak terlihat adalah temuan mengejutkan ini: **kelompok TERKAYA justru yang paling SEDIKIT berhutang**, sementara kelompok kelas menengah ke atas (Grup 2) justru yang paling agresif memaksimalkan utang mereka. Ini membalikkan asumsi umum.

---

### 3.2 Pola Perilaku Tersembunyi dari Association Rules Mining (ARM)

Sistem ARM menganalisis ratusan kombinasi atribut dari 99.994 pengajuan dan menemukan **10 pola asosiasi kuat** yang tidak terlihat di laporan biasa:

#### Pola Terkuat #1 — Jebakan KPR Berlapis (Kekuatan: 38x lebih pasti)
**JIKA** nasabah mengambil KPR kedua (Piggyback/HELOC) dari investor swasta  
**MAKA** total utangnya hampir pasti akan melampaui nilai rumah yang dibeli (LTV > 100%)

> **Analisis Peluang Bisnis:** Tawarkan program konsolidasi utang (Debt Consolidation) dengan suku bunga tetap khusus atau produk asuransi kredit tambahan (credit insurance) untuk melindungi nasabah dan memitigasi risiko kredit macet bagi bank.

#### Pola #2 — Generasi Muda & Properti Ekonomis (Kekuatan: 19,7x lebih pasti)
**JIKA** pemohon berusia di bawah 25 tahun dan mengambil cicilan jangka pendek  
**MAKA** mereka hampir pasti memilih properti Manufactured Housing

> **Analisis Peluang Bisnis:** Luncurkan paket pembiayaan KPR mikro khusus 'Rumah Pertama Generasi Muda' untuk Manufactured Housing dengan uang muka fleksibel dan opsi cicilan progresif guna menarik pasar nasabah pemula (first-time buyers).

#### Pola #3 — Investor Properti Punya Perilaku Khas (Kekuatan: 13,5x lebih pasti)
**JIKA** nasabah membeli properti Multifamily (kos/apartemen)  
**MAKA** dapat dipastikan tujuannya adalah investasi/bisnis sewa, bukan untuk ditinggali

> **Analisis Peluang Bisnis:** Buat produk KPR Investasi Properti Komersial dengan fitur cross-selling asuransi properti sewa dan integrasi layanan pengelolaan kas (cash management) untuk membantu investor/landlord mengelola arus kas sewa mereka.

#### Pola #4 — Ekosistem VA Loan yang Tertutup (Kekuatan: 10,7x lebih pasti)
**JIKA** nasabah melakukan Cash-out Refinance dengan uang muka nyaris 0%  
**MAKA** hampir pasti nasabah tersebut adalah peserta program VA Loan (Veteran)

> **Analisis Peluang Bisnis:** Tawarkan produk tabungan atau investasi tambahan (cross-selling) kepada nasabah veteran yang melakukan cash-out refinance untuk membantu mereka menaruh dana segar hasil refinance tersebut ke dalam portofolio investasi yang aman.

#### Pola #5-10 — Pola Tambahan Signifikan
- **Multifamily + Bunga Sedang -> Jumbo Loan (Kekuatan 12x):** Desain paket bundling investasi properti komersial yang menggabungkan KPR plafon besar (> $647K) dengan bunga tetap menengah serta fasilitas kredit modal kerja untuk renovasi.
- **Beli Multifamily Baru -> Jumbo Loan (Kekuatan 11,3x):** Jalin kemitraan eksklusif (partnership) dengan pengembang apartemen/ruko baru untuk menawarkan skema KPR Jumbo Investor instan di lokasi strategis.
- **Pre-Approval + Ginnie Mae -> DP Minim (Kekuatan 9,8x):** Optimalkan layanan 'Instant Pre-Approval' berbasis digital khusus untuk segmen program pemerintah guna mempermudah pembeli rumah pertama berpendapatan rendah.
- **VA Loan + Bunga Rendah -> Ginnie Mae (Kekuatan 9,1x):** Gunakan sekuritisasi Ginnie Mae untuk mendanai KPR berbiaya rendah secara berkelanjutan, sekaligus menawarkan produk khusus veteran (VA-tailored products).
- **DTI > 60% + Manufactured Housing -> Tenor Pendek (Kekuatan 8,1x):** Tawarkan jasa pendampingan konsolidasi utang atau program perbaikan skor kredit bagi nasabah berisiko tinggi ini seraya membatasi tenor KPR.

---

### 3.3 Deteksi 3.301 Kasus yang Butuh Perhatian

Dari 99.994 pengajuan, sistem anomali mendeteksi **3.301 kasus yang menyimpang** dari pola normal:

| Kategori | Jumlah Kasus | Apa Artinya | Tindakan |
|---|---|---|---|
| **Sinyal Risiko Kredit Tinggi** | 76 kasus | Kombinasi gaji rendah + pinjaman jumbo + leverage agresif | Prioritas review manual sebelum disetujui |
| **Data Error** | 179 kasus | Nilai tidak logis (bunga 0%, LTV > 150%) | Eskalasi ke tim data untuk koreksi |
| **Profil Konservatif (Prospek)** | 372 kasus | "Terlalu sehat" — pendapatan sangat tinggi tapi pinjaman sangat kecil | Tawarkan produk Wealth Management |
| **Perlu Tinjauan Manual** | 2.674 kasus | Pola statistik tidak biasa, perlu validasi manusia | Masuk daftar audit internal berkala |

> **Yang Tidak Terlihat di Data Mentah:** Secara individual, setiap komponen dari kasus-kasus ini tampak normal. Yang membuat mereka anomali adalah **kombinasi** dari semua faktor tersebut secara bersamaan. Ini tidak mungkin ditemukan tanpa algoritma deteksi berlapis.

---

## Bagian 4: Jawaban atas Pertanyaan Sentral

### "Apa yang kami temukan yang TIDAK sudah jelas dari data mentah?"

**Temuan 1 — Perilaku Leverage yang Paradoksal**  
Asumsi umum: "Orang kaya pinjam banyak, orang biasa pinjam sedikit."  
Kenyataan yang ditemukan: Justru sebaliknya. Kelompok terkaya (Grup 3, penghasilan $204k) memilih LTV rendah dan uang muka besar. **Ini tidak terlihat dalam laporan ringkasan biasa.**

**Temuan 2 — VA Loan Bukan Sekadar Program, Ini Ekosistem**  
Data mentah menunjukkan VA Loan sebagai salah satu kolom dari banyak kolom. ARM mengungkap bahwa VA Loan membentuk jaringan perilaku yang sangat terstruktur dan bisa diprediksi dengan kepastian 85–95%.

**Temuan 3 — Generasi Muda Punya Jalur Tersendiri**  
Tidak ada laporan standar yang langsung menyoroti bahwa usia pemohon di bawah 25 tahun hampir selalu berujung ke Manufactured Housing dengan tenor pendek. **Ini adalah ceruk pasar yang belum digarap secara maksimal.**

**Temuan 4 — Anomali Bukan Hanya Alarm Bahaya**  
Dari 3.301 "kasus aneh", ternyata 372 di antaranya adalah nasabah dengan kesehatan finansial yang justru terlalu baik. **Sistem anomali secara tidak terduga menghasilkan daftar prospek bisnis premium.**

---

## Bagian 5: Rekomendasi Strategis

### Rekomendasi 1: Diferensiasi Produk Berdasarkan Segmen
Buat tiga jalur produk yang berbeda:
- **Jalur Stabilitas** (Grup 1): KPR standar dengan proses mudah dan cepat
- **Jalur Premium** (Grup 2): Produk berbunga kompetitif dengan monitoring DTI otomatis
- **Jalur Wealth** (Grup 3): Bukan produk KPR, melainkan layanan Wealth Management & investasi

### Rekomendasi 2: Program Bundling VA Loan
Ciptakan paket khusus "Veteran Financial Bundle": KPR VA sepaket dengan kartu kredit limit tinggi dan fasilitas pinjaman renovasi.

### Rekomendasi 3: Divisi Kredit Perumahan Ekonomis
Buat jalur persetujuan fast-track khusus untuk Manufactured Housing yang menyasar segmen usia muda dan pendapatan entry-level.

### Rekomendasi 4: Konversi Daftar Anomali Menjadi Pipeline Bisnis
Dari 372 nasabah "Profil Konservatif", buat tim relationship manager khusus yang proaktif menghubungi mereka untuk menawarkan produk Wealth Management.

### Rekomendasi 5: Sistem Peringatan Dini Kredit Berlapis
Implementasikan flag otomatis untuk nasabah yang memiliki kombinasi risiko tinggi (LTV > 100% + DTI > 60% + KPR berlapis).

---

## Lampiran: Metodologi Teknis (Ringkas)

| Fase | Teknik | Tools | Parameter |
|---|---|---|---|
| Preprocessing | Imputasi, Encoding, Binning, Normalisasi | Python, Pandas | 99.994 baris, 80 kolom |
| Clustering | K-Means | Scikit-learn | K=3 |
| ARM | Apriori Algorithm | mlxtend | min_support=0.001, min_confidence=0.5 |
| Anomaly Detection | Isolation Forest + LOF | Scikit-learn | contamination=0.05 |

---

*Laporan ini merupakan bagian dari HMDA Data Mining Project — Phase 5: Visualization and Knowledge Presentation*  
*Data: HMDA 2022 | Platform Dashboard: Python Dash | © 2026 Insight Communicator Team*
