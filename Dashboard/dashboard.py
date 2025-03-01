import os
import calendar
import pandas as pd
import streamlit as st
import plotly.express as px

# Dapatkan direktori file dashboard.py dan bangun path relatif ke file dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "all_data.csv")  # karena file berada di folder yang sama

if not os.path.exists(DATA_PATH):
    st.error(f"File tidak ditemukan: {DATA_PATH}")
    st.stop()

# Muat data
df = pd.read_csv(DATA_PATH)

# Ubah kolom dteday menjadi tipe datetime
df['dteday'] = pd.to_datetime(df['dteday'])

# Ubah data kategorik menjadi informasi deskriptif

# Musim: 1 -> Musim Semi, 2 -> Musim Panas, 3 -> Musim Gugur, 4 -> Musim Dingin
musim_map = {1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"}
df['season'] = df['season'].map(musim_map)

# Cuaca: 1 -> Cerah, 2 -> Berkabut, 3 -> Hujan Ringan/Salju, 4 -> Hujan Lebat/Es
weathersit_map = {1: "Cerah", 2: "Berkabut", 3: "Hujan Ringan/Salju", 4: "Hujan Lebat/Es"}
df['weathersit'] = df['weathersit'].map(weathersit_map)

# Tahun: 0 -> 2011, 1 -> 2012
df['yr'] = df['yr'].map({0: 2011, 1: 2012})

# Bulan: konversi angka bulan ke nama bulan
df['mnth'] = df['mnth'].apply(lambda x: calendar.month_name[x])

# Hari dalam seminggu: 0 -> Minggu, 1 -> Senin, dst.
weekday_map = {
    0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu",
    4: "Kamis", 5: "Jumat", 6: "Sabtu"
}
df['weekday'] = df['weekday'].map(weekday_map)

# Kolom 'hr' dibiarkan sebagai angka; isi nilai NaN dengan 0 dan konversi ke integer
df['hr'] = df['hr'].fillna(0).astype(int)

st.title("Dashboard Bike Sharing")
st.write("Dashboard interaktif berdasarkan data Bike Sharing.")

# Tampilkan data mentah (opsional)
if st.checkbox("Tampilkan Data Mentah"):
    st.write(df)

# Sidebar untuk filter tanggal
min_date = df['dteday'].min()
max_date = df['dteday'].max()
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date])

if len(date_range) != 2:
    st.error("Silakan pilih rentang tanggal yang benar.")
else:
    start_date, end_date = date_range
    filtered_df = df[(df['dteday'] >= pd.to_datetime(start_date)) & 
                     (df['dteday'] <= pd.to_datetime(end_date))]

    st.subheader("Jumlah Sewa per Hari")
    # Agregasi jumlah sewa per hari
    daily_df = filtered_df.groupby('dteday', as_index=False)['total_count'].sum()
    fig_line = px.line(daily_df, x='dteday', y='total_count', title="Jumlah Sewa per Hari",
                       labels={"dteday": "Tanggal", "total_count": "Jumlah Sewa"})
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Rata-rata Jumlah Sewa per Jam (Jam Kerja)")
    # Filter data hanya untuk jam kerja, misalnya dari jam 7 sampai jam 18
    working_hours_df = filtered_df[filtered_df['hr'].between(7, 18)]
    hourly_df = working_hours_df.groupby('hr', as_index=False)['total_count'].mean().sort_values('hr')
    fig_bar = px.bar(hourly_df, x='hr', y='total_count', 
                     title="Rata-rata Jumlah Sewa per Jam (Jam Kerja)",
                     labels={"hr": "Jam", "total_count": "Rata-rata Jumlah Sewa"},
                     color="total_count", color_continuous_scale="Blues")
    fig_bar.update_layout(xaxis=dict(dtick=1),
                          title={'x': 0.5, 'xanchor': 'center'},
                          template='plotly_white')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("""
    **Catatan:** Nilai pada sumbu y menunjukkan rata-rata jumlah sewa per jam kerja. 
    Misalnya, jika grafik menampilkan nilai sekitar **400**, artinya secara rata-rata terjadi *empat ratus sewa* per jam kerja.
    """)

    st.subheader("Pengaruh Suhu terhadap Jumlah Sewa")
    # Scatter plot: Pengaruh suhu terhadap jumlah sewa dengan warna berdasarkan kondisi cuaca
    fig_scatter = px.scatter(filtered_df, x='temp', y='total_count', color='weathersit',
                             title="Pengaruh Suhu terhadap Jumlah Sewa",
                             labels={"temp": "Suhu (nilai normalisasi)", "total_count": "Jumlah Sewa", "weathersit": "Cuaca"})
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("""
    **Catatan:** Nilai suhu pada grafik merupakan nilai normalisasi antara 0 dan 1, 
    di mana 0 berarti sangat dingin dan 1 berarti sangat panas.
    """)

    st.subheader("Rata-rata Jumlah Sewa berdasarkan Musim")
    # Agregasi rata-rata jumlah sewa per musim, diurutkan dari yang paling sedikit ke paling banyak
    musim_df = filtered_df.groupby('season', as_index=False)['total_count'].mean().sort_values('total_count', ascending=True)
    fig_season = px.bar(musim_df, x='season', y='total_count', title="Rata-rata Jumlah Sewa berdasarkan Musim",
                        labels={"season": "Musim", "total_count": "Rata-rata Jumlah Sewa"})
    st.plotly_chart(fig_season, use_container_width=True)
