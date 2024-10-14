import streamlit as st
import pandas as pd
import gdown
import geopandas as gpd
import os
import shutil
from tempfile import TemporaryDirectory

# Google Sheets tiešā CSV saite
google_sheet_csv_url = "https://docs.google.com/spreadsheets/d/1u-myVB6WYK0Zp18g7YDZt59AdrmHB0nA4rvQehYbcjg/export?format=csv"

# Funkcija, lai iegūtu lietotāja datus no Google Sheets
@st.cache_data  # Atjaunināts dekorators
def get_user_data():
    try:
        df = pd.read_csv(google_sheet_csv_url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Kļūda iegūstot lietotāju datus: {e}")
        return pd.DataFrame()

# Pārējais jūsu skripts paliek nemainīgs

# ... [Atlikušais kods no jūsu iepriekšējā skripta] ...

# Galvenā plūsma
if st.session_state.logged_in:
    main_app()
else:
    login_screen()
