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
data_path = os.path.join(base_dir, 'data', 'processed_dataset.csv')

try:
    df_rules = pd.read_csv(rules_path)
    top_10_rules = df_rules.head(10).copy()
    
    # Translate to very simple business language but keep financial terms
    business_rules = [
        {"desc": "KPR kedua (Piggyback/HELOC) dari investor swasta", "result": "Cenderung menyebabkan utang melampaui nilai rumah (LTV > 100%)", "lift": 38.02},
        {"desc": "Nasabah muda (di bawah 25 tahun) dengan cicilan pendek", "result": "Sangat sering memilih properti Manufactured Housing", "lift": 19.73},
        {"desc": "Pembelian properti tipe Multifamily (Apartemen/Kos)", "result": "Secara konsisten ditujukan untuk investasi atau bisnis sewa", "lift": 13.51},
        {"desc": "Pinjaman Jumbo (Non-Conforming) dengan jaminan pemerintah", "result": "Sebagian besar berasal dari program khusus VA Loan (Veteran)", "lift": 12.53},
        {"desc": "Pembeli properti Multifamily dengan bunga standar", "result": "Rata-rata mengambil pinjaman Jumbo (Non-Conforming)", "lift": 12.00},
        {"desc": "Pembelian rumah baru berjenis properti Multifamily", "result": "Juga berujung pada nilai pinjaman Jumbo (Non-Conforming)", "lift": 11.34},
        {"desc": "Nasabah dengan uang muka nyaris 0% yang melakukan Cash-out Refinance", "result": "Biasanya memanfaatkan fasilitas dari VA Loan (Veteran)", "lift": 10.72},
        {"desc": "Nasabah dengan Pre-Approval yang didukung oleh Ginnie Mae", "result": "Hampir selalu difasilitasi dengan uang muka sangat minim (LTV 95-100%)", "lift": 9.77},
        {"desc": "Nasabah VA Loan (Veteran) yang mendapat bunga di bawah 3%", "result": "Sebagian besar disokong oleh program penjaminan Ginnie Mae", "lift": 9.09},
        {"desc": "Nasabah dengan rasio Debt-to-Income (DTI) di atas 60%", "result": "Umumnya terpaksa mengambil jangka waktu pinjaman yang lebih pendek", "lift": 8.09}
    ]
except Exception as e:
    business_rules = []
    print(f"Error loading rules: {e}")

try:
    df_anomalies = pd.read_csv(anomalies_path)
    anomaly_counts = df_anomalies['typology'].value_counts().reset_index()
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
    anomaly_counts = pd.DataFrame()
    print(f"Error loading anomalies: {e}")

try:
    df_pca = pd.read_csv(pca_path)
except Exception as e:
    df_pca = pd.DataFrame()
    print(f"Error loading PCA data: {e}")

try:
    df_raw = pd.read_csv(data_path, nrows=3000)
    for col in ['loan_amount', 'income', 'interest_rate', 'combined_loan_to_value_ratio']:
        df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')
except Exception as e:
    df_raw = pd.DataFrame()
    print(f"Error loading raw data: {e}")

# Layout Komponen

def create_header():
    return html.Div(className="dashboard-header", children=[
        html.H1("Insight Komunikator: Pasar KPR 2022"),
        html.P("Mengungkap pola tersembunyi, segmentasi nasabah, dan deteksi risiko dari 100.000 data pengajuan Kredit Pemilikan Rumah (HMDA 2022).")
    ])

