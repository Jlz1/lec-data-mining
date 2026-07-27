import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import os

# Inisialisasi App
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True
)
app.title = "HMDA 2022 Data Mining Dashboard"

# --- Design system chart chrome (SpaceX-inspired, varian light/shop-site) ---
# D-DIN tidak tersedia di Google Fonts, jadi memakai substitusi resmi dari design
# spec: Inter, dengan fallback ke Arial Narrow untuk mempertahankan cut kondensed.
PLOT_FONT = "Inter, 'Arial Narrow', Arial, Verdana, sans-serif"
PLOT_INK = '#000000'
PLOT_INK_MUTE = '#5a5a5f'
PLOT_GRID = 'rgba(0,0,0,0.10)'
PLOT_HAIRLINE = '#e0e0e8'

pio.templates['spacex'] = go.layout.Template(
    layout=dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family=PLOT_FONT, color=PLOT_INK, size=12),
        title=dict(font=dict(family=PLOT_FONT, color=PLOT_INK)),
        legend=dict(font=dict(family=PLOT_FONT, color=PLOT_INK_MUTE, size=11)),
        hoverlabel=dict(
            bgcolor='#ffffff', bordercolor='#000000',
            font=dict(family=PLOT_FONT, color=PLOT_INK, size=12)
        ),
        # automargin + standoff: sumbu memesan ruangnya sendiri, jadi label tidak
        # pernah terpotong dan judul sumbu tidak menabrak angka tick.
        xaxis=dict(gridcolor=PLOT_GRID, zerolinecolor=PLOT_HAIRLINE,
                   linecolor=PLOT_HAIRLINE, tickfont=dict(color=PLOT_INK_MUTE),
                   automargin=True, title=dict(standoff=14, font=dict(color=PLOT_INK_MUTE, size=12))),
        yaxis=dict(gridcolor=PLOT_GRID, zerolinecolor=PLOT_HAIRLINE,
                   linecolor=PLOT_HAIRLINE, tickfont=dict(color=PLOT_INK_MUTE),
                   automargin=True, title=dict(standoff=14, font=dict(color=PLOT_INK_MUTE, size=12))),
    )
)
pio.templates.default = 'spacex'

# Load data (dummy agregasi untuk performa UI jika file berat, namun kita ambil data asli dari phase sebelumnya)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rules_path = os.path.join(base_dir, 'reports', '3-association-rules.csv')
anomalies_path = os.path.join(base_dir, 'reports', '4-anomalies.csv')
pca_path = os.path.join(base_dir, 'reports', 'pca_clusters.csv')
data_path = os.path.join(base_dir, 'data', 'processed_dataset.csv')

try:
    df_rules = pd.read_csv(rules_path)
    top_10_rules = df_rules.head(10).copy()
    
    # Translate to very simple business language but keep financial terms
    business_rules = [
        {"kondisi": "KPR kedua (Piggyback/HELOC) dari investor swasta", "hasil": "Utang melampaui nilai rumah (LTV > 100%)", "peluang_bisnis": "Mitigasi Risiko: Tawarkan program konsolidasi utang (penggabungan cicilan dengan bunga tetap) dan asuransi kredit tambahan untuk mencegah risiko kredit macet akibat total utang yang melampaui harga rumah.", "lift": 38.02, "risk": "high"},
        {"kondisi": "Nasabah muda (di bawah 25 tahun) + cicilan menengah", "hasil": "Memilih properti Manufactured Housing", "peluang_bisnis": "Produk Baru: Luncurkan paket KPR 'Rumah Pertama Anak Muda' untuk rumah siap rakit (manufactured housing) dengan DP fleksibel dan cicilan bertahap yang ramah bagi pembeli pemula.", "lift": 19.73, "risk": "medium"},
        {"kondisi": "Pembelian properti tipe Multifamily (Apartemen/Kos)", "hasil": "Ditujukan untuk investasi atau bisnis sewa", "peluang_bisnis": "Cross-Selling & Layanan: Buat produk KPR Investasi Properti Sewa yang dibundling dengan asuransi properti dan layanan pengelolaan arus kas (cash management) bagi pemilik kos/apartemen.", "lift": 13.51, "risk": "low"},
        {"kondisi": "Pinjaman Jumbo (Non-Conforming) + jaminan pemerintah", "hasil": "Berasal dari program VA Loan (Veteran)", "peluang_bisnis": "Pemasaran Segmen Premium: Buat kampanye KPR Jumbo khusus Veteran dengan bunga bersaing dan biaya administrasi ringan untuk menggaet nasabah bernilai tinggi dari segmen pensiunan militer.", "lift": 12.53, "risk": "low"},
        {"kondisi": "Properti Multifamily + bunga sedang (3-5%)", "hasil": "Pinjaman Jumbo Non-Conforming (> $647K)", "peluang_bisnis": "Bundling Kredit: Sediakan paket KPR Plafon Besar (> $647K) yang dilengkapi fasilitas kredit modal kerja untuk renovasi dan perawatan apartemen/kos-kosan.", "lift": 12.00, "risk": "medium"},
        {"kondisi": "Pembelian rumah baru tipe Multifamily", "hasil": "Pinjaman Jumbo Non-Conforming (> $647K)", "peluang_bisnis": "Kemitraan Developer: Gandeng pengembang apartemen/ruko baru untuk menyediakan skema KPR Investor instan langsung di lokasi proyek yang sedang berkembang.", "lift": 11.34, "risk": "medium"},
        {"kondisi": "Uang muka nyaris 0% (LTV 95-100%) + Cash-out Refinance", "hasil": "Menggunakan fasilitas VA Loan (Veteran)", "peluang_bisnis": "Retensi & Cross-Selling: Tawarkan produk tabungan atau investasi aman kepada nasabah veteran yang melakukan pencairan dana tunai (cash-out refinance) agar dana segar mereka dikelola di bank kita.", "lift": 10.72, "risk": "high"},
        {"kondisi": "Pre-Approval + didukung Ginnie Mae", "hasil": "Uang muka sangat minim (LTV 95-100%)", "peluang_bisnis": "Layanan Digital Cepat: Sediakan fitur 'Persetujuan Awal Instant' (Instant Pre-Approval) digital untuk mempermudah pembeli rumah pertama berpenghasilan menengah-bawah dalam pengajuan KPR.", "lift": 9.77, "risk": "low"},
        {"kondisi": "VA Loan (Veteran) + bunga rendah (di bawah 3%)", "hasil": "Disokong program penjaminan Ginnie Mae", "peluang_bisnis": "Penjualan Produk Tambahan: Manfaatkan dukungan penjaminan pemerintah untuk ekspansi KPR berbiaya rendah, seraya menawarkan produk tambahan (kartu kredit/asuransi khusus) kepada nasabah veteran.", "lift": 9.09, "risk": "low"},
        {"kondisi": "DTI di atas 60% + rumah Manufactured Housing", "hasil": "Tenor pinjaman lebih pendek (15-25 tahun)", "peluang_bisnis": "Pendampingan & Kontrol Risiko: Tawarkan pendampingan pengelolaan utang dan perbaikan skor kredit bagi nasabah berbeban utang tinggi, sambil membatasi jangka waktu pinjaman agar risiko gagal bayar dapat ditekan.", "lift": 8.09, "risk": "high"}
    ]
except Exception as e:
    business_rules = []
    print(f"Error loading rules: {e}")

try:
    df_anomalies = pd.read_csv(anomalies_path)
    
    # Tier mapping
    tier_counts = df_anomalies['tier'].value_counts().reset_index()
    tier_counts.columns = ['Tier', 'Jumlah']
    
    # Filter only priority rows (Confirmed + High Confidence) for typology breakdown
    priority_tiers = ['Confirmed (2 metode)', 'High Confidence']
    df_priority = df_anomalies[df_anomalies['tier'].isin(priority_tiers)]
    
    anomaly_counts = df_priority['typology'].value_counts().reset_index()
    anomaly_counts.columns = ['Tipologi', 'Jumlah']
    
    # Translate typology to simple words
    tipologi_map = {
        'Unclassified / Manual Review': 'Perlu Tinjauan Manual (Anomali)',
        'Rare Legitimate': 'Profil Konservatif (Leverage Rendah)',
        'Data Error': 'Data Error (Mustahil Secara Fisik/Logika)',
        'Potential Risk Signal': 'Sinyal Risiko Kredit Tinggi'
    }
    anomaly_counts['Tipologi_Indo'] = anomaly_counts['Tipologi'].map(tipologi_map)
except Exception as e:
    df_anomalies = pd.DataFrame()
    df_priority = pd.DataFrame()
    anomaly_counts = pd.DataFrame()
    tier_counts = pd.DataFrame()
    print(f"Error loading anomalies: {e}")

try:
    df_pca = pd.read_csv(pca_path)
except Exception as e:
    df_pca = pd.DataFrame()
    print(f"Error loading PCA data: {e}")

try:
    profile_path = os.path.join(base_dir, 'reports', 'cluster_profile_summary.csv')
    df_profile = pd.read_csv(profile_path)
except Exception as e:
    df_profile = pd.DataFrame()
    print(f"Error loading cluster profile summary: {e}")

try:
    df_raw = pd.read_csv(data_path, nrows=3000)
    for col in ['loan_amount', 'income', 'interest_rate', 'combined_loan_to_value_ratio']:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')
except Exception as e:
    df_raw = pd.DataFrame()
    print(f"Error loading raw data: {e}")


def fmt_count(value):
    """Format current artifact counts in the Indonesian dashboard style."""
    return f"{int(value):,}".replace(",", ".")


def wrap_label(text, width=20):
    """Pecah label sumbu jadi beberapa baris TANPA mengubah kata-katanya.

    Label tipologi yang panjang membuat automargin memesan >250px di kiri
    sehingga batang grafik tergencet. Dipecah per baris, teksnya tetap utuh
    dan terbaca penuh tapi kolom labelnya jauh lebih ramping.
    """
    lines, current = [], ""
    for word in text.split():
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return "<br>".join(lines)


def priority_typology_count(typology):
    if df_priority.empty or "typology" not in df_priority.columns:
        return 0
    return int((df_priority["typology"] == typology).sum())

# Layout Komponen

def create_header():
    return html.Div(className="dashboard-header", children=[
        html.H1("Insight Komunikator: HMDA 2022"),
    ])

