import streamlit as st
import geopandas as gpd
import requests
import zipfile
import os
import shutil
import webbrowser
from io import BytesIO
from tempfile import TemporaryDirectory

# Funkcija ZIP faila izsaiņošanai
def unzip_file(zip_data, extract_to):
    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
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

# Lejupielādēt ZIP failu no GitHub
def download_zip_from_github(url):
    response = requests.get(url)
    if response.status_code == 200:
        zip_data = BytesIO(response.content)
        return zip_data
    else:
        st.error("ZIP faila lejupielāde neizdevās no GitHub.")
        return None

# Norādi saiti uz GitHub failu
!wget https://github.com/Frerjs/LAS_download/raw/main/LASMAP.zip -O LASMAP.zip

st.title("LAS failu lejupielāde no GitHub un pārklājuma noteikšana")

# Lejupielādēt ZIP failu no GitHub
st.write("Lejupielādē ZIP failu no GitHub...")
zip_data = download_zip_from_github(github_url)

# Lietotājam piedāvā augšupielādēt kontūras SHP failu
uploaded_shp = st.file_uploader("Augšupielādē savu kontūras SHP failu (SHP, SHX, DBF)", type=["shp", "shx", "dbf"])

if uploaded_shp and zip_data:
    # Izveido pagaidu direktoriju, lai uzglabātu SHP failus un izsaiņotu ZIP failu
    with TemporaryDirectory() as temp_dir:
        # Izsaiņot ZIP failu no GitHub
        unzip_file(zip_data, temp_dir)

        # Saglabāt augšupielādēto SHP failu pagaidu mapē
        shp_file_path = os.path.join(temp_dir, uploaded_shp.name)
        with open(shp_file_path, 'wb') as f:
            f.write(uploaded_shp.getbuffer())

        # Ielādēt SHP failu
        gdf = gpd.read_file(os.path.join(temp_dir, 'LASMAP.shp'))

        # Mēģināt ielādēt kontūras failu, ja visi nepieciešamie faili ir augšupielādēti
        try:
            contour_gdf = gpd.read_file(shp_file_path)

            # Piedāvā izvēlēties lejupielādes mapi
            st.write("Izvēlies mapi, kurā saglabāt lejupielādes.")
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

        except Exception as e:
            st.error(f"Radās kļūda, nolasot kontūras failu: {e}")

else:
    st.write("Lūdzu, augšupielādē kontūras SHP failu un/vai gaidi, līdz ZIP fails ir lejupielādēts.")