def tab_1_executive():
    return html.Div(className="tab-content", children=[
        dbc.Row([
            dbc.Col(html.Div(className="glass-card metric-card", children=[
                html.Div("Total Pengajuan KPR", className="metric-title"),
                html.Div("99.994", className="metric-value")
            ]), width=3),
            dbc.Col(html.Div(className="glass-card metric-card", children=[
                html.Div("Segmen Pasar Utama", className="metric-title"),
                html.Div("3", className="metric-value"),
                html.Div("Kelompok Nasabah Berbeda", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=3),
            dbc.Col(html.Div(className="glass-card metric-card", children=[
                html.Div("Pola Perilaku Unik", className="metric-title"),
                html.Div("10", className="metric-value"),
                html.Div("Temuan Tersembunyi", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=3),
            dbc.Col(html.Div(className="glass-card metric-card", children=[
                html.Div("Deteksi Pengajuan Berisiko", className="metric-title"),
                html.Div("3.301", className="metric-value", style={'color': '#f43f5e'}),
                html.Div("Kasus Perlu Perhatian", style={'color': 'var(--text-secondary)', 'fontSize': '0.9rem'})
            ]), width=3),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H3("Apa yang kita pelajari dari data mentah?"),
                html.Div(className="insight-item", children=[
                    html.Div("1. Pasar KPR Punya 3 Kelompok Berbeda", className="insight-title"),
                    html.Div("Pelanggan kita tidaklah sama secara finansial. Mereka terbagi menjadi 3 segmen utama yang strategi pembiayaan dan toleransi leverage-nya benar-benar berbeda. Ada yang sangat konservatif, ada yang agresif memaksimalkan leverage.", className="insight-desc")
                ]),
                html.Div(className="insight-item", children=[
                    html.Div("2. Perilaku Tersembunyi Nasabah", className="insight-title"),
                    html.Div("Kami menemukan kebiasaan perilaku yang spesifik. Misalnya, korelasi kuat antara usia pemohon yang sangat muda dengan pemilihan Manufactured Housing. Hal seperti ini tidak selalu terlihat dalam laporan agregasi standar.", className="insight-desc")
                ]),
                html.Div(className="insight-item", children=[
                    html.Div("3. Ribuan Data Berbahaya Lolos dari Sistem Standar", className="insight-title"),
                    html.Div("Sistem deteksi standar tidak cukup. Kami menemukan ribuan pengajuan di mana komponen seperti gaji, LTV, dan suku bunga secara mandiri tampak normal, tetapi kombinasinya mengindikasikan sinyal risiko yang tinggi.", className="insight-desc")
                ]),
            ]), width=12)
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
                    "Setiap titik = satu pengajuan KPR. Titik yang mengelompok artinya nasabah tersebut sangat mirip satu sama lain. "
                    "Ketiga warna ini adalah tiga 'dunia' yang berbeda di dalam pasar yang sama.",
                    className="small text-muted mb-2"
                ),
                dcc.Graph(figure=fig_pca, config={'displayModeBar': False}, style={'height': '320px'})
            ]), width=8),
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
                html.P("Menjaga stabilitas dan volume portofolio KPR — tulang punggung pendapatan rutin perusahaan.", className="small text-muted")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", style={'borderTop': '3px solid #f43f5e'}, children=[
                html.H4("Grup 2: Peminjam Agresif", style={'color': '#f43f5e'}),
                html.P("25,3% dari seluruh nasabah", className="badge badge-high-risk mb-3"),
                html.P("Profesional berpenghasilan tinggi yang sengaja meminjam jauh lebih besar dari kebutuhannya untuk mendapatkan properti premium."),
                html.Hr(style={'borderColor': 'rgba(255,255,255,0.1)'}),
                html.P(html.B("Peluang Bisnis:"), className="mb-1"),
                html.P("Sumber pendapatan bunga terbesar. Tawarkan produk KPR premium dengan layanan dedicated relationship manager dan fleksibilitas tenor.", className="small text-muted"),
                html.P(html.B("Risiko yang Perlu Diawasi:"), className="mb-1"),
                html.P("Rasio utang mereka paling tinggi — paling rentan jika terjadi guncangan ekonomi. Perlu sistem monitoring cicilan yang aktif.", className="small text-muted")
            ]), width=4),
            dbc.Col(html.Div(className="glass-card h-100", style={'borderTop': '3px solid #10b981'}, children=[
                html.H4("Grup 3: Konservatif HNW", style={'color': '#10b981'}),
                html.P("32,1% dari seluruh nasabah", className="badge badge-low-risk mb-3"),
                html.P("Penghasilan paling tinggi, namun secara mengejutkan mereka hanya meminjam sedikit. Uang muka mereka sangat besar."),
                html.Hr(style={'borderColor': 'rgba(255,255,255,0.1)'}),
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
        fig_arm = px.scatter(
            plot_df,
            x='support',
            y='confidence',
            size='lift',
            color='lift',
            hover_data=['antecedents', 'consequents'],
            color_continuous_scale=[(0, '#3b82f6'), (0.5, '#14b8a6'), (1, '#f97316')],
            labels={'support': 'Volume Pasar (Ukuran Segmen)', 'confidence': 'Kepastian Pola', 'lift': 'Potensi Nilai Bisnis'}
        )
        fig_arm.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc', family="Plus Jakarta Sans"),
            margin=dict(l=20, r=20, t=20, b=20),
            coloraxis_colorbar=dict(title="Nilai Peluang")
        )
        # Rule Network Graph menggunakan Plotly
        # Ambil top 12 rules untuk network agar tidak terlalu padat
        top_rules = df_rules.head(12).copy()
        node_x, node_y, node_text, node_color, edge_x, edge_y = [], [], [], [], [], []
        nodes = {}
        node_idx = 0
        import math
        all_labels = list(top_rules['antecedents']) + list(top_rules['consequents'])
        unique_labels = list(dict.fromkeys(all_labels))
        n = len(unique_labels)
        for i, label in enumerate(unique_labels):
            angle = 2 * math.pi * i / n
            x = math.cos(angle)
            y = math.sin(angle)
            nodes[label] = (x, y)
            short = label[:35] + '...' if len(label) > 35 else label
            node_x.append(x); node_y.append(y); node_text.append(short)
            node_color.append('#3b82f6' if label in list(top_rules['antecedents']) else '#f97316')
        for _, row in top_rules.iterrows():
            x0, y0 = nodes[row['antecedents']]
            x1, y1 = nodes[row['consequents']]
            edge_x += [x0, x1, None]; edge_y += [y0, y1, None]
        fig_network = go.Figure()
        fig_network.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines',
            line=dict(width=1.5, color='rgba(148,163,184,0.3)'), hoverinfo='none'))
        fig_network.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers+text',
            marker=dict(size=18, color=node_color, line=dict(width=2, color='rgba(255,255,255,0.3)')),
            text=node_text, textposition='top center',
            textfont=dict(size=9, color='#f8fafc'), hoverinfo='text'))
        fig_network.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc'), showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    else:
        fig_arm = go.Figure()
        fig_network = go.Figure()

    rules_html = []
    for i, rule in enumerate(business_rules[:4]):
        rules_html.append(
            html.Div(className="glass-card mb-3", children=[
                dbc.Row([
                    dbc.Col([
                        html.Span(f"Pola ARM #{i+1}", className="badge badge-medium-risk mb-2" if rule['lift'] > 15 else "badge badge-low-risk mb-2"),
                        html.H5("JIKA " + rule['desc']),
                        html.H5("MAKA " + rule['result'], style={'color': 'var(--accent-teal)'}),
                    ], width=9),
                    dbc.Col([
                        html.Div(className="text-center", children=[
                            html.Div("Potensi Bisnis", className="small text-muted"),
                            html.Div(f"{rule['lift']}x", style={'fontFamily': 'var(--font-heading)', 'fontSize': '2rem', 'fontWeight': 'bold', 'color': 'var(--accent-orange)'}),
                            html.Div("Lebih Akurat", className="small text-muted")
                        ])
                    ], width=3, className="d-flex flex-column justify-content-center align-items-center border-start border-secondary")
                ])
            ])
        )

    return html.Div(className="tab-content", children=[
        html.Div("Peta Peluang Bisnis Tersembunyi (Hasil Analisis ARM)", className="section-title"),
        html.P("Setiap titik mewakili satu peluang bisnis spesifik. Semakin besar dan terang titiknya, semakin tinggi kepastian bahwa nasabah akan mengambil produk tersebut — cocok dijadikan target Cross-Selling atau peringatan risiko.", className="mb-4 text-muted"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H4("Sebaran 100 Pola Perilaku Terkuat"),
                html.P("Sumbu X = seberapa besar segmen pasar ini. Sumbu Y = seberapa pasti polanya terjadi.", className="small text-muted mb-2"),
                dcc.Graph(figure=fig_arm, config={'displayModeBar': False})
            ]), width=6),
            dbc.Col(html.Div(className="glass-card mb-4", children=[
                html.H4("Jaringan Hubungan Antar Pola (Rule Network)"),
                html.P("Biru = kondisi awal (JIKA). Oranye = hasil yang terjadi (MAKA). Garis = kekuatan hubungan.", className="small text-muted mb-2"),
                dcc.Graph(figure=fig_network, config={'displayModeBar': False})
            ]), width=6),
        ]),
        html.Div("4 Peluang Bisnis Utama dari Pola Nasabah", className="section-title mt-2"),
        html.Div(rules_html)
    ])


