import gdown
import zipfile
import os

# Google Drive faila ID
file_id = "FAILE_ID_NO_GOOGLE_DRIVE"

# Izveido tiešsaistes lejupielādes URL
download_url = f"https://drive.google.com/uc?id={file_id}"

# Norādi, kur saglabāt lejupielādēto failu
output_path = "LASMAP.zip"

# Lejupielādē ZIP failu no Google Drive
gdown.download(download_url, output_path, quiet=False)

# Izsaiņot ZIP failu
with zipfile.ZipFile(output_path, 'r') as zip_ref:
    zip_ref.extractall("extracted_files")

print("ZIP fails veiksmīgi izsaiņots!")
