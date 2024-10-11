import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import geopandas as gpd
import gdown
import os
import shutil
from tempfile import TemporaryDirectory

# Google Sheets piekļuves iestatīšana
def load_credentials():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_credentials.json', scope)
    client = gspread.authorize(creds)
    return client

# Funkcija, lai iegūtu lietotājus un paroles no Google Sheets
def get_user_data():
    client = load_credentials()
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1u-myVB6WYK0Zp18g7YDZt59AdrmHB0nA4rvQehYbcjg/edit?usp=sharing')
    worksheet = sheet.get_worksheet(0)  # pieņemot, ka dati ir pirmajā lapā
    data = worksheet.get_all_records()  # Iegūst visus datus kā sarakstu
    return data

# Funkcija, lai pārbaudītu pieteikšanās datus
def check_login(username, password, users):
    for user in users:
        if user['username'] == username and user['password'] == password:
            return True
    return False

# Login sadaļa
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Pieteikšanās")

    # Iegūst lietotājvārdus un paroles no Google Sheets
    users = get_user_data()

    # Lietotājvārds un parole
    username = st.text_input("Lietotājvārds")
    password = st.text_input("Parole", type="password")

    # Login poga
    if st.button("Pieteikties"):
        if check_login(username, password, users):
            st.session_state.logged_in = True
            st.success("Veiksmīgi pieteicies!")
        else:
            st.error("Nepareizs lietotājvārds vai parole.")
else:
    # Ja pieteicies, tad parāda visu pārējo lietotnes daļu
    # Google Drive faila ID un ZIP faila atrašanās vieta
    file_id = "1Xo7gVZ2WOm6yWv6o0-jCs_OsVQZQdffQ"
    output_zip_path = "LASMAP.zip"

    # Jaunais virsraksts
    st.write("Lejupielādē LAS datu karšu lapas...")

    # Progresjosla un lejupielādes process
    progress_bar = st.progress(0)
    progress_percentage = 0

    try:
        # Lejupielādē ZIP failu no Google Drive
        if download_from_google_drive(file_id, output_zip_path):
            progress_percentage += 0.3
            progress_bar.progress(progress_percentage)
        
            # Izveido pagaidu direktoriju ZIP faila izsaiņošanai
            extracted_folder = "LASMAP_extracted"
            if os.path.exists(extracted_folder):
                shutil.rmtree(extracted_folder)  # Dzēš, ja jau eksistē
            os.makedirs(extracted_folder, exist_ok=True)

            # Izsaiņo ZIP failu
            try:
                shutil.unpack_archive(output_zip_path, extracted_folder)
                progress_percentage += 0.3
                progress_bar.progress(progress_percentage)
            except Exception as e:
                st.error(f"Kļūda izsaiņojot ZIP failu: {e}")
        
            # Ielādē SHP failu
            try:
                shp_file_path = os.path.join(extracted_folder, 'LASMAP.shp')
                gdf = gpd.read_file(shp_file_path)
                progress_percentage += 0.4
                progress_bar.progress(progress_percentage)
            except Exception as e:
                st.error(f"Kļūda SHP faila ielādē: {e}")

            # Lietotājam piedāvā augšupielādēt SHP komponentes failus (SHP, SHX, DBF)
            uploaded_shp = st.file_uploader("Augšupielādē savu kontūras SHP failu komponentes (SHP, SHX, DBF)", type=["shp", "shx", "dbf"], accept_multiple_files=True)

            if uploaded_shp and len(uploaded_shp) == 3:
                start_button = st.button("Sākt")

                if start_button:
                    with TemporaryDirectory() as temp_dir:
                        # Saglabāt visus augšupielādētos failus pagaidu mapē
                        for uploaded_file in uploaded_shp:
                            output_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(output_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())

                        # Ielādē kontūras SHP failu
                        shp_file_path = [f.name for f in uploaded_shp if f.name.endswith('.shp')][0]
                        shp_file_path = os.path.join(temp_dir, shp_file_path)

                        try:
                            contour_gdf = gpd.read_file(shp_file_path)

                            # Pārbaudīt, vai kontūras ģeometrija pārklājas ar poligoniem no LASMAP
                            total_polygons = len(gdf)
                            matched_polygons = 0  # Skaitīt pārklājušos poligonus
                            links = []  # Saglabāt saites

                            # Progresjoslas izveide
                            progress_bar = st.progress(0)
                            progress_percentage = 0

                            for index, row in gdf.iterrows():
                                if 'link' in row and row['link']:  # Pārbaudīt, vai ir "link" atribūts
                                    polygon = row.geometry
                                    # Pārbaudīt pārklāšanos ar kontūru faila ģeometriju
                                    if contour_gdf.intersects(polygon).any():
                                        matched_polygons += 1
                                        link = row['link']
                                        links.append(link)  # Saglabāt saiti sarakstā
                                    
                                    # Atjauno progresjoslu
                                    progress_percentage = (index + 1) / total_polygons
                                    progress_bar.progress(progress_percentage)

                            if matched_polygons == 0:
                                st.warning("Neviens poligons nepārklājās ar kontūras failu.")
                            else:
                                st.success(f"Atrasti {matched_polygons} poligoni, kas pārklājas.")

                                # Parādīt brīdinājuma tekstu par uznirstošo logu bloķētāju
                                st.warning("Lūdzu, izslēdziet uznirstošo logu bloķētāju, lai lejupielādētu visus datus ar vienu klikšķi.")

                                # Parādīt visas saites un pievienot HTML pogu, lai tās visas atvērtu vienlaicīgi ar aizkavi
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
