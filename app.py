import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Seleksi Pegawai", layout="wide")

st.title("🏆 Sistem Cerdas Seleksi Pegawai")
st.markdown("""
Sistem ini menggunakan algoritma **Simple Additive Weighting (SAW)** untuk memberikan rekomendasi berdasarkan kriteria objektif perusahaan.
""")

# --- 2. SIDEBAR PENGATURAN BOBOT ---
st.sidebar.header("⚙️ Pengaturan Bobot SAW")
st.sidebar.info("Tentukan bobot kriteria (Total harus 100%)")
w1 = st.sidebar.slider("Nilai Tes Tertulis %", 0, 100, 40)
w2 = st.sidebar.slider("Nilai Wawancara %", 0, 100, 40)
w3 = st.sidebar.slider("Pengalaman Kerja %", 0, 100, 20)

total_bobot = w1 + w2 + w3
bobot_values = [w1/100, w2/100, w3/100]

# --- 3. INPUT DATASET ---
st.subheader("📁 Unggah Dataset Pegawai")
uploaded_file = st.file_uploader("Pilih file CSV", type="csv")

if uploaded_file is not None:
    try:
        # Membaca data dengan deteksi separator otomatis
        df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8-sig')
        
        # Standarisasi kolom: hapus spasi dan ubah ke huruf kecil
        df.columns = df.columns.str.strip().str.lower()

        with st.expander("Lihat Data Mentah (5 Teratas)"):
            st.write(df.head())

        # Validasi Total Bobot
        if total_bobot != 100:
            st.sidebar.error(f"❌ Total Bobot: {total_bobot}%. Harus 100%!")
            st.warning("Silakan sesuaikan slider di samping agar total menjadi 100%.")
        else:
            # Kolom kriteria sesuai dataset kamu
            kriteria = ['nilai_tes_tertulis', 'nilai_wawancara', 'pengalaman_kerja_tahun']
            
            # Cek apakah kolom yang dibutuhkan ada di file
            if all(k in df.columns for k in kriteria):
                
                # --- 4. PROSES ALGORITMA SAW ---
                
                # A. Normalisasi (Benefit)
                df_norm = df.copy()
                for k in kriteria:
                    df_norm[k] = df[k] / df[k].max()
                
                # B. Perhitungan Skor Akhir (Perkalian Bobot)
                df['skor_akhir'] = (
                    (df_norm['nilai_tes_tertulis'] * bobot_values[0]) +
                    (df_norm['nilai_wawancara'] * bobot_values[1]) +
                    (df_norm['pengalaman_kerja_tahun'] * bobot_values[2])
                )
                
                # C. Perangkingan
                df_final = df.sort_values(by='skor_akhir', ascending=False).reset_index(drop=True)
                df_final['ranking'] = df_final.index + 1
                
                # --- 5. TAMPILAN DASHBOARD HASIL ---
                st.divider()
                st.subheader("📌 2. Hasil Perangkingan Pelamar")
                
                # Ringkasan Metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Pelamar", len(df))
                m2.metric("Skor Tertinggi", f"{df_final['skor_akhir'].max():.3f}")
                m3.metric("Kandidat Terbaik", df_final.iloc[0]['nama'].title())

                st.write("") # Spasi

                # Tabel dan Grafik
                col_tabel, col_grafik = st.columns([3, 2])
                
                with col_tabel:
                    st.write("### 📋 Tabel 10 Peringkat Teratas")
                    # Pilih kolom yang ditampilkan agar rapi
                    tampil_kolom = ['ranking', 'nama', 'skor_akhir', 'rekomendasi']
                    st.dataframe(df_final[tampil_kolom].head(10), use_container_width=True)

                with col_grafik:
                    st.write("### 📈 Grafik Perbandingan Skor")
                    fig = px.bar(
                        df_final.head(10), 
                        x='nama', 
                        y='skor_akhir', 
                        color='skor_akhir',
                        color_continuous_scale='RdYlGn', # Merah ke Hijau
                        labels={'nama': 'Nama Pelamar', 'skor_akhir': 'Skor Akhir'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.error("❌ Kolom tidak sesuai!")
                st.info(f"Kolom yang ditemukan: {list(df.columns)}")
                st.write("Pastikan file CSV memiliki kolom: `nilai_tes_tertulis`, `nilai_wawancara`, dan `pengalaman_kerja_tahun`.")

    except Exception as e:
        st.error(f"Terjadi kesalahan teknis: {e}")

else:
    # Tampilan awal jika belum ada file
    st.info("👋 Selamat Datang! Silakan unggah file CSV dataset pelamar di atas untuk memulai perhitungan SAW.")
    st.write("Contoh format kolom yang dibutuhkan: `nama`, `nilai_tes_tertulis`, `nilai_wawancara`, `pengalaman_kerja_tahun`.")

