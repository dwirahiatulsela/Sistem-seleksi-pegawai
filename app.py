import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sistem Seleksi Pegawai", layout="wide")
st.title("🏆 Sistem Cerdas Seleksi Pegawai")

# --- SIDEBAR PENGATURAN BOBOT ---
st.sidebar.header("⚙️ Pengaturan Bobot SAW")
w1 = st.sidebar.slider("Nilai Tes Tertulis %", 0, 100, 40)
w2 = st.sidebar.slider("Nilai Wawancara %", 0, 100, 40)
w3 = st.sidebar.slider("Pengalaman Kerja %", 0, 100, 20)

total_bobot = w1 + w2 + w3
bobot_values = [w1/100, w2/100, w3/100]

try:
    # Membaca data
    df = pd.read_csv('dataset_seleksi_pegawai_tetap.csv', sep=None, engine='python', encoding='utf-8-sig')
    df.columns = df.columns.str.strip().str.lower()

    if total_bobot != 100:
        st.sidebar.error(f"⚠️ Total Bobot: {total_bobot}%. Harus 100%!")
    else:
        # Kriteria yang tersedia di file Anda
        kriteria = ['nilai_tes_tertulis', 'nilai_wawancara', 'pengalaman_kerja_tahun']
        
        # 1. Normalisasi
        df_norm = df.copy()
        for k in kriteria:
            df_norm[k] = df[k] / df[k].max()
        
        # 2. Hitung Skor Akhir
        df['skor_akhir'] = (
            (df_norm['nilai_tes_tertulis'] * bobot_values[0]) +
            (df_norm['nilai_wawancara'] * bobot_values[1]) +
            (df_norm['pengalaman_kerja_tahun'] * bobot_values[2])
        )
        
        # 3. Ranking
        df_final = df.sort_values(by='skor_akhir', ascending=False).reset_index(drop=True)
        df_final['ranking'] = df_final.index + 1
        
        # --- TAMPILAN ---
        st.subheader("📌 Hasil Perangkingan Pelamar")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pelamar", len(df))
        m2.metric("Skor Tertinggi", f"{df_final['skor_akhir'].max():.3f}")
        m3.metric("Kandidat Terbaik", df_final.iloc[0]['nama'].title())

        st.divider()
        c1, c2 = st.columns([3, 2])
        with c1:
            st.write("### 📋 Daftar 10 Besar")
            st.dataframe(df_final[['ranking', 'nama', 'skor_akhir', 'rekomendasi']].head(10), use_container_width=True)
        with c2:
            st.write("### 📈 Visualisasi Skor")
            fig = px.bar(df_final.head(10), x='nama', y='skor_akhir', 
                         color='skor_akhir', labels={'nama':'Nama Pelamar', 'skor_akhir':'Total Skor'})
            st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Terjadi kesalahan: {e}")
