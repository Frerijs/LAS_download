import streamlit as st
import geopandas as gpd
import requests
import zipfile
import os
import shutil
import webbrowser

# Funkcija, lai lejupielādētu failu
def download_data(url, output_filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_filename, 'wb') as file:
            file.write(response.content)
        st.write(f"Fails '{output_filename}' veiksmīgi lejuplādēts.")
    else:
        st.write(f"Lejupielāde neizdevās: {url}")

# Funkcija ZIP faila izsaiņošanai
def unzip_file(zip_file_path, extract_to):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    st.write(f"ZIP fails izsaiņots uz: {extract_to}")

# Pārējais kods

# Google Drive faila ID un cita loģika

# Šeit tiek izpildītas visas lejupielādes, kad lietotājs apstiprina vienu saiti
def download_all_links(links, download_folder):
    for i, link in enumerate(links):
        filename = os.path.join(download_folder, f'downloaded_data_{i}.las')
        st.write(f"Lejupielādē failu no: {link}")
        download_data(link, filename)

# Galvenā daļa ...
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

            # Piedāvā izvēlēties lejupielādes mapi
            download_folder = st.text_input("Ievadi lejupielādes mapi:", value=os.getcwd())
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            # Atrasto saišu saglabāšana
            links = []

            # Pārbaudīt, vai kontūras ģeometrija pārklājas ar poligoniem no LASMAP
            total_polygons = len(gdf)
            progress_bar = st.progress(0)

            for index, row in gdf.iterrows():
                if 'link' in row and row['link']:  # Pārbaudīt, vai ir "link" atribūts
                    polygon = row.geometry
                    # Pārbaudīt pārklāšanos ar kontūru faila ģeometriju
                    if contour_gdf.intersects(polygon).any():
                        link = row['link']
                        links.append(link)  # Pievienot saiti sarakstam
                        st.write(f"Atrasts pārklājums. Saites: {link}")
                        
                    progress_bar.progress(int((index + 1) / total_polygons * 100))

            # Ja atrastas saites, piedāvā pabeigt visas lejupielādes
            if links:
                if st.button("Apstiprināt un lejupielādēt visus failus"):
                    download_all_links(links, download_folder)
            else:
                st.warning("Neviens poligons nepārklājās ar kontūras failu.")
        except Exception as e:
            st.error(f"Kļūda, ielādējot SHP failu: {e}")
else:
    st.write("Lūdzu, augšupielādē SHP, SHX un DBF failus vienlaikus.")