def tab_1_executive():
    return html.Div(className="tab-content", children=[
        html.Div("HMDA 2022 ", className="section-title"),
        html.P("Analisis dataset pengajuan Kredit Pemilikan Rumah (KPR) dari institusi keuangan AS yang dilaporkan di bawah payung regulasi federal HMDA (Home Mortgage Disclosure Act). Kami telah menyaring dan membersihkan data mentahnya agar siap memberikan insight bisnis yang tajam.", className="mb-4 text-muted"),
        
        # --- BARIS 1: Metrik Utama ---
        dbc.Row([
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Data Mentah", className="metric-title"),
                html.Div("100.000", className="metric-value"),
                html.Div("Pengajuan", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Data Siap Analisis", className="metric-title"),
                html.Div("99.994", className="metric-value", style={'color': '#059669'}),
                html.Div("Setelah Hapus Duplikat", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Kolom Mentah", className="metric-title"),
                html.Div("99", className="metric-value"),
                html.Div("Variabel", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Fitur Final", className="metric-title"),
                html.Div("80", className="metric-value", style={'color': '#2563eb'}),
                html.Div("Setelah Encoding & Seleksi", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Data Kosong Awal", className="metric-title"),
                html.Div("2,85 Juta", className="metric-value", style={'color': '#b45309'}),
                html.Div("Sel yang Kosong", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Kelengkapan Akhir", className="metric-title"),
                html.Div("96,5%", className="metric-value", style={'color': '#059669'}),
                html.Div("Sisa Kosong: Kolom Finansial*", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
        ], className="mb-4"),
        html.P("* Beberapa kolom finansial (suku bunga, LTV, biaya pinjaman) tersimpan sebagai teks bercampur nilai non-numerik di sumber data, menyisakan celah imputasi kecil. Fase Clustering & Anomaly Detection tetap melakukan imputasi ulang sebelum pemodelan, jadi tidak ada nilai kosong yang mencapai model manapun — detail lengkap di tab \"7. Metodologi & Validitas\".", className="small text-muted mb-4", style={'marginTop': '-0.75rem'}),

        # --- BARIS 2: Profil Finansial ---
        html.H4("Profil Finansial Nasabah", className="mb-3 mt-5", style={'color': 'var(--accent-blue)'}),
        html.P("Nilai pinjaman & pendapatan sangat right-skewed (ekor outlier ekstrem), jadi Median dijadikan angka utama — lebih representatif dibanding Rata-rata untuk data finansial yang timpang. Ini konsisten dengan temuan skewness di Fase 1 & 3.", className="small text-muted mb-3", style={'maxWidth': '900px'}),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100 text-center", children=[
                html.H5("Nilai Pinjaman (Loan)", className="mb-3", style={'color': 'var(--text-secondary)'}),
                html.Div("$225K", className="stat-highlight", style={'color': '#2563eb'}),
                html.Div("Median", className="small text-muted mb-2"),
                html.Div("Rata-rata: $306K (naik krn outlier)", className="small mb-1"),
                html.Div("Range: $5K - $93,2 Juta", className="small text-muted")
            ]), width=3),
            dbc.Col(html.Div(className="glass-card h-100 text-center", children=[
                html.H5("Pendapatan (Income)", className="mb-3", style={'color': 'var(--text-secondary)'}),
                html.Div("$95K", className="stat-highlight", style={'color': '#059669'}),
                html.Div("Median / Tahun", className="small text-muted mb-2"),
                html.Div("Rata-rata: $153,6K (outlier ekstrem)", className="small mb-1"),
                html.Div("Range: $0 - $1,08 Juta", className="small text-muted")
            ]), width=3),
            dbc.Col(html.Div(className="glass-card h-100 text-center", children=[
                html.H5("Suku Bunga (Interest)", className="mb-3", style={'color': 'var(--text-secondary)'}),
                html.Div("4,77%", className="stat-highlight", style={'color': '#c2410c'}),
                html.Div("Rata-rata", className="small text-muted mb-2"),
                html.Div("Median: 4,75%", className="small mb-1"),
                html.Div("Range: 0% - 15,25%", className="small text-muted")
            ]), width=3),
            dbc.Col(html.Div(className="glass-card h-100 text-center", children=[
                html.H5("LTV", className="mb-3", style={'color': 'var(--text-secondary)'}),
                html.Div("74,0%", className="stat-highlight", style={'color': '#e11d48'}),
                html.Div("Rata-rata LTV", className="small text-muted mb-2"),
                html.Div("Median: 78,2%", className="small mb-1"),
                html.Div("Lebih rendah = Lebih aman", className="small text-muted")
            ]), width=3),
        ], className="mb-4"),

        # --- BARIS 3: Komposisi ---
        html.H4("Siapa Saja yang Mengajukan KPR?", className="mb-3 mt-5", style={'color': 'var(--accent-teal)'}),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Tipe Produk KPR", className="mb-3", style={'color': 'var(--text-secondary)', 'textAlign': 'center'}),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("Konvensional"), html.Strong("79,4%")]),
                html.Div(className="progress mb-3", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '79.4%', 'backgroundColor': '#2563eb'})
                ]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("FHA (Pemerintah)"), html.Strong("12,4%")]),
                html.Div(className="progress mb-3", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '12.4%', 'backgroundColor': '#059669'})
                ]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("VA (Veteran)"), html.Strong("7,5%")]),
                html.Div(className="progress mb-0", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '7.5%', 'backgroundColor': '#b45309'})
                ])
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Tujuan Pinjaman", className="mb-3", style={'color': 'var(--text-secondary)', 'textAlign': 'center'}),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("Pembelian Rumah Baru"), html.Strong("49,0%")]),
                html.Div(className="progress mb-3", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '49.0%', 'backgroundColor': '#6d28d9'})
                ]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("Refinancing (termasuk Cash-out)"), html.Strong("33,2%")]),
                html.Div(className="progress mb-3", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '33.2%', 'backgroundColor': '#ec4899'})
                ]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("Perbaikan Rumah"), html.Strong("9,3%")]),
                html.Div(className="progress mb-0", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '9.3%', 'backgroundColor': '#14b8a6'})
                ])
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Jenis Kelamin Pemohon", className="mb-3", style={'color': 'var(--text-secondary)', 'textAlign': 'center'}),
                html.Div(className="d-flex justify-content-center align-items-center", children=[
                    html.Div(className="text-center me-4", children=[
                        html.H3("30,8%", style={'color': '#000000', 'marginBottom': '5px', 'fontSize': '32px'}),
                        html.Span("Pria", className="text-muted")
                    ]),
                    html.Div(style={'width': '1px', 'height': '40px', 'backgroundColor': '#e0e0e8'}),
                    html.Div(className="text-center ms-4", children=[
                        html.H3("20,7%", style={'color': '#000000', 'marginBottom': '5px', 'fontSize': '32px'}),
                        html.Span("Wanita", className="text-muted")
                    ])
                ]),
                html.P("48,5% sisanya adalah pengajuan Joint (bersama pasangan/co-applicant) atau data jenis kelamin tidak tersedia — proporsi ini cukup besar untuk dicatat, bukan diabaikan.", className="small text-muted text-center mt-3 mb-0")
            ]), width=4),
        ], className="mb-4"),

        # --- BARIS 4: Proses Pembersihan ---
        html.H4("Proses Pembersihan Data (Data Preprocessing Pipeline)", className="mb-3 mt-5", style={'color': 'var(--text-secondary)'}),
        dbc.Row([
            dbc.Col(html.Div(className="pipeline-step", children=[html.Strong("1. Data Mentah"), html.Br(), html.Span("100.000 Baris", className="small text-muted")]), width=2),
            dbc.Col(html.Div(className="pipeline-arrow", children="➔"), width=1, style={'padding': 0, 'width': '4%'}),
            dbc.Col(html.Div(className="pipeline-step", children=[html.Strong("2. Buang Kolom"), html.Br(), html.Span("Hapus data ambigu/bocor", className="small text-muted")]), width=2),
            dbc.Col(html.Div(className="pipeline-arrow", children="➔"), width=1, style={'padding': 0, 'width': '4%'}),
            dbc.Col(html.Div(className="pipeline-step", children=[html.Strong("3. Hapus Duplikat"), html.Br(), html.Span("6 baris identik dihapus", className="small text-muted")]), width=2),
            dbc.Col(html.Div(className="pipeline-arrow", children="➔"), width=1, style={'padding': 0, 'width': '4%'}),
            dbc.Col(html.Div(className="pipeline-step", children=[html.Strong("4. Isi Data Kosong"), html.Br(), html.Span("Imputasi Median/Mode (96,5%)", className="small text-muted")]), width=2),
            dbc.Col(html.Div(className="pipeline-arrow", children="➔"), width=1, style={'padding': 0, 'width': '4%'}),
            dbc.Col(html.Div(className="pipeline-step", style={'borderColor': '#000000'}, children=[html.Strong("5. Data Siap Pakai", style={'color': '#000000'}), html.Br(), html.Span("80 Fitur Final", className="small text-muted")]), width=2),
        ], className="align-items-center mb-5", style={'justifyContent': 'center'}),
        
        # --- BARIS 5: Ringkasan Temuan ---
        html.H4("3 Ringkasan Temuan Proyek", className="mb-3", style={'color': 'var(--text-secondary)'}),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.Div("1. Tiga Kelompok Pasar Utama", className="insight-title", style={'color': '#2563eb'}),
                html.Div("Nasabah kita tidaklah sama. Sistem AI membagi mereka menjadi 3 segmen besar dengan strategi meminjam yang sangat berbeda, dari yang super aman hingga yang sangat berisiko.", className="insight-desc")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.Div("2. Pola Bisnis Tersembunyi", className="insight-title", style={'color': '#059669'}),
                html.Div("Kami menemukan kebiasaan nasabah yang tak kasat mata. Contohnya, ada ceruk pasar besar pada anak muda bergaji rendah yang selalu menyasar properti siap rakit (Manufactured Housing).", className="insight-desc")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.Div("3. Deteksi Otomatis Kasus Berisiko", className="insight-title", style={'color': '#e11d48'}),
                html.Div(f"Sistem kami menemukan {fmt_count(len(df_priority))} kasus pengajuan yang secara individual angkanya tampak normal, tapi saat digabungkan mengindikasikan sinyal risiko yang tinggi dan perlu ditinjau manusia.", className="insight-desc")
            ]), width=4)
        ])
    ])

