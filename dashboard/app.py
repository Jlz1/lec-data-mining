import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Inisialisasi App
app = dash.Dash(
    __name__, 
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True
)
app.title = "HMDA 2022 Data Mining Dashboard"

# Load data (dummy agregasi untuk performa UI jika file berat, namun kita ambil data asli dari phase sebelumnya)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rules_path = os.path.join(base_dir, 'reports', '3-association-rules.csv')
anomalies_path = os.path.join(base_dir, 'reports', '4-anomalies.csv')
pca_path = os.path.join(base_dir, 'reports', 'pca_clusters.csv')
cluster_summary_path = os.path.join(base_dir, 'reports', 'cluster_profile_summary.csv')
data_path = os.path.join(base_dir, 'data', 'processed_dataset.csv')

try:
    df_rules = pd.read_csv(rules_path)
    top_10_rules = df_rules.head(10).copy()
    
    # Translate to very simple business language but keep financial terms
    business_rules = [
        {"kondisi": "KPR kedua (Piggyback/HELOC) dari investor swasta", "hasil": "Utang melampaui nilai rumah (LTV > 100%)", "peluang_bisnis": "Tawarkan program konsolidasi utang (Debt Consolidation) dengan suku bunga tetap khusus atau produk asuransi kredit tambahan (credit insurance) untuk melindungi nasabah dan memitigasi risiko kredit macet bagi bank.", "lift": 38.02, "risk": "high"},
        {"kondisi": "Nasabah muda (di bawah 25 tahun) + cicilan menengah", "hasil": "Memilih properti Manufactured Housing", "peluang_bisnis": "Luncurkan paket pembiayaan KPR mikro khusus 'Rumah Pertama Generasi Muda' untuk Manufactured Housing dengan uang muka fleksibel dan opsi cicilan progresif guna menarik pasar nasabah pemula (first-time buyers).", "lift": 19.73, "risk": "medium"},
        {"kondisi": "Pembelian properti tipe Multifamily (Apartemen/Kos)", "hasil": "Ditujukan untuk investasi atau bisnis sewa", "peluang_bisnis": "Buat produk KPR Investasi Properti Komersial dengan fitur cross-selling asuransi properti sewa dan integrasi layanan pengelolaan kas (cash management) untuk membantu investor/landlord mengelola arus kas sewa mereka.", "lift": 13.51, "risk": "low"},
        {"kondisi": "Pinjaman Jumbo (Non-Conforming) + jaminan pemerintah", "hasil": "Berasal dari program VA Loan (Veteran)", "peluang_bisnis": "Mengembangkan kampanye pemasaran KPR Jumbo khusus Veteran (VA Jumbo Loan) dengan suku bunga bersaing dan biaya administrasi rendah untuk merebut pangsa pasar nasabah pensiunan militer/veteran bernilai tinggi.", "lift": 12.53, "risk": "low"},
        {"kondisi": "Properti Multifamily + bunga sedang (3-5%)", "hasil": "Pinjaman Jumbo Non-Conforming (> $647K)", "peluang_bisnis": "Desain paket bundling investasi properti komersial yang menggabungkan KPR plafon besar (> $647K) dengan bunga tetap menengah serta fasilitas kredit modal kerja untuk renovasi atau perawatan properti multifamily.", "lift": 12.00, "risk": "medium"},
        {"kondisi": "Pembelian rumah baru tipe Multifamily", "hasil": "Pinjaman Jumbo Non-Conforming (> $647K)", "peluang_bisnis": "Jalin kemitraan eksklusif (partnership) dengan pengembang (developer) apartemen atau ruko baru untuk menawarkan skema KPR Jumbo Investor instan di lokasi-lokasi strategis yang sedang berkembang.", "lift": 11.34, "risk": "medium"},
        {"kondisi": "Uang muka nyaris 0% (LTV 95-100%) + Cash-out Refinance", "hasil": "Menggunakan fasilitas VA Loan (Veteran)", "peluang_bisnis": "Tawarkan produk tabungan atau investasi tambahan (cross-selling) kepada nasabah veteran yang melakukan cash-out refinance untuk membantu mereka menaruh dana segar hasil refinance tersebut ke dalam portofolio investasi yang aman.", "lift": 10.72, "risk": "high"},
        {"kondisi": "Pre-Approval + didukung Ginnie Mae", "hasil": "Uang muka sangat minim (LTV 95-100%)", "peluang_bisnis": "Optimalkan layanan 'Instant Pre-Approval' berbasis digital khusus untuk segmen program pemerintah guna mempermudah pembeli rumah pertama berpendapatan rendah mendapatkan persetujuan KPR secara cepat.", "lift": 9.77, "risk": "low"},
        {"kondisi": "VA Loan (Veteran) + bunga rendah (di bawah 3%)", "hasil": "Disokong program penjaminan Ginnie Mae", "peluang_bisnis": "Gunakan sekuritisasi Ginnie Mae untuk mendanai KPR berbiaya rendah secara berkelanjutan, sekaligus menawarkan kartu kredit atau asuransi kendaraan khusus veteran (VA-tailored products) kepada nasabah ini.", "lift": 9.09, "risk": "low"},
        {"kondisi": "DTI di atas 60% + rumah Manufactured Housing", "hasil": "Tenor pinjaman lebih pendek (15-25 tahun)", "peluang_bisnis": "Tawarkan jasa pendampingan konsolidasi utang atau program perbaikan skor kredit bagi nasabah DTI tinggi ini, seraya membatasi tenor KPR mereka untuk mempercepat pelunasan dan menekan risiko default.", "lift": 8.09, "risk": "high"}
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
    df_cluster_summary = pd.read_csv(cluster_summary_path).set_index('cluster_name')
except Exception as e:
    df_cluster_summary = pd.DataFrame()
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
                html.Div("99.994", className="metric-value", style={'color': '#10b981'}),
                html.Div("Setelah Hapus Duplikat", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Kolom Mentah", className="metric-title"),
                html.Div("99", className="metric-value"),
                html.Div("Variabel", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Kolom Dipakai", className="metric-title"),
                html.Div("56", className="metric-value", style={'color': '#3b82f6'}),
                html.Div("Fitur Terpenting", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Data Kosong Awal", className="metric-title"),
                html.Div("2,85 Juta", className="metric-value", style={'color': '#f59e0b'}),
                html.Div("Sel yang Kosong", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
            dbc.Col(html.Div(className="glass-card metric-card h-100", children=[
                html.Div("Data Kosong Akhir", className="metric-title"),
                html.Div("0", className="metric-value", style={'color': '#10b981'}),
                html.Div("100% Terisi (Imputed)", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=2),
        ], className="mb-4"),
        
        # --- BARIS 2: Profil Finansial ---
        html.H4("Profil Finansial Nasabah", className="mb-3 mt-5", style={'color': 'var(--accent-blue)'}),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100 text-center", children=[
                html.H5("Nilai Pinjaman (Loan)", className="mb-3", style={'color': 'var(--text-secondary)'}),
                html.Div("$204K", className="stat-highlight", style={'color': '#3b82f6'}),
                html.Div("Rata-rata", className="small text-muted mb-2"),
                html.Div("Median: $175K", className="small mb-1"),
                html.Div("Range: $5K - $1.5M", className="small text-muted")
            ]), width=3),
            dbc.Col(html.Div(className="glass-card h-100 text-center", children=[
                html.H5("Pendapatan (Income)", className="mb-3", style={'color': 'var(--text-secondary)'}),
                html.Div("$95K", className="stat-highlight", style={'color': '#10b981'}),
                html.Div("Rata-rata / Tahun", className="small text-muted mb-2"),
                html.Div("Median: $65K", className="small mb-1"),
                html.Div("Range: $1K - $774K", className="small text-muted")
            ]), width=3),
            dbc.Col(html.Div(className="glass-card h-100 text-center", children=[
                html.H5("Suku Bunga (Interest)", className="mb-3", style={'color': 'var(--text-secondary)'}),
                html.Div("4,12%", className="stat-highlight", style={'color': '#f97316'}),
                html.Div("Rata-rata", className="small text-muted mb-2"),
                html.Div("Median: 4.00%", className="small mb-1"),
                html.Div("Range: 0% - 10,45%", className="small text-muted")
            ]), width=3),
            dbc.Col(html.Div(className="glass-card h-100 text-center", children=[
                html.H5("Utang vs Nilai Rumah", className="mb-3", style={'color': 'var(--text-secondary)'}),
                html.Div("68,5%", className="stat-highlight", style={'color': '#f43f5e'}),
                html.Div("Rata-rata LTV", className="small text-muted mb-2"),
                html.Div("Median: 75%", className="small mb-1"),
                html.Div("Lebih rendah = Lebih aman", className="small text-muted")
            ]), width=3),
        ], className="mb-4"),

        # --- BARIS 3: Komposisi ---
        html.H4("Siapa Saja yang Mengajukan KPR?", className="mb-3 mt-5", style={'color': 'var(--accent-teal)'}),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Tipe Produk KPR", className="mb-3", style={'color': 'var(--text-secondary)', 'textAlign': 'center'}),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("Konvensional"), html.Strong("42,3%")]),
                html.Div(className="progress mb-3", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '42.3%', 'backgroundColor': '#3b82f6'})
                ]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("FHA (Pemerintah)"), html.Strong("28,2%")]),
                html.Div(className="progress mb-3", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '28.2%', 'backgroundColor': '#10b981'})
                ]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("VA (Veteran)"), html.Strong("19,2%")]),
                html.Div(className="progress mb-0", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '19.2%', 'backgroundColor': '#f59e0b'})
                ])
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Tujuan Pinjaman", className="mb-3", style={'color': 'var(--text-secondary)', 'textAlign': 'center'}),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("Pembelian Rumah Baru"), html.Strong("45,2%")]),
                html.Div(className="progress mb-3", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '45.2%', 'backgroundColor': '#8b5cf6'})
                ]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("Refinancing (KPR Ulang)"), html.Strong("42,1%")]),
                html.Div(className="progress mb-3", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '42.1%', 'backgroundColor': '#ec4899'})
                ]),
                html.Div(className="d-flex justify-content-between mb-2", children=[html.Span("Perbaikan Rumah"), html.Strong("12,7%")]),
                html.Div(className="progress mb-0", style={'height': '8px', 'backgroundColor': 'rgba(255,255,255,0.1)'}, children=[
                    html.Div(className="progress-bar", style={'width': '12.7%', 'backgroundColor': '#14b8a6'})
                ])
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Jenis Kelamin", className="mb-3", style={'color': 'var(--text-secondary)', 'textAlign': 'center'}),
                html.Div(className="d-flex justify-content-center align-items-center h-100", children=[
                    html.Div(className="text-center me-4", children=[
                        html.H3("52,3%", style={'color': '#3b82f6', 'marginBottom': '5px'}),
                        html.Span("Pria", className="text-muted")
                    ]),
                    html.Div(style={'width': '1px', 'height': '40px', 'backgroundColor': 'rgba(255,255,255,0.2)'}),
                    html.Div(className="text-center ms-4", children=[
                        html.H3("47,7%", style={'color': '#ec4899', 'marginBottom': '5px'}),
                        html.Span("Wanita", className="text-muted")
                    ])
                ])
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
            dbc.Col(html.Div(className="pipeline-step", children=[html.Strong("4. Isi Data Kosong"), html.Br(), html.Span("100% Imputasi Sukses", className="small text-muted")]), width=2),
            dbc.Col(html.Div(className="pipeline-arrow", children="➔"), width=1, style={'padding': 0, 'width': '4%'}),
            dbc.Col(html.Div(className="pipeline-step", style={'borderColor': '#10b981'}, children=[html.Strong("5. Data Siap Pakai", style={'color': '#10b981'}), html.Br(), html.Span("Kualitas Data 98%", className="small text-muted")]), width=2),
        ], className="align-items-center mb-5", style={'justifyContent': 'center'}),
        
        # --- BARIS 5: Ringkasan Temuan ---
        html.H4("3 Ringkasan Temuan Proyek", className="mb-3", style={'color': 'var(--text-secondary)'}),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.Div("1. Tiga Kelompok Pasar Utama", className="insight-title", style={'color': '#3b82f6'}),
                html.Div("Nasabah kita tidaklah sama. Sistem AI membagi mereka menjadi 3 segmen besar dengan strategi meminjam yang sangat berbeda, dari yang super aman hingga yang sangat berisiko.", className="insight-desc")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.Div("2. Pola Bisnis Tersembunyi", className="insight-title", style={'color': '#10b981'}),
                html.Div("Kami menemukan kebiasaan nasabah yang tak kasat mata. Contohnya, ada ceruk pasar besar pada anak muda bergaji rendah yang selalu menyasar properti siap rakit (Manufactured Housing).", className="insight-desc")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.Div("3. Deteksi Otomatis Kasus Berisiko", className="insight-title", style={'color': '#f43f5e'}),
                html.Div(f"Sistem kami menemukan {fmt_count(len(df_priority))} kasus pengajuan yang secara individual angkanya tampak normal, tapi saat digabungkan mengindikasikan sinyal risiko yang tinggi dan perlu ditinjau manusia.", className="insight-desc")
            ]), width=4)
        ])
    ])

