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
        {"kondisi": "KPR kedua (Piggyback/HELOC) dari investor swasta", "hasil": "Utang melampaui nilai rumah (LTV > 100%)", "insight": "Pinjaman kedua (piggyback/HELOC) mendorong total utang melewati nilai rumah. Karena tidak memenuhi syarat Fannie/Freddie, pinjaman berisiko tinggi ini dijual ke pembeli non-GSE.", "lift": 38.02, "risk": "high"},
        {"kondisi": "Nasabah muda (di bawah 25 tahun) + cicilan menengah", "hasil": "Memilih properti Manufactured Housing", "insight": "Rumah manufactured (pabrikan) adalah jalur kepemilikan rumah termurah, sering dipilih pemohon muda atau berpendapatan rendah sebagai segmen entry-level.", "lift": 19.73, "risk": "medium"},
        {"kondisi": "Pembelian properti tipe Multifamily (Apartemen/Kos)", "hasil": "Ditujukan untuk investasi atau bisnis sewa", "insight": "Properti multifamily hampir selalu untuk investasi/disewakan, bukan ditempati pemilik. Ini menandai segmen landlord/investor properti.", "lift": 13.51, "risk": "low"},
        {"kondisi": "Pinjaman Jumbo (Non-Conforming) + jaminan pemerintah", "hasil": "Berasal dari program VA Loan (Veteran)", "insight": "Pinjaman VA menyasar veteran dan biasanya disekuritisasi via Ginnie Mae. Muncul kuat pada plafon di atas batas konvensional.", "lift": 12.53, "risk": "low"},
        {"kondisi": "Properti Multifamily + bunga sedang (3-5%)", "hasil": "Pinjaman Jumbo Non-Conforming (> $647K)", "insight": "Pola segmen pasar yang tidak terlihat dari tabulasi sederhana: investor multifamily konsisten mengambil pinjaman besar dengan bunga standar.", "lift": 12.00, "risk": "medium"},
        {"kondisi": "Pembelian rumah baru tipe Multifamily", "hasil": "Pinjaman Jumbo Non-Conforming (> $647K)", "insight": "Pembelian properti multifamily baru secara konsisten membutuhkan plafon di atas batas konvensional, menunjukkan segmen investor yang aktif.", "lift": 11.34, "risk": "medium"},
        {"kondisi": "Uang muka nyaris 0% (LTV 95-100%) + Cash-out Refinance", "hasil": "Menggunakan fasilitas VA Loan (Veteran)", "insight": "VA mengizinkan cash-out refinance hingga LTV sangat tinggi (mendekati 100%), kelonggaran yang jarang ada pada kredit konvensional.", "lift": 10.72, "risk": "high"},
        {"kondisi": "Pre-Approval + didukung Ginnie Mae", "hasil": "Uang muka sangat minim (LTV 95-100%)", "insight": "Ginnie Mae hanya mensekuritisasi program pemerintah (FHA/VA/USDA) yang memang dirancang untuk uang muka minimal.", "lift": 9.77, "risk": "low"},
        {"kondisi": "VA Loan (Veteran) + bunga rendah (di bawah 3%)", "hasil": "Disokong program penjaminan Ginnie Mae", "insight": "Pinjaman VA hampir selalu berakhir di Ginnie Mae sebagai penjamin utama sekuritas KPR program pemerintah.", "lift": 9.09, "risk": "low"},
        {"kondisi": "DTI di atas 60% + rumah Manufactured Housing", "hasil": "Tenor pinjaman lebih pendek (15-25 tahun)", "insight": "Kredit rumah manufactured umumnya bertenor lebih pendek karena plafonnya kecil dan sebagian berbentuk chattel loan. DTI tinggi memperkuat pola ini.", "lift": 8.09, "risk": "high"}
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
                        html.Span("Insight: ", style={'fontWeight': '600'}),
                        rule['insight']
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
        margin=dict(l=10, r=10, t=10, b=120),
        legend=dict(orientation='h', yanchor='top', y=-0.2, xanchor='center', x=0.5),
        xaxis_title='Pendapatan Nasabah (Income)', yaxis_title='Nilai Pinjaman (Loan Amount)'
    )

    return html.Div(className="tab-content", children=[
        html.Div("Deteksi 3.301 Kasus Prioritas Tinggi (Dari 100.000 Pengajuan)", className="section-title"),
        html.P("Sistem AI mendeteksi kasus-kasus aneh menggunakan metode berlapis. Ini bukan berarti pengajuan mereka ditolak, tetapi sangat direkomendasikan untuk ditinjau oleh manusia."),
        
        dbc.Row([
            dbc.Col(html.Div(className="glass-card mb-4 h-100", children=[
                html.H4("Posisi Nasabah Anomali vs Normal"),
                html.P("Titik berwarna = anomali yang terdeteksi. Abu-abu = data normal. Terlihat jelas anomali berada di luar pola umum.", className="small text-muted mb-2"),
                dcc.Graph(figure=fig_outlier, config={'displayModeBar': False}, style={'height': '450px'})
            ]), width=7),
            dbc.Col(html.Div(className="glass-card h-100", children=[
                html.H4("Pengelompokan Kasus Tidak Wajar"),
                dcc.Graph(figure=fig_bar, config={'displayModeBar': False}, style={'height': '450px'})
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
    app.run_server(debug=True, port=8050)