def tab_segmentation():
    # === CHARTS ===
    cluster_colors = {'Kelas Menengah (Grup 1)': '#2563eb', 'Peminjam Agresif (Grup 2)': '#e11d48', 'Konservatif HNW (Grup 3)': '#059669'}

    # Chart pembanding: LTV (hampir sama) vs Rasio Pinjaman-ke-Pendapatan (jelas beda).
    # Sumber: reports/cluster_profile_summary.csv -- rata-rata aktual per cluster.
    # Chart ini sengaja menampilkan keduanya berdampingan supaya jelas variabel MANA
    # yang benar-benar membedakan segmen, dan mana yang TIDAK.
    if not df_profile.empty:
        order = ['Kelas Menengah (Grup 1)', 'Peminjam Agresif (Grup 2)', 'Konservatif HNW (Grup 3)']
        prof = df_profile.set_index('cluster_name').reindex(order).reset_index()
        short = ['Grup 1<br>Kelas Menengah', 'Grup 2<br>Peminjam Agresif', 'Grup 3<br>Konservatif HNW']
        bar_cols = [cluster_colors[c] for c in order]

        fig_diff = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                'Rasio Pinjaman ÷ Pendapatan<br><sub style="color:#000000">JELAS BERBEDA — ini pembedanya</sub>',
                'Rasio Utang ÷ Nilai Rumah (LTV)<br><sub style="color:#5a5a5f">HAMPIR SAMA — bukan pembeda</sub>'
            ),
            horizontal_spacing=0.16
        )
        fig_diff.add_trace(go.Bar(
            x=short, y=prof['loan_to_income_ratio'],
            marker_color=bar_cols,
            text=[f"{v:.2f}x" for v in prof['loan_to_income_ratio']],
            textposition='outside', textfont=dict(size=13, color=PLOT_INK),
            hovertemplate='%{x}<br>Pinjaman = %{y:.2f}x pendapatan tahunan<extra></extra>',
            showlegend=False
        ), row=1, col=1)
        fig_diff.add_trace(go.Bar(
            x=short, y=prof['avg_ltv'],
            marker_color=bar_cols, marker_opacity=0.45,
            text=[f"{v:.1f}%" for v in prof['avg_ltv']],
            textposition='outside', textfont=dict(size=13, color=PLOT_INK),
            hovertemplate='%{x}<br>LTV rata-rata = %{y:.1f}%<extra></extra>',
            showlegend=False
        ), row=1, col=2)
        fig_diff.update_yaxes(range=[0, 3.1], title_text='kali pendapatan', row=1, col=1,
                              automargin=True, title_standoff=10, tickfont=dict(size=10),
                              showgrid=True, gridcolor=PLOT_GRID)
        # Sumbu-y LTV dimulai dari 0 (bukan di-zoom) supaya kemiripan ketiganya terlihat
        # apa adanya -- memotong sumbu akan membesar-besarkan selisih 2 poin persen.
        fig_diff.update_yaxes(range=[0, 100], title_text='% nilai rumah', row=1, col=2,
                              automargin=True, title_standoff=10, tickfont=dict(size=10),
                              showgrid=True, gridcolor=PLOT_GRID)
        fig_diff.update_xaxes(tickfont=dict(size=10))
        fig_diff.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=PLOT_INK, family=PLOT_FONT),
            margin=dict(l=8, r=8, t=76, b=8), bargap=0.45
        )
        for ann in fig_diff['layout']['annotations'][:2]:
            ann['font'] = dict(size=12, color=PLOT_INK)
    else:
        fig_diff = go.Figure()

    # Donut chart proporsi
    fig_donut = go.Figure(data=[go.Pie(
        labels=['Kelas Menengah (Grup 1)', 'Peminjam Agresif (Grup 2)', 'Konservatif HNW (Grup 3)'],
        values=[42.58, 25.34, 32.08],
        hole=.55,
        marker_colors=['#2563eb', '#e11d48', '#059669'],
        textinfo='percent',
        insidetextfont=dict(color='#ffffff', size=13),
    )])
    fig_donut.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=PLOT_INK),
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
        annotations=[dict(text='<b>100K<br>Nasabah</b>', x=0.5, y=0.5, font_size=14, showarrow=False, font_color=PLOT_INK)]
    )

    # PCA Scatter
    if not df_pca.empty:
        fig_pca = px.scatter(
            df_pca.sample(min(1500, len(df_pca))),
            x='pca_x', y='pca_y',
            color='cluster_name',
            color_discrete_map=cluster_colors,
            hover_data=['loan_amount', 'income'],
            labels={'pca_x': 'Dimensi 1', 'pca_y': 'Dimensi 2', 'cluster_name': 'Segmen'},
            opacity=0.65
        )
        fig_pca.update_traces(marker=dict(size=5))
        fig_pca.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=PLOT_INK, family=PLOT_FONT),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
    else:
        fig_pca = go.Figure()

    return html.Div(className="tab-content", children=[
        html.Div("Siapa Sebenarnya Nasabah KPR Kita?", className="section-title"),
        html.P(
            "Data 100.000 pengajuan KPR dianalisis dan hasilnya mengejutkan: nasabah kita bukan satu kelompok yang homogen. "
            "Mereka terbagi secara alami menjadi 3 segmen dengan perilaku keuangan yang SANGAT berbeda. "
            "Memahami perbedaan ini adalah kunci untuk menentukan strategi produk, pemasaran, dan mitigasi risiko yang tepat sasaran.",
            className="mb-4 text-muted"
        ),

        # --- BARIS 1: Donut + Peta Cluster ---
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Proporsi Tiap Segmen Nasabah"),
                html.P("Lebih dari 4 dari 10 nasabah berada di segmen Kelas Menengah.", className="small text-muted mb-2"),
                dcc.Graph(figure=fig_donut, config={'displayModeBar': False}, responsive=True, style={'height': '320px'})
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Peta Posisi Nasabah (Cluster Map)"),
                html.P(
                    "Setiap titik = satu pengajuan KPR. Titik yang mengelompok artinya nasabah tersebut sangat mirip satu sama lain. "
                    "Ketiga warna ini adalah tiga 'dunia' yang berbeda di dalam pasar yang sama.",
                    className="small text-muted mb-2"
                ),
                dcc.Graph(figure=fig_pca, config={'displayModeBar': False}, responsive=True, style={'height': '320px'}),
                html.P(
                    "Peta 2D ini adalah proyeksi PCA dari 14 fitur asli — 2 dimensi ini hanya menangkap ±27,9% dari total variasi data (PC1 15,3% + PC2 12,6%). "
                    "Artinya: pemisahan warna yang terlihat di sini justru KONSERVATIF — cluster sebenarnya lebih terpisah di ruang 14 dimensi daripada yang tampak di 2D ini.",
                    className="small text-muted mt-2 mb-0", style={'fontStyle': 'italic'}
                )
            ]), width=8),
        ], className="mb-4"),

        # --- BARIS 1b: Apa yang SEBENARNYA membedakan ketiga segmen ---
        html.Div("Apa yang Sebenarnya Membedakan Ketiga Segmen?", className="section-title"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.P([
                    "Banyak orang mengira segmen nasabah dibedakan oleh besar uang muka (LTV). ",
                    html.B("Data kami menunjukkan itu tidak benar."),
                    " Grafik kiri dan kanan memakai skala yang sama-sama dimulai dari nol, jadi bisa dibandingkan apa adanya:"
                ], className="small text-muted mb-2"),
                dcc.Graph(figure=fig_diff, config={'displayModeBar': False}, responsive=True, style={'height': '340px'}),
                html.P([
                    html.B("Cara membacanya: "),
                    "Grup 3 (paling kaya, pendapatan $207.565) hanya meminjam ", html.B("1,53x"),
                    " pendapatan tahunannya, sedangkan Grup 2 yang berpendapatan lebih rendah ($152.332) meminjam ", html.B("2,47x"),
                    " — jadi kelipatan pinjaman justru MENURUN di segmen paling kaya. Sebaliknya, LTV ketiganya nyaris sama (72,99%–75,18%), "
                    "begitu juga suku bunga (4,69%–4,87%). Kesimpulan jujurnya: ketiga segmen ini dibedakan oleh ",
                    html.B("seberapa besar pinjaman relatif terhadap pendapatan"),
                    ", BUKAN oleh uang muka atau bunga."
                ], className="small text-muted mt-2 mb-1"),
                html.P([
                    html.B("Batas klaim: "),
                    "karena LTV mereka sama, data TIDAK mendukung kesimpulan bahwa Grup 3 menyetor uang muka lebih besar. "
                    "Yang konsisten dengan data: mereka membeli properti lebih murah relatif kemampuannya. Untuk memastikan mana yang benar "
                    "dibutuhkan data aset/tabungan yang tidak tersedia di HMDA."
                ], className="small mb-0", style={'color': '#5a5a5f', 'fontStyle': 'italic'}),
                html.P("Sumber angka: reports/cluster_profile_summary.csv (rata-rata aktual anggota tiap cluster) — identik dengan angka di laporan Phase 2 & 5.",
                       className="small text-muted mt-2 mb-0", style={'fontSize': '0.75rem'})
            ]), width=12),
        ]),

        # --- BARIS 2: Profil 3 Segmen ---
        html.Div("Profil & Peluang Bisnis Tiap Segmen", className="section-title"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", style={'borderTop': '3px solid #2563eb'}, children=[
                html.H4("Grup 1: Kelas Menengah", style={'color': '#2563eb'}),
                html.P("42,58% dari seluruh nasabah (42.579 orang)", className="badge badge-low-risk mb-3"),
                html.P("Pembeli rumah pertama atau keluarga kelas menengah tipikal. Pendapatan $107.483, pinjaman $256.726 — setara 2,39x pendapatan tahunan."),
                html.Hr(style={'borderColor': '#e0e0e8'}),
                html.P(html.B("Peluang Bisnis:"), className="mb-1"),
                html.P("Segmen ini paling besar volumenya. Fokus pada produk KPR standar dengan proses mudah dan cepat. Mereka sangat menghargai kemudahan administrasi dan suku bunga yang kompetitif.", className="small text-muted"),
                html.P(html.B("Dampak:"), className="mb-1"),
                html.P("Menjaga stabilitas dan volume portofolio KPR tulang punggung pendapatan rutin perusahaan.", className="small text-muted")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", style={'borderTop': '3px solid #e11d48'}, children=[
                html.H4("Grup 2: Peminjam Agresif", style={'color': '#e11d48'}),
                html.P("25,34% dari seluruh nasabah (25.336 orang)", className="badge badge-high-risk mb-3"),
                html.P("Profesional berpendapatan tinggi ($152.332) dengan pinjaman terbesar ($375.773) — setara 2,47x pendapatan tahunan, kelipatan tertinggi dari semua segmen."),
                html.Hr(style={'borderColor': '#e0e0e8'}),
                html.P(html.B("Peluang Bisnis:"), className="mb-1"),
                html.P("Pendapatan bunga per nasabah tertinggi (~$17.763/tahun). Tawarkan produk KPR premium dengan layanan dedicated relationship manager dan fleksibilitas tenor. Catatan: secara total portofolio, Grup 1 tetap penyumbang bunga terbesar karena jumlah nasabahnya jauh lebih banyak.", className="small text-muted"),
                html.P(html.B("Risiko yang Perlu Diawasi:"), className="mb-1"),
                html.P("Rasio utang mereka paling tinggi paling rentan jika terjadi guncangan ekonomi. Perlu sistem monitoring cicilan yang aktif.", className="small text-muted")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", style={'borderTop': '3px solid #059669'}, children=[
                html.H4("Grup 3: Konservatif HNW", style={'color': '#059669'}),
                html.P("32,08% dari seluruh nasabah (32.079 orang)", className="badge badge-low-risk mb-3"),
                html.P("Penghasilan paling tinggi ($207.565), namun secara mengejutkan mereka meminjam paling sedikit relatif kemampuannya — hanya 1,53x pendapatan tahunan."),
                html.Hr(style={'borderColor': '#e0e0e8'}),
                html.P(html.B("Peluang Bisnis:"), className="mb-1"),
                html.P("Jangan tawarkan KPR — mereka tidak terlalu butuh. Tawarkan produk Wealth Management, reksa dana, asuransi jiwa premium, atau deposito.", className="small text-muted"),
                html.P(html.B("Dampak:"), className="mb-1"),
                html.P("Meningkatkan Fee-based Income (pendapatan dari komisi produk) tanpa menambah risiko kredit macet sama sekali.", className="small text-muted")
            ]), width=4),
        ])
    ])


