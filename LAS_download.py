import streamlit as st
import geopandas as gpd
import gdown
import os
import shutil
from tempfile import TemporaryDirectory

# Funkcija, lai lejupielādētu failu no Google Drive, izmantojot gdown
def download_from_google_drive(file_id, output_filename):
    try:
        download_url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(download_url, output_filename, quiet=False)
        st.success(f"Fails veiksmīgi lejupielādēts: {output_filename}")
    except Exception as e:
        st.error(f"Kļūda lejupielādējot failu: {e}")

# Funkcija, lai izveidotu *.bat failu ar atrastajām saitēm
def create_bat_file(links):
    bat_content = ""
    for link in links:
        bat_content += f'start {link}\n'
    return bat_content

# Google Drive faila ID un ZIP faila atrašanās vieta
file_id = "1Xo7gVZ2WOm6yWv6o0-jCs_OsVQZQdffQ"  # Pārliecinies, ka šis ID ir pareizs
output_zip_path = "LASMAP.zip"

# Lejupielādē ZIP failu no Google Drive
st.write("Lejupielādē ZIP failu no Google Drive...")
try:
    download_from_google_drive(file_id, output_zip_path)
    
    # Izveido pagaidu direktoriju ZIP faila izsaiņošanai
    extracted_folder = "LASMAP_extracted"
    if os.path.exists(extracted_folder):
        shutil.rmtree(extracted_folder)  # Dzēš, ja jau eksistē
    os.makedirs(extracted_folder, exist_ok=True)

    # Izsaiņo ZIP failu
    st.write("Izsaiņo ZIP failu...")
    try:
        shutil.unpack_archive(output_zip_path, extracted_folder)
        st.success("ZIP fails veiksmīgi izsaiņots!")
    except Exception as e:
        st.error(f"Kļūda izsaiņojot ZIP failu: {e}")
    
    # Ielādē SHP failu
    try:
        shp_file_path = os.path.join(extracted_folder, 'LASMAP.shp')
        gdf = gpd.read_file(shp_file_path)
        st.success("SHP fails veiksmīgi ielādēts!")
    except Exception as e:
        st.error(f"Kļūda SHP faila ielādē: {e}")

    # Lietotājam piedāvā augšupielādēt SHP komponentes failus (SHP, SHX, DBF)
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

                # Ielādē kontūras SHP failu
                shp_file_path = [f.name for f in uploaded_shp if f.name.endswith('.shp')][0]
                shp_file_path = os.path.join(temp_dir, shp_file_path)

                try:
                    contour_gdf = gpd.read_file(shp_file_path)
                    st.success("Kontūras SHP fails veiksmīgi ielādēts!")

                    # Pārbaudīt, vai kontūras ģeometrija pārklājas ar poligoniem no LASMAP
                    total_polygons = len(gdf)
                    matched_polygons = 0  # Skaitīt pārklājušos poligonus
                    links = []  # Saglabāt saites

                    # Progresjoslas izveide
                    progress_bar = st.progress(0)

                    for index, row in gdf.iterrows():
                        if 'link' in row and row['link']:  # Pārbaudīt, vai ir "link" atribūts
                            polygon = row.geometry
                            # Pārbaudīt pārklāšanos ar kontūru faila ģeometriju
                            if contour_gdf.intersects(polygon).any():
                                matched_polygons += 1
                                link = row['link']
                                links.append(link)  # Saglabāt saiti sarakstā
                                st.write(f"Atrasta saite: {link}")
                            
                            # Atjauno progresjoslu
                            progress_percentage = (index + 1) / total_polygons
                            progress_bar.progress(progress_percentage)

                    if matched_polygons == 0:
                        st.warning("Neviens poligons nepārklājās ar kontūras failu.")
                    else:
                        st.success(f"Atrasti {matched_polygons} poligoni, kas pārklājas.")
                        
                        # Izveidot BAT failu un piedāvāt to lejupielādei
                        bat_content = create_bat_file(links)
                        st.download_button(label="Lejupielādēt BAT failu", data=bat_content, file_name="open_links.bat", mime="application/octet-stream")
                        
                except Exception as e:
                    st.error(f"Kļūda, ielādējot kontūras SHP failu: {e}")
    else:
        st.warning("Lūdzu, augšupielādē SHP, SHX un DBF failus vienlaikus.")
except Exception as e:
    st.error(f"Kļūda ZIP faila lejupielādē no Google Drive: {e}")
