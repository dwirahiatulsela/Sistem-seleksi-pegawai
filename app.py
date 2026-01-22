import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Seleksi Pegawai", layout="wide")

st.title("🏆 Sistem Cerdas Seleksi Pegawai Tetap")
st.markdown("Implementasi Algoritma **Simple Additive Weighting (SAW)**")

# --- SIDEBAR: PENGATURAN BOBOT ---
st.sidebar.header("⚙️ Pengaturan Bobot")
w1 = st.sidebar.slider("Kinerja %", 0, 100, 40)
w2 = st.sidebar.slider("Disiplin %", 0, 100, 20)
w3 = st.sidebar.slider("Kerjasama %", 0, 100, 15)
w4 = st.sidebar.slider("Loyalitas %", 0, 100, 10)
w5 = st.sidebar.slider("Psikotes %", 0, 100, 15)

total_bobot = w1 + w2 + w3 + w4 + w5
bobot_values = [w1/100, w2/100, w3/100, w4/100, w5/100]

# --- PROSES DATA ---
try:
    # Membaca file CSV
    df = pd.read_csv('dataset_seleksi_pegawai_tetap.csv')
    
    # Membersihkan nama kolom dari spasi yang tidak terlihat
    df.columns = df.columns.str.strip()

    if total_bobot != 100:
        st.sidebar.error(f"⚠️ Total Bobot: {total_bobot}%. Harus 100%!")
    else:
        # Nama kolom sesuai dengan file CSV Anda (Capital Case)
        kriteria = ['Kinerja', 'Disiplin', 'Kerjasama', 'Loyalitas', 'Psikotes']
        
        # 1. Normalisasi (SAW)
        df_norm = df.copy()
        for col in kriteria:
            # Mengubah nilai menjadi skala 0-1
            df_norm[col] = df[col] / df[col].max()
        
        # 2. Perhitungan Skor Akhir
        df['Skor_Akhir'] = (
            (df_norm['Kinerja'] * bobot_values[0]) +
            (df_norm['Disiplin'] * bobot_values[1]) +
            (df_norm['Kerjasama'] * bobot_values[2]) +
            (df_norm['Loyalitas'] * bobot_values[3]) +
            (df_norm['Psikotes'] * bobot_values[4])
        )
        
        # 3. Ranking
        df_final = df.sort_values(by='Skor_Akhir', ascending=False).reset_index(drop=True)
        df_final['Ranking'] = df_final.index + 1

        # --- TAMPILAN DASHBOARD ---
        st.subheader("📌 Ringkasan Rekomendasi")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pegawai", len(df))
        m2.metric("Skor Tertinggi", f"{df_final['Skor_Akhir'].max():.3f}")
        m3.metric("Kandidat Terbaik", df_final.iloc[0]['Nama'])

        st.divider()

        col_tabel, col_grafik = st.columns([3, 2])
        
        with col_tabel:
            st.write("### 📋 Tabel Peringkat (Top 10)")
            # Menampilkan kolom yang penting saja
            st.dataframe(df_final[['Ranking', 'Nama', 'Skor_Akhir']].head(10), use_container_width=True)

        with col_grafik:
            st.write("### 📈 Visualisasi Skor")
            fig = px.bar(df_final.head(10), x='Nama', y='Skor_Akhir', 
                         color='Skor_Akhir', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)

except FileNotFoundError:
    st.error("❌ File 'dataset_seleksi_pegawai_tetap.csv' tidak ditemukan. Pastikan file sudah di-upload ke GitHub.")
except Exception as e:
    st.error(f"❌ Terjadi kesalahan teknis: {e}")