def tab_segmentation():
    # === CHARTS ===
    cluster_colors = {'Kelas Menengah (Grup 1)': '#3b82f6', 'Peminjam Agresif (Grup 2)': '#f43f5e', 'Konservatif HNW (Grup 3)': '#10b981'}

    # Donut chart proporsi
    fig_donut = go.Figure(data=[go.Pie(
        labels=['Kelas Menengah (Grup 1)', 'Peminjam Agresif (Grup 2)', 'Konservatif HNW (Grup 3)'],
        values=[42.6, 25.3, 32.1],
        hole=.55,
        marker_colors=['#3b82f6', '#f43f5e', '#10b981'],
        textinfo='percent',
    )])
    fig_donut.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8fafc'),
        margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
        annotations=[dict(text='<b>100K<br>Nasabah</b>', x=0.5, y=0.5, font_size=14, showarrow=False, font_color='#f8fafc')]
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
            font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
    else:
        fig_pca = go.Figure()

    # Grafik pembanding karakteristik antar-segmen (mengukuhkan klaim di kartu profil
    # dengan angka nyata hasil clustering pada SELURUH 99.994 baris, bukan sekadar narasi)
    cluster_order = ['Kelas Menengah (Grup 1)', 'Peminjam Agresif (Grup 2)', 'Konservatif HNW (Grup 3)']

    def _bar_compare(series_key, y_title, value_fmt='{:,.0f}'):
        if df_cluster_summary.empty:
            return go.Figure()
        ordered = df_cluster_summary.reindex(cluster_order)
        fig = go.Figure(data=[go.Bar(
            x=cluster_order,
            y=ordered[series_key],
            marker_color=[cluster_colors[c] for c in cluster_order],
            text=[value_fmt.format(v) for v in ordered[series_key]],
            textposition='outside'
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc', family='Plus Jakarta Sans', size=11),
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(title=y_title, showgrid=True, gridcolor='rgba(148,163,184,0.12)', tickfont=dict(size=10)),
        )
        return fig

    if not df_cluster_summary.empty:
        fig_income_cmp = _bar_compare('avg_income', 'Rata-rata Pendapatan ($, ribuan)')
        fig_loan_cmp = _bar_compare('avg_loan_amount', 'Rata-rata Pinjaman ($)')
        fig_leverage_cmp = _bar_compare('loan_to_income_ratio', 'Pinjaman / Pendapatan (kali)', value_fmt='{:.2f}x')
    else:
        fig_income_cmp = fig_loan_cmp = fig_leverage_cmp = go.Figure()

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
                dcc.Graph(figure=fig_donut, config={'displayModeBar': False}, style={'height': '320px'})
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Peta Posisi Nasabah (Cluster Map)"),
                html.P(
                    "Setiap titik = satu pengajuan KPR, diproyeksikan dari 14 fitur finansial ke 2 dimensi (PCA) agar bisa dilihat mata. "
                    "Titik yang mengelompok artinya nasabah tersebut sangat mirip satu sama lain. "
                    "Ketiga warna ini adalah tiga 'dunia' yang berbeda di dalam pasar yang sama.",
                    className="small text-muted mb-2"
                ),
                dcc.Graph(figure=fig_pca, config={'displayModeBar': False}, style={'height': '320px'})
            ]), width=8),
        ], className="mb-4"),

        # --- BARIS 1.5: Pembanding Kuantitatif Antar Segmen ---
        html.Div("Apakah Klaim di Atas Didukung Data? (Perbandingan Kuantitatif)", className="section-title"),
        html.P(
            "Ketiga grafik ini dihitung langsung dari rata-rata seluruh 99.994 nasabah di tiap segmen, "
            "sebagai bukti kuantitatif atas klaim karakteristik pada kartu profil di bawah.",
            className="mb-3 text-muted small"
        ),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Rata-rata Pendapatan", className="mb-2"),
                dcc.Graph(figure=fig_income_cmp, config={'displayModeBar': False}, style={'height': '260px'})
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Rata-rata Nilai Pinjaman", className="mb-2"),
                dcc.Graph(figure=fig_loan_cmp, config={'displayModeBar': False}, style={'height': '260px'})
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H5("Rasio Leverage (Pinjaman / Pendapatan)", className="mb-2"),
                dcc.Graph(figure=fig_leverage_cmp, config={'displayModeBar': False}, style={'height': '260px'})
            ]), width=4),
        ], className="mb-4"),

        # --- BARIS 2: Profil 3 Segmen ---
        html.Div("Profil & Peluang Bisnis Tiap Segmen", className="section-title"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", style={'borderTop': '3px solid #3b82f6'}, children=[
                html.H4("Grup 1: Kelas Menengah", style={'color': '#3b82f6'}),
                html.P("42,6% dari seluruh nasabah", className="badge badge-low-risk mb-3"),
                html.P("Mereka adalah pembeli rumah pertama atau keluarga kelas menengah tipikal. Pinjam secukupnya, cicil dengan disiplin."),
                html.Hr(style={'borderColor': 'rgba(255,255,255,0.1)'}),
                html.P(html.B("Peluang Bisnis:"), className="mb-1"),
                html.P("Segmen ini paling besar volumenya. Fokus pada produk KPR standar dengan proses mudah dan cepat. Mereka sangat menghargai kemudahan administrasi dan suku bunga yang kompetitif.", className="small text-muted"),
                html.P(html.B("Dampak:"), className="mb-1"),
                html.P("Menjaga stabilitas dan volume portofolio KPR tulang punggung pendapatan rutin perusahaan.", className="small text-muted")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", style={'borderTop': '3px solid #f43f5e'}, children=[
                html.H4("Grup 2: Peminjam Agresif", style={'color': '#f43f5e'}),
                html.P("25,3% dari seluruh nasabah", className="badge badge-high-risk mb-3"),
                html.P("Profesional berpenghasilan tinggi yang sengaja meminjam jauh lebih besar dari kebutuhannya untuk mendapatkan properti premium."),
                html.Hr(style={'borderColor': 'rgba(255,255,255,0.1)'}),
                html.P(html.B("Peluang Bisnis:"), className="mb-1"),
                html.P("Sumber pendapatan bunga terbesar. Tawarkan produk KPR premium dengan layanan dedicated relationship manager dan fleksibilitas tenor.", className="small text-muted"),
                html.P(html.B("Risiko yang Perlu Diawasi:"), className="mb-1"),
                html.P("Rasio utang mereka paling tinggi paling rentan jika terjadi guncangan ekonomi. Perlu sistem monitoring cicilan yang aktif.", className="small text-muted")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", style={'borderTop': '3px solid #10b981'}, children=[
                html.H4("Grup 3: Konservatif HNW", style={'color': '#10b981'}),
                html.P("32,1% dari seluruh nasabah", className="badge badge-low-risk mb-3"),
                html.P("Penghasilan paling tinggi, namun secara mengejutkan mereka hanya meminjam sedikit. Uang muka mereka sangat besar."),
                html.Hr(style={'borderColor': 'rgba(255,255,255,0.1)'}),
                html.P(html.B("Peluang Bisnis:"), className="mb-1"),
                html.P("Jangan tawarkan KPR  mereka tidak terlalu butuh. Tawarkan produk Wealth Management, reksa dana, asuransi jiwa premium, atau deposito.", className="small text-muted"),
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
            color_continuous_scale=[(0, '#3b82f6'), (0.3, '#14b8a6'), (0.6, '#facc15'), (1, '#f97316')],
            labels={
                'jangkauan_pasar': 'Jangkauan Pasar (% dari Total Nasabah)',
                'tingkat_kepastian': 'Tingkat Kepastian Pola (%)',
                'lift': 'Kekuatan Pola'
            }
        )
        fig_arm.update_traces(
            marker=dict(line=dict(width=1, color='rgba(255,255,255,0.25)'), sizemin=5),
            hovertemplate=(
                '<b>Kekuatan Pola: %{marker.color:.1f}x</b><br>'
                'Jangkauan Pasar: %{x:.2f}%<br>'
                'Tingkat Kepastian: %{y:.0f}%'
                '<extra></extra>'
            )
        )
        fig_arm.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
            margin=dict(l=60, r=20, t=10, b=60),
            coloraxis_colorbar=dict(
                title=dict(text='Kekuatan<br>Pola', font=dict(size=12)),
                ticksuffix='x',
                len=0.65,
                thickness=14,
                outlinewidth=0
            ),
            xaxis=dict(
                ticksuffix='%',
                showgrid=True,
                gridcolor='rgba(148,163,184,0.12)',
                gridwidth=1,
                zeroline=False,
                title=dict(text='Jangkauan Pasar (% dari Total Nasabah)', font=dict(size=13)),
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                ticksuffix='%',
                showgrid=True,
                gridcolor='rgba(148,163,184,0.12)',
                gridwidth=1,
                zeroline=False,
                title=dict(text='Tingkat Kepastian Pola (%)', font=dict(size=13)),
                tickfont=dict(size=11),
                range=[55, 105]
            )
        )
        # Rule Network: Flow diagram bisnis yang mudah dipahami
        # Gunakan semua 10 rules dari business_rules
        import math
        flow_rules = [
            {'kondisi': 'KPR Kedua dari<br>Investor Swasta', 'hasil': 'Utang Melampaui<br>Nilai Rumah (LTV &gt;100%)', 'lift': 38.0, 'kondisi_plain': 'KPR Kedua dari Investor Swasta', 'hasil_plain': 'Utang Melampaui Nilai Rumah'},
            {'kondisi': 'Nasabah Muda<br>(Usia &lt; 25 Tahun)', 'hasil': 'Pilih Manufactured<br>Housing', 'lift': 19.7, 'kondisi_plain': 'Nasabah Muda (Usia di bawah 25)', 'hasil_plain': 'Pilih Manufactured Housing'},
            {'kondisi': 'Beli Properti<br>Multifamily (Kos)', 'hasil': 'Tujuan Investasi<br>atau Bisnis Sewa', 'lift': 13.5, 'kondisi_plain': 'Beli Properti Multifamily', 'hasil_plain': 'Tujuan Investasi/Bisnis Sewa'},
            {'kondisi': 'Pinjaman Jumbo +<br>Jaminan Pemerintah', 'hasil': 'Program<br>VA Loan Veteran', 'lift': 12.5, 'kondisi_plain': 'Pinjaman Jumbo + Jaminan Pemerintah', 'hasil_plain': 'Program VA Veteran'},
            {'kondisi': 'Multifamily +<br>Bunga Sedang (3-5%)', 'hasil': 'Pinjaman Jumbo<br>Non-Conforming', 'lift': 12.0, 'kondisi_plain': 'Multifamily + Bunga Sedang', 'hasil_plain': 'Pinjaman Jumbo Non-Conforming'},
            {'kondisi': 'Beli Rumah Baru<br>Tipe Multifamily', 'hasil': 'Pinjaman Jumbo<br>Non-Conforming', 'lift': 11.3, 'kondisi_plain': 'Beli Rumah Baru Tipe Multifamily', 'hasil_plain': 'Pinjaman Jumbo Non-Conforming'},
            {'kondisi': 'Uang Muka ~0% +<br>Cash-out Refinance', 'hasil': 'Fasilitas<br>VA Loan Veteran', 'lift': 10.7, 'kondisi_plain': 'Uang Muka ~0% + Cash-out Refinance', 'hasil_plain': 'Fasilitas VA Loan Veteran'},
            {'kondisi': 'Pre-Approval +<br>Ginnie Mae', 'hasil': 'Uang Muka Sangat<br>Minim (LTV 95-100%)', 'lift': 9.8, 'kondisi_plain': 'Pre-Approval + Ginnie Mae', 'hasil_plain': 'Uang Muka Minim (LTV 95-100%)'},
            {'kondisi': 'VA Loan Veteran +<br>Bunga &lt; 3%', 'hasil': 'Disokong<br>Ginnie Mae', 'lift': 9.1, 'kondisi_plain': 'VA Loan Veteran + Bunga rendah', 'hasil_plain': 'Disokong Ginnie Mae'},
            {'kondisi': 'DTI &gt; 60% +<br>Manufactured Housing', 'hasil': 'Tenor Pinjaman<br>Lebih Pendek', 'lift': 8.1, 'kondisi_plain': 'DTI tinggi + Manufactured Housing', 'hasil_plain': 'Tenor Pinjaman Lebih Pendek'},
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
                line=dict(width=1 + rule['lift'] / 20, color='rgba(59,130,246,0.25)'),
                hoverinfo='none', showlegend=False
            ))
            # Arrow head
            fig_network.add_annotation(
                x=0.82, y=y_pos, ax=0.18, ay=y_pos,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=1.5,
                arrowcolor='rgba(20,184,166,0.5)'
            )
            # Node Kondisi (kiri)
            fig_network.add_trace(go.Scatter(
                x=[0], y=[y_pos], mode='markers',
                marker=dict(size=node_size, color='#3b82f6',
                            line=dict(width=1.5, color='rgba(96,165,250,0.5)')),
                hovertext='Kondisi: ' + rule['kondisi_plain'],
                hoverinfo='text',
                showlegend=False
            ))
            # Label Kondisi di kiri node
            fig_network.add_annotation(
                x=-0.08, y=y_pos,
                text=rule['kondisi'],
                showarrow=False,
                xanchor='right', yanchor='middle',
                font=dict(size=9, color='#e2e8f0', family='Plus Jakarta Sans'),
                xref='x', yref='y'
            )
            # Node Hasil (kanan)
            fig_network.add_trace(go.Scatter(
                x=[1], y=[y_pos], mode='markers',
                marker=dict(size=node_size, color='#14b8a6',
                            line=dict(width=1.5, color='rgba(45,212,191,0.5)')),
                hovertext='Hasil: ' + rule['hasil_plain'] + ' | Kekuatan: ' + str(rule['lift']) + 'x',
                hoverinfo='text',
                showlegend=False
            ))
            # Label Hasil di kanan node
            fig_network.add_annotation(
                x=1.08, y=y_pos,
                text=rule['hasil'],
                showarrow=False,
                xanchor='left', yanchor='middle',
                font=dict(size=9, color='#e2e8f0', family='Plus Jakarta Sans'),
                xref='x', yref='y'
            )
            # Lift label di tengah
            fig_network.add_annotation(
                x=0.5, y=y_pos + 0.15,
                text='<b>' + str(rule['lift']) + 'x</b>',
                showarrow=False,
                font=dict(size=9, color='#facc15', family='Plus Jakarta Sans'),
                xref='x', yref='y'
            )
        fig_network.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
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
    risk_color = {'high': '#f43f5e', 'medium': '#f97316', 'low': '#10b981'}
    rules_html = []
    for i, rule in enumerate(business_rules):
        rules_html.append(
            dbc.Col(
                html.Div(className="glass-card mb-3 h-100", style={'borderLeft': f'3px solid {risk_color.get(rule["risk"], "#3b82f6")}'}, children=[
                    html.Div(className="d-flex justify-content-between align-items-start mb-2", children=[
                        html.Span(f"Pola #{i+1}", className=risk_badge.get(rule['risk'], 'badge badge-low-risk')),
                        html.Div(f"{rule['lift']}x", style={'fontFamily': 'var(--font-heading)', 'fontSize': '1.5rem', 'fontWeight': 'bold', 'color': 'var(--accent-orange)', 'lineHeight': '1'})
                    ]),
                    html.P([
                        html.Span("Kondisi: ", style={'color': '#94a3b8', 'fontWeight': '600'}),
                        rule['kondisi']
                    ], className="mb-1 small"),
                    html.P([
                        html.Span("Hasil: ", style={'color': '#14b8a6', 'fontWeight': '600'}),
                        rule['hasil']
                    ], className="mb-2 small", style={'color': '#5eead4'}),
                    html.Hr(style={'borderColor': 'rgba(255,255,255,0.08)', 'margin': '8px 0'}),
                    html.P([
                        html.Span("Analisis Peluang Bisnis: ", style={'color': '#38bdf8', 'fontWeight': '600'}),
                        rule['peluang_bisnis']
                    ], className="mb-0 small text-muted")
                ]),
                width=6
            )
        )

    return html.Div(className="tab-content", children=[
        html.Div("Peta Peluang Bisnis Tersembunyi (Hasil Analisis ARM)", className="section-title"),
        html.P("Setiap titik mewakili satu peluang bisnis spesifik. Semakin besar dan terang titiknya, semakin tinggi kepastian bahwa nasabah akan mengambil produk tersebut — cocok dijadikan target Cross-Selling atau peringatan risiko.", className="mb-4 text-muted"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H4("Peta 100 Peluang Bisnis Terkuat"),
                html.P([
                    "Setiap gelembung = satu pola perilaku nasabah. ",
                    html.B("Makin ke kanan"),
                    " = makin banyak nasabah yang terlibat. ",
                    html.B("Makin ke atas"),
                    " = makin pasti polanya terjadi. ",
                    html.B("Makin besar & terang"),
                    " = makin kuat peluang bisnisnya."
                ], className="small text-muted mb-2"),
                dcc.Graph(figure=fig_arm, config={'displayModeBar': False}, style={'height': '520px'})
            ]), width=6),
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H4("10 Pola Perilaku Nasabah Terkuat"),
                dcc.Graph(figure=fig_network, config={'displayModeBar': False}, style={'height': '500px'}),
                html.P([
                    html.Span("●", style={'color': '#3b82f6'}), " Kondisi → ",
                    html.Span("●", style={'color': '#14b8a6'}), " Hasil"
                ], className="small text-muted text-center mt-2 mb-0")
            ]), width=6),
        ]),
        html.Div("10 Peluang Bisnis dari Pola Nasabah", className="section-title mt-2"),
        html.P("Setiap kartu menunjukkan satu pola tersembunyi dari data. Angka oranye menunjukkan seberapa kuat pola ini dibanding rata-rata populasi.", className="mb-3 text-muted small"),
        dbc.Row(rules_html)
    ])


