import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Seleksi Pegawai", layout="wide")

st.title("🏆 Sistem Cerdas Seleksi Pegawai Tetap")
st.markdown("Menggunakan Algoritma **Simple Additive Weighting (SAW)**")

# --- SIDEBAR: BOBOT ---
st.sidebar.header("⚙️ Pengaturan Bobot")
w1 = st.sidebar.slider("Kinerja %", 0, 100, 40)
w2 = st.sidebar.slider("Disiplin %", 0, 100, 20)
w3 = st.sidebar.slider("Kerjasama %", 0, 100, 15)
w4 = st.sidebar.slider("Loyalitas %", 0, 100, 10)
w5 = st.sidebar.slider("Psikotes %", 0, 100, 15)

total_bobot = w1 + w2 + w3 + w4 + w5
bobot = [w1/100, w2/100, w3/100, w4/100, w5/100]

# --- LOAD DATA ---
# Langsung membaca file yang ada di folder yang sama
try:
    df = pd.read_csv('dataset_seleksi_pegawai_tetap.csv')
    
    if total_bobot != 100:
        st.sidebar.error(f"Total Bobot: {total_bobot}%. Harus 100%!")
    else:
        # Nama kolom sesuai file CSV Anda
        kriteria = ['Kinerja', 'Disiplin', 'Kerjasama', 'Loyalitas', 'Psikotes']
        
        # 1. Normalisasi (SAW)
        df_norm = df.copy()
        for col in kriteria:
            df_norm[col] = df[col] / df[col].max()
        
        # 2. Hitung Skor Akhir
        df['Skor_Akhir'] = (
            (df_norm['Kinerja'] * bobot[0]) +
            (df_norm['Disiplin'] * bobot[1]) +
            (df_norm['Kerjasama'] * bobot[2]) +
            (df_norm['Loyalitas'] * bobot[3]) +
            (df_norm['Psikotes'] * bobot[4])
        )
        
        # 3. Ranking
        df_final = df.sort_values(by='Skor_Akhir', ascending=False).reset_index(drop=True)
        df_final['Ranking'] = df_final.index + 1

        # --- TAMPILAN ---
        st.subheader("📌 Ringkasan Hasil")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Kandidat", len(df))
        c2.metric("Skor Tertinggi", f"{df_final['Skor_Akhir'].max():.3f}")
        c3.metric("Rekomendasi Utama", df_final.iloc[0]['Nama'])

        st.divider()

        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.subheader("📊 Tabel Ranking (Top 10)")
            st.dataframe(df_final[['Ranking', 'Nama', 'Skor_Akhir']].head(10), use_container_width=True)

        with col_right:
            st.subheader("📈 Visualisasi Skor")
            fig = px.bar(df_final.head(10), x='Nama', y='Skor_Akhir', color='Skor_Akhir',
                         color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

except FileNotFoundError:
    st.error("File 'dataset_seleksi_pegawai_tetap.csv' tidak ditemukan di repositori!")