def tab_arm_visualization():
    # Buat Scatter Plot untuk Visualisasi ARM (Support vs Confidence vs Lift)
    if not df_rules.empty:
        plot_df = df_rules.head(100).copy()
        # Konversi ke format persen agar mudah dipahami stakeholder
        plot_df['jangkauan_pasar'] = plot_df['support'] * 100
        plot_df['tingkat_kepastian'] = plot_df['confidence'] * 100
        fig_arm = px.scatter(
            plot_df,
            x='jangkauan_pasar',
            y='tingkat_kepastian',
            size='lift',
            color='lift',
            hover_data=['antecedents', 'consequents'],
            color_continuous_scale=[(0, '#1d4ed8'), (0.3, '#0f766e'), (0.6, '#ca8a04'), (1, '#c2410c')],
            labels={
                'jangkauan_pasar': 'Jangkauan Pasar (% dari Total Nasabah)',
                'tingkat_kepastian': 'Tingkat Kepastian Pola (%)',
                'lift': 'Skor Peluang'
            }
        )
        fig_arm.update_traces(
            marker=dict(line=dict(width=1, color='rgba(0,0,0,0.25)'), sizemin=5),
            hovertemplate=(
                '<b>Skor Peluang: %{marker.color:.1f}</b><br>'
                'Jangkauan Pasar: %{x:.2f}%<br>'
                'Tingkat Kepastian: %{y:.0f}%'
                '<extra></extra>'
            )
        )
        fig_arm.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=PLOT_INK, family=PLOT_FONT),
            margin=dict(l=8, r=8, t=16, b=8),
            coloraxis_colorbar=dict(
                title=dict(text='Skor<br>Peluang', font=dict(size=11), side='top'),
                ticksuffix='',
                len=0.65,
                x=1.02, xpad=6,
                thickness=14,
                outlinewidth=0
            ),
            xaxis=dict(
                ticksuffix='%',
                showgrid=True,
                gridcolor=PLOT_GRID,
                gridwidth=1,
                zeroline=False,
                title=dict(text='Jangkauan Pasar (% dari Total Nasabah)', font=dict(size=12), standoff=14),
                automargin=True,
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                ticksuffix='%',
                showgrid=True,
                gridcolor=PLOT_GRID,
                gridwidth=1,
                zeroline=False,
                title=dict(text='Tingkat Kepastian Pola (%)', font=dict(size=12), standoff=14),
                automargin=True,
                tickfont=dict(size=11),
                range=[55, 105]
            )
        )
        # Rule Network: Flow diagram bisnis yang mudah dipahami
        # Gunakan semua 10 rules dari business_rules
        import math
        flow_rules = [
            {'kondisi': 'KPR Kedua dari<br>Investor Swasta', 'hasil': 'Utang Melampaui<br>Nilai Rumah (LTV &gt;100%)', 'lift': 38.0, 'support': 0.16, 'confidence': 61, 'kondisi_plain': 'KPR Kedua dari Investor Swasta', 'hasil_plain': 'Utang Melampaui Nilai Rumah'},
            {'kondisi': 'Nasabah Muda<br>(Usia &lt; 25 Tahun)', 'hasil': 'Pilih Manufactured<br>Housing', 'lift': 19.7, 'support': 0.14, 'confidence': 86, 'kondisi_plain': 'Nasabah Muda (Usia di bawah 25)', 'hasil_plain': 'Pilih Manufactured Housing'},
            {'kondisi': 'Beli Properti<br>Multifamily (Kos)', 'hasil': 'Tujuan Investasi<br>atau Bisnis Sewa', 'lift': 13.5, 'support': 0.41, 'confidence': 100, 'kondisi_plain': 'Beli Properti Multifamily', 'hasil_plain': 'Tujuan Investasi/Bisnis Sewa'},
            {'kondisi': 'Pinjaman Jumbo +<br>Jaminan Pemerintah', 'hasil': 'Program<br>VA Loan Veteran', 'lift': 12.5, 'support': 0.10, 'confidence': 94, 'kondisi_plain': 'Pinjaman Jumbo + Jaminan Pemerintah', 'hasil_plain': 'Program VA Veteran'},
            {'kondisi': 'Multifamily +<br>Bunga Sedang (3-5%)', 'hasil': 'Pinjaman Jumbo<br>Non-Conforming', 'lift': 12.0, 'support': 0.10, 'confidence': 75, 'kondisi_plain': 'Multifamily + Bunga Sedang', 'hasil_plain': 'Pinjaman Jumbo Non-Conforming'},
            {'kondisi': 'Beli Rumah Baru<br>Tipe Multifamily', 'hasil': 'Pinjaman Jumbo<br>Non-Conforming', 'lift': 11.3, 'support': 0.10, 'confidence': 71, 'kondisi_plain': 'Beli Rumah Baru Tipe Multifamily', 'hasil_plain': 'Pinjaman Jumbo Non-Conforming'},
            {'kondisi': 'Uang Muka ~0% +<br>Cash-out Refinance', 'hasil': 'Fasilitas<br>VA Loan Veteran', 'lift': 10.7, 'support': 0.18, 'confidence': 80, 'kondisi_plain': 'Uang Muka ~0% + Cash-out Refinance', 'hasil_plain': 'Fasilitas VA Loan Veteran'},
            {'kondisi': 'Pre-Approval +<br>Ginnie Mae', 'hasil': 'Uang Muka Sangat<br>Minim (LTV 95-100%)', 'lift': 9.8, 'support': 0.10, 'confidence': 75, 'kondisi_plain': 'Pre-Approval + Ginnie Mae', 'hasil_plain': 'Uang Muka Minim (LTV 95-100%)'},
            {'kondisi': 'VA Loan Veteran +<br>Bunga &lt; 3%', 'hasil': 'Disokong<br>Ginnie Mae', 'lift': 9.1, 'support': 0.50, 'confidence': 73, 'kondisi_plain': 'VA Loan Veteran + Bunga rendah', 'hasil_plain': 'Disokong Ginnie Mae'},
            {'kondisi': 'DTI &gt; 60% +<br>Manufactured Housing', 'hasil': 'Tenor Pinjaman<br>Lebih Pendek', 'lift': 8.1, 'support': 0.40, 'confidence': 81, 'kondisi_plain': 'DTI tinggi + Manufactured Housing', 'hasil_plain': 'Tenor Pinjaman Lebih Pendek'},
        ]
        fig_network = go.Figure()
        n_rules = len(flow_rules)
        # Posisi: Kondisi di kiri (x=0), Hasil di kanan (x=1), diurutkan dari atas ke bawah
        for i, rule in enumerate(flow_rules):
            y_pos = n_rules - 1 - i  # top-to-bottom
            # Ukuran node (lebih kecil agar tidak menabrak teks)
            node_size = 12 + (rule['lift'] / 38.0) * 10
            # Edge (garis penghubung)
            fig_network.add_trace(go.Scatter(
                x=[0.15, 0.85], y=[y_pos, y_pos], mode='lines',
                line=dict(width=1 + rule['lift'] / 20, color='rgba(0,0,0,0.18)'),
                hoverinfo='none', showlegend=False
            ))
            # Arrow head
            fig_network.add_annotation(
                x=0.82, y=y_pos, ax=0.18, ay=y_pos,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=1.5,
                arrowcolor='rgba(0,0,0,0.35)'
            )
            # Node Kondisi (kiri)
            fig_network.add_trace(go.Scatter(
                x=[0], y=[y_pos], mode='markers',
                marker=dict(size=node_size, color='#1d4ed8',
                            line=dict(width=1.5, color='rgba(29,78,216,0.35)')),
                hovertext=(
                    f"<b>Pola #{i+1}</b><br>"
                    f"Kondisi: {rule['kondisi_plain']}<br>"
                    f"Hasil: {rule['hasil_plain']}<br><br>"
                    f"<b>Skor Peluang: {rule['lift']:.1f}</b><br>"
                    f"Jangkauan Pasar: {rule['support']:.2f}%<br>"
                    f"Tingkat Kepastian: {rule['confidence']:.0f}%"
                ),
                hoverinfo='text',
                showlegend=False
            ))
            # Label Kondisi di kiri node
            fig_network.add_annotation(
                x=-0.08, y=y_pos,
                text=rule['kondisi'],
                showarrow=False,
                xanchor='right', yanchor='middle',
                font=dict(size=9, color=PLOT_INK, family=PLOT_FONT),
                xref='x', yref='y'
            )
            # Node Hasil (kanan)
            fig_network.add_trace(go.Scatter(
                x=[1], y=[y_pos], mode='markers',
                marker=dict(size=node_size, color='#0f766e',
                            line=dict(width=1.5, color='rgba(15,118,110,0.35)')),
                hovertext=(
                    f"<b>Pola #{i+1}</b><br>"
                    f"Kondisi: {rule['kondisi_plain']}<br>"
                    f"Hasil: {rule['hasil_plain']}<br><br>"
                    f"<b>Skor Peluang: {rule['lift']:.1f}</b><br>"
                    f"Jangkauan Pasar: {rule['support']:.2f}%<br>"
                    f"Tingkat Kepastian: {rule['confidence']:.0f}%"
                ),
                hoverinfo='text',
                showlegend=False
            ))
            # Label Hasil di kanan node
            fig_network.add_annotation(
                x=1.08, y=y_pos,
                text=rule['hasil'],
                showarrow=False,
                xanchor='left', yanchor='middle',
                font=dict(size=9, color=PLOT_INK, family=PLOT_FONT),
                xref='x', yref='y'
            )
            # Lift label di tengah
            fig_network.add_annotation(
                x=0.5, y=y_pos + 0.15,
                text='<b>Pola #' + str(i+1) + '</b>',
                showarrow=False,
                font=dict(size=9, color=PLOT_INK_MUTE, family=PLOT_FONT),
                xref='x', yref='y'
            )
        fig_network.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=PLOT_INK, family=PLOT_FONT),
            showlegend=False,
            margin=dict(l=150, r=160, t=10, b=10),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[-0.55, 1.55]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                       range=[-0.8, n_rules - 0.2])
        )
    else:
        fig_arm = go.Figure()
        fig_network = go.Figure()

    risk_badge = {'high': 'badge badge-high-risk', 'medium': 'badge badge-medium-risk', 'low': 'badge badge-low-risk'}
    risk_color = {'high': '#e11d48', 'medium': '#c2410c', 'low': '#059669'}
    rules_html = []
    for i, rule in enumerate(business_rules):
        if ': ' in rule['peluang_bisnis']:
            category_title, category_desc = rule['peluang_bisnis'].split(': ', 1)
            peluang_p_children = [
                html.Span(f"{category_title}: ", style={'color': '#000000', 'fontWeight': '600'}),
                category_desc
            ]
        else:
            peluang_p_children = [
                html.Span(rule['peluang_bisnis'])
            ]

        rules_html.append(
            dbc.Col(
                html.Div(className="glass-card mb-3 h-100", style={'borderLeft': f'3px solid {risk_color.get(rule["risk"], "#2563eb")}'}, children=[
                    html.Div(className="d-flex justify-content-between align-items-start mb-2", children=[
                        html.Span(f"Pola #{i+1}", className=risk_badge.get(rule['risk'], 'badge badge-low-risk')),
                        html.Div("", style={'fontFamily': 'var(--font-heading)', 'fontSize': '1.5rem', 'fontWeight': 'bold', 'color': 'var(--accent-orange)', 'lineHeight': '1'})
                    ]),
                    html.P([
                        html.Span("Kondisi: ", style={'color': '#5a5a5f', 'fontWeight': '600'}),
                        rule['kondisi']
                    ], className="mb-1 small"),
                    html.P([
                        html.Span("Hasil: ", style={'color': '#000000', 'fontWeight': '600'}),
                        rule['hasil']
                    ], className="mb-2 small", style={'color': '#000000'}),
                    html.Hr(style={'borderColor': '#e0e0e8', 'margin': '8px 0'}),
                    html.P(peluang_p_children, className="mb-0 small text-muted")
                ]),
                width=6
            )
        )

    return html.Div(className="tab-content", children=[
        html.Div("Peta Peluang Bisnis Tersembunyi (Hasil Analisis ARM)", className="section-title"),
        html.P("Setiap titik mewakili satu peluang bisnis spesifik. Semakin besar dan terang titiknya, semakin tinggi kepastian bahwa nasabah akan mengambil produk tersebut, sehingga cocok dijadikan target Cross-Selling atau peringatan risiko.", className="mb-4 text-muted"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H4("Peta 100 Peluang Bisnis Terkuat"),
                dcc.Graph(figure=fig_arm, config={'displayModeBar': False}, responsive=True, style={'height': '520px'})
            ]), width=6),
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H4("10 Pola Perilaku Nasabah Terkuat"),
                dcc.Graph(figure=fig_network, config={'displayModeBar': False}, responsive=True, style={'height': '500px'}),
                html.P([
                    html.Span("●", style={'color': '#1d4ed8'}), " Kondisi → ",
                    html.Span("●", style={'color': '#0f766e'}), " Hasil"
                ], className="small text-muted text-center mt-2 mb-0")
            ]), width=6),
        ]),
        html.Div("10 Peluang Bisnis dari Pola Nasabah", className="section-title mt-2"),
        html.P("Setiap kartu menunjukkan satu pola tersembunyi dari data beserta rekomendasi aksi bisnis yang relevan.", className="mb-3 text-muted small"),
        dbc.Row(rules_html)
    ])