def tab_distributions():
    figs = []
    dist_insights = [
        {
            'col': 'loan_amount', 'label': 'Seberapa Besar Pinjaman Nasabah?',
            'color': '#3b82f6',
            'insight': 'Mayoritas nasabah mengajukan pinjaman di kisaran moderat. Namun ada ekor panjang di kanan — ini adalah segmen Jumbo Loan (nasabah agresif & investor) yang jumlahnya kecil tapi bernilai tinggi.',
            'opportunity': 'Jangan buat produk yang terlalu standar. Ada dua pasar: pasar massal (pinjaman kecil-menengah) dan pasar premium (Jumbo Loan). Keduanya butuh pendekatan yang berbeda.'
        },
        {
            'col': 'income', 'label': 'Sebaran Penghasilan Pemohon KPR',
            'color': '#10b981',
            'insight': 'Sebagian besar pemohon berpenghasilan menengah. Tapi ada segmen kecil dengan penghasilan sangat tinggi yang justru meminjam di bawah kapasitasnya — ini adalah kelompok Konservatif HNW.',
            'opportunity': 'Segmen berpenghasilan sangat tinggi ini adalah target utama Wealth Management. Mereka tidak datang mencari KPR, tapi bisa ditawarkan produk investasi & asuransi bermargin tinggi.'
        },
        {
            'col': 'interest_rate', 'label': 'Distribusi Suku Bunga yang Diterima',
            'color': '#f97316',
            'insight': 'Suku bunga terkonsentrasi di 2 rentang: sangat rendah (program VA/Veteran) dan moderat (pasar umum). Adanya dua puncak ini membuktikan ada dua ekosistem pembiayaan yang terpisah.',
            'opportunity': 'Nasabah yang mendapat bunga sangat rendah hampir pasti adalah peserta program Veteran. Ini adalah segmen yang bisa di-bundle dengan produk finansial khusus untuk mempertahankan loyalitas mereka.'
        },
        {
            'col': 'combined_loan_to_value_ratio', 'label': 'Distribusi Rasio Utang vs Nilai Rumah (LTV)',
            'color': '#f43f5e',
            'insight': 'Mayoritas nasabah berada di LTV 60–95% (zona normal). Namun ada kasus ekstrem di atas 100% — artinya nilai pinjaman melampaui harga rumah. Ini adalah zona merah risiko kredit macet.',
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
                color_discrete_sequence=[d['color']],
                labels={d['col']: '', 'count': 'Jumlah Pengajuan'}
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
                margin=dict(l=10, r=10, t=5, b=10), showlegend=False
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
                dcc.Graph(figure=d['fig'], config={'displayModeBar': False}, style={'height': '200px'}),
                html.Hr(style={'borderColor': 'rgba(255,255,255,0.1)', 'margin': '12px 0'}),
                html.P(html.B("Apa yang terlihat: "), className="mb-1 small"),
                html.P(d['insight'], className="small text-muted mb-2"),
                html.P(html.B("Peluang Bisnis: "), className="mb-1 small"),
                html.P(d['opportunity'], className="small", style={'color': 'var(--accent-teal)'}),
            ]), width=6)
        )

    return html.Div(className="tab-content", children=[
        html.Div("Memahami Pasar dari Distribusi Data", className="section-title"),
        html.P(
            "Grafik distribusi menunjukkan 'bentuk' pasar KPR kita — di mana konsentrasinya, seberapa merata atau terpolarisasi, "
            "dan di mana peluang bisnis tersembunyi berada. Setiap grafik dilengkapi dengan interpretasi dan rekomendasi langsung untuk tim bisnis.",
            className="mb-4 text-muted"
        ),
        dbc.Row(cards)
    ])


