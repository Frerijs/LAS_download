import streamlit as st
import geopandas as gpd
import requests

# Funkcija, lai lejupielādētu failu no saites
def download_data(url, output_filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_filename, 'wb') as file:
            file.write(response.content)
        return f"Fails '{output_filename}' veiksmīgi lejuplādēts."
    else:
        return "Lejuplāde neizdevās."

# Ielādēt SHP failu bez ģeometrijas
@st.cache_data
def load_shp_file(shp_file_path):
    return gpd.read_file(shp_file_path, ignore_geometry=True)

# Ceļš uz SHP failu
shp_file_path = 'path_to_your_shp/LASMAP.shp'

# Ielādēt SHP failu
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
