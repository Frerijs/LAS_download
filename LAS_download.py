import streamlit as st
import requests
import zipfile
import os

def download_zip_from_github(url, output_filename):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/vnd.github.v3.raw'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        return True
    else:
        st.error(f"Neizdevās lejupielādēt ZIP failu no GitHub. Statusa kods: {response.status_code}")
        return False

# URL uz GitHub failu
github_url = "https://github.com/Frerjs/LAS_download/raw/main/LASMAP.zip"
output_zip_path = "LASMAP.zip"

# Lejupielādēt ZIP failu
if download_zip_from_github(github_url, output_zip_path):
    st.write(f"Fails veiksmīgi lejupielādēts: {output_zip_path}")
    
    # Izsaiņot ZIP failu
    with zipfile.ZipFile(output_zip_path, 'r') as zip_ref:
        zip_ref.extractall("extracted_files")
        st.write("ZIP fails veiksmīgi izsaiņots!")
else:
    st.write("ZIP faila lejupielāde neizdevās.")