def tab_distributions():
    figs = []
    dist_insights = [
        {
            'col': 'loan_amount', 'label': 'Seberapa Besar Pinjaman Nasabah?',
            'color': '#2563eb',
            'insight': 'Mayoritas nasabah mengajukan pinjaman di kisaran moderat. Namun ada ekor panjang di kanan, yaitu segmen Jumbo Loan (nasabah agresif & investor) yang jumlahnya kecil tapi bernilai tinggi.',
            'opportunity': 'Jangan buat produk yang terlalu standar. Ada dua pasar: pasar massal (pinjaman kecil-menengah) dan pasar premium (Jumbo Loan). Keduanya butuh pendekatan yang berbeda.'
        },
        {
            'col': 'income', 'label': 'Sebaran Penghasilan Pemohon KPR',
            'color': '#059669',
            'insight': 'Sebagian besar pemohon berpenghasilan menengah. Tapi ada segmen kecil dengan penghasilan sangat tinggi yang justru meminjam di bawah kapasitasnya, yaitu kelompok Konservatif HNW.',
            'opportunity': 'Segmen berpenghasilan sangat tinggi ini adalah target utama Wealth Management. Mereka tidak datang mencari KPR, tapi bisa ditawarkan produk investasi & asuransi bermargin tinggi.'
        },
        {
            'col': 'interest_rate', 'label': 'Distribusi Suku Bunga yang Diterima',
            'color': '#c2410c',
            'insight': 'Suku bunga terkonsentrasi di 2 rentang: sangat rendah (program VA/Veteran) dan moderat (pasar umum). Adanya dua puncak ini membuktikan ada dua ekosistem pembiayaan yang terpisah.',
            'opportunity': 'Nasabah yang mendapat bunga sangat rendah hampir pasti adalah peserta program Veteran. Ini adalah segmen yang bisa di-bundle dengan produk finansial khusus untuk mempertahankan loyalitas mereka.'
        },
        {
            'col': 'combined_loan_to_value_ratio', 'label': 'Distribusi Rasio LTV',
            'color': '#e11d48',
            'insight': 'Mayoritas nasabah berada di LTV 60–95% (zona normal). Namun ada kasus ekstrem di atas 100%, di mana nilai pinjaman melampaui harga rumah. Ini adalah zona merah risiko kredit macet.',
            'opportunity': 'Nasabah dengan LTV di atas 95% perlu dimonitor ketat. Di sisi lain, nasabah dengan LTV di bawah 50% (uang muka besar) adalah kandidat terbaik untuk ditawari produk premium tambahan.'
        },
    ]
    if not df_raw.empty:
        for d in dist_insights:
            data_col = df_raw[d['col']].dropna()
            q99 = data_col.quantile(0.99)
            q01 = data_col.quantile(0.01)
            data_col = data_col[(data_col >= q01) & (data_col <= q99)]
            fig = px.histogram(
                data_col, nbins=50,
                color_discrete_sequence=[d['color']]
            )
            # px menerima Series polos sehingga judul sumbunya jatuh ke default
            # "value"/"count" -- diset eksplisit sesuai maksud semula.
            fig.update_xaxes(title_text='', tickfont=dict(size=10))
            fig.update_yaxes(title_text='Jumlah Pengajuan', tickfont=dict(size=10),
                             title_font=dict(size=11))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=PLOT_INK, family=PLOT_FONT),
                margin=dict(l=8, r=16, t=8, b=8), showlegend=False,
                bargap=0.04
            )
            d['fig'] = fig
    else:
        for d in dist_insights:
            d['fig'] = go.Figure()

    cards = []
    for d in dist_insights:
        cards.append(
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H5(d['label'], style={'color': d['color']}),
                dcc.Graph(figure=d['fig'], config={'displayModeBar': False}, responsive=True, style={'height': '240px'}),
                html.Hr(style={'borderColor': '#e0e0e8', 'margin': '12px 0'}),
                html.P(html.B("Apa yang terlihat: "), className="mb-1 small"),
                html.P(d['insight'], className="small text-muted mb-2"),
                html.P(html.B("Peluang Bisnis: "), className="mb-1 small"),
                html.P(d['opportunity'], className="small", style={'color': 'var(--accent-teal)'}),
            ]), width=6)
        )

    return html.Div(className="tab-content", children=[
        html.Div("Memahami Pasar dari Distribusi Data", className="section-title"),
        html.P(
            "Grafik distribusi menunjukkan 'bentuk' pasar KPR kita untuk melihat di mana konsentrasinya, seberapa merata atau terpolarisasi, "
            "dan di mana peluang bisnis tersembunyi berada. Setiap grafik dilengkapi dengan interpretasi dan rekomendasi langsung untuk tim bisnis.",
            className="mb-4 text-muted"
        ),
        dbc.Row(cards)
    ])


