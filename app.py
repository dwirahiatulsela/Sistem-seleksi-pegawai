import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Rekomendasi Pegawai Tetap", layout="wide")

# --- JUDUL & HEADER ---
st.title("🏆 Sistem Cerdas Seleksi Pegawai Tetap")
st.markdown("""
Sistem ini menggunakan algoritma **Simple Additive Weighting (SAW)** untuk memberikan rekomendasi 
berdasarkan kriteria objektif perusahaan.
""")

# --- SIDEBAR: PENGATURAN BOBOT (ALGORITMA SAW) ---
st.sidebar.header("⚙️ Pengaturan Bobot Kriteria")
st.sidebar.info("Total bobot harus 100%")

w1 = st.sidebar.slider("Kinerja (C1) %", 0, 100, 40)
w2 = st.sidebar.slider("Disiplin (C2) %", 0, 100, 20)
w3 = st.sidebar.slider("Kerjasama (C3) %", 0, 100, 15)
w4 = st.sidebar.slider("Loyalitas (C4) %", 0, 100, 10)
w5 = st.sidebar.slider("Psikotes (C5) %", 0, 100, 15)

total_bobot = w1 + w2 + w3 + w4 + w5
bobot_normalized = [w1/100, w2/100, w3/100, w4/100, w5/100]

if total_bobot != 100:
    st.sidebar.error(f"⚠️ Total Bobot: {total_bobot}%. Harus 100%!")

# --- UPLOAD DATASET ---
st.subheader("📁 1. Unggah Dataset Pegawai")
uploaded_file = st.file_uploader("Pilih file CSV (Gunakan 100 data dummy yang tadi)", type=["csv"])

if uploaded_file is not None and total_bobot == 100:
    df = pd.read_csv(uploaded_file)
    
    # --- PROSES ALGORITMA SAW ---
    with st.expander("Lihat Detail Proses Perhitungan"):
        st.write("Data Mentah (5 Data Teratas):")
        st.dataframe(df.head())

        # 1. Normalisasi
        # Kriteria Benefit: Nilai / Nilai Maksimal
        df_norm = df.copy()
        kriteria = ['kinerja', 'disiplin', 'kerjasama', 'loyalitas', 'psikotes']
        for col in kriteria:
            df_norm[col] = df[col] / df[col].max()
        
        st.write("Data Setelah Normalisasi (Skala 0-1):")
        st.dataframe(df_norm.head())

    # 2. Perhitungan Skor Akhir
    df['Skor_Akhir'] = (
        (df_norm['kinerja'] * bobot_normalized[0]) +
        (df_norm['disiplin'] * bobot_normalized[1]) +
        (df_norm['kerjasama'] * bobot_normalized[2]) +
        (df_norm['loyalitas'] * bobot_normalized[3]) +
        (df_norm['psikotes'] * bobot_normalized[4])
    )

    # 3. Perangkingan
    df_final = df.sort_values(by='Skor_Akhir', ascending=False).reset_index(drop=True)
    df_final['Ranking'] = df_final.index + 1

    # --- TAMPILAN HASIL ---
    st.divider()
    st.subheader("📊 2. Hasil Rekomendasi (Top 10)")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        # Menampilkan 10 besar
        top_10 = df_final.head(10)
        st.table(top_10[['Ranking', 'nama', 'Skor_Akhir']])

    with col2:
        # Visualisasi Bar Chart
        fig = px.bar(top_10, x='nama', y='Skor_Akhir', 
                     title="Perbandingan Skor Top 10",
                     color='Skor_Akhir', color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)

    # --- KESIMPULAN / AKSI ---
    st.subheader("✅ 3. Kesimpulan Sistem")
    best_candidate = df_final.iloc[0]['nama']
    st.success(f"Pegawai dengan rekomendasi tertinggi adalah **{best_candidate}** dengan skor **{df_final.iloc[0]['Skor_Akhir']:.4f}**")

    # Download hasil
    csv_result = df_final.to_csv(index=False).encode('utf-8')
    st.download_button("Download Hasil Ranking Lengkap (.csv)", data=csv_result, file_name="hasil_seleksi_pegawai.csv")

else:
    st.warning("Silakan unggah file CSV untuk memulai proses seleksi.")