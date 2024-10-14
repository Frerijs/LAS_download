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
        df.columns = df.columns.str.strip().str.lower()  # Noņem atstarpes un pārvērš uz maziem burtiem
        return df
    except Exception as e:
        st.error(f"Kļūda iegūstot lietotāju datus: {e}")
        return pd.DataFrame()

# Funkcija, lai pārbaudītu lietotāja pieteikšanos
def authenticate(username, password, users_df):
    if 'username' not in users_df.columns or 'password' not in users_df.columns:
        st.error("Google Sheets datiem trūkst 'username' vai 'password' kolonnas.")
        return False
    user_row = users_df[users_df['username'].str.lower() == username.lower()]
    if not user_row.empty:
        stored_password = user_row['password'].values[0]
        if stored_password.strip() == password:
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

# Funkcija, lai izveidotu HTML kodu, kas atver visas saites vienlaikus ar aizkavi
def create_open_all_links_button(links):
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
        html_content += f'<a href="{link}" target="_blank">{link}</a><br>'
    html_content += """
    <script>
    function openAllLinks() {
        var links = document.getElementsByTagName('a');
        for (var i = 0; i < links.length; i++) {
            (function(i) {
                setTimeout(function() {
                    window.open(links[i].href, '_blank');
                }, i * 500); 
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

# Inicializē sesijas stāvokli
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''

# Funkcija, lai pārvaldītu pieteikšanās procesu
def login_screen():
    st.title("Pieteikšanās")
    username = st.text_input("Lietotājvārds").strip()
    password = st.text_input("Parole", type="password").strip()
    
    if st.button("Pieslēgties"):
        if username == "" or password == "":
            st.error("Lūdzu, ievadiet gan lietotājvārdu, gan paroli.")
            return
        users = get_user_data()
        if authenticate(username, password, users):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Veiksmīgi pieteicies!")
            # Pāriet uz galveno aplikāciju
        else:
            st.error("Nepareizs lietotājvārds vai parole.")

# Funkcija, lai attēlotu galveno aplikācijas saturu
def main_app():
    st.success(f"Veiksmīgi pieteicies, {st.session_state.username}!")
    
    # Progresjosla un lejupielādes process
    progress_bar = st.progress(0)
    progress_percentage = 0

    # Jaunais virsraksts
    st.write("Lejupielādē LAS datu karšu lapas...")

    try:
        if download_from_google_drive(file_id, output_zip_path):
            progress_percentage += 0.3
            progress_bar.progress(progress_percentage)

            # Izveido pagaidu direktoriju ZIP faila izsaiņošanai
            extracted_folder = "LASMAP_extracted"
            if os.path.exists(extracted_folder):
                shutil.rmtree(extracted_folder)
            os.makedirs(extracted_folder, exist_ok=True)

            try:
                shutil.unpack_archive(output_zip_path, extracted_folder)
                progress_percentage += 0.3
                progress_bar.progress(progress_percentage)
            except Exception as e:
                st.error(f"Kļūda izsaiņojot ZIP failu: {e}")

            try:
                shp_file_path = os.path.join(extracted_folder, 'LASMAP.shp')
                gdf = gpd.read_file(shp_file_path)
                progress_percentage += 0.4
                progress_bar.progress(progress_percentage)
            except Exception as e:
                st.error(f"Kļūda SHP faila ielādē: {e}")

            uploaded_shp = st.file_uploader("Augšupielādē savu kontūras SHP failu komponentes (SHP, SHX, DBF)", type=["shp", "shx", "dbf"], accept_multiple_files=True)

            if uploaded_shp and len(uploaded_shp) == 3:
                start_button = st.button("Sākt")

                if start_button:
                    with TemporaryDirectory() as temp_dir:
                        for uploaded_file in uploaded_shp:
                            output_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(output_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())

                        shp_file_name = [f.name for f in uploaded_shp if f.name.endswith('.shp')]
                        if not shp_file_name:
                            st.error("SHP fails nav atrasts.")
                            return
                        shp_file_path = os.path.join(temp_dir, shp_file_name[0])

                        try:
                            contour_gdf = gpd.read_file(shp_file_path)
                            total_polygons = len(gdf)
                            matched_polygons = 0
                            links = []

                            progress_bar = st.progress(0)
                            progress_percentage = 0

                            for index, row in gdf.iterrows():
                                if 'link' in row and pd.notna(row['link']):
                                    polygon = row.geometry
                                    if contour_gdf.intersects(polygon).any():
                                        matched_polygons += 1
                                        link = row['link']
                                        links.append(link)
                                        progress_percentage = (index + 1) / total_polygons
                                        progress_bar.progress(progress_percentage)

                            if matched_polygons == 0:
                                st.warning("Neviens poligons nepārklājās ar kontūras failu.")
                            else:
                                st.success(f"Atrasti {matched_polygons} poligoni, kas pārklājas.")
                                st.warning("Lūdzu, izslēdziet uznirstošo logu bloķētāju, lai lejupielādētu visus datus ar vienu klikšķi.")
                                html_content = create_open_all_links_button(links)
                                st.components.v1.html(html_content, height=300)

                        except Exception as e:
                            st.error(f"Kļūda, ielādējot kontūras SHP failu: {e}")
            else:
                st.warning("Lūdzu, augšupielādē SHP, SHX un DBF failus vienlaikus.")
        else:
            st.error("Kļūda ZIP faila lejupielādē no Google Drive.")
    except Exception as e:
        st.error(f"Kļūda: {e}")

# Ja pieteicies, rāda galveno aplikāciju, ja nē, rāda pieteikšanās ekrānu
if not st.session_state.logged_in:
    login_screen()
else:
    main_app()
