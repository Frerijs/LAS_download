import gdown
import os

# Funkcija, lai lejupielādētu failu no Google Drive
def download_file_from_google_drive(file_id, output_path):
    download_url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(download_url, output_path, quiet=False)

# Lejupielādē katru no SHP komponentēm
file_ids = {
    "LASMAP.shp": "ID_FOR_SHP_FILE",
    "LASMAP.dbf": "ID_FOR_DBF_FILE",
    "LASMAP.shx": "ID_FOR_SHX_FILE",
    "LASMAP.prj": "ID_FOR_PRJ_FILE",
    "LASMAP.cpg": "ID_FOR_CPG_FILE"
}

# Izveido direktoriju failu saglabāšanai
output_dir = "LASMAP_files"
os.makedirs(output_dir, exist_ok=True)

# Lejupielādēt visus failus
for filename, file_id in file_ids.items():
    output_path = os.path.join(output_dir, filename)
    download_file_from_google_drive(file_id, output_path)

print("Visi faili veiksmīgi lejupielādēti!")