def tab_4_anomalies():
    # Bar chart untuk tipologi
    if not anomaly_counts.empty:
        plot_counts = anomaly_counts[anomaly_counts['Tipologi'] != 'Unclassified / Manual Review'].copy()
        plot_counts['Tipologi_Wrap'] = plot_counts['Tipologi_Indo'].map(wrap_label)
        fig_bar = px.bar(
            plot_counts,
            y='Tipologi_Wrap',
            x='Jumlah',
            orientation='h',
            color='Tipologi',
            color_discrete_map={
                'Unclassified / Manual Review': '#c2410c',
                'Rare Legitimate': '#059669',
                'Data Error': '#dc2626',
                'Potential Risk Signal': '#b45309'
            },
            text='Jumlah'
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=PLOT_INK, family=PLOT_FONT),
            showlegend=False,
            margin=dict(l=8, r=8, t=16, b=8),
            bargap=0.35
        )
        fig_bar.update_yaxes(title="", tickfont=dict(size=11))
        # Headroom 18% supaya label angka di ujung bar (textposition='outside')
        # tidak terpotong tepi kanan.
        fig_bar.update_xaxes(
            title_text='Jumlah Kasus', tickfont=dict(size=10),
            range=[0, plot_counts['Jumlah'].max() * 1.18]
        )
        fig_bar.update_traces(
            texttemplate='%{text}', textposition='outside', cliponaxis=False,
            textfont=dict(size=11, color=PLOT_INK)
        )
    else:
        fig_bar = go.Figure()

    # Donut chart untuk tier
    if not tier_counts.empty:
        # Susun urutan dan warna
        tier_order = ['Normal', 'Suspected (1 metode)', 'Confirmed (2 metode)', 'High Confidence']
        tier_colors = ['#334155', '#2563eb', '#b45309', '#dc2626']
        
        fig_tier = go.Figure(data=[go.Pie(
            labels=tier_counts['Tier'],
            values=tier_counts['Jumlah'],
            hole=.6,
            marker_colors=[
                '#dc2626' if t == 'High Confidence' else 
                '#b45309' if t == 'Confirmed (2 metode)' else 
                '#2563eb' if t == 'Suspected (1 metode)' else '#334155' 
                for t in tier_counts['Tier']
            ],
            textinfo='percent',
            insidetextfont=dict(color='#ffffff', size=13)
        )])
        fig_tier.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=PLOT_INK),
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
            annotations=[dict(text='<b>Deteksi<br>Berlapis</b>', x=0.5, y=0.5, font_size=14, showarrow=False, font_color=PLOT_INK)]
        )
    else:
        fig_tier = go.Figure()

    # Outlier Scatter Plot: tampilkan posisi anomali vs data normal
    fig_outlier = go.Figure()
    if not df_raw.empty and not df_priority.empty:
        normal_sample = df_raw[['loan_amount', 'income']].dropna().sample(min(800, len(df_raw)))
        fig_outlier.add_trace(go.Scatter(
            x=normal_sample['income'], y=normal_sample['loan_amount'],
            mode='markers', name='Nasabah Normal',
            marker=dict(color='rgba(0,0,0,0.18)', size=5),
            hovertemplate='Income: %{x}<br>Loan: %{y}<extra></extra>'
        ))
        # Hanya plot prioritas
        outlier_sample = df_priority[['income', 'loan_amount', 'typology']].dropna().head(400)
        color_map = {'Potential Risk Signal': '#b45309', 'Data Error': '#dc2626', 'Rare Legitimate': '#059669', 'Unclassified / Manual Review': '#c2410c'}
        for typ, grp in outlier_sample.groupby('typology'):
            fig_outlier.add_trace(go.Scatter(
                x=grp['income'], y=grp['loan_amount'],
                mode='markers', name=tipologi_map.get(typ, typ),
                marker=dict(color=color_map.get(typ, '#fff'), size=9, symbol='diamond',
                            line=dict(width=1, color='#000000')),
                hovertemplate='Income: %{x}<br>Loan: %{y}<extra></extra>'
            ))
    fig_outlier.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=PLOT_INK, family=PLOT_FONT),
        margin=dict(l=8, r=16, t=16, b=8),
        # Legenda didorong cukup jauh ke bawah agar tidak menimpa judul sumbu-x;
        # automargin yang menyediakan ruangnya, bukan margin bawah hardcoded.
        legend=dict(orientation='h', yanchor='top', y=-0.22, xanchor='center', x=0.5,
                    font=dict(size=11)),
        xaxis=dict(title=dict(text='Pendapatan Nasabah (Income)', standoff=16),
                   tickfont=dict(size=10)),
        yaxis=dict(title=dict(text='Nilai Pinjaman (Loan Amount)', standoff=16),
                   tickfont=dict(size=10))
    )

    return html.Div(className="tab-content", children=[
        html.Div("Sistem Peringatan Dini: Deteksi Kasus Tidak Wajar (Anomali)", className="section-title"),
        html.P("Dari 99.994 pengajuan kredit, sistem AI mendeteksi kasus-kasus aneh yang berpotensi menjadi risiko kredit atau error data. Kasus ini disaring melalui 3 metode pengawasan cerdas.", className="mb-4 text-muted"),
        
        # --- BARIS 1: Metrik Proses ---
        dbc.Row([
            dbc.Col(html.Div(className="glass-card metric-card", children=[
                html.Div("Total Anomali Ditemukan", className="metric-title"),
                html.Div(fmt_count(len(df_anomalies)), className="metric-value")
            ]), width=3),
            dbc.Col(html.Div(className="glass-card metric-card", style={'borderColor': '#000000'}, children=[
                html.Div("Prioritas Tinggi (Confirmed/HC)", className="metric-title"),
                html.Div(fmt_count(len(df_priority)), className="metric-value", style={'color': '#e11d48'}),
                html.Div("Kasus Paling Janggal", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=3),
            dbc.Col(html.Div(className="glass-card metric-card", children=[
                html.Div("Metode Pengawasan", className="metric-title"),
                html.Div("3 Lapis", className="metric-value"),
                html.Div("IQR, Z-Score, Isolation Forest", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=6),
        ], className="mb-4"),

        # --- BARIS 2: Cara Kerja & Tier ---
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Tingkat Kepercayaan Sistem (Tier)"),
                html.P("Semakin banyak metode yang menangkap kejanggalan, semakin tinggi prioritas kasus tersebut.", className="small text-muted mb-2"),
                dcc.Graph(figure=fig_tier, config={'displayModeBar': False}, responsive=True, style={'height': '300px'})
            ]), width=5),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Bagaimana Sistem Menangkap Anomali?"),
                html.P("Kasus tidak hanya ditolak karena satu angka aneh, tetapi dianalisis dari berbagai sisi secara bersamaan:", className="small text-muted mb-3"),
                
                html.Div(className="mb-3", children=[
                    html.Strong("1. Filter IQR (Kewajaran Nilai)", style={'color': '#000000'}),
                    html.P("Melihat batas normal nilai tiap bagian, misalnya gaji terlalu ekstrem.", className="small text-muted mb-1")
                ]),
                html.Div(className="mb-3", children=[
                    html.Strong("2. Z-Score (Distribusi Ekstrem)", style={'color': '#000000'}),
                    html.P("Mendeteksi angka yang benar-benar mustahil secara statistik normal.", className="small text-muted mb-1")
                ]),
                html.Div(className="mb-3", children=[
                    html.Strong("3. Isolation Forest (Anomali Kombinasi)", style={'color': '#000000'}),
                    html.P("Menangkap kombinasi aneh. Misalnya: Gaji tampak wajar, hutang tampak wajar, tapi jika digabung (gaji kecil berhutang besar), AI akan menangkapnya.", className="small text-muted mb-0")
                ])
            ]), width=7),
        ], className="mb-4"),
        
        # --- BARIS 3: Visualisasi Utama ---
        html.Div(f"Peta Kasus Prioritas ({fmt_count(len(df_priority))} Kasus High Confidence & Confirmed)", className="section-title mt-4"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card mb-4 h-100", children=[
                html.H4(f"Posisi {fmt_count(len(df_priority))} Nasabah Paling Janggal vs Normal"),
                html.P("Titik berwarna adalah kasus prioritas. Titik abu-abu adalah data normal. Terlihat jelas anomali berada di luar pola umum.", className="small text-muted mb-2"),
                dcc.Graph(figure=fig_outlier, config={'displayModeBar': False}, responsive=True, style={'height': '420px'})
            ]), width=7),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Pengelompokan Jenis Kasus Prioritas"),
                dcc.Graph(figure=fig_bar, config={'displayModeBar': False}, responsive=True, style={'height': '420px'})
            ]), width=5),
        ], className="mb-4"),
        
        # --- BARIS 4: Tipologi ---
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", style={'borderLeft': '4px solid #b45309'}, children=[
                html.H5(f"Sinyal Risiko Kredit Tinggi ({fmt_count(priority_typology_count('Potential Risk Signal'))} Kasus)", className="mb-2", style={'color': '#b45309'}),
                html.P(html.B("Definisi:"), className="small mb-1"),
                html.P("Pendapatan rendah (di bawah rata-rata) dikombinasikan dengan pinjaman Jumbo (sangat besar) dan leverage/utang yang sangat agresif.", className="small text-muted mb-2"),
                html.P(html.B("Aksi Bisnis:"), className="small mb-1"),
                html.P("Kirim ke tim Underwriting untuk verifikasi manual secara mendalam (enhanced verification) sebelum persetujuan kredit.", className="small mb-0")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", style={'borderLeft': '4px solid #dc2626'}, children=[
                html.H5(f"Data Error ({fmt_count(priority_typology_count('Data Error'))} Kasus)", className="mb-2", style={'color': '#dc2626'}),
                html.P(html.B("Definisi:"), className="small mb-1"),
                html.P("Nilai finansial yang melanggar batas fisik/logika bisnis. Misalnya: Suku bunga 0% atau rasio utang vs nilai rumah (LTV) > 150%.", className="small text-muted mb-2"),
                html.P(html.B("Aksi Bisnis:"), className="small mb-1"),
                html.P("Kembalikan ke tim Data Engineering (Bukan ke analis risiko) untuk koreksi pada sistem penginputan aplikasi kredit.", className="small mb-0")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", style={'borderLeft': '4px solid #059669'}, children=[
                html.H5(f"Profil Konservatif / Prospek ({fmt_count(priority_typology_count('Rare Legitimate'))} Kasus)", className="mb-2", style={'color': '#059669'}),
                html.P(html.B("Definisi:"), className="small mb-1"),
                html.P("Nasabah sangat kaya (Ultra High-Net-Worth) namun mengambil pinjaman yang sangat kecil dengan uang muka raksasa.", className="small text-muted mb-2"),
                html.P(html.B("Aksi Bisnis:"), className="small mb-1"),
                html.P("JANGAN tandai sebagai risiko. Jadikan daftar ini sebagai prospek target (leads) untuk produk Priority Banking atau Wealth Management.", className="small mb-0")
            ]), width=4)
        ])
    ])

def build_crossphase_heatmap():
    """Heatmap konsentrasi: pola ARM (Phase 3) & tipologi anomali (Phase 4) per segmen (Phase 2).

    Nilai = rasio konsentrasi terhadap proporsi populasi tiap segmen
    (Grup 1=42,6% · Grup 2=25,3% · Grup 3=32,1%). 1,00x = tersebar merata;
    >1,25x = benar-benar menumpuk di segmen itu. Angka dihitung dengan menempelkan
    label cluster Phase 2 ke baris yang cocok pola ARM dan ke baris anomali via row_index.
    """
    cols = ['Grup 1<br>Kelas Menengah', 'Grup 2<br>Peminjam Agresif', 'Grup 3<br>Konservatif HNW']
    rows = [
        'Data Error (179)',
        'Rumah manufactured (#2,#10)',
        'Pinjaman VA/Veteran (#4,#7,#9)',
        'Sinyal Risiko Kredit (76)',
        'Profil Konservatif/Prospek (372)',
        'Perlu Tinjauan Manual (2.693)',
        'Pinjaman Jumbo (#4,#5,#6)',
        'Multifamily/Investor (#3,#5,#6)',
    ]
    ratio = [
        [1.33, 0.79, 0.73],
        [1.20, 0.56, 1.09],
        [0.99, 1.17, 0.89],
        [0.93, 1.45, 0.74],
        [0.52, 1.53, 1.22],
        [0.60, 1.93, 0.79],
        [0.51, 1.43, 1.31],
        [1.75, 0.75, 0.20],
    ]
    pct = [
        [56.4, 20.1, 23.5],
        [50.9, 14.2, 34.9],
        [42.0, 29.5, 28.5],
        [39.5, 36.8, 23.7],
        [22.3, 38.7, 39.0],
        [25.7, 49.0, 25.3],
        [21.7, 36.2, 42.1],
        [74.6, 19.1, 6.4],
    ]
    # Skala diverging berpusat di 1,00x: biru = kurang dari proporsi populasi,
    # oranye/merah = menumpuk. Titik tengah dikunci di 1.0 lewat zmid supaya
    # warna netral benar-benar berarti "tersebar merata", bukan rata-rata data.
    fig = go.Figure(data=go.Heatmap(
        z=ratio, x=cols, y=rows,
        customdata=pct,
        colorscale=[[0, '#5b8fd4'], [0.35, '#a9c8ec'], [0.5, '#f0f0fa'],
                    [0.68, '#f5c26b'], [1, '#e8798f']],
        zmid=1.0, zmin=0.2, zmax=2.0,
        text=[[f"{r:.2f}x" for r in row] for row in ratio],
        texttemplate="%{text}",
        textfont=dict(size=12, family=PLOT_FONT),
        hovertemplate=('<b>%{y}</b><br>%{x}<br>'
                       'Porsi di segmen ini: %{customdata:.1f}%<br>'
                       'Konsentrasi: %{z:.2f}x populasi<extra></extra>'),
        colorbar=dict(
            # Judul dipasang di sisi bar (bukan di atasnya) supaya tidak
            # bertabrakan dengan tick teratas yang dua baris.
            title=dict(text='Konsentrasi', font=dict(size=11), side='right'),
            tickvals=[0.5, 1.0, 1.5, 2.0],
            ticktext=['0,5x<br>kurang', '1,0x<br>merata', '1,5x', '2,0x<br>menumpuk'],
            tickfont=dict(size=9), len=0.78, y=0.5, yanchor='middle',
            thickness=14, outlinewidth=0
        )
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=PLOT_INK, family=PLOT_FONT),
        margin=dict(l=8, r=8, t=8, b=8),
        xaxis=dict(side='top', tickfont=dict(size=10), automargin=True),
        yaxis=dict(tickfont=dict(size=10), autorange='reversed', automargin=True)
    )
    return fig


