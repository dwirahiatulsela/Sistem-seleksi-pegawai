import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sistem Seleksi Pegawai", layout="wide")
st.title("🏆 Sistem Cerdas Seleksi Pegawai Tetap")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Pengaturan Bobot")
w1 = st.sidebar.slider("Kinerja %", 0, 100, 40)
w2 = st.sidebar.slider("Disiplin %", 0, 100, 20)
w3 = st.sidebar.slider("Kerjasama %", 0, 100, 15)
w4 = st.sidebar.slider("Loyalitas %", 0, 100, 10)
w5 = st.sidebar.slider("Psikotes %", 0, 100, 15)

total_bobot = w1 + w2 + w3 + w4 + w5
bobot_values = [w1/100, w2/100, w3/100, w4/100, w5/100]

try:
    # 1. Membaca file dengan encoding universal untuk menghilangkan karakter aneh
    df = pd.read_csv('dataset_seleksi_pegawai_tetap.csv', sep=None, engine='python', encoding='utf-8-sig')
    
    # 2. STANDARISASI KOLOM (Menghapus spasi dan mengubah ke Huruf Kecil agar mudah dicocokkan)
    df.columns = df.columns.str.strip().str.lower()
    
    # Mencari nama kolom yang mirip di file CSV Anda
    # Karena di CSV Anda "Kinerja", setelah di-lower jadi "kinerja"
    map_kolom = {
        'nama': 'nama',
        'kinerja': 'kinerja',
        'disiplin': 'disiplin',
        'kerjasama': 'kerjasama',
        'loyalitas': 'loyalitas',
        'psikotes': 'psikotes'
    }

    if total_bobot != 100:
        st.sidebar.error(f"⚠️ Total Bobot: {total_bobot}%. Harus 100%!")
    else:
        # 3. NORMALISASI (SAW)
        df_norm = df.copy()
        kriteria = ['kinerja', 'disiplin', 'kerjasama', 'loyalitas', 'psikotes']
        
        for k in kriteria:
            df_norm[k] = df[k] / df[k].max()
        
        # 4. HITUNG SKOR
        df['skor_akhir'] = (
            (df_norm['kinerja'] * bobot_values[0]) +
            (df_norm['disiplin'] * bobot_values[1]) +
            (df_norm['kerjasama'] * bobot_values[2]) +
            (df_norm['loyalitas'] * bobot_values[3]) +
            (df_norm['psikotes'] * bobot_values[4])
        )
        
        # 5. RANKING
        df_final = df.sort_values(by='skor_akhir', ascending=False).reset_index(drop=True)
        
        # TAMPILAN
        st.subheader("📌 Hasil Rekomendasi")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Pegawai", len(df))
        m2.metric("Skor Tertinggi", f"{df_final['skor_akhir'].max():.3f}")
        # Gunakan nama kolom asli yang sudah di-lower
        m3.metric("Kandidat Terbaik", df_final.iloc[0]['nama'].title())

        st.divider()
        c1, c2 = st.columns([3, 2])
        with c1:
            st.write("### 📋 Top 10 Ranking")
            # Menampilkan kolom Nama dan Skor Akhir (huruf kecil sesuai hasil standarisasi)
            st.dataframe(df_final[['nama', 'skor_akhir']].head(10), use_container_width=True)
        with c2:
            st.write("### 📈 Grafik Skor")
            fig = px.bar(df_final.head(10), x='nama', y='skor_akhir', color='skor_akhir')
            st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error: {e}")
    st.write("Kolom yang terdeteksi di file Anda:", list(df.columns) if 'df' in locals() else "File tidak terbaca")
