import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Tentukan path file CSV Anda (sesuaikan jika perlu)
DATA_PATH = r"C:\Users\SURYA\Downloads\proyek_analisis_data\Dashboard\all_data.csv"

if not os.path.exists(DATA_PATH):
    st.error(f"File tidak ditemukan: {DATA_PATH}")
    st.stop()

# Muat data
df = pd.read_csv(DATA_PATH)

# Ubah kolom dteday menjadi tipe datetime
df['dteday'] = pd.to_datetime(df['dteday'])

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
    filtered_df = df[(df['dteday'] >= pd.to_datetime(start_date)) & (df['dteday'] <= pd.to_datetime(end_date))]

    st.subheader("Total Count Harian")
    # Agregasi total_count per hari
    daily_df = filtered_df.groupby('dteday', as_index=False)['total_count'].sum()
    fig_line = px.line(daily_df, x='dteday', y='total_count', title="Total Count per Hari")
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Rata-rata Total Count per Jam")
    # Agregasi rata-rata total_count per jam
    hourly_df = filtered_df.groupby('hr', as_index=False)['total_count'].mean()
    fig_bar = px.bar(hourly_df, x='hr', y='total_count', title="Rata-rata Total Count per Jam",
                     labels={"hr": "Jam", "total_count": "Total Count"})
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Pengaruh Suhu terhadap Total Count")
    # Scatter plot total_count vs temp dengan warna berdasarkan weathersit
    fig_scatter = px.scatter(filtered_df, x='temp', y='total_count', color='weathersit',
                             title="Total Count vs Temperature",
                             labels={"temp": "Temperature", "total_count": "Total Count", "weathersit": "Weather"})
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Rata-rata Total Count berdasarkan Season")
    # Agregasi rata-rata total_count per season
    season_df = filtered_df.groupby('season', as_index=False)['total_count'].mean()
    fig_season = px.bar(season_df, x='season', y='total_count', title="Rata-rata Total Count berdasarkan Season",
                        labels={"season": "Season", "total_count": "Total Count"})
    st.plotly_chart(fig_season, use_container_width=True)
