import streamlit as st
import geopandas as gpd
import os
import shutil
from tempfile import TemporaryDirectory

# Funkcija, lai parādītu saites kā klikšķināmas
def display_links(links):
    for link in links:
        st.markdown(f"[Klikšķini šeit, lai atvērtu saiti]({link})")

# Google Drive faila ID
file_id = "1Xo7gVZ2WOm6yWv6o0-jCs_OsVQZQdffQ"
output_zip_path = "LASMAP.zip"

# Progresbar un pogas pievienošana
st.write("Ielādē ZIP failu no Google Drive...")
progress_message = st.empty()
progress_message.write("Sākas lejupielāde...")
# Iedomāsimies, ka ZIP fails ir ielādēts un izsaiņots šeit

# Simulācija: ģenerēti dati no "LASMAP"
extracted_folder = "LASMAP_extracted"
shp_file_path = os.path.join(extracted_folder, 'LASMAP.shp')

try:
    # Simulācija: Ielādē "LASMAP" SHP failu
    # Reālais scenārijs būtu gdf = gpd.read_file(shp_file_path)
    gdf = gpd.GeoDataFrame()  # Aizstāj šo ar īsto SHP datu ielādi
    st.write("SHP fails veiksmīgi ielādēts.")

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

                    # Pārbaudīt, vai kontūras ģeometrija pārklājas ar poligoniem no LASMAP
                    progress_bar = st.progress(0)
                    total_polygons = len(gdf)
                    matched_polygons = 0  # Skaitīt pārklājušos poligonus
                    links = []  # Saglabāt saites

                    for index, row in gdf.iterrows():
                        if 'link' in row and row['link']:  # Pārbaudīt, vai ir "link" atribūts
                            polygon = row.geometry
                            # Pārbaudīt pārklāšanos ar kontūru faila ģeometriju
                            if contour_gdf.intersects(polygon).any():
                                matched_polygons += 1
                                link = row['link']
                                links.append(link)  # Saglabāt saiti sarakstā
                                st.write(f"Atrasta saite: {link}")
                                
                            progress_bar.progress(min(int((index + 1) / total_polygons * 100), 100))

                    if matched_polygons == 0:
                        st.warning("Neviens poligons nepārklājās ar kontūras failu.")
                    else:
                        # Parādīt visas saites kā klikšķināmas
                        st.write("Atrasto saišu saraksts:")
                        display_links(links)
                        st.success(f"Atrasti {matched_polygons} poligoni, kas pārklājas.")
                except Exception as e:
                    st.error(f"Kļūda, ielādējot SHP failu: {e}")
    else:
        st.write("Lūdzu, augšupielādē SHP, SHX un DBF failus vienlaikus.")
except Exception as e:
    st.error(f"Kļūda SHP faila ielādē: {e}")