def tab_strategic_recommendations():
    fig_cross = build_crossphase_heatmap()

    # Streamlined strategic recommendations focusing purely on key points and core actions
    recommendations = [
        {
            'rank': 1,
            'title': 'Program KPR Investasi Properti Multifamily',
            'impact': 'VERY HIGH',
            'impact_color': '#e11d48',
            'border_color': '#e11d48',
            'key_point': 'Investor Multifamily secara konsisten menyasar Pinjaman Jumbo bernilai tinggi — namun 74,6% dari mereka justru berada di segmen Kelas Menengah (Grup 1), bukan segmen premium. Posisikan produknya sebagai KPR investasi terjangkau, bukan produk mewah.',
            'actions': [
                'Paket KPR Jumbo Investasi + fasilitas kredit modal kerja renovasi',
                'Kemitraan eksklusif dengan pengembang apartemen/ruko di lokasi strategis',
                'Layanan cash management terintegrasi untuk kelola arus kas sewa'
            ]
        },
        {
            'rank': 2,
            'title': 'Layanan Wealth Management Nasabah Ultra-Kaya',
            'impact': 'HIGH',
            'impact_color': '#059669',
            'border_color': '#059669',
            'key_point': 'Segmen Konservatif HNW (32,08%) berpendapatan tertinggi ($207.565) tapi meminjam hanya 1,53x pendapatan — kelipatan terendah dari semua segmen. Target utama produk non-KPR bermargin tinggi.',
            'actions': [
                'Konversi 372 nasabah anomali konservatif jadi prospek Priority Banking — ambil lintas segmen, jangan hanya Grup 3 (hanya 39% ada di sana)',
                'Cross-selling Reksa Dana, Asuransi Jiwa Premium, dan Deposito',
                'Tingkatkan Fee-based Income tanpa menambah risiko kredit'
            ]
        },
        {
            'rank': 3,
            'title': 'KPR Mikro "Rumah Pertama" Manufactured Housing',
            'impact': 'HIGH',
            'impact_color': '#2563eb',
            'border_color': '#2563eb',
            'key_point': 'Ceruk pasar spesifik nasabah muda (<25 tahun) yang secara konsisten memilih Manufactured Housing sebagai hunian pertama.',
            'actions': [
                'KPR Mikro Fast-Track khusus pemuda dengan uang muka fleksibel',
                'Skema cicilan progresif sesuai pertumbuhan karier nasabah',
                'Kanal pengajuan digital self-service yang cepat dan efisien'
            ]
        },
        {
            'rank': 4,
            'title': 'Integrasi Sistem Deteksi Anomali Kredit Otomatis',
            'impact': 'HIGH',
            'impact_color': '#b45309',
            'border_color': '#b45309',
            'key_point': 'Mencegah risiko kredit dari 3.320 kasus anomali kombinasi yang berpotensi lolos dari pemeriksaan underwriting manual biasa.',
            'actions': [
                'Integrasikan model Isolation Forest ke pipeline persetujuan kredit',
                'Verifikasi mendalam untuk 76 kasus sinyal risiko kredit tinggi',
                'Eskalasi 179 kasus data error ke tim Data Engineering untuk perbaikan'
            ]
        },
        {
            'rank': 5,
            'title': 'Program KPR Jumbo Khusus Veteran (VA Jumbo)',
            'impact': 'MEDIUM',
            'impact_color': '#6d28d9',
            'border_color': '#6d28d9',
            'key_point': 'Pasar loyal nasabah Veteran dengan pola pembiayaan bersubsidi pemerintah yang sangat terprediksi dan berisiko rendah.',
            'actions': [
                'Kampanye VA Jumbo Loan dengan bunga bersaing dan bebas biaya admin',
                'Cross-sell produk tabungan/investasi untuk nasabah cash-out refinance',
                'Optimalisasi sekuritisasi Ginnie Mae untuk pendanaan berkelanjutan'
            ]
        },
        {
            'rank': 6,
            'title': 'Konsolidasi Utang & Proteksi KPR Kedua',
            'impact': 'MEDIUM',
            'impact_color': '#c2410c',
            'border_color': '#c2410c',
            'key_point': 'Mitigasi risiko kredit pada KPR kedua dari investor swasta yang memiliki kecenderungan utang melampaui nilai rumah (LTV >100%).',
            'actions': [
                'Program konsolidasi utang dengan suku bunga tetap khusus',
                'Wajib asuransi kredit tambahan untuk seluruh skema KPR kedua',
                'Monitoring aktif rasio LTV untuk peminjam di atas 95%'
            ]
        },
    ]

    # Ghost outlined pill chips — hue tetap dipertahankan karena membawa makna
    # tingkat dampak (data), bukan dekorasi.
    impact_badge_style = {
        'VERY HIGH': {'backgroundColor': 'transparent', 'color': '#be123c', 'border': '1px solid rgba(190,18,60,0.4)'},
        'HIGH': {'backgroundColor': 'transparent', 'color': '#5a5a5f', 'border': '1px solid #e0e0e8'},
        'MEDIUM': {'backgroundColor': 'transparent', 'color': '#b45309', 'border': '1px solid rgba(180,83,9,0.4)'},
    }

    rank_cards = []
    for rec in recommendations:
        badge_s = impact_badge_style.get(rec['impact'], impact_badge_style['MEDIUM'])
        action_lis = [html.Li(a, className="mb-1") for a in rec['actions']]

        card = dbc.Col(
            html.Div(className="glass-card h-100 p-4", style={
                'borderLeft': f'4px solid {rec["border_color"]}',
                'display': 'flex',
                'flexDirection': 'column',
                'justifyContent': 'space-between'
            }, children=[
                html.Div([
                    # Header: Rank + Title + Impact Badge
                    html.Div(className="d-flex align-items-center justify-content-between mb-3", children=[
                        html.Div(className="d-flex align-items-center gap-2", children=[
                            html.Span(f"#{rec['rank']}", style={
                                'backgroundColor': 'transparent',
                                'color': '#000000',
                                'border': '1px solid #000000',
                                'fontWeight': '700',
                                'fontSize': '0.72rem',
                                'letterSpacing': '1.17px',
                                'padding': '4px 12px',
                                'borderRadius': '32px',
                                'fontFamily': 'var(--font-heading)'
                            }),
                            html.H5(rec['title'], className="mb-0", style={
                                'fontFamily': 'var(--font-heading)',
                                'fontWeight': '700',
                                'fontSize': '1.05rem',
                                'color': '#000000'
                            })
                        ]),
                        html.Span(f"{rec['impact']}", style={
                            **badge_s,
                            'padding': '4px 12px',
                            'borderRadius': '32px',
                            'fontSize': '0.68rem',
                            'fontWeight': '700',
                            'letterSpacing': '0.96px',
                            'whiteSpace': 'nowrap'
                        })
                    ]),

                    # Poin Utama
                    html.P(rec['key_point'], className="small mb-3", style={
                        'color': '#5a5a5f',
                        'lineHeight': '1.5',
                        'fontSize': '0.88rem'
                    }),

                    # Rekomendasi Aksi
                    html.Div([
                        html.Strong("Rekomendasi Aksi:", style={'color': '#5a5a5f', 'fontSize': '0.8rem', 'display': 'block', 'marginBottom': '6px'}),
                        html.Ul(action_lis, className="ps-3 mb-0 small text-muted", style={'lineHeight': '1.4'})
                    ])
                ])
            ]),
            width=6
        )
        rank_cards.append(card)

    return html.Div(className="tab-content", children=[
        # Header
        html.Div(className="text-center mb-4", children=[
            html.H2("Business Strategic Recommendations", style={
                'fontFamily': 'var(--font-heading)',
                'fontWeight': '700',
                'color': 'var(--text-primary)',
                'fontSize': '2.1rem',
                'marginBottom': '6px'
            }),

        ]),

        # --- SINTESIS LINTAS-FASE: dasar bukti di balik rekomendasi ---
        html.Div("Dasar Bukti: Menyilangkan Ketiga Analisis", className="section-title"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.P([
                    "Rekomendasi di bawah tidak berdiri di atas satu analisis saja. Kami menempelkan label segmen (dari Clustering) "
                    "ke setiap pola perilaku (dari ARM) dan setiap kasus anomali (dari Anomaly Detection), lalu mengukur ",
                    html.B("di segmen mana masing-masing benar-benar menumpuk"), "."
                ], className="small text-muted mb-2"),
                dcc.Graph(figure=fig_cross, config={'displayModeBar': False}, responsive=True, style={'height': '420px'}),
                html.P([
                    html.B("Cara membacanya: "),
                    "1,00x berarti tersebar merata mengikuti besar populasi segmen. Di atas 1,25x (warna oranye/merah) berarti "
                    "benar-benar menumpuk di segmen itu. Di bawah 0,8x (biru) berarti justru jarang ditemukan di sana."
                ], className="small text-muted mt-2 mb-3"),
                dbc.Row([
                    dbc.Col(html.Div(className="glass-card h-100", style={'borderLeft': '3px solid #e11d48'}, children=[
                        html.Div("Investor multifamily ada di segmen mass-market, bukan segmen kaya", className="small mb-1", style={'fontWeight': '700', 'letterSpacing': '0.8px', 'textTransform': 'uppercase', 'color': '#000000'}),
                        html.P("74,6% (1,75x — konsentrasi tertinggi di seluruh analisis) berada di Grup 1, dan hampir tidak ada di Grup 3 (0,20x). Mereka membeli rumah petak/apartemen lama untuk disewakan, bukan properti mewah.", className="small text-muted mb-0"),
                        html.P("→ Produk KPR Investasi jangan diposisikan sebagai produk premium.", className="small mb-0", style={'color': '#000000'})
                    ]), width=6, className="mb-3"),
                    dbc.Col(html.Div(className="glass-card h-100", style={'borderLeft': '3px solid #b45309'}, children=[
                        html.Div("Grup 2 adalah pusat gravitasi hampir semua anomali", className="small mb-1", style={'fontWeight': '700', 'letterSpacing': '0.8px', 'textTransform': 'uppercase', 'color': '#000000'}),
                        html.P("Hanya 25,3% populasi, tapi memuat 49,0% kasus yang perlu diperiksa manusia (1,93x — tertinggi). Ini menguatkan temuan segmentasi bahwa Grup 2 punya beban pinjaman terberat (2,47x pendapatan) — dua metode berbeda menunjuk segmen yang sama.", className="small text-muted mb-0"),
                        html.P("→ Alokasikan kapasitas underwriting mengikuti Grup 2, jangan dibagi rata.", className="small mb-0", style={'color': '#000000'})
                    ]), width=6, className="mb-3"),
                    dbc.Col(html.Div(className="glass-card h-100", style={'borderLeft': '3px solid #059669'}, children=[
                        html.Div("Prospek wealth management tidak hanya di Grup 3", className="small mb-1", style={'fontWeight': '700', 'letterSpacing': '0.8px', 'textTransform': 'uppercase', 'color': '#000000'}),
                        html.P("Dugaan awal: 372 kasus \"Profil Konservatif\" = Grup 3. Kenyataannya hanya 39,0% di Grup 3, sementara 38,7% ada di Grup 2 dengan konsentrasi lebih tinggi (1,53x vs 1,22x).", className="small text-muted mb-0"),
                        html.P("→ Menyaring prospek hanya dari Grup 3 akan kehilangan ~4 dari 10 prospek terbaik.", className="small mb-0", style={'color': '#000000'})
                    ]), width=6, className="mb-3"),
                    dbc.Col(html.Div(className="glass-card h-100", style={'borderLeft': '3px solid #2563eb'}, children=[
                        html.Div("Program Veteran memotong semua kelas ekonomi", className="small mb-1", style={'fontWeight': '700', 'letterSpacing': '0.8px', 'textTransform': 'uppercase', 'color': '#000000'}),
                        html.P("Pinjaman VA menyebar hampir merata (0,89x–1,17x) di ketiga segmen — status veteran tidak terikat kelas ekonomi. Sementara pinjaman jumbo justru pembeda paling tegas (Grup 1 hanya 0,51x).", className="small text-muted mb-0"),
                        html.P("→ Program bundling veteran butuh varian untuk ketiga segmen, bukan satu paket seragam.", className="small mb-0", style={'color': '#000000'})
                    ]), width=6, className="mb-3"),
                ]),
                html.P([
                    html.B("Batas klaim: "),
                    "semua angka di atas adalah konsentrasi statistik, bukan sebab-akibat. Menumpuknya investor multifamily di Grup 1 "
                    "tidak berarti berada di Grup 1 menyebabkan seseorang jadi investor properti. Label segmen juga dibentuk tanpa variabel "
                    "harga kredit (lihat tab 7), jadi ini membandingkan segmen pendapatan–pinjaman–wilayah dengan pola produk, bukan segmen risiko formal."
                ], className="small mb-0", style={'color': '#5a5a5f', 'fontStyle': 'italic'})
            ]), width=12),
        ]),

        html.Div("Rekomendasi Prioritas", className="section-title"),

        # Priority Legend
        html.Div(className="d-flex justify-content-center gap-4 mb-4 flex-wrap", children=[
            html.Div(className="d-flex align-items-center", children=[
                html.Div(style={'width': '10px', 'height': '10px', 'borderRadius': '50%', 'backgroundColor': '#be123c', 'marginRight': '6px'}),
                html.Span("Very High Impact", className="small text-muted")
            ]),
            html.Div(className="d-flex align-items-center", children=[
                html.Div(style={'width': '10px', 'height': '10px', 'borderRadius': '50%', 'backgroundColor': '#5a5a5f', 'marginRight': '6px'}),
                html.Span("High Impact", className="small text-muted")
            ]),
            html.Div(className="d-flex align-items-center", children=[
                html.Div(style={'width': '10px', 'height': '10px', 'borderRadius': '50%', 'backgroundColor': '#b45309', 'marginRight': '6px'}),
                html.Span("Medium Impact", className="small text-muted")
            ]),
        ]),

        # Cards Layout Grid with clean row spacing
        dbc.Row(rank_cards, className="g-4 mb-4")
    ])


