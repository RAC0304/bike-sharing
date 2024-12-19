import streamlit as st
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# Set up logging (Optional: Adjust logging level as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Load data outside the main function for caching
@st.cache_data 
def load_data():
    try:
        hour_df_2012 = pd.read_csv('hour_df_2012_cleaned.csv')
        day_df_summer_2011 = pd.read_csv('day_df_summer_2011_cleaned.csv')
        return hour_df_2012, day_df_summer_2011
    except FileNotFoundError:
        st.error("Data files not found. Please ensure 'hour_df_2012_cleaned.csv' and 'day_df_summer_2011_cleaned.csv' are in the same directory as your script.")
        return None, None 
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        st.error(f"Error loading data: {e}")
        return None, None

# Main function
def main():
    # Load data
    hour_df_2012, day_df_summer_2011 = load_data()

    # Check if data loading was successful
    if hour_df_2012 is None or day_df_summer_2011 is None:
        st.stop()  

    # --- Sidebar ---
    st.sidebar.title("Bike Sharing Dashboard")

    # Try to load the bike image
    try:
        image = Image.open('bike.png')
        st.sidebar.image(image, use_container_width=True)
    except Exception as e:
        logger.warning(f"Could not load bike image: {e}")
        st.sidebar.warning("Could not load bike image")

    # Convert date columns
    hour_df_2012['dteday'] = pd.to_datetime(hour_df_2012['dteday'])
    day_df_summer_2011['dteday'] = pd.to_datetime(day_df_summer_2011['dteday'])

    # Date filters
    min_date_hour = hour_df_2012['dteday'].min()
    max_date_hour = hour_df_2012['dteday'].max()
    min_date_day = day_df_summer_2011['dteday'].min()
    max_date_day = day_df_summer_2011['dteday'].max()

    date_filter_hour = st.sidebar.date_input(
        "Filter Date (Hourly Data 2012)", 
        (min_date_hour, max_date_hour)
    )
    
    date_filter_day = st.sidebar.date_input(
        "Filter Date (Daily Summer 2011)", 
        (min_date_day, max_date_day)
    )

    # --- Main Content ---
    st.title("Bike Sharing Analysis Dashboard")

    # Filter data
    filtered_hour_df = hour_df_2012[
        (hour_df_2012['dteday'].dt.date >= date_filter_hour[0]) & 
        (hour_df_2012['dteday'].dt.date <= date_filter_hour[1])
    ]

    filtered_day_df = day_df_summer_2011[
        (day_df_summer_2011['dteday'].dt.date >= date_filter_day[0]) & 
        (day_df_summer_2011['dteday'].dt.date <= date_filter_day[1])
    ]

    # --- Visualizations ---
    
    # 1. Hourly Rentals
    st.subheader("Hourly Bike Rentals (2012)")
    st.write("Visualisasi ini menunjukkan rata-rata jumlah penyewaan sepeda per jam pada tahun 2012, dibedakan berdasarkan hari kerja dan akhir pekan.")
    
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    average_rentals_per_hour = filtered_hour_df.groupby(['hr', 'is_weekend'])['cnt'].mean().reset_index()
    sns.lineplot(data=average_rentals_per_hour, x='hr', y='cnt', hue='is_weekend', ax=ax1)
    ax1.set_title('Rata-rata Penyewaan Sepeda per Jam (2012)')
    ax1.set_xlabel('Jam')
    ax1.set_ylabel('Jumlah Penyewaan')
    ax1.set_xticks(range(24))
    ax1.legend(title='Tipe Hari', labels=['Hari Kerja', 'Akhir Pekan'])
    ax1.grid(True)
    st.pyplot(fig1)

    # 2. Weekend vs Weekday Distribution
    st.write("Box plot ini menunjukkan sebaran penyewaan sepeda pada hari kerja dan akhir pekan pada tahun 2012.")
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=filtered_hour_df, x='is_weekend', y='cnt', ax=ax2)
    ax2.set_title('Distribusi Penyewaan Sepeda pada Hari Kerja dan Akhir Pekan (2012)')
    ax2.set_xlabel('Tipe Hari')
    ax2.set_ylabel('Jumlah Penyewaan')
    ax2.set_xticklabels(['Hari Kerja', 'Akhir Pekan'])
    ax2.grid(True)
    st.pyplot(fig2)

    # 3. Summer 2011 Analysis
    st.subheader("Summer 2011 Bike Rentals (Impact of Weather)")
    st.write("Visualisasi ini menunjukkan hubungan antara suhu dan jumlah penyewaan sepeda selama musim panas tahun 2011, serta rata-rata penyewaan berdasarkan kondisi cuaca.")

    # Temperature vs Rentals
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=filtered_day_df, x='temp', y='cnt', hue='weathersit', ax=ax3)
    ax3.set_title('Hubungan antara Suhu dan Jumlah Penyewaan (Musim Panas 2011)')
    ax3.set_xlabel('Suhu (Celcius)')
    ax3.set_ylabel('Jumlah Penyewaan')
    ax3.grid(True)
    st.pyplot(fig3)

    # Weather Impact
    average_rentals_by_weather = filtered_day_df.groupby('weathersit')['cnt'].mean().reset_index()
    fig4, ax4 = plt.subplots(figsize=(8, 6))
    sns.barplot(data=average_rentals_by_weather, x='weathersit', y='cnt', ax=ax4)
    ax4.set_title('Rata-rata Penyewaan Sepeda berdasarkan Kondisi Cuaca (Musim Panas 2011)')
    ax4.set_xlabel('Kondisi Cuaca')
    ax4.set_ylabel('Jumlah Penyewaan')
    ax4.set_xticklabels(['Cerah', 'Berawan', 'Gerimis', 'Hujan Lebat'])
    ax4.grid(True)
    st.pyplot(fig4)

if __name__ == "__main__":
    main()