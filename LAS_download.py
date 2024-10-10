import streamlit as st
import fiona
import zipfile
import os
import geopandas as gpd

# Funkcija ZIP faila izsaiņošanai
def unzip_file(zip_file_path, extract_to):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Ceļš uz ZIP failu
zip_file_path = 'LASMAP.zip'
extract_to = 'extracted_shp'

# Izsaiņot ZIP failu
unzip_file(zip_file_path, extract_to)

# Ceļš uz SHP failu pēc izsaiņošanas
shp_file_path = os.path.join(extract_to, 'LASMAP.shp')

# Izmēģini, vai SHP failu var atvērt ar fiona
try:
    with fiona.open(shp_file_path, 'r') as src:
        st.write(f"Fails veiksmīgi atvērts: {src.name}")
except Exception as e:
    st.write(f"Kļūda, atverot SHP failu: {e}")

# Mēģini ielādēt SHP failu ar geopandas, ja tas atveras
try:
    gdf = gpd.read_file(shp_file_path)
    st.write(gdf.head())
except Exception as e:
    st.write(f"Kļūda, nolasot SHP failu ar GeoPandas: {e}")
