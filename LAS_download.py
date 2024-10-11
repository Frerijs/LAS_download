import streamlit as st
import pandas as pd

# Google Sheets tiešā CSV saite
google_sheet_csv_url = "https://docs.google.com/spreadsheets/d/1u-myVB6WYK0Zp18g7YDZt59AdrmHB0nA4rvQehYbcjg/export?format=csv"

# Funkcija, lai iegūtu lietotāja datus no Google Sheets
def get_user_data():
    df = pd.read_csv(google_sheet_csv_url)
    df.columns = df.columns.str.strip()  # Noņem atstarpes kolonnu nosaukumiem
    st.write("Kolonnu nosaukumi:", df.columns.tolist())  # Izdrukā kolonnu nosaukumus pārbaudei
    return df

# Funkcija, lai pārbaudītu lietotāja pieteikšanos
def authenticate(username, password, users_df):
    user_row = users_df[users_df['username'] == username]
    if not user_row.empty:
        if user_row['password'].values[0] == password:
            return True
    return False

# Streamlit lietotāja interfeiss
st.title("Pieteikšanās")

username = st.text_input("Lietotājvārds")
password = st.text_input("Parole", type="password")

if st.button("Pieslēgties"):
    users = get_user_data()
    if authenticate(username, password, users):
        st.success("Veiksmīgi pieteicies!")
        # Šeit var pievienot galveno funkcionalitāti, ja pieteikšanās ir veiksmīga
    else:
        st.error("Nepareizs lietotājvārds vai parole.")