def tab_methodology():
    # Silhouette by K chart (rationale for K=3)
    k_vals = [2, 3, 4, 5, 6]
    sil_vals = [0.1405, 0.1535, 0.1338, 0.1516, 0.1516]
    bar_colors = ['#334155' if k != 3 else '#059669' for k in k_vals]
    fig_sil = go.Figure(data=[go.Bar(
        x=[f"K={k}" for k in k_vals], y=sil_vals,
        marker_color=bar_colors,
        text=[f"{v:.4f}" for v in sil_vals], textposition='outside'
    )])
    fig_sil.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=PLOT_INK, family=PLOT_FONT),
        margin=dict(l=8, r=8, t=16, b=8), showlegend=False,
        yaxis=dict(title=dict(text='Silhouette Score', standoff=12), range=[0, 0.19],
                   showgrid=True, gridcolor=PLOT_GRID, automargin=True),
        xaxis=dict(showgrid=False)
    )

    pipeline_rows = [
        ("1. Preprocessing", "Median/Mode Imputation, One-Hot Encoding, Quantile Binning, StandardScaler",
         "Median dipilih (bukan mean) karena data finansial right-skewed — mean akan tertarik outlier. One-hot dipakai agar tidak memaksakan urutan palsu pada kategori nominal."),
        ("2. Segmentation", "K-Means (K=3) + DBSCAN + Hierarchical/Ward untuk validasi silang",
         "K=3 dipilih karena silhouette tertinggi (0,1535) di antara K=2..6 DAN satu-satunya yang menghasilkan interpretasi bisnis yang jelas (mass-market / agresif / konservatif-HNW)."),
        ("3. Association Rules", "Apriori + domain-based binning (bukan qcut otomatis)",
         "Domain binning dipilih setelah qcut terbukti gagal pada loan_term (74% data terjebak di 1 bin, 360 bulan) — batas domain (mis. LTV 80% = ambang bebas PMI) punya makna bisnis langsung."),
        ("4. Anomaly Detection", "IQR + Z-score (univariat) + Isolation Forest (multivariat), cross-ref ke cluster Fase 2",
         "Tiga metode dipakai berlapis karena masing-masing menangkap jenis anomali berbeda — IQR/Z-score bisa saling menutupi (masking effect), Isolation Forest menangkap kombinasi nilai yang wajar sendiri-sendiri tapi janggal bersama."),
        ("5. Knowledge Discovery", "Sintesis lintas-fase + dashboard interaktif",
         "Setiap insight di dashboard ini disyaratkan muncul di ≥2 metode (lihat Corroboration) sebelum ditulis sebagai temuan utama, bukan hasil satu model saja."),
    ]
    pipeline_table = dbc.Table([
        html.Thead(html.Tr([html.Th("Fase"), html.Th("Metode & Parameter Kunci"), html.Th("Rasionalisasi (Kenapa)")])),
        html.Tbody([
            html.Tr([html.Td(html.B(p)), html.Td(m, className="small"), html.Td(r, className="small text-muted")])
            for p, m, r in pipeline_rows
        ])
    ], bordered=False, hover=True, responsive=True, className="align-middle")

    corroboration_cards = [
        {"title": "Silhouette Score (K=3)", "value": "0,1535", "desc": "Tertinggi di antara K=2..6 pada sampel 10.000 baris — dasar kuantitatif pemilihan K=3.", "color": "#2563eb"},
        {"title": "Adjusted Rand Index", "value": "0,356", "desc": "K-Means vs Agglomerative-Ward (n=800): korroborasi MODERAT, jujur bukan sempurna. Cluster HNW paling stabil lintas metode.", "color": "#059669"},
        {"title": "Reproduksi DBSCAN", "value": "7,26%", "desc": "Noise rate direproduksi ULANG persis sama (363/5.000) di Fase 4 dari Fase 2 — bukti pipeline deterministik & konsisten.", "color": "#b45309"},
        {"title": "Overlap IF x DBSCAN", "value": "32,0%", "desc": "Anomali Isolation Forest (finansial) vs noise DBSCAN (geografis-demografis): overlap sebagian, BUKAN 100% — keduanya sengaja memotret sudut pandang berbeda.", "color": "#e11d48"},
    ]

    limitations = [
        ("Korelasi, bukan kausalitas", "Semua pola (cluster, association rules, anomali) adalah asosiasi statistik. \"Usia < 25 → Manufactured Housing\" (lift 19,7x) menunjukkan ko-kemunculan, BUKAN hubungan sebab-akibat. Rekomendasi bisnis di sini adalah hipotesis yang layak diuji lebih lanjut (mis. A/B test), bukan kepastian."),
        ("Snapshot satu tahun (2022)", "2022 adalah tahun kenaikan suku bunga agresif The Fed. Pola bisa bergeser signifikan di tahun lain — generalisasi lintas tahun perlu divalidasi ulang, tidak diasumsikan otomatis berlaku."),
        ("Clustering tak mencakup harga kredit langsung", "interest_rate, LTV, rate_spread, DTI tersimpan sebagai teks di sumber data sehingga otomatis ter-exclude dari filter numerik Fase 2. Tiga segmen nasabah terbentuk dari loan_amount + income + konteks wilayah — bukan langsung dari suku bunga/leverage individual."),
        ("Kode demografis diperlakukan kontinu", "Kode ras/etnis numerik ikut sebagai fitur jarak Euclidean K-Means walau bersifat nominal (tanpa urutan bermakna). Nama segmen merujuk pada profil finansial dominan, bukan klasifikasi demografis — tidak untuk keputusan berbasis ras/etnis individu."),
        ("Sampling untuk algoritma berat", "DBSCAN (5.000 baris) & Hierarchical (800 baris) memakai subsample acak berseed tetap (reproducible) karena kompleksitas O(N²)/O(N³) — bukan sensus penuh 99.994 baris."),
        ("Representativitas data HMDA", "Data hanya mencakup pemohon yang benar-benar mengajukan KPR ke lembaga pelapor — tidak merepresentasikan rumah tangga yang tidak mengajukan sama sekali."),
    ]

    return html.Div(className="tab-content", children=[
        html.Div("Metodologi, Validitas & Batasan Analisis", className="section-title"),
        html.P("Setiap insight bisnis di dashboard ini bersandar pada pipeline yang bisa diaudit: pilihan metode punya alasan, klaim utama dikonfirmasi lebih dari satu metode, dan kami menyatakan secara terbuka apa yang TIDAK bisa diklaim dari analisis ini.", className="mb-4 text-muted"),

        html.H4("Pipeline & Rasionalisasi Tiap Fase", className="mb-3", style={'color': 'var(--accent-blue)'}),
        html.Div(className="glass-card mb-4", children=[pipeline_table]),

        html.H4("Validasi Korroborasi Kuantitatif", className="mb-3 mt-5", style={'color': 'var(--accent-teal)'}),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100 text-center", style={'borderTop': f'3px solid {c["color"]}'}, children=[
                html.Div(c["title"], className="metric-title mb-2"),
                html.Div(c["value"], className="stat-highlight", style={'color': c["color"]}),
                html.P(c["desc"], className="small text-muted mt-2 mb-0")
            ]), width=3) for c in corroboration_cards
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Kenapa K=3? (Silhouette Score per K)", className="mb-3"),
                dcc.Graph(figure=fig_sil, config={'displayModeBar': False}, responsive=True, style={'height': '260px'}),
                html.P("Catatan jujur: nilai absolut ~0,15 tergolong sedang (bukan pemisahan tajam >0,5) — wajar untuk data finansial kontinu yang tumpang-tindih alami. K=3 adalah pilihan RELATIF TERBAIK, bukan klaim cluster terpisah sempurna.", className="small text-muted mt-2 mb-0")
            ]), width=12),
        ], className="mb-4"),

        html.H4("Batasan & Kejujuran Analisis (Limitations)", className="mb-3 mt-5", style={'color': 'var(--accent-rose)'}),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", style={'borderLeft': '3px solid #e11d48'}, children=[
                html.H5(title, className="mb-2", style={'color': '#e11d48', 'fontSize': '1rem'}),
                html.P(desc, className="small text-muted mb-0")
            ]), width=6, className="mb-3") for title, desc in limitations
        ]),
    ])

# Main Layout
# tab_id wajib diisi eksplisit di dash-bootstrap-components 2.x — tanpa itu tidak
# ada tab yang ditandai aktif, sehingga active_label_class_name tidak pernah kena.
TAB_SPECS = [
    ("tab-1", "1. Common Information", tab_1_executive),
    ("tab-2", "2. Segmentation Nasabah", tab_segmentation),
    ("tab-3", "3. Visualization ARM", tab_arm_visualization),
    ("tab-4", "4. Market Distribution", tab_distributions),
    ("tab-5", "5. Anomali Detection", tab_4_anomalies),
    ("tab-6", "6. Strategic Recommendation", tab_strategic_recommendations),
    ("tab-7", "7. Metodologi & Validitas", tab_methodology),
]

app.layout = html.Div([
    create_header(),
    dbc.Container([
        dbc.Tabs([
            dbc.Tab(
                builder(),
                label=label,
                tab_id=tab_id,
                label_class_name="custom-tab",
                active_label_class_name="custom-tab-selected",
            )
            for tab_id, label, builder in TAB_SPECS
        ], active_tab="tab-1", className="custom-tabs"),
        
        html.Div(className="dashboard-footer", children=[
            "© 2026 Insight Communicator | HMDA Data Mining Project - Phase 5"
        ])
    ], fluid=True, className="px-5")
])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run(debug=True, port=port)
