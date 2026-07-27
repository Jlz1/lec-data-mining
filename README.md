"# Project LEC Data Mining — Pasar KPR Amerika Serikat (HMDA 2022)

An enterprise-grade unsupervised data mining project analyzing 100,000 Home Mortgage Disclosure Act (HMDA) 2022 records through **Clustering**, **Association Rule Mining (ARM)**, and **Multi-Method Outlier Detection**.

## 📖 Dokumentasi & Analisis Mendalam
Untuk melihat laporan komprehensif mengenai arsitektur teknis, metodologi statistik, temuan 3 klaster pasar, 10 aturan asosiasi bisnis, dan klasifikasi anomali, silakan baca dokumentasi utama proyek:
👉 **[Analisis Mendalam Proyek HMDA (ANALISIS_MENDALAM_PROYEK_HMDA.md)](file:///D:/BCA/Cawu%205/Data%20Mining/LEC/LEC%20Data%20Mining/ANALISIS_MENDALAM_PROYEK_HMDA.md)**

---

## 🚀 Cara Menjalankan Proyek
1. Pastikan file data mentah `2022_public_lar_csv.csv` telah diletakkan di dalam folder `data/`.
2. Install seluruh dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Untuk menjalankan aplikasi Interactive Streamlit Dashboard:
   ```bash
   streamlit run dashboard/app.py
   ```