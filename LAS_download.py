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
@st.cache_data
def get_user_data():
    try:
        df = pd.read_csv(google_sheet_csv_url)
        df.columns = df.columns.str.strip()  # Noņem atstarpes kolonnu nosaukumiem
        return df
    except Exception as e:
        st.error(f"Kļūda ielādējot lietotāju datus: {e}")
        return pd.DataFrame()  # Atgriež tukšu DataFrame, ja rodas kļūda

# Funkcija, lai pārbaudītu lietotāja pieteikšanos
def authenticate(username, password, users_df):
    user_row = users_df[users_df['username'] == username]
    if not user_row.empty:
        if user_row['password'].values[0] == password:
            return True
    return False

# Funkcija, lai lejupielādētu failu no Google Drive, izmantojot gdown
def download_from_google_drive(file_id, output_filename):
    try:
        download_url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(download_url, output_filename, quiet=False)
        return True
    except Exception as e:
        st.error(f"Kļūda lejupielādējot failu: {e}")
        return False

# Funkcija, lai izveidotu HTML pogu, kas atver visas saites vienlaikus ar aizkavi
def create_open_all_links_button(links):
    # HTML ar JS, kas rada pogu un ar JS palīdzību atver visas saites ar 0.5 sek. aizkavi
    html_content = """
    <html>
    <head>
    <style>
    .button {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
    }
    </style>
    </head>
    <body>
    """
    for link in links:
        html_content += f'<a href="{link}" target="_blank" style="display:none;">{link}</a>'
    html_content += """
    <script>
    function openAllLinks() {
        var links = document.getElementsByTagName('a');
        for (var i = 0; i < links.length; i++) {
            (function(i) {
                setTimeout(function() {
                    window.open(links[i].href, '_blank');
                }, i * 500); // 0.5 sekunde starp katru saiti
            })(i);
        }
    }
    </script>
    <button class="button" onclick="openAllLinks()">Lejupielādēt visus datus</button>
    </body></html>
    """
    return html_content

# Google Drive faila ID un ZIP faila atrašanās vieta
file_id = "1Xo7gVZ2WOm6yWv6o0-jCs_OsVQZQdffQ"
output_zip_path = "LASMAP.zip"

# Inicializē sesijas stāvokli, ja nav jau inicializēts
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ''

if 'data_downloaded' not in st.session_state:
    st.session_state.data_downloaded = False
    st.session_state.gdf = None

def login():
    st.title("Pieteikšanās")

    with st.form("login_form"):
        username = st.text_input("Lietotājvārds")
        password = st.text_input("Parole", type="password")
        submit_button = st.form_submit_button("Pieslēgties")

    if submit_button:
        if username and password:
            users = get_user_data()
            if not users.empty:
                if authenticate(username, password, users):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Veiksmīgi pieteicies!")
                else:
                    st.error("Nepareizs lietotājvārds vai parole.")
            else:
                st.error("Nevar ielādēt lietotāju datus.")
        else:
            st.warning("Lūdzu, aizpildiet abus laukus.")

def logout():
    st.session_state.authenticated = False
    st.session_state.username = ''
    st.session_state.data_downloaded = False
    st.session_state.gdf = None
    st.success("Jūs esat izlogojies.")

