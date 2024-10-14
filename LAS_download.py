import streamlit as st
import pandas as pd

# Google Sheets tiešā CSV saite
google_sheet_csv_url = "https://docs.google.com/spreadsheets/d/1u-myVB6WYK0Zp18g7YDZt59AdrmHB0nA4rvQehYbcjg/export?format=csv"

@st.cache
def get_user_data():
    try:
        df = pd.read_csv(google_sheet_csv_url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Kļūda iegūstot lietotāju datus: {e}")
        return pd.DataFrame()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''

def login_screen():
    st.title("Pieteikšanās")
    with st.form(key='login_form'):
        username = st.text_input("Lietotājvārds").strip()
        password = st.text_input("Parole", type="password").strip()
        submit_button = st.form_submit_button(label="Pieslēgties")
    if submit_button:
        if username == "" or password == "":
            st.error("Lūdzu, ievadiet gan lietotājvārdu, gan paroli.")
            return
        users = get_user_data()
        if 'username' in users.columns and 'password' in users.columns:
            user_row = users[users['username'].str.lower() == username.lower()]
            if not user_row.empty and user_row['password'].values[0].strip() == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Veiksmīgi pieteicies!")
            else:
                st.error("Nepareizs lietotājvārds vai parole.")
        else:
            st.error("Kolonnas 'username' un 'password' nav atrastas datu failā.")

def main_app():
    st.success(f"Veiksmīgi pieteicies, {st.session_state.username}!")
    # Šeit pievienojiet galveno aplikācijas kodu

if st.session_state.logged_in:
    main_app()
else:
    login_screen()