def tab_4_anomalies():
    # Bar chart untuk tipologi
    if not anomaly_counts.empty:
        fig_bar = px.bar(
            anomaly_counts, 
            y='Tipologi_Indo', 
            x='Jumlah',
            orientation='h',
            color='Tipologi',
            color_discrete_map={
                'Unclassified / Manual Review': '#f97316',
                'Rare Legitimate': '#10b981',
                'Data Error': '#ef4444',
                'Potential Risk Signal': '#f59e0b'
            },
            text='Jumlah'
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig_bar.update_yaxes(title="")
        fig_bar.update_traces(texttemplate='%{text}', textposition='outside')
    else:
        fig_bar = go.Figure()

    # Donut chart untuk tier
    if not tier_counts.empty:
        # Susun urutan dan warna
        tier_order = ['Normal', 'Suspected (1 metode)', 'Confirmed (2 metode)', 'High Confidence']
        tier_colors = ['#334155', '#3b82f6', '#f59e0b', '#ef4444']
        
        fig_tier = go.Figure(data=[go.Pie(
            labels=tier_counts['Tier'],
            values=tier_counts['Jumlah'],
            hole=.6,
            marker_colors=[
                '#ef4444' if t == 'High Confidence' else 
                '#f59e0b' if t == 'Confirmed (2 metode)' else 
                '#3b82f6' if t == 'Suspected (1 metode)' else '#334155' 
                for t in tier_counts['Tier']
            ],
            textinfo='percent'
        )])
        fig_tier.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc'),
            margin=dict(t=20, b=20, l=20, r=20),
            legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5),
            annotations=[dict(text='<b>Deteksi<br>Berlapis</b>', x=0.5, y=0.5, font_size=14, showarrow=False, font_color='#f8fafc')]
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
            marker=dict(color='rgba(148,163,184,0.3)', size=5),
            hovertemplate='Income: %{x}<br>Loan: %{y}<extra></extra>'
        ))
        # Hanya plot prioritas
        outlier_sample = df_priority[['income', 'loan_amount', 'typology']].dropna().head(400)
        color_map = {'Potential Risk Signal': '#f59e0b', 'Data Error': '#ef4444', 'Rare Legitimate': '#10b981', 'Unclassified / Manual Review': '#f97316'}
        for typ, grp in outlier_sample.groupby('typology'):
            fig_outlier.add_trace(go.Scatter(
                x=grp['income'], y=grp['loan_amount'],
                mode='markers', name=tipologi_map.get(typ, typ),
                marker=dict(color=color_map.get(typ, '#fff'), size=9, symbol='diamond',
                            line=dict(width=1, color='white')),
                hovertemplate='Income: %{x}<br>Loan: %{y}<extra></extra>'
            ))
    fig_outlier.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
        margin=dict(l=10, r=10, t=10, b=120),
        legend=dict(orientation='h', yanchor='top', y=-0.2, xanchor='center', x=0.5),
        xaxis_title='Pendapatan Nasabah (Income)', yaxis_title='Nilai Pinjaman (Loan Amount)'
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
            dbc.Col(html.Div(className="glass-card metric-card", style={'borderColor': '#f43f5e', 'boxShadow': '0 0 10px rgba(244,63,94,0.1)'}, children=[
                html.Div("Prioritas Tinggi (Confirmed/HC)", className="metric-title", style={'color': '#f43f5e'}),
                html.Div(fmt_count(len(df_priority)), className="metric-value", style={'color': '#f43f5e'}),
                html.Div("Kasus Paling Janggal", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=3),
            dbc.Col(html.Div(className="glass-card metric-card", children=[
                html.Div("Metode Pengawasan", className="metric-title"),
                html.Div("3 Lapis", className="metric-value", style={'color': '#38bdf8'}),
                html.Div("IQR, Z-Score, Isolation Forest", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=6),
        ], className="mb-4"),

        # --- BARIS 2: Cara Kerja & Tier ---
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Tingkat Kepercayaan Sistem (Tier)"),
                html.P("Semakin banyak metode yang menangkap kejanggalan, semakin tinggi prioritas kasus tersebut.", className="small text-muted mb-2"),
                dcc.Graph(figure=fig_tier, config={'displayModeBar': False}, style={'height': '300px'})
            ]), width=5),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Bagaimana Sistem Menangkap Anomali?"),
                html.P("Kasus tidak hanya ditolak karena satu angka aneh, tetapi dianalisis dari berbagai sisi secara bersamaan:", className="small text-muted mb-3"),
                
                html.Div(className="mb-3", children=[
                    html.Strong("1. Filter IQR (Kewajaran Nilai)", style={'color': '#38bdf8'}),
                    html.P("Melihat batas normal nilai tiap bagian, misalnya gaji terlalu ekstrem.", className="small text-muted mb-1")
                ]),
                html.Div(className="mb-3", children=[
                    html.Strong("2. Z-Score (Distribusi Ekstrem)", style={'color': '#10b981'}),
                    html.P("Mendeteksi angka yang benar-benar mustahil secara statistik normal.", className="small text-muted mb-1")
                ]),
                html.Div(className="mb-3", children=[
                    html.Strong("3. Isolation Forest (Anomali Kombinasi)", style={'color': '#f59e0b'}),
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
                dcc.Graph(figure=fig_outlier, config={'displayModeBar': False}, style={'height': '420px'})
            ]), width=7),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Pengelompokan Jenis Kasus Prioritas"),
                dcc.Graph(figure=fig_bar, config={'displayModeBar': False}, style={'height': '420px'})
            ]), width=5),
        ], className="mb-4"),
        
        # --- BARIS 4: Tipologi ---
        dbc.Row([
            dbc.Col(html.Div(className="d-flex flex-column gap-3", children=[
                html.Div(className="glass-card", style={'borderLeft': '4px solid #f59e0b'}, children=[
                    html.H5(f"Sinyal Risiko Kredit Tinggi ({fmt_count(priority_typology_count('Potential Risk Signal'))} Kasus)", className="mb-2", style={'color': '#f59e0b'}),
                    html.P(html.B("Definisi:"), className="small mb-1"),
                    html.P("Pendapatan rendah (di bawah rata-rata) dikombinasikan dengan pinjaman Jumbo (sangat besar) dan leverage/utang yang sangat agresif.", className="small text-muted mb-2"),
                    html.P(html.B("Aksi Bisnis:"), className="small mb-1"),
                    html.P("Kirim ke tim Underwriting untuk verifikasi manual secara mendalam (enhanced verification) sebelum persetujuan kredit.", className="small mb-0")
                ]),
                html.Div(className="glass-card", style={'borderLeft': '4px solid #ef4444'}, children=[
                    html.H5(f"Data Error ({fmt_count(priority_typology_count('Data Error'))} Kasus)", className="mb-2", style={'color': '#ef4444'}),
                    html.P(html.B("Definisi:"), className="small mb-1"),
                    html.P("Nilai finansial yang melanggar batas fisik/logika bisnis. Misalnya: Suku bunga 0% atau rasio utang vs nilai rumah (LTV) > 150%.", className="small text-muted mb-2"),
                    html.P(html.B("Aksi Bisnis:"), className="small mb-1"),
                    html.P("Kembalikan ke tim Data Engineering (Bukan ke analis risiko) untuk koreksi pada sistem penginputan aplikasi kredit.", className="small mb-0")
                ]),
            ]), width=6),
            dbc.Col(html.Div(className="d-flex flex-column gap-3", children=[
                html.Div(className="glass-card", style={'borderLeft': '4px solid #10b981'}, children=[
                    html.H5(f"Profil Konservatif / Prospek ({fmt_count(priority_typology_count('Rare Legitimate'))} Kasus)", className="mb-2", style={'color': '#10b981'}),
                    html.P(html.B("Definisi:"), className="small mb-1"),
                    html.P("Nasabah sangat kaya (Ultra High-Net-Worth) namun mengambil pinjaman yang sangat kecil dengan uang muka raksasa.", className="small text-muted mb-2"),
                    html.P(html.B("Aksi Bisnis:"), className="small mb-1"),
                    html.P("JANGAN tandai sebagai risiko. Jadikan daftar ini sebagai prospek target (leads) untuk produk Priority Banking atau Wealth Management.", className="small mb-0")
                ]),
                html.Div(className="glass-card", style={'borderLeft': '4px solid #f97316'}, children=[
                    html.H5(f"Perlu Tinjauan Manual ({fmt_count(priority_typology_count('Unclassified / Manual Review'))} Kasus)", className="mb-2", style={'color': '#f97316'}),
                    html.P(html.B("Definisi:"), className="small mb-1"),
                    html.P("Anomali nyata secara statistik kombinasi (AI) tetapi tidak masuk ke dalam kotak risiko standar.", className="small text-muted mb-2"),
                    html.P(html.B("Aksi Bisnis:"), className="small mb-1"),
                    html.P("Masukkan ke daftar pantauan audit (watchlist). Underwriter dapat menggunakan daftar ini untuk audit keamanan internal secara berkala.", className="small mb-0")
                ])
            ]), width=6)
        ])
    ])