def main_app():
    st.title("LAS Datu Lejupielāde")

    st.write(f"Veiksmīgi pieteicies, **{st.session_state.username}**!")

    # Log-off poga
    if st.button("Iziet"):
        logout()
        st.experimental_rerun()

    st.markdown("---")
    st.header("Lejupielādēt LASMAP Datus")

    if not st.session_state.data_downloaded:
        if st.button("Lejupielādēt LASMAP ZIP"):
            with st.spinner("Lejupielādē LASMAP.zip..."):
                success = download_from_google_drive(file_id, output_zip_path)
                if success:
                    st.success("ZIP fails veiksmīgi lejupielādēts.")
                    # Izveido pagaidu direktoriju ZIP faila izsaiņošanai
                    extracted_folder = "LASMAP_extracted"
                    if os.path.exists(extracted_folder):
                        shutil.rmtree(extracted_folder)  # Dzēš, ja jau eksistē
                    os.makedirs(extracted_folder, exist_ok=True)

                    # Izsaiņo ZIP failu
                    try:
                        shutil.unpack_archive(output_zip_path, extracted_folder)
                        st.success("ZIP fails veiksmīgi izsaiņots.")
                    except Exception as e:
                        st.error(f"Kļūda izsaiņojot ZIP failu: {e}")
                        return

                    # Ielādē SHP failu
                    try:
                        shp_file_path = os.path.join(extracted_folder, 'LASMAP.shp')
                        gdf = gpd.read_file(shp_file_path)
                        st.session_state.gdf = gdf
                        st.session_state.data_downloaded = True
                        st.success("SHP fails veiksmīgi ielādēts.")
                    except Exception as e:
                        st.error(f"Kļūda SHP faila ielādē: {e}")
    else:
        st.success("LASMAP dati jau ir lejupielādēti un ielādēti.")

    if st.session_state.data_downloaded:
        st.header("Augšupielādēt Kontūras SHP Failus")
        uploaded_shp = st.file_uploader(
            "Augšupielādē savu kontūras SHP failu komponentes (SHP, SHX, DBF)",
            type=["shp", "shx", "dbf"],
            accept_multiple_files=True
        )

        if uploaded_shp:
            # Pārbauda, vai ir augšupielādēti visi nepieciešamie faili
            uploaded_extensions = [os.path.splitext(file.name)[1].lower() for file in uploaded_shp]
            required_extensions = ['.shp', '.shx', '.dbf']
            if all(ext in uploaded_extensions for ext in required_extensions):
                st.success("Visi nepieciešamie faili ir augšupielādēti.")
                if st.button("Apstrādāt Kontūras"):
                    with st.spinner("Apstrādā kontūras SHP failus..."):
                        with TemporaryDirectory() as temp_dir:
                            # Saglabāt visus augšupielādētos failus pagaidu mapē
                            for uploaded_file in uploaded_shp:
                                output_path = os.path.join(temp_dir, uploaded_file.name)
                                with open(output_path, 'wb') as f:
                                    f.write(uploaded_file.getbuffer())

                            # Identificēt un ielādēt kontūras SHP failu
                            shp_files = [f for f in uploaded_shp if f.name.lower().endswith('.shp')]
                            if not shp_files:
                                st.error("Nav atrasts SHP fails augšupielādētajos failos.")
                                return
                            
                            # Pieņemsim, ka ir tikai viens SHP fails
                            shp_file = shp_files[0]
                            shp_file_path = os.path.join(temp_dir, shp_file.name)
                            
                            if not os.path.exists(shp_file_path):
                                st.error(f"SHP fails nav atrasts: {shp_file_path}")
                                return

                            try:
                                contour_gdf = gpd.read_file(shp_file_path)
                            except Exception as e:
                                st.error(f"Kļūda kontūras SHP faila ielādē: {e}")
                                return

                            # Pārbaudīt, vai kontūras ģeometrija pārklājas ar poligoniem no LASMAP
                            gdf = st.session_state.gdf
                            total_polygons = len(gdf)
                            matched_polygons = 0  # Skaitīt pārklājušos poligonus
                            links = []  # Saglabāt saites

                            progress_bar = st.progress(0)
                            progress_percentage = 0

                            for index, row in gdf.iterrows():
                                if 'link' in row and pd.notna(row['link']):
                                    polygon = row.geometry
                                    # Pārbaudīt pārklāšanos ar kontūru faila ģeometriju
                                    if contour_gdf.intersects(polygon).any():
                                        matched_polygons += 1
                                        link = row['link']
                                        links.append(link)

                                # Atjauno progresijoslu
                                progress_percentage = (index + 1) / total_polygons
                                progress_bar.progress(progress_percentage)

                            if matched_polygons == 0:
                                st.warning("Neviens poligons nepārklājās ar kontūras failu.")
                            else:
                                st.success(f"Atrasti {matched_polygons} poligoni, kas pārklājas.")
                                st.warning("Lūdzu, izslēdziet uznirstošo logu bloķētāju, lai lejupielādētu visus datus ar vienu klikšķi.")
                                html_content = create_open_all_links_button(links)
                                st.components.v1.html(html_content, height=100)
            else:
                st.warning("Lūdzu, augšupielādē SHP, SHX un DBF failus vienlaikus.")

# Galvenais izpildes punkts
if st.session_state.authenticated:
    main_app()
else:
    login()
