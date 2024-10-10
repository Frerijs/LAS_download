import streamlit as st
import geopandas as gpd
import requests
import zipfile
import os

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

# Ceļš uz ZIP failu
zip_file_path = 'LASMAP.zip'
extract_to = 'extracted_shp'

# Izsaiņot ZIP failu
unzip_file(zip_file_path, extract_to)

# Ceļš uz SHP failu pēc izsaiņošanas
shp_file_path = os.path.join(extract_to, 'LASMAP.shp')

# Ielādēt SHP failu
@st.cache_data
def load_shp_file(shp_file_path):
    return gpd.read_file(shp_file_path, ignore_geometry=True)

gdf = load_shp_file(shp_file_path)

# Izvēlēties poligonu, pēc kura lejuplādēt datus
st.title("Poligonu datu lejupielāde")
selected_polygon = st.selectbox("Izvēlies poligonu", gdf.index)

# Parādīt izvēlētā poligona atribūtus
polygon_data = gdf.iloc[selected_polygon]
st.write("Poligona dati:", polygon_data)

# Iegūt saiti no 'link' atribūta
if 'link' in polygon_data:
    link = polygon_data['link']
    st.write(f"Lejupielādes saite: {link}")
    
    # Poga lejupielādēšanai
    if st.button("Lejupielādēt datus"):
        filename = f"downloaded_data_{selected_polygon}.zip"  # Vai cits nosaukums
        result = download_data(link, filename)
        st.write(result)
else:
    st.write("Šim poligonam nav 'link' atribūta.")
