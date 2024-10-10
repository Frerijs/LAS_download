import streamlit as st
import geopandas as gpd
import requests
import zipfile
import os
import shutil
import webbrowser
from tempfile import TemporaryDirectory

# Funkcija, lai lejupielādētu ZIP failu no Google Drive
def download_zip_from_google_drive(file_id, output_filename):
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        total_length = int(response.headers.get('content-length', 0))
        progress_bar = st.progress(0)
        downloaded = 0
        with open(output_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress_bar.progress(min(int(downloaded / total_length * 100), 100))
        return True
    else:
        st.error(f"Neizdevās lejupielādēt ZIP failu no Google Drive. Statusa kods: {response.status_code}")
        return False

# Funkcija ZIP faila izsaiņošanai
def unzip_file(zip_file_path, extract_to):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    st.write(f"ZIP fails izsaiņots uz: {extract_to}")

# Funkcija, lai lejupielādētu failu no saites
def download_data(url, output_filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_filename, 'wb') as file:
            file.write(response.content)
        return output_filename
    else:
        return None

# Funkcija, lai saglabātu visus failus ZIP arhīvā
def save_as_zip(file_paths, output_zip_path):
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for file in file_paths:
            zipf.write(file, os.path.basename(file))
    return output_zip_path

# Google Drive faila ID
file_id = "1Xo7gVZ2WOm6yWv6o0-jCs_OsVQZQdffQ"
output_zip_path = "LASMAP.zip"

# Progresbar un pogas pievienošana
st.write("Lejupielādē ZIP failu no Google Drive...")
progress_message = st.empty()
progress_message.write("Sākas lejupielāde...")
if download_zip_from_google_drive(file_id, output_zip_path):
    st.write(f"Fails veiksmīgi lejupielādēts: {output_zip_path}")
    
    # Izveido pagaidu direktoriju ZIP faila izsaiņošanai
    extracted_folder = "LASMAP_extracted"
    if os.path.exists(extracted_folder):
        shutil.rmtree(extracted_folder)  # Izdzēst, ja jau eksistē
    os.makedirs(extracted_folder, exist_ok=True)

    # Izsaiņo ZIP failu
    unzip_file(output_zip_path, extracted_folder)
    st.write("ZIP fails veiksmīgi izsaiņots!")

    # Ielādēt SHP failu
    try:
        shp_file_path = os.path.join(extracted_folder, 'LASMAP.shp')
        gdf = gpd.read_file(shp_file_path)
        st.write("SHP fails veiksmīgi ielādēts.")
    except Exception as e:
        st.error(f"Kļūda SHP faila ielādē: {e}")

    # Lietotājam piedāvā augšupielādēt visus SHP komponentes failus vienlaikus
    uploaded_shp = st.file_uploader("Augšupielādē savu kontūras SHP failu komponentes (SHP, SHX, DBF)", type=["shp", "shx", "dbf"], accept_multiple_files=True)

    if uploaded_shp and len(uploaded_shp) == 3:
        start_button = st.button("Sākt")

        if start_button:
            with TemporaryDirectory() as temp_dir:
                st.write("Saglabā augšupielādētos failus...")
                # Saglabāt visus augšupielādētos failus pagaidu mapē
                for uploaded_file in uploaded_shp:
                    output_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(output_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())

                # Meklēt SHP failu un ielādēt ar GeoPandas
                shp_file_path = [f.name for f in uploaded_shp if f.name.endswith('.shp')][0]
                shp_file_path = os.path.join(temp_dir, shp_file_path)

                try:
                    # Ielādēt kontūras SHP failu
                    contour_gdf = gpd.read_file(shp_file_path)
                    st.write("Kontūras SHP fails veiksmīgi ielādēts.")

                    # Piedāvā izvēlēties lejupielādes mapi ar manuālu ceļa ievadīšanu
                    download_folder = st.text_input("Ievadi lejupielādes mapi:", value=os.getcwd())
                    if not os.path.exists(download_folder):
                        os.makedirs(download_folder)

                    # Pārbaudīt, vai kontūras ģeometrija pārklājas ar poligoniem no LASMAP
                    progress_bar = st.progress(0)
                    total_polygons = len(gdf)
                    matched_polygons = 0  # Skaitīt pārklājušos poligonus
                    file_paths = []  # Saglabāt ceļus uz lejupielādētajiem failiem

                    for index, row in gdf.iterrows():
                        if 'link' in row and row['link']:  # Pārbaudīt, vai ir "link" atribūts
                            polygon = row.geometry
                            # Pārbaudīt pārklāšanos ar kontūru faila ģeometriju
                            if contour_gdf.intersects(polygon).any():
                                matched_polygons += 1
                                link = row['link']
                                filename = os.path.join(download_folder, f'downloaded_data_{index}.zip')
                                st.write(f"Lejupielādē failu no: {link}")
                                result = download_data(link, filename)
                                if result:
                                    file_paths.append(result)
                                    st.write(f"Fails '{filename}' veiksmīgi lejuplādēts.")
                        
                            progress_bar.progress(min(int((index + 1) / total_polygons * 100), 100))

                    if matched_polygons == 0:
                        st.warning("Neviens poligons nepārklājās ar kontūras failu.")
                    else:
                        # Saglabāt visus failus ZIP arhīvā
                        zip_output_path = os.path.join(download_folder, 'all_downloads.zip')
                        zip_result = save_as_zip(file_paths, zip_output_path)
                        st.success(f"Lejupielādes process pabeigts. Pārklājās {matched_polygons} poligoni.")
                        # Nodrošināt saiti uz ZIP failu
                        st.write(f"[Lejupielādēt visus failus ZIP arhīvā]({zip_output_path})")
                except Exception as e:
                    st.error(f"Kļūda, ielādējot SHP failu: {e}")
    else:
        st.write("Lūdzu, augšupielādē SHP, SHX un DBF failus vienlaikus.")
else:
    st.error("ZIP faila lejupielāde neizdevās.")
