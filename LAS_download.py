import streamlit as st
import geopandas as gpd
import requests
import zipfile
import os
import gdown
import shutil
import webbrowser

# Funkcija, lai lejupielādētu ZIP failu no Google Drive
def download_zip_from_google_drive(file_id, output_filename):
    download_url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(download_url, output_filename, quiet=False)

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

# Google Drive faila ID (no tavām dotajām saitēm)
file_id = "1Xo7gVZ2WOm6yWv6o0-jCs_OsVQZQdffQ"
output_zip_path = "LASMAP.zip"

# Lejupielādē ZIP failu no Google Drive
st.write("Lejupielādē ZIP failu no Google Drive...")
download_zip_from_google_drive(file_id, output_zip_path)

# Pārbaudi, vai ZIP fails tika veiksmīgi lejupielādēts
if os.path.exists(output_zip_path):
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

    # Lietotājam piedāvā augšupielādēt kontūras SHP failu
    uploaded_shp = st.file_uploader("Augšupielādē savu kontūras SHP failu (SHP, SHX, DBF)", type=["shp", "shx", "dbf"])

    if uploaded_shp:
        with TemporaryDirectory() as temp_dir:
            # Saglabāt augšupielādēto SHP failu pagaidu mapē
            shp_file_path = os.path.join(temp_dir, uploaded_shp.name)
            with open(shp_file_path, 'wb') as f:
                f.write(uploaded_shp.getbuffer())

            # Ielādēt kontūras SHP failu
            contour_gdf = gpd.read_file(shp_file_path)

            # Piedāvā izvēlēties lejupielādes mapi
            download_folder = st.text_input("Lejupielādes mape", value=os.getcwd())

            # Pārbaudīt, vai kontūras ģeometrija pārklājas ar poligoniem no LASMAP
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
            st.success("Lejupielādes process pabeigts.")
    else:
        st.write("Lūdzu, augšupielādē kontūras SHP failu.")
else:
    st.error("ZIP faila lejupielāde neizdevās.")