def tab_conclusions():
    return html.Div(className="tab-content", children=[
        html.Div("Eksekusi & Dampak Finansial dari Pola Tersembunyi", className="section-title"),
        html.P("Berdasarkan pemetaan kebiasaan nasabah (ARM), berikut adalah strategi nyata yang bisa langsung diterapkan perusahaan beserta dampak finansialnya.", className="mb-4 text-muted"),
        
        dbc.Row([
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H4("1. Monetisasi Segmen High-Net-Worth yang Pasif", style={'color': 'var(--accent-blue)'}),
                html.P("Temuan: Orang kaya (Grup 3) secara mengejutkan jarang memaksimalkan limit utangnya dan sangat berhati-hati (Konservatif)."),
                html.P(html.B("Peluang Bisnis: ")),
                html.P("Berhenti menargetkan mereka dengan iklan KPR. Alihkan mereka ke produk Wealth Management, reksadana, atau asuransi jiwa premium berbalut investasi."),
                html.P(html.B("Dampak: ")),
                html.P("Meningkatkan pemasukan dari komisi (Fee-based Income) tanpa menambah risiko gagal bayar (NPL) sama sekali.", className="text-muted mb-0")
            ]), width=12),
            
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H4("2. Optimalisasi Bundling Program Veteran (VA Loan)", style={'color': 'var(--accent-orange)'}),
                html.P("Temuan: Nasabah Veteran punya pola pasti: minta bunga terendah, uang muka 0%, dan sangat hobi mencairkan uang tunai (Cash-out)."),
                html.P(html.B("Peluang Bisnis: ")),
                html.P("Ciptakan program 'Bundling Veteran': Tawarkan KPR VA otomatis sepaket dengan fasilitas kartu kredit limit tinggi atau pinjaman renovasi rumah."),
                html.P(html.B("Dampak: ")),
                html.P("Meningkatkan jumlah produk yang dipakai per nasabah (Cross-sell Ratio) dan mengamankan loyalitas nasabah dengan profil khusus ini.", className="text-muted mb-0")
            ]), width=12),
            
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H4("3. Ekspansi Pasar Properti Ekonomis (Manufactured Housing)", style={'color': 'var(--accent-teal)'}),
                html.P("Temuan: Anak muda bergaji rendah (Entry-level) selalu berujung mengambil rumah siap rakit (Manufactured Housing) dengan tenor pendek."),
                html.P(html.B("Peluang Bisnis: ")),
                html.P("Buat divisi kredit mikro perumahan khusus untuk melayani developer penyedia Manufactured Housing. Jadikan proses persetujuannya instan (Fast-track)."),
                html.P(html.B("Dampak: ")),
                html.P("Mendominasi ceruk pasar (niche market) perumahan ekonomis dengan perputaran uang (cash-flow) cepat karena tenor cicilan yang lebih pendek.", className="text-muted mb-0")
            ]), width=12),
            
            dbc.Col(html.Div(className="glass-card", children=[
                html.H4("4. Mitigasi Risiko pada Investor Properti Agresif", style={'color': 'var(--accent-rose)'}),
                html.P("Temuan: Orang yang membeli properti Multifamily (kos/apartemen) sangat sering memanfaatkan pinjaman sekunder (KPR Kedua) hingga batas maksimal."),
                html.P(html.B("Peluang Bisnis (Mitigasi): ")),
                html.P("Ketatkan syarat persetujuan (Underwriting) khusus untuk investor Multifamily. Tawarkan produk KPR berbunga *floating* (mengambang) alih-alih tetap (fixed) untuk mereka."),
                html.P(html.B("Dampak: ")),
                html.P("Menekan potensi kerugian besar akibat gagal bayar (Mitigasi Risiko) dari segmen peminjam yang paling agresif berutang.", className="text-muted mb-0")
            ]), width=12)
        ])
    ])

# Main Layout
app.layout = html.Div([
    create_header(),
    dbc.Container([
        dbc.Tabs([
            dbc.Tab(tab_1_executive(), label="1. Common Information", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_segmentation(), label="2. Segmentation Nasabah", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_arm_visualization(), label="3. Visualization ARM", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_distributions(), label="4. Market Distribution", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_4_anomalies(), label="5. Anomali Detection", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_conclusions(), label="6. Conclusion", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
        ], className="custom-tabs"),
        
        html.Div(className="text-center mt-5 mb-4 text-muted small", children=[
            "© 2026 Insight Communicator | HMDA Data Mining Project - Phase 5"
        ])
    ], fluid=True, className="px-5")
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)