def tab_cluster_map():
    if not df_pca.empty:
        cluster_colors = {'Kelas Menengah (Grup 1)': '#3b82f6', 'Peminjam Agresif (Grup 2)': '#f43f5e', 'Konservatif HNW (Grup 3)': '#10b981'}
        fig_pca = px.scatter(
            df_pca.sample(min(1500, len(df_pca))),
            x='pca_x', y='pca_y',
            color='cluster_name',
            color_discrete_map=cluster_colors,
            hover_data=['loan_amount', 'income'],
            labels={'pca_x': 'Dimensi 1 (PCA)', 'pca_y': 'Dimensi 2 (PCA)', 'cluster_name': 'Segmen Nasabah'},
            opacity=0.7
        )
        fig_pca.update_traces(marker=dict(size=6))
        fig_pca.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc', family='Plus Jakarta Sans'),
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5)
        )
        # Bar chart distribusi per cluster
        cluster_dist = df_pca['cluster_name'].value_counts().reset_index()
        cluster_dist.columns = ['Segmen', 'Jumlah']
        fig_dist_cluster = px.bar(
            cluster_dist, x='Segmen', y='Jumlah',
            color='Segmen',
            color_discrete_map=cluster_colors,
            text='Jumlah'
        )
        fig_dist_cluster.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc'), showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        fig_dist_cluster.update_traces(texttemplate='%{text}', textposition='outside')
    else:
        fig_pca = go.Figure()
        fig_dist_cluster = go.Figure()

    return html.Div(className="tab-content", children=[
        html.Div("Peta Visual Segmentasi Nasabah (Cluster Map)", className="section-title"),
        html.P("Setiap titik mewakili satu pengajuan KPR. Titik yang berdekatan berarti nasabah tersebut memiliki profil finansial yang mirip satu sama lain. Cluster yang terpisah jauh artinya perilaku keuangannya sangat berbeda.", className="mb-4 text-muted"),
        dbc.Row([
            dbc.Col(html.Div(className="glass-card", children=[
                html.H4("Posisi Setiap Nasabah dalam Ruang 2D (PCA)"),
                dcc.Graph(figure=fig_pca, config={'displayModeBar': False}, style={'height': '420px'})
            ]), width=8),
            dbc.Col(html.Div(className="glass-card", children=[
                html.H4("Ukuran Tiap Segmen"),
                dcc.Graph(figure=fig_dist_cluster, config={'displayModeBar': False}, style={'height': '420px'})
            ]), width=4),
        ])
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
                'Perlu Tinjauan Manual (Anomali)': '#f97316',
                'Profil Konservatif (Leverage Rendah)': '#10b981',
                'Data Error (Mustahil Secara Fisik/Logika)': '#ef4444',
                'Sinyal Risiko Kredit Tinggi': '#f59e0b'
            }
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#f8fafc'),
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig_bar.update_yaxes(title="")
    else:
        fig_bar = go.Figure()

    # Outlier Scatter Plot: tampilkan posisi anomali vs data normal
    fig_outlier = go.Figure()
    if not df_raw.empty and not df_anomalies.empty:
        normal_sample = df_raw[['loan_amount', 'income']].dropna().sample(min(800, len(df_raw)))
        fig_outlier.add_trace(go.Scatter(
            x=normal_sample['income'], y=normal_sample['loan_amount'],
            mode='markers', name='Nasabah Normal',
            marker=dict(color='rgba(148,163,184,0.3)', size=5),
            hovertemplate='Income: %{x}<br>Loan: %{y}<extra></extra>'
        ))
        outlier_sample = df_anomalies[['income', 'loan_amount', 'typology']].dropna().head(400)
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
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation='h', yanchor='bottom', y=-0.35, xanchor='center', x=0.5),
        xaxis_title='Pendapatan Nasabah (Income)', yaxis_title='Nilai Pinjaman (Loan Amount)'
    )

    return html.Div(className="tab-content", children=[
        html.Div("Deteksi 3.301 Kasus Prioritas Tinggi (Dari 100.000 Pengajuan)", className="section-title"),
        html.P("Sistem AI mendeteksi kasus-kasus aneh menggunakan metode berlapis. Ini bukan berarti pengajuan mereka ditolak, tetapi sangat direkomendasikan untuk ditinjau oleh manusia."),
        
        dbc.Row([
            dbc.Col(html.Div(className="glass-card mb-4 h-100", children=[
                html.H4("Posisi Nasabah Anomali vs Normal"),
                html.P("Titik berwarna = anomali yang terdeteksi. Abu-abu = data normal. Terlihat jelas anomali berada di luar pola umum.", className="small text-muted mb-2"),
                dcc.Graph(figure=fig_outlier, config={'displayModeBar': False}, style={'height': '350px'})
            ]), width=7),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Pengelompokan Kasus Tidak Wajar"),
                dcc.Graph(figure=fig_bar, config={'displayModeBar': False}, style={'height': '350px'})
            ]), width=5),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col(html.Div(className="d-flex flex-column gap-3", children=[
                html.Div(className="glass-card", children=[
                    html.H5(html.Span("Sinyal Risiko Kredit Tinggi (76 Kasus)", className="badge badge-high-risk")),
                    html.P("Pendapatan rendah dikombinasikan dengan pinjaman Jumbo dan leverage yang agresif. Saran: Underwriting review secara manual sangat direkomendasikan.", className="small")
                ]),
                html.Div(className="glass-card", children=[
                    html.H5(html.Span("Data Error (179 Kasus)", className="badge badge-high-risk")),
                    html.P("Nilai finansial yang melanggar batas fisik/logika (Misal: Suku bunga 0% atau LTV > 150%). Saran: Eskalasi ke tim Data Engineering untuk koreksi.", className="small")
                ]),
            ]), width=6),
            dbc.Col(html.Div(className="d-flex flex-column gap-3", children=[
                html.Div(className="glass-card", children=[
                    html.H5(html.Span("Profil Konservatif / Prospek (372 Kasus)", className="badge badge-low-risk")),
                    html.P("Anomali yang muncul dari nasabah Ultra High-Net-Worth yang memiliki rasio leverage sangat rendah. Saran: Prospek ideal untuk Wealth Management.", className="small")
                ]),
                html.Div(className="glass-card", children=[
                    html.H5(html.Span("Perlu Tinjauan Manual (2.674 Kasus)", className="badge badge-medium-risk")),
                    html.P("Penyimpangan data yang terdeteksi oleh sistem anomali namun butuh audit manusia untuk validasi. Saran: Masukkan ke daftar pantauan audit internal.", className="small")
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
            dbc.Tab(tab_1_executive(), label="1. Ringkasan Eksekutif", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_segmentation(), label="2. Segmentasi Nasabah", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_arm_visualization(), label="3. Visualisasi ARM", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_distributions(), label="4. Distribusi Pasar", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_4_anomalies(), label="5. Deteksi Anomali", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
            dbc.Tab(tab_conclusions(), label="6. Kesimpulan & Peluang", tabClassName="custom-tab", activeTabClassName="custom-tab-selected"),
        ], className="custom-tabs"),
        
        html.Div(className="text-center mt-5 mb-4 text-muted small", children=[
            "© 2026 Insight Communicator | HMDA Data Mining Project - Phase 5"
        ])
    ], fluid=True, className="px-5")
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
