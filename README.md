"# Project LEC Data Mining — Pasar KPR Amerika Serikat (HMDA 2022)

An enterprise-grade unsupervised data mining project analyzing 100,000 Home Mortgage Disclosure Act (HMDA) 2022 records through **Clustering**, **Association Rule Mining (ARM)**, and **Multi-Method Outlier Detection**.

## 📖 Laporan Pengetahuan
Laporan final yang merangkum seluruh fase, temuan, dan interpretasi bisnis tersedia di:
👉 **[Knowledge Discovery Report](reports/5-knowledge-discovery-report.txt)**

---

## 🚀 Cara Menjalankan Proyek
1. Pastikan file data mentah `2022_public_lar_csv.csv` telah diletakkan di dalam folder `data/`.
2. Install seluruh dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Untuk menjalankan aplikasi Interactive Plotly Dash Dashboard:
   ```bash
   python dashboard/app.py
   ```

   Dashboard dapat dibuka di `http://127.0.0.1:8050/`.
