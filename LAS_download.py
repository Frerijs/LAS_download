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
        with open(output_filename, 'wb') as f:
            total_length = int(response.headers.get('content-length', 0))
            progress_bar = st.progress(0)
            downloaded = 0

            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    progress_bar.progress(int(downloaded / total_length * 100))
        return True
    else:
        st.error(f"Neizdevās lejupielādēt ZIP failu no Google Drive. Statusa kods: {response.status_code}")
        return False

# Funkcija ZIP faila izsaiņošanai
def unzip_file(zip_file_path, extract_to):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Funkcija, lai lejupielādētu failu no saites
def download_data(url, output_filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_filename, 'wb') as file:
            file.write(response.content)
        return f"Fails '{output_filename}' veiksmīgi lejuplādēts."
    else:
        return "Lejuplāde neizdevās."

# Google Drive faila ID
file_id = "1Xo7gVZ2WOm6yWv6o0-jCs_OsVQZQdffQ"
output_zip_path = "LASMAP.zip"

# Lejupielādē ZIP failu no Google Drive
st.write("Lejupielādē ZIP failu no Google Drive...")
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
    shp_file_path = os.path.join(extracted_folder, 'LASMAP.shp')
    gdf = gpd.read_file(shp_file_path)

    # Lietotājam piedāvā augšupielādēt visus SHP komponentes failus vienlaikus
    uploaded_shp = st.file_uploader("Augšupielādē savu kontūras SHP failu komponentes (SHP, SHX, DBF)", type=["shp", "shx", "dbf"], accept_multiple_files=True)

    if uploaded_shp and len(uploaded_shp) == 3:
        start_button = st.button("Sākt")

        if start_button:
            # Izveido pagaidu direktoriju augšupielādētajiem failiem
            with TemporaryDirectory() as temp_dir:
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

                    # Piedāvā izvēlēties lejupielādes mapi
                    download_folder = st.text_input("Lejupielādes mape", value=os.getcwd())

                    # Pārbaudīt, vai kontūras ģeometrija pārklājas ar poligoniem no LASMAP
                    progress_bar = st.progress(0)
                    total_polygons = len(gdf)

                    for index, row in gdf.iterrows():
                        if 'link' in row and row['link']:  # Pārbaudīt, vai ir "link" atribūts
                            polygon = row.geometry
                            # Pārbaudīt pārklāšanos ar kontūru faila ģeometriju
                            if contour_gdf.intersects(polygon).any():
                                link = row['link']
                                filename = os.path.join(download_folder, f'downloaded_data_{index}.zip')
                                st.write(f"Lejupielādē failu no: {link}")
                                result = download_data(link, filename)
                                st.write(result)
                                
                                # Automātiski atvērt linku tīmekļa pārlūkā
                                webbrowser.open(link)
                            else:
                                st.write(f"Poligons {index} nepārklājas ar kontūras failu.")
                        
                        # Atjaunināt progresu
                        progress_bar.progress(int((index + 1) / total_polygons * 100))

                    st.success("Lejupielādes process pabeigts.")
                except Exception as e:
                    st.error(f"Kļūda, ielādējot SHP failu: {e}")
    else:
        st.write("Lūdzu, augšupielādē SHP, SHX un DBF failus vienlaikus.")
else:
    st.error("ZIP faila lejupielāde neizdevās.")
